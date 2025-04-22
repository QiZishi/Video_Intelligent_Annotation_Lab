import os
import json
import random
import sys
from openai import OpenAI
from PyQt5.QtWidgets import (QMessageBox, QProgressDialog, QDialog, QVBoxLayout, QHBoxLayout, 
                            QFormLayout, QLineEdit, QDialogButtonBox, QLabel, QGroupBox,
                            QPushButton, QComboBox, QTextEdit, QFileDialog, QApplication)
from PyQt5.QtCore import Qt, QSize

# 添加资源路径处理函数
def resource_path(relative_path):
    """获取资源的绝对路径，兼容开发环境和打包后的环境"""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# 默认配置
DEFAULT_CONFIG = {
    "api_keys": [
        "your_api_key_here"
    ],
    "api_base": "https://api.deepseek.com",
    "model": "deepseek-reasoner",
    "system_prompt": "填入系统提示语",
    "user_prompt_template": "{description}\n\n视频诊断结果为：{final_diagnosis}\n\n以上是你观察到的视频内容，现在请基于你的观察结果，详细思考分析<填入用户需求>？",
    "human_prompt_template": "<image>\n分析所给的视频,告诉我<填入用户需求> "
}

# 配置文件路径，使用resource_path
DEFAULT_CONFIG_PATH = resource_path("config/default_api_config.json")
USER_CONFIG_PATH = resource_path("config/user_api_config.json")

# 打印调试信息
print(f"API配置路径: DEFAULT={DEFAULT_CONFIG_PATH}, USER={USER_CONFIG_PATH}")

