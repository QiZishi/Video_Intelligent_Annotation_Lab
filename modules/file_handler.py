import os
import json
import jsonlines
import shutil
import cv2
import sys
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QProgressDialog
from PyQt5.QtCore import QObject, pyqtSignal, Qt
import traceback  # 引入 traceback 模块

def resource_path(relative_path):
    """获取资源的绝对路径，兼容开发环境和打包后的环境"""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class FileHandler(QObject):
    """文件处理器，负责文件和文件夹的操作"""
    
    # 定义信号
    loading_started = pyqtSignal()  # 加载开始信号
    loading_finished = pyqtSignal(str, list, list, str, str)  # 加载完成信号(视频路径, 图片列表, 已有标注列表, 视频描述, 文件夹名称)
    
    def __init__(self):
        super().__init__()
        self.current_folder_index = -1
        self.folders = []
        self.data_folder_name = ""  # 当前导入的数据文件夹名称
        self.output_folder = self.get_output_folder_from_settings()
        self.output_jsonl = []  # 存储从文件加载或新生成的jsonl数据
        self.api_config = self._load_api_config()  # 加载API配置以获取human_prompt_template

    def _load_api_config(self):
        """加载API配置文件以获取模板"""
        # 使用resource_path函数正确构建配置文件路径
        default_config_path = resource_path("config/default_api_config.json")
        user_config_path = resource_path("config/user_api_config.json")
        default_config = {
            "human_prompt_template": "<image>\n<填入用户提问> "
        }

        # 打印调试信息
        print(f"尝试加载配置文件，默认配置路径: {default_config_path}")
        print(f"用户配置路径: {user_config_path}")

        config_to_load = default_config_path
        if os.path.exists(user_config_path):
            config_to_load = user_config_path

        try:
            with open(config_to_load, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
                if "human_prompt_template" not in loaded_config:
                    loaded_config["human_prompt_template"] = default_config["human_prompt_template"]
                return loaded_config
        except Exception as e:
            print(f"加载API配置时出错: {e}, 使用默认配置。")
            try:
                with open(default_config_path, 'r', encoding='utf-8') as f:
                    default_cfg_content = json.load(f)
                    if "human_prompt_template" not in default_cfg_content:
                        default_cfg_content["human_prompt_template"] = default_config["human_prompt_template"]
                    return default_cfg_content
            except:
                return default_config

    def get_output_folder_from_settings(self):
        """从配置文件读取输出文件夹设置"""
        default_output_folder = os.path.join(os.path.expanduser("~"), "Desktop", "视频标注结果")
        # 使用resource_path函数正确构建配置文件路径
        settings_file = resource_path("config/output_folder_config.json")
        
        print(f"尝试加载输出文件夹配置: {settings_file}")
        
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    if "output_folder" in settings and os.path.exists(settings["output_folder"]):
                        return settings["output_folder"]
            except Exception as e:
                print(f"读取输出文件夹配置失败: {str(e)}")
        os.makedirs(default_output_folder, exist_ok=True)
        return default_output_folder

    def import_folder(self, parent=None):
        """
        导入数据文件夹，并根据输出文件确定起始点
        
        Args:
            parent: 父窗口对象
            
        Returns:
            tuple: (文件夹列表, 起始索引, 加载的输出数据)
        """
        folder_path = QFileDialog.getExistingDirectory(parent, "选择数据文件夹")
        if not folder_path:
            return [], -1, []
            
        progress = QProgressDialog("正在扫描文件夹...", None, 0, 0, parent)
        progress.setWindowTitle("导入数据")
        progress.setWindowModality(Qt.WindowModal)
        progress.setCancelButton(None)
        progress.setMinimumDuration(0)
        progress.show()
            
        self.data_folder_name = os.path.basename(folder_path)
        
        folders = []
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            if os.path.isdir(item_path):
                has_video = False
                for file in os.listdir(item_path):
                    if file.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                        has_video = True
                        break
                if has_video:
                    folders.append(item_path)
                
        if not folders:
            progress.close()
            QMessageBox.warning(parent, "警告", "所选文件夹中没有包含视频文件的子文件夹")
            return [], -1, []
            
        output_data_folder = os.path.join(self.output_folder, self.data_folder_name)
        jsonl_path = os.path.join(output_data_folder, f"{self.data_folder_name}.jsonl")
        start_index = 0
        self.output_jsonl = []

        if os.path.exists(jsonl_path):
            try:
                with jsonlines.open(jsonl_path, mode='r') as reader:
                    self.output_jsonl = [entry for entry in reader]
                    
                processed_videos = set()
                for entry in self.output_jsonl:
                    video_path = entry.get("video", "")
                    if video_path.startswith("videos/"):
                        video_name = video_path[7:]
                        processed_videos.add(video_name)
                
                found_unprocessed = False
                for i, folder in enumerate(folders):
                    has_unprocessed_video_in_folder = False
                    for file in os.listdir(folder):
                        if file.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                            if file not in processed_videos:
                                start_index = i
                                found_unprocessed = True
                                has_unprocessed_video_in_folder = True
                                break
                    if has_unprocessed_video_in_folder:
                        break

                if not found_unprocessed and folders:
                    start_index = len(folders)

            except Exception as e:
                print(f"读取或解析标注数据出错: {str(e)}")
                QMessageBox.warning(parent, "警告", f"读取现有标注文件失败: {str(e)}\n将从第一个文件夹开始。")
                start_index = 0
                self.output_jsonl = []
        else:
            start_index = 0
            self.output_jsonl = []

        progress.close()
        self.folders = folders
        return self.folders, start_index, self.output_jsonl

    def load_next_folder(self, current_index, folders, parent=None):
        """
        查找并加载下一个未处理的文件夹索引
        
        Args:
            current_index: 当前文件夹索引
            folders: 文件夹列表
            parent: 父窗口对象 (可选)
            
        Returns:
            int: 下一个未处理文件夹的索引，如果没有则返回 len(folders)
        """
        if not folders:
            return 0

        output_data_folder = os.path.join(self.output_folder, self.data_folder_name)
        jsonl_path = os.path.join(output_data_folder, f"{self.data_folder_name}.jsonl")
        processed_videos = set()
        if os.path.exists(jsonl_path):
            try:
                with jsonlines.open(jsonl_path, mode='r') as reader:
                    self.output_jsonl = [entry for entry in reader]
                for entry in self.output_jsonl:
                    video_path = entry.get("video", "")
                    if video_path.startswith("videos/"):
                        processed_videos.add(video_path[7:])
            except Exception as e:
                print(f"查找下一个文件夹时读取jsonl失败: {str(e)}")
                pass

        next_index = len(folders)
        for i in range(current_index + 1, len(folders)):
            folder = folders[i]
            has_unprocessed_video_in_folder = False
            for file in os.listdir(folder):
                if file.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                    if file not in processed_videos:
                        next_index = i
                        has_unprocessed_video_in_folder = True
                        break
            if has_unprocessed_video_in_folder:
                break

        return next_index

    def parse_annotation_line(self, line):
        """解析单行标注数据，更加健壮地处理各种格式"""
        try:
            line = line.strip()
            if not line:
                return None
                
            # 调试信息
            print(f"正在解析标注行: {line}")
            
            # 确认行中包含时间范围的分隔符"-"
            if '-' not in line:
                print(f"警告: 标注行缺少时间范围分隔符'-': {line}")
                return None
                
            # 提取时间范围和标签
            time_range_part = line
            label_part = ""
            
            # 处理带有标签的情况（用冒号分隔）
            if ':' in line:
                # 找到第一个"-"后面的第一个":"，确保正确分割时间范围和标签
                dash_index = line.find('-')
                post_dash_colon = line.find(':', dash_index)
                
                if post_dash_colon > dash_index:
                    # 时间范围部分包含冒号，需要特别处理（例如 00:00:01-00:00:05: 标签）
                    time_range_part = line[:post_dash_colon]
                    label_part = line[post_dash_colon+1:].strip()
                else:
                    # 简单情况，只在时间范围后有一个冒号（例如 00:01-00:05: 标签）
                    parts = line.split(':', 1)
                    time_range_part = parts[0].strip()
                    if len(parts) > 1:
                        label_part = parts[1].strip()
            
            # 解析时间范围
            if '-' in time_range_part:
                time_parts = time_range_part.split('-', 1)
                start_time = time_parts[0].strip()
                end_time = time_parts[1].strip()
                
                # 确保时间格式有效
                if not start_time or not end_time:
                    print(f"警告: 无效的时间范围格式: {time_range_part}")
                    return None
                    
                return {
                    'start_time': start_time,
                    'end_time': end_time,
                    'label': label_part
                }
                    
            return None
        except Exception as e:
            print(f"解析标注行时出错: {str(e)}, 行: {line}")
            return None



    def load_folder_by_index(self, folder_index, folders, viewing_history_entry=None, parent=None):
        """
        按索引加载指定文件夹的数据。优先从传入的 history_entry 或 self.output_jsonl 加载标注信息。
        
        Args:
            folder_index: 文件夹索引
            folders: 文件夹列表
            viewing_history_entry: (可选) 正在查看的历史记录条目
            parent: 父窗口对象
            
        Returns:
            tuple: (索引, 视频路径, 图片列表, 标注列表, 视频描述, 诊断结果)
        """
        if not folders or folder_index < 0 or folder_index >= len(folders):
            return folder_index, "", [], [], "", ""
            
        current_folder = folders[folder_index]
        
        progress = QProgressDialog("正在加载数据...", None, 0, 0, parent)
        progress.setWindowTitle("加载文件夹")
        progress.setWindowModality(Qt.WindowModal)
        progress.setCancelButton(None)
        progress.setMinimumDuration(0)
        progress.show()
        
        video_path = ""
        video_name = ""
        for file in os.listdir(current_folder):
            if file.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                video_path = os.path.join(current_folder, file)
                video_name = file
                break
                
        image_paths = []
        for file in os.listdir(current_folder):
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                image_paths.append(os.path.join(current_folder, file))

        annotations = []
        video_desc = ""
        final_diag = ""
        
        entry_to_load = viewing_history_entry

        if not entry_to_load and video_name:
            for entry in self.output_jsonl:
                if entry.get("video") == f"videos/{video_name}":
                    entry_to_load = entry
                    break

        if entry_to_load:
            try:
                raw_desc = entry_to_load.get('raw_description', '')
                if raw_desc:
                    print(f"解析raw_description: {raw_desc[:100]}...")  # 只打印前100个字符作为调试
                    
                    # 提取诊断结果
                    diag_parts = raw_desc.split('\n\n最终诊断结果:', 1)
                    desc_content = diag_parts[0].strip()
                    if len(diag_parts) > 1:
                        final_diag = diag_parts[1].strip()
                    else:
                        desc_content = raw_desc.strip()
                        final_diag = ""

                    # 提取视频描述和标注片段
                    anno_parts = desc_content.split('\n\n标注片段:', 1)
                    if len(anno_parts) > 1:
                        # 提取视频描述
                        if '视频总描述:' in anno_parts[0]:
                            video_desc = anno_parts[0].split('视频总描述:', 1)[1].strip()
                        else:
                            video_desc = anno_parts[0].strip()

                        # 处理标注片段
                        annotation_text = anno_parts[1].strip()
                        if annotation_text:
                            annotation_lines = annotation_text.split('\n')
                            print(f"找到 {len(annotation_lines)} 行标注数据")
                            
                            for line in annotation_lines:
                                annotation = self.parse_annotation_line(line)
                                if annotation:
                                    annotations.append(annotation)
                                    
                            print(f"成功解析 {len(annotations)} 个标注")
                    else:
                        # 没有标注片段部分
                        if '视频总描述:' in desc_content:
                            video_desc = desc_content.split('视频总描述:', 1)[1].strip()
                        else:
                            video_desc = desc_content
                        annotations = []
                else:
                    video_desc = ""
                    final_diag = ""
                    annotations = []

            except Exception as e:
                print(f"从JSONL条目解析数据时出错: {str(e)}")
                traceback.print_exc()
                annotations = []
                video_desc = ""
                final_diag = ""

        progress.close()
        return folder_index, video_path, image_paths, annotations, video_desc, final_diag
        
    def generate_annotation_data(self, video_path, annotations, video_description, 
                                   final_diagnosis, thinking_chain, ai_answer, parent=None):
        """
        生成单个 JSONL 条目数据结构（不写入文件，不复制视频）
        
        Args:
            video_path: 视频文件路径
            annotations: 视频标注列表
            video_description: 视频总描述
            final_diagnosis: 最终诊断结果
            thinking_chain: 思维链
            ai_answer: AI回答
            parent: 父窗口对象 (可选)
            
        Returns:
            dict: 生成的 JSONL 条目字典，如果出错则返回 None
        """
        try:
            if not video_path or not os.path.exists(video_path):
                QMessageBox.warning(parent, "警告", "视频文件不存在")
                return None
            
            duration = round(self.get_video_duration(video_path), 3)
            video_name = os.path.basename(video_path)
            
            if not hasattr(self, 'data_folder_name') or not self.data_folder_name:
                parent_folder = os.path.dirname(os.path.dirname(video_path))
                self.data_folder_name = os.path.basename(parent_folder)
                if not self.data_folder_name:
                    self.data_folder_name = "video_annotations"
            
            formatted_annotations = "\n".join([
                f"{a['start_time']}-{a['end_time']}: {a['label']}" 
                for a in annotations
            ])
            
            description_parts = []
            if video_description:
                description_parts.append(f"视频总描述:\n{video_description}")
            if formatted_annotations:
                description_parts.append(f"标注片段:\n{formatted_annotations}")
            
            description = "\n\n".join(description_parts)
            
            ai_response = f"<think>\n{thinking_chain}\n</think>\n\n<answer>\n{ai_answer}\n</answer>"
            
            human_prompt = self.api_config.get("human_prompt_template", "<image>\n<填入用户提问> ")

            jsonl_entry = {
                "video": f"videos/{video_name}",
                "conversations": [
                    {"from": "human", "value": human_prompt},
                    {"from": "gpt", "value": ai_response}
                ],
                "duration": duration,
                "raw_description": f"{description}\n\n最终诊断结果: {final_diagnosis}"
            }
            
            return jsonl_entry
                
        except Exception as e:
            QMessageBox.critical(parent, "错误", f"生成标注数据结构时出错: {str(e)}")
            traceback.print_exc()
            return None

    def get_video_duration(self, video_path):
        """获取视频时长（秒）"""
        if not os.path.exists(video_path):
            return 0
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return 0
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        if fps <= 0:
            return 0
        
        duration = frame_count / fps
        cap.release()
        
        return duration

    def save_annotation_data(self, new_entry, parent=None):
        """
        将新的或更新的标注条目保存到输出 JSONL 文件，并复制对应的视频文件。
        会覆盖写入整个 JSONL 文件。
        
        Args:
            new_entry: 要保存或更新的单个 JSONL 条目字典
            parent: 父窗口对象
            
        Returns:
            bool: 是否成功保存
        """
        if not new_entry:
            QMessageBox.warning(parent, "警告", "没有有效的标注条目可保存")
            return False
            
        try:
            progress = QProgressDialog("正在保存数据...", None, 0, 0, parent)
            progress.setWindowTitle("保存数据")
            progress.setWindowModality(Qt.WindowModal)
            progress.setCancelButton(None)
            progress.setMinimumDuration(0)
            progress.show()
            
            video_field = new_entry.get("video", "")
            if not video_field.startswith("videos/"):
                QMessageBox.warning(parent, "警告", "无效的视频字段格式")
                progress.close()
                return False
                
            video_name = video_field[7:]
            
            if not hasattr(self, 'data_folder_name') or not self.data_folder_name:
                 self.data_folder_name = "video_annotations"
                 print("警告: data_folder_name 未设置，使用默认值 'video_annotations'")

            output_data_folder = os.path.join(self.output_folder, self.data_folder_name)
            os.makedirs(output_data_folder, exist_ok=True)
            videos_folder = os.path.join(output_data_folder, "videos")
            os.makedirs(videos_folder, exist_ok=True)
            
            output_video_path = os.path.join(videos_folder, video_name)
            src_video_path = None
            if hasattr(self, 'folders') and self.folders:
                for folder in self.folders:
                    potential_src = os.path.join(folder, video_name)
                    if os.path.exists(potential_src):
                        src_video_path = potential_src
                        break
            
            if src_video_path:
                if not os.path.exists(output_video_path) or os.path.getmtime(src_video_path) > os.path.getmtime(output_video_path):
                    try:
                        shutil.copy2(src_video_path, output_video_path)
                        print(f"视频文件已复制到: {output_video_path}")
                    except Exception as copy_err:
                        QMessageBox.warning(parent, "警告", f"复制视频文件失败: {str(copy_err)}\n标注数据仍会尝试保存。")
            else:
                QMessageBox.warning(parent, "警告", f"未找到源视频文件 '{video_name}' 用于复制。")

            jsonl_path = os.path.join(output_data_folder, f"{self.data_folder_name}.jsonl")
            
            existing_entries = []
            if os.path.exists(jsonl_path):
                try:
                    with jsonlines.open(jsonl_path, mode='r') as reader:
                        existing_entries = [entry for entry in reader]
                except Exception as read_err:
                    print(f"读取现有 JSONL 文件失败: {read_err}")

            found_existing = False
            for i, entry in enumerate(existing_entries):
                if entry.get("video") == video_field:
                    new_entry["id"] = entry.get("id", i + 1)
                    existing_entries[i] = new_entry
                    found_existing = True
                    break
            
            if not found_existing:
                new_entry["id"] = len(existing_entries) + 1
                existing_entries.append(new_entry)

            try:
                with jsonlines.open(jsonl_path, mode='w') as writer:
                    existing_entries.sort(key=lambda x: x.get("id", float('inf')))
                    for item in existing_entries:
                        writer.write(item)
                print(f"JSONL 数据已保存到: {jsonl_path}")
            except Exception as write_err:
                 progress.close()
                 QMessageBox.critical(parent, "错误", f"写入 JSONL 文件失败: {str(write_err)}")
                 traceback.print_exc()
                 return False
                    
            progress.close()
            self.output_jsonl = existing_entries
            return True
            
        except Exception as e:
            if 'progress' in locals() and progress:
                progress.close()
            QMessageBox.critical(parent, "错误", f"保存数据时发生意外错误: {str(e)}")
            traceback.print_exc()
            return False