class ModelSettingsDialog(QDialog):
    """模型参数设置对话框"""
    
    def __init__(self, api_handler, parent=None):
        super().__init__(parent)
        self.api_handler = api_handler
        loaded_config = self.api_handler.get_config()
        self.config = DEFAULT_CONFIG.copy()
        self.config.update(loaded_config)
        
        self.setWindowTitle("模型参数设置")
        self.resize(700, 650)
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
                border-radius: 10px;
            }
            QLabel {
                color: #333;
                font-size: 13px;
            }
            QLineEdit, QTextEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
                font-size: 13px;
            }
            QLineEdit:focus, QTextEdit:focus {
                border: 1px solid #3498db;
                background-color: #f0f7fc;
            }
            QPushButton {
                background-color: #4a86e8;
                color: white;
                border-radius: 6px;
                padding: 8px 15px;
                font-size: 13px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #3a76d8;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ddd;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                color: #2980b9;
                font-size: 14px;
            }
        """)
        
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 连接设置
        connection_group = QGroupBox("连接设置")
        connection_layout = QVBoxLayout()
        
        # API设置表单
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        # API Base URL
        self.api_base_edit = QLineEdit(self.config["api_base"])
        form_layout.addRow("API Base URL:", self.api_base_edit)
        
        # 模型名称
        self.model_edit = QLineEdit(self.config["model"])
        form_layout.addRow("模型名称:", self.model_edit)
        
        # API Key （只显示一个或部分内容）
        self.api_key_edit = QLineEdit()
        if self.config["api_keys"]:
            key_preview = f"{self.config['api_keys'][0][:10]}******"
            self.api_key_edit.setPlaceholderText(f"当前有 {len(self.config['api_keys'])} 个API密钥")
        else:
            self.api_key_edit.setPlaceholderText("请添加API密钥")
        self.api_key_edit.setEchoMode(QLineEdit.Password)
        
        # API密钥操作区
        api_key_layout = QHBoxLayout()
        api_key_layout.addWidget(self.api_key_edit)
        
        # 添加API密钥按钮
        add_key_button = QPushButton("添加密钥")
        add_key_button.clicked.connect(self.add_api_key)
        api_key_layout.addWidget(add_key_button)
        
        # 清空所有密钥按钮
        clear_keys_button = QPushButton("清空密钥")
        clear_keys_button.clicked.connect(self.clear_api_keys)
        clear_keys_button.setStyleSheet("background-color: #e74c3c;")
        api_key_layout.addWidget(clear_keys_button)
        
        form_layout.addRow("API密钥:", api_key_layout)
        connection_layout.addLayout(form_layout)
        connection_group.setLayout(connection_layout)
        layout.addWidget(connection_group)
        
        # 提示语设置
        prompt_group = QGroupBox("提示语设置")
        prompt_layout = QVBoxLayout()
        prompt_layout.setSpacing(10)
        
        # 系统提示语
        system_prompt_label = QLabel("系统提示语:")
        prompt_layout.addWidget(system_prompt_label)
        
        self.system_prompt_edit = QTextEdit()
        self.system_prompt_edit.setPlainText(self.config["system_prompt"])
        self.system_prompt_edit.setMinimumHeight(60)
        prompt_layout.addWidget(self.system_prompt_edit)
        
        # 用户提示语模板
        user_prompt_label = QLabel("用户提示语模板:")
        prompt_layout.addWidget(user_prompt_label)
        
        self.user_prompt_edit = QTextEdit()
        self.user_prompt_edit.setPlainText(self.config["user_prompt_template"])
        self.user_prompt_edit.setMinimumHeight(80)
        prompt_layout.addWidget(self.user_prompt_edit)
        
        template_info = QLabel("提示: 在模板中使用 {description} 和 {final_diagnosis} 作为视频描述和诊断结果的占位符")
        template_info.setStyleSheet("color: #7f8c8d; font-style: italic; font-size: 12px;")
        prompt_layout.addWidget(template_info)
        
        # 人类提问模板
        human_prompt_label = QLabel("人类提问模板:")
        prompt_layout.addWidget(human_prompt_label)
        
        self.human_prompt_edit = QTextEdit()
        self.human_prompt_edit.setPlainText(self.config.get("human_prompt_template", DEFAULT_CONFIG["human_prompt_template"]))
        self.human_prompt_edit.setMinimumHeight(60)
        prompt_layout.addWidget(self.human_prompt_edit)
        
        human_template_info = QLabel("提示: 这是保存在JSONL文件中 'conversations' 里 'human' 角色的 'value' 内容。")
        human_template_info.setStyleSheet("color: #7f8c8d; font-style: italic; font-size: 12px;")
        prompt_layout.addWidget(human_template_info)
        
        prompt_group.setLayout(prompt_layout)
        layout.addWidget(prompt_group)
        
        # 说明信息
        info_label = QLabel("说明: 本软件仅支持符合OpenAI API格式的模型调用，请确保您设置的API提供商支持该格式。")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #7f8c8d; padding: 10px; background-color: #f0f0f0; border-radius: 4px;")
        layout.addWidget(info_label)
        
        # 重置和保存按钮
        button_layout = QHBoxLayout()
        
        reset_button = QPushButton("恢复默认设置")
        reset_button.clicked.connect(self.reset_defaults)
        reset_button.setStyleSheet("""
            QPushButton {
                background-color: #7f8c8d;
                color: white;
            }
            QPushButton:hover {
                background-color: #6f7c7d;
            }
        """)
        button_layout.addWidget(reset_button)
        
        button_layout.addStretch()
        
        # 对话框按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.button(QDialogButtonBox.Ok).setText("保存设置")
        button_box.button(QDialogButtonBox.Cancel).setText("取消")
        button_box.accepted.connect(self.save_settings)
        button_box.rejected.connect(self.reject)
        button_layout.addWidget(button_box)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def add_api_key(self):
        """添加新的API密钥"""
        api_key = self.api_key_edit.text().strip()
        if not api_key:
            QMessageBox.warning(self, "警告", "请输入有效的API密钥")
            return
            
        # 添加新密钥
        if "api_keys" not in self.config:
            self.config["api_keys"] = []
            
        self.config["api_keys"].append(api_key)
        
        # 更新显示
        self.api_key_edit.clear()
        self.api_key_edit.setPlaceholderText(f"当前有 {len(self.config['api_keys'])} 个API密钥")
        
        QMessageBox.information(self, "成功", "API密钥已添加")
    
    def clear_api_keys(self):
        """清空所有API密钥"""
        reply = QMessageBox.question(self, "确认",
                                    "确定要清空所有API密钥吗？",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.config["api_keys"] = []
            self.api_key_edit.setPlaceholderText("请添加API密钥")
            QMessageBox.information(self, "成功", "已清空所有API密钥")
    
    def reset_defaults(self):
        """重置为默认设置"""
        reply = QMessageBox.question(self, "确认",
                                    "确定要恢复默认设置吗？这将覆盖所有当前配置。",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.config = DEFAULT_CONFIG.copy()
            
            # 更新界面
            self.api_base_edit.setText(self.config["api_base"])
            self.model_edit.setText(self.config["model"])
            self.system_prompt_edit.setPlainText(self.config["system_prompt"])
            self.user_prompt_edit.setPlainText(self.config["user_prompt_template"])
            self.human_prompt_edit.setPlainText(self.config["human_prompt_template"])
            
            if self.config["api_keys"]:
                key_preview = f"{self.config['api_keys'][0][:10]}******"
                self.api_key_edit.setPlaceholderText(f"当前有 {len(self.config['api_keys'])} 个API密钥")
            else:
                self.api_key_edit.setPlaceholderText("请添加API密钥")
                
            QMessageBox.information(self, "成功", "已恢复默认设置")
    
    def save_settings(self):
        """保存设置"""
        # 收集界面上的设置
        api_base = self.api_base_edit.text().strip()
        model = self.model_edit.text().strip()
        system_prompt = self.system_prompt_edit.toPlainText().strip()
        user_prompt_template = self.user_prompt_edit.toPlainText().strip()
        human_prompt_template = self.human_prompt_edit.toPlainText().strip()
        
        # 验证必填字段
        if not api_base or not model:
            QMessageBox.warning(self, "错误", "API Base URL 和模型名称不能为空")
            return
            
        # 更新配置
        self.config["api_base"] = api_base
        self.config["model"] = model
        self.config["system_prompt"] = system_prompt
        self.config["user_prompt_template"] = user_prompt_template
        self.config["human_prompt_template"] = human_prompt_template
        
        # 保存配置
        self.api_handler.set_config(self.config)
        
        # 关闭对话框
        self.accept()


class APIHandler:
    """API处理类，负责与LLM API交互"""
    
    def __init__(self):
        """初始化API处理器，加载配置"""
        self.config = self._load_config()
        
    def _load_config(self):
        """加载配置文件"""
        # 确保配置目录存在
        config_dir = os.path.dirname(DEFAULT_CONFIG_PATH)
        os.makedirs(config_dir, exist_ok=True)
        
        # 如果用户配置不存在，尝试创建默认配置文件
        if not os.path.exists(DEFAULT_CONFIG_PATH):
            try:
                with open(DEFAULT_CONFIG_PATH, 'w', encoding='utf-8') as f:
                    json.dump(DEFAULT_CONFIG, f, indent=4, ensure_ascii=False)
            except Exception as e:
                print(f"无法创建默认配置文件: {e}")
        
        # 首先尝试加载用户配置
        if os.path.exists(USER_CONFIG_PATH):
            try:
                with open(USER_CONFIG_PATH, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # 验证配置有效性
                for key in DEFAULT_CONFIG:
                    if key not in config:
                        config[key] = DEFAULT_CONFIG[key]
                return config
            except Exception as e:
                print(f"加载用户配置出错: {e}")
        
        # 如果用户配置无效，使用默认配置
        return DEFAULT_CONFIG.copy()
    
    def save_config(self, config_path=None):
        """保存当前配置"""
        if config_path is None:
            config_path = USER_CONFIG_PATH
            
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存配置出错: {e}")
            return False
    
    def get_config(self):
        """获取当前配置"""
        return self.config.copy()
    
    def set_config(self, config):
        """设置并保存配置"""
        self.config = config
        return self.save_config()
    
    def reset_to_defaults(self):
        """重置为默认配置"""
        self.config = DEFAULT_CONFIG.copy()
        return self.save_config()
    
    def call_api(self, description, final_diagnosis, parent=None):
            """
            调用API生成推理数据
            
            Args:
                description: 视频描述内容，包含标注片段和总描述
                final_diagnosis: 医生给出的最终诊断结果
                parent: 父窗口对象，用于显示进度对话框
                
            Returns:
                dict: 包含reasoning_content和content的字典
            """
            # 显示进度对话框
            progress = None
            
            # 检查API密钥
            if not self.config.get("api_keys"):
                QMessageBox.warning(parent, "API调用失败", "未设置API密钥，请先在模型参数设置中添加密钥。")
                return {
                    "reasoning": "未设置API密钥",
                    "answer": "无法获取分析结果，缺少API密钥。"
                }
            
            # 使用QProgressDialog代替QMessageBox作为进度指示器
            if parent:
                progress = QProgressDialog("AI模型正在生成标注数据，请耐心等待...", None, 0, 0, parent)
                progress.setWindowTitle("数据生成")
                progress.setCancelButton(None)  # 禁用取消按钮
                progress.setWindowModality(Qt.NonModal)  # 设为非模态对话框
                progress.setMinimumDuration(500)  # 只有操作超过500ms才显示
                progress.show()
                QApplication.processEvents()  # 确保UI更新
            
            # 随机选择一个API密钥
            api_key = random.choice(self.config.get("api_keys", DEFAULT_CONFIG["api_keys"]))
            api_base = self.config.get("api_base", DEFAULT_CONFIG["api_base"])
            model = self.config.get("model", DEFAULT_CONFIG["model"])
    
            try:
                client = OpenAI(api_key=api_key, base_url=api_base)
    
                # 使用自定义提示语模板格式化用户提示语
                user_prompt_template = self.config.get("user_prompt_template", DEFAULT_CONFIG["user_prompt_template"])
                user_prompt = user_prompt_template.format(
                    description=description,
                    final_diagnosis=final_diagnosis
                )
                
                # 使用自定义系统提示语
                system_prompt = self.config.get("system_prompt", DEFAULT_CONFIG["system_prompt"])
    
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                )
    
                # 提取结果，兼容不同的API返回格式
                if api_base == "https://api.deepseek.com":
                    # DeepSeek API返回格式
                    try:
                        reasoning_content = response.choices[0].message.reasoning_content
                    except AttributeError:
                        # 如果不支持reasoning_content，尝试从message中提取
                        reasoning_content = ""
                    content = response.choices[0].message.content
                elif api_base == "https://api.wisediag.com/v1":
                    # WiseDiag API返回格式
                    model_output = response.choices[0].message.content
                    if "```thinking" in model_output and "```" in model_output.split("```thinking")[1]:
                        # 提取思维链 (在```thinking和下一个```之间的内容)
                        thinking_start = model_output.find("```thinking") + len("```thinking")
                        thinking_end = model_output.find("```", thinking_start)
                        reasoning_content = model_output[thinking_start:thinking_end].strip()
                        # 提取答案 (在第二个```之后的所有内容)
                        content = model_output[thinking_end + 3:].strip()
                    else:
                        # 如果没有标准格式，默认全部内容作为答案
                        reasoning_content = ""
                        content = model_output
                else:
                    # 其他API返回格式
                    reasoning_content = ""
                    content = response.choices[0].message.content
    
                return {
                    "reasoning": reasoning_content,
                    "answer": content
                }
    
            except Exception as e:
                error_msg = f"API调用错误: {str(e)}"
                print(error_msg)
                
                QMessageBox.warning(parent, "API调用失败", f"无法获取分析结果: {str(e)}\n请检查网络连接或API设置后重试。")
                
                return {
                    "reasoning": error_msg,
                    "answer": "无法获取分析结果，请检查网络连接或API设置。"
                }
            finally:
                # 无论成功还是失败，都确保进度对话框被关闭
                if progress:
                    progress.close()
                    # 显式删除对话框，确保资源被释放
                    progress.deleteLater()
