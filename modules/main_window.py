import os
import json
import jsonlines
import traceback
import sys
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QRect, QSettings
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QLineEdit, QTextEdit, 
                             QListWidget, QListWidgetItem, QFileDialog, 
                             QMessageBox, QTabWidget, QSplitter, QGroupBox,
                             QDialog, QDialogButtonBox, QFormLayout, QComboBox, QInputDialog,
                             QAction, QToolBar, QStatusBar, QApplication, QFrame, QCheckBox,
                             QScrollArea)
from PyQt5.QtGui import QIcon, QFont, QColor, QPalette

# 导入模块前添加资源路径处理函数
def resource_path(relative_path):
    """获取资源的绝对路径，兼容开发环境和打包后的环境"""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

from .video_player import VideoPlayer
from .image_viewer import ImageViewer
from .annotation_manager import AnnotationManager, AnnotationDialog
from .api_handler import APIHandler, ModelSettingsDialog
from .help_dialog import HelpDialog
from .file_handler import FileHandler


class OutputFolderDialog(QDialog):
    """输出文件夹设置对话框"""
    
    def __init__(self, current_folder, parent=None):
        super().__init__(parent)
        self.current_folder = current_folder
        self.default_folder = os.path.join(os.path.expanduser("~"), "Desktop", "视频标注结果")
        
        # 加载用户设置，使用resource_path
        self.settings_file = resource_path("config/output_folder_config.json")
        self.load_settings()
        
        self.setWindowTitle("输出文件夹设置")
        self.resize(500, 200)
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI界面"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 标题
        title_label = QLabel("设置输出文件夹")
        title_label.setStyleSheet("font-size: 16px; color: #2980b9; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # 当前输出文件夹
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(15)
        
        self.folder_edit = QLineEdit(self.current_folder)
        self.folder_edit.setReadOnly(True)
        self.folder_edit.setMinimumWidth(350)
        
        folder_layout = QHBoxLayout()
        folder_layout.addWidget(self.folder_edit)
        
        browse_button = QPushButton("浏览...")
        browse_button.clicked.connect(self.browse_folder)
        folder_layout.addWidget(browse_button)
        
        form_layout.addRow("当前输出文件夹:", folder_layout)
        layout.addLayout(form_layout)
        
        # 恢复默认按钮
        restore_button = QPushButton("恢复默认位置")
        restore_button.clicked.connect(self.restore_default)
        restore_button.setStyleSheet("""
            QPushButton {
                background-color: #7f8c8d;
                color: white;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #6f7c7d;
            }
        """)
        
        # 确定取消按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.button(QDialogButtonBox.Ok).setText("确定")
        button_box.button(QDialogButtonBox.Cancel).setText("取消")
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(restore_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(button_box)
        
        layout.addSpacing(10)
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
        
    def browse_folder(self):
        """浏览并选择新的输出文件夹"""
        folder = QFileDialog.getExistingDirectory(self, "选择输出文件夹", self.folder_edit.text())
        if folder:
            self.folder_edit.setText(folder)
            
    def restore_default(self):
        """恢复默认输出文件夹"""
        self.folder_edit.setText(self.default_folder)
            
    def get_selected_folder(self):
        """获取选择的文件夹路径"""
        return self.folder_edit.text()
        
    def load_settings(self):
        """加载设置"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    if "output_folder" in settings and os.path.exists(settings["output_folder"]):
                        self.current_folder = settings["output_folder"]
                    else:
                        self.current_folder = self.default_folder
            except:
                self.current_folder = self.default_folder
        else:
            # 确保配置目录存在
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            self.current_folder = self.default_folder
            
    def save_settings(self, folder_path):
        """保存设置"""
        settings = {"output_folder": folder_path}
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            QMessageBox.warning(self, "保存失败", f"保存配置文件失败: {str(e)}")
            return False


class DiagnosisLabelSettingsDialog(QDialog):
    """诊断结果标签设置对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("诊断结果标签设置")
        self.resize(800, 1200)
        self.default_labels = [
            "标签1", "标签2", "标签3"
        ]
        
        # 加载用户自定义标签，使用resource_path
        self.settings_file = resource_path("config/diagnosis_labels_config.json")
        self.diagnosis_labels = self.load_settings()
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI界面"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 标题
        title_label = QLabel("诊断结果标签设置")
        title_label.setStyleSheet("font-size: 16px; color: #2980b9; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # 标签列表
        label_group = QGroupBox("标签列表")
        label_layout = QVBoxLayout()
        
        self.label_list = QListWidget()
        self.label_list.setSelectionMode(QListWidget.SingleSelection)
        self.update_label_list()
        label_layout.addWidget(self.label_list)
        
        # 操作按钮
        buttons_layout = QHBoxLayout()
        
        self.add_button = QPushButton("新增")
        self.add_button.clicked.connect(self.add_label)
        self.add_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        buttons_layout.addWidget(self.add_button)
        
        self.edit_button = QPushButton("编辑")
        self.edit_button.clicked.connect(self.edit_label)
        self.edit_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db; 
                color: white;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        buttons_layout.addWidget(self.edit_button)
        
        self.delete_button = QPushButton("删除")
        self.delete_button.clicked.connect(self.delete_label)
        self.delete_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        buttons_layout.addWidget(self.delete_button)
        
        label_layout.addLayout(buttons_layout)
        label_group.setLayout(label_layout)
        layout.addWidget(label_group)
        
        # 提示信息
        info_label = QLabel("注意: 修改标签后，在下次启动程序时生效。'其他'选项将始终保留。")
        info_label.setStyleSheet("color: #7f8c8d; font-style: italic;")
        layout.addWidget(info_label)
        
        # 底部按钮
        bottom_layout = QHBoxLayout()
        
        restore_button = QPushButton("恢复默认设置")
        restore_button.clicked.connect(self.restore_defaults)
        restore_button.setStyleSheet("""
            QPushButton {
                background-color: #7f8c8d;
                color: white;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #6f7c7d;
            }
        """)
        bottom_layout.addWidget(restore_button)
        
        bottom_layout.addStretch()
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.button(QDialogButtonBox.Ok).setText("确定")
        button_box.button(QDialogButtonBox.Cancel).setText("取消")
        button_box.accepted.connect(self.save_and_accept)
        button_box.rejected.connect(self.reject)
        bottom_layout.addWidget(button_box)
        
        layout.addLayout(bottom_layout)
        
        self.setLayout(layout)
    
    def update_label_list(self):
        """更新标签列表"""
        self.label_list.clear()
        for label in self.diagnosis_labels:
            self.label_list.addItem(label)
    
    def add_label(self):
        """添加新标签"""
        label, ok = QInputDialog.getText(self, "添加标签", "请输入新的诊断结果标签:")
        if ok and label.strip():
            label = label.strip()
            # 检查是否已存在
            if label in self.diagnosis_labels:
                QMessageBox.warning(self, "警告", f"标签 '{label}' 已存在")
                return
                
            self.diagnosis_labels.append(label)
            self.update_label_list()
    
    def edit_label(self):
        """编辑选中的标签"""
        current_item = self.label_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请先选择一个标签")
            return
            
        current_label = current_item.text()
        new_label, ok = QInputDialog.getText(self, "编辑标签", 
                                           "请修改诊断结果标签:", 
                                           QLineEdit.Normal, 
                                           current_label)
        
        if ok and new_label.strip() and new_label != current_label:
            # 检查是否已存在
            if new_label in self.diagnosis_labels:
                QMessageBox.warning(self, "警告", f"标签 '{new_label}' 已存在")
                return
                
            # 更新标签
            index = self.diagnosis_labels.index(current_label)
            self.diagnosis_labels[index] = new_label
            self.update_label_list()
    
    def delete_label(self):
        """删除选中的标签"""
        current_item = self.label_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请先选择一个标签")
            return
            
        current_label = current_item.text()
        reply = QMessageBox.question(self, "确认删除", 
                                   f"确定要删除标签 '{current_label}' 吗?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.diagnosis_labels.remove(current_label)
            self.update_label_list()
    
    def restore_defaults(self):
        """恢复默认标签设置"""
        reply = QMessageBox.question(self, "确认", 
                                   "确定要恢复默认标签设置吗? 这将删除所有自定义标签。",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.diagnosis_labels = self.default_labels.copy()
            self.update_label_list()
    
    def load_settings(self):
        """加载设置"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    if "diagnosis_labels" in settings and isinstance(settings["diagnosis_labels"], list):
                        return settings["diagnosis_labels"]
            except Exception as e:
                print(f"读取诊断标签配置失败: {str(e)}")
                
        return self.default_labels.copy()
    
    def save_and_accept(self):
        """保存设置并接受对话框"""
        try:
            # 确保配置目录存在
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            
            # 保存设置
            settings = {"diagnosis_labels": self.diagnosis_labels}
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)
                
            self.accept()
            
        except Exception as e:
            QMessageBox.warning(self, "保存失败", f"保存配置文件失败: {str(e)}")


class DiagnosisSelector(QWidget):
    """诊断结果多选组件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        # 主布局设置为 QVBoxLayout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0) # 移除边距，让 ScrollArea 填充

        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True) # 允许内部控件调整大小
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff) # 禁用水平滚动条
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded) # 需要时显示垂直滚动条

        # 创建用于放置复选框的容器 QWidget
        checkbox_container = QWidget()
        self.layout = QVBoxLayout(checkbox_container) # 复选框的布局放在容器里
        self.checkboxes = []

        # 从配置文件加载诊断类型，使用resource_path
        self.settings_file = resource_path("config/diagnosis_labels_config.json")
        self.default_diagnosis_types = [
            "标签1", "标签2", "标签3"
        ]
        
        self.diagnosis_types = self.load_diagnosis_types()
        # 确保"其他"选项一定在最后
        if "其他" in self.diagnosis_types:
            self.diagnosis_types.remove("其他")
        self.diagnosis_types.append("其他")
        
        # 创建复选框
        font_size = QApplication.font().pointSizeF() * 0.8
        checkbox_style = f"font-size: {font_size}pt;"
        for diagnosis in self.diagnosis_types:
            checkbox = QCheckBox(diagnosis)
            checkbox.setStyleSheet(checkbox_style)
            if diagnosis == "其他":
                checkbox.stateChanged.connect(self.handle_other_changed)
            self.layout.addWidget(checkbox)
            self.checkboxes.append(checkbox)
            
        # 创建其他诊断输入框
        self.other_input = QLineEdit()
        self.other_input.setPlaceholderText("请输入其他诊断结果...")
        self.other_input.setVisible(False)
        self.other_input.setStyleSheet(checkbox_style)
        self.layout.addWidget(self.other_input)
        
        self.layout.setSpacing(8)
        self.layout.addStretch() # 添加伸缩项到底部

        # 将复选框容器设置为滚动区域的控件
        scroll_area.setWidget(checkbox_container)

        # 将滚动区域添加到主布局
        main_layout.addWidget(scroll_area)

        # 为滚动区域设置一个最大高度，以限制其显示区域
        scroll_area.setMaximumHeight(300) # 限制诊断结果区域的高度为 200 像素

    def load_diagnosis_types(self):
        """从配置文件加载诊断类型"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    if "diagnosis_labels" in settings and isinstance(settings["diagnosis_labels"], list):
                        return settings["diagnosis_labels"]
            except:
                pass
                
        return self.default_diagnosis_types.copy()
        
    def handle_other_changed(self, state):
        """处理'其他'选项的状态变化"""
        self.other_input.setVisible(state == Qt.Checked)
        
    def get_selected_diagnoses(self):
        """获取所有选中的诊断结果"""
        results = []
        for i, checkbox in enumerate(self.checkboxes):
            if checkbox.isChecked():
                if i == len(self.diagnosis_types) - 1 and self.other_input.text().strip():
                    # '其他'选项有自定义输入
                    results.append(self.other_input.text().strip())
                else:
                    results.append(checkbox.text())
                    
        return results
        
    def set_selected_diagnoses(self, diagnoses):
        """设置选中的诊断结果"""

        # 清除"其他"输入框
        self.other_input.setText("")
        self.other_input.setVisible(False)
        
        # 清除当前选择
        for checkbox in self.checkboxes:
            checkbox.setChecked(False)
            
        # 检查是否有自定义诊断
        other_diagnosis = None
        
        # 设置新的选择
        for diagnosis in diagnoses:
            found = False
            for i, checkbox in enumerate(self.checkboxes):
                if checkbox.text() == diagnosis:
                    checkbox.setChecked(True)
                    found = True
                    break
                    
            # 如果没有找到，可能是自定义诊断
            if not found:
                other_diagnosis = diagnosis
                
        # 如果有自定义诊断，设置"其他"选项
        if other_diagnosis:
            self.checkboxes[-1].setChecked(True)
            self.other_input.setText(other_diagnosis)


class MainWindow(QMainWindow):
    """
    主窗口类，整合所有功能模块
    """
    
    def __init__(self):
        super().__init__()

        self.current_folder_index = -1
        self.folders = []
        self.current_video_path = ""
        self.current_images = []
        self.annotations = []
        
        # 新增状态：用于历史记录导航
        self.viewing_history_index = None

        # 初始化文件处理器、API处理器和标注管理器
        self.file_handler = FileHandler()
        self.api_handler = APIHandler()
        self.annotation_manager = AnnotationManager()
        
        # 标记当前加载的数据是否已修改但尚未保存
        self.data_modified = False
        
        self.setup_ui()
        self.apply_stylesheet()
        self.setup_connections()
        
        self.setWindowTitle("智能视频标注分析平台（慧影）- VIAL (Video Intelligent Annotation Lab)")
        self.reset_ui_to_initial_state()

    def apply_stylesheet(self):
        """应用全局样式表"""
        default_font_size = QApplication.font().pointSizeF()
        large_font_size = default_font_size * 1.5
        group_box_font_size = default_font_size * 1.3 # 统一 GroupBox 标题字体大小

        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: #f5f5f5;
            }}
            QWidget {{
                font-family: 'Microsoft YaHei', 'Segoe UI', Arial;
                font-size: {default_font_size}pt;
            }}
            QGroupBox::title {{
                font-size: {group_box_font_size}pt;
                font-weight: bold;
                color: #2980b9; /* 设置标题为蓝色 */
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 3px;
            }}
            QGroupBox {{
                border: 1px solid #ccc;
                border-radius: 5px;
                margin-top: 1ex; /* leave space at the top for the title */
                font-size: {default_font_size}pt; /* GroupBox 内其他控件字体大小 */
            }}
            QListWidget {{
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                padding: 4px;
                font-size: {large_font_size}pt;
            }}
            QListWidget::item {{
                padding: 8px;
                border-bottom: 1px solid #eee;
            }}
            QTextEdit {{
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 6px;
                background-color: white;
                font-size: {large_font_size}pt;
            }}
            QCheckBox {{
                spacing: 10px;
                font-size: {large_font_size}pt;
            }}
            QCheckBox::indicator {{
                width: {int(16 * 1.2)}px;
                height: {int(16 * 1.2)}px;
            }}
            QPushButton {{
                padding: 6px 12px;
                border-radius: 4px;
                min-height: 28px; /* 统一按钮最小高度 */
            }}
            /* 为工具栏按钮设置特定样式 */
            QToolBar QPushButton {{
                color: black; /* 默认文字颜色为黑色 */
                background-color: #bdc3c7; /* 默认背景灰色 */
            }}
            QToolBar QPushButton:enabled {{
                background-color: #3498db; /* 启用时背景蓝色 */
                color: black; /* 启用时文字黑色 */
            }}
            QToolBar QPushButton:disabled {{
                background-color: #ecf0f1; /* 禁用时背景浅灰色 */
                color: #95a5a6; /* 禁用时文字灰色 */
            }}
            QToolBar QPushButton:hover:enabled {{
                background-color: #2980b9; /* 鼠标悬停时深蓝色 */
            }}
        """)

    def setup_ui(self):
        # 创建中央窗口部件
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)
        
        # 顶部工具栏
        self.create_toolbar()
        
        # 创建主分割区域
        main_splitter = QSplitter(Qt.Horizontal)
        
        # 左侧区域 - 视频播放和图片查看
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)
        
        # 创建选项卡
        tab_widget = QTabWidget()
        tab_widget.setMinimumHeight(900)  # 增大视频播放区域高度
        
        # 视频选项卡
        video_tab = QWidget()
        video_layout = QVBoxLayout(video_tab)
        video_layout.setContentsMargins(0, 0, 0, 0)
        
        self.video_player = VideoPlayer()
        
        video_layout.addWidget(self.video_player)
        
        tab_widget.addTab(video_tab, "视频")
        
        # 图片选项卡
        image_tab = QWidget()
        image_layout = QVBoxLayout(image_tab)
        image_layout.setContentsMargins(0, 0, 0, 0)
        
        self.image_viewer = ImageViewer()
        image_layout.addWidget(self.image_viewer)
        
        tab_widget.addTab(image_tab, "图片")
        
        left_layout.addWidget(tab_widget)
        
        # 标注列表
        annotation_group = QGroupBox("视频片段标注") # GroupBox 标题将应用全局样式
        annotation_layout = QVBoxLayout()
        annotation_layout.setContentsMargins(10, 15, 10, 10) # 顶部边距调整以适应标题
        
        self.annotation_list = QListWidget()
        self.annotation_list.setSelectionMode(QListWidget.SingleSelection)
        self.annotation_list.itemDoubleClicked.connect(self.edit_annotation)
        self.annotation_list.setMinimumHeight(120)
        annotation_layout.addWidget(self.annotation_list)
        
        annotation_buttons = QHBoxLayout()
        
        self.add_annotation_button = QPushButton("添加")
        self.add_annotation_button.setIcon(QIcon.fromTheme("list-add"))
        self.add_annotation_button.setToolTip("添加新的视频片段标注")
        self.add_annotation_button.clicked.connect(self.add_annotation)
        # 设置添加按钮样式：绿色背景，白色文字
        self.add_annotation_button.setStyleSheet("background-color: #2ecc71; color: white;")
        annotation_buttons.addWidget(self.add_annotation_button)
        
        self.edit_annotation_button = QPushButton("编辑")
        self.edit_annotation_button.setIcon(QIcon.fromTheme("document-edit"))
        self.edit_annotation_button.setToolTip("编辑所选视频片段标注")
        self.edit_annotation_button.clicked.connect(self.edit_selected_annotation)
        # 设置编辑按钮样式：蓝色背景，白色文字
        self.edit_annotation_button.setStyleSheet("background-color: #3498db; color: white;")
        annotation_buttons.addWidget(self.edit_annotation_button)
        
        self.delete_annotation_button = QPushButton("删除")
        self.delete_annotation_button.setIcon(QIcon.fromTheme("edit-delete"))
        self.delete_annotation_button.setToolTip("删除所选视频片段标注")
        # 设置删除按钮样式：红色背景，白色文字
        self.delete_annotation_button.setStyleSheet("background-color: #e74c3c; color: white;")
        self.delete_annotation_button.clicked.connect(self.delete_annotation)
        annotation_buttons.addWidget(self.delete_annotation_button)
        
        annotation_layout.addLayout(annotation_buttons)
        annotation_group.setLayout(annotation_layout)
        
        left_layout.addWidget(annotation_group)
        
        # 将左侧添加到分割器
        main_splitter.addWidget(left_widget)
        
        # 右侧区域 - 标注列表和描述
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)
        
        # 视频总描述区域
        description_group = QGroupBox("视频总描述") # GroupBox 标题将应用全局样式
        description_layout = QVBoxLayout()
        description_layout.setContentsMargins(10, 15, 10, 10) # 顶部边距调整
        
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("请在此输入视频总体描述，不少于10个字...")
        self.description_edit.setMinimumHeight(10)
        self.description_edit.textChanged.connect(lambda: setattr(self, 'data_modified', True))
        description_layout.addWidget(self.description_edit)
        
        # 诊断结果选择区域
        diagnosis_group = QGroupBox("诊断结果(可多选)") # 使用 QGroupBox 包裹诊断结果，标题将应用全局样式
        diagnosis_layout = QVBoxLayout(diagnosis_group) # 布局应用于新的 GroupBox
        diagnosis_layout.setContentsMargins(10, 15, 10, 10) # 调整边距

        # 使用 DiagnosisSelector 实例 (内部已包含 ScrollArea)
        self.diagnosis_selector = DiagnosisSelector()

        for checkbox in self.diagnosis_selector.checkboxes:
            checkbox.stateChanged.connect(lambda state, cb=checkbox: setattr(self, 'data_modified', True))
        self.diagnosis_selector.other_input.textChanged.connect(lambda: setattr(self, 'data_modified', True))
        diagnosis_layout.addWidget(self.diagnosis_selector) # 直接添加 DiagnosisSelector
        
        # 将诊断结果 GroupBox 添加到描述布局中
        description_layout.addWidget(diagnosis_group)
        description_group.setLayout(description_layout) # 将 description_layout 设置为 description_group 的布局
        
        # 将 description_group 添加到右侧主布局，并设置拉伸因子为 1 (较小)
        right_layout.addWidget(description_group, 1) # 第一个拉伸因子

        
        # AI分析结果区域（思维链和答案）
        analysis_group = QGroupBox("AI分析结果") # GroupBox 标题将应用全局样式
        analysis_layout = QVBoxLayout()
        analysis_layout.setContentsMargins(10, 15, 10, 10) # 顶部边距调整
        
        # 思维链输入框
        thinking_label = QLabel("思维链:")
        thinking_label.setStyleSheet(f"font-weight: bold; font-size: {QApplication.font().pointSizeF() * 1.2}pt;")
        analysis_layout.addWidget(thinking_label)
        
        self.thinking_chain_edit = QTextEdit()
        self.thinking_chain_edit.setPlaceholderText("AI分析思路将显示在这里...")
        self.thinking_chain_edit.setMinimumHeight(150)
        self.thinking_chain_edit.textChanged.connect(lambda: setattr(self, 'data_modified', True))
        analysis_layout.addWidget(self.thinking_chain_edit)
        
        # 答案输入框
        answer_label = QLabel("大模型回答:")
        answer_label.setStyleSheet(f"font-weight: bold; font-size: {QApplication.font().pointSizeF() * 1.2}pt;")
        analysis_layout.addWidget(answer_label)
        
        self.ai_answer_edit = QTextEdit()
        self.ai_answer_edit.setPlaceholderText("AI分析结论将显示在这里...")
        self.ai_answer_edit.setMinimumHeight(150)
        self.ai_answer_edit.textChanged.connect(lambda: setattr(self, 'data_modified', True))
        analysis_layout.addWidget(self.ai_answer_edit)
        
        analysis_group.setLayout(analysis_layout)
        
        # 将 analysis_group 添加到右侧主布局，并设置拉伸因子为 2 (较大)
        # 这使得 analysis_group 获得比 description_group 更多的垂直空间
        right_layout.addWidget(analysis_group, 2) # 第二个拉伸因子，是上面的两倍
        
        # 操作按钮
        action_layout = QHBoxLayout()
        
        self.generate_button = QPushButton("生成标注数据")
        self.generate_button.setIcon(QIcon.fromTheme("document-save"))
        self.generate_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                font-weight: bold;
                min-height: 32px;
                color: white;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        self.generate_button.clicked.connect(self.generate_annotation_data)
        action_layout.addWidget(self.generate_button)
        
        self.save_button = QPushButton("确定保存")
        self.save_button.setIcon(QIcon.fromTheme("go-next"))
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                font-weight: bold;
                min-height: 32px;
                color: white;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.save_button.clicked.connect(self.save_and_load_next)
        action_layout.addWidget(self.save_button)
        
        # 将按钮布局添加到右侧主布局，不设置拉伸因子，使其保持在底部
        right_layout.addLayout(action_layout)
        
        # 将右侧添加到分割器
        main_splitter.addWidget(right_widget)
        
        # 设置分割比例 (调整为大约 1:1)
        # 假设总宽度为 1300
        main_splitter.setSizes([650, 650]) # 调整比例使左侧占约 1/2
        
        main_layout.addWidget(main_splitter)
        
        self.setCentralWidget(central_widget)
        
        # 底部状态栏
        self.statusBar = QStatusBar()
        
        # 设置状态栏
        self.setStatusBar(self.statusBar)
        
        # 初始状态
        self.update_ui_state(False)

    def create_toolbar(self):
        """创建工具栏"""
        toolbar = QToolBar("主工具栏")
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # 导入数据文件夹按钮
        import_action = QAction(QIcon.fromTheme("folder-open", QIcon()), "导入数据文件夹", self)
        import_action.setStatusTip("导入包含视频和图片的数据文件夹")
        import_action.triggered.connect(self.import_folder)
        toolbar.addAction(import_action)
        
        toolbar.addSeparator()
        
        # 当前文件夹信息
        self.folder_info_label = QLabel("当前文件夹: 无")
        toolbar.addWidget(self.folder_info_label)
        
        # 添加回溯按钮到工具栏
        self.prev_folder_btn = QPushButton("查看上一条已存数据")
        # 样式将在 apply_stylesheet 中统一设置
        self.prev_folder_btn.clicked.connect(self.load_previous_history_entry)
        self.prev_folder_btn.setEnabled(False)
        toolbar.addWidget(self.prev_folder_btn)
        
        self.current_folder_btn = QPushButton("返回当前待处理数据")
        # 样式将在 apply_stylesheet 中统一设置
        self.current_folder_btn.clicked.connect(self.return_to_current_folder)
        self.current_folder_btn.setEnabled(False)
        toolbar.addWidget(self.current_folder_btn)
        
        toolbar.addSeparator()
        
        # 模型参数设置按钮
        settings_action = QAction(QIcon.fromTheme("preferences-system", QIcon()), "模型参数设置", self)
        settings_action.setStatusTip("配置API连接和提示语参数")
        settings_action.triggered.connect(self.open_model_settings)
        toolbar.addAction(settings_action)
        
        # 输出文件夹设置按钮
        output_folder_action = QAction(QIcon.fromTheme("folder-documents", QIcon()), "输出文件夹设置", self)
        output_folder_action.setStatusTip("设置标注数据输出文件夹")
        output_folder_action.triggered.connect(self.open_output_folder_settings)
        toolbar.addAction(output_folder_action)
        
        # 诊断结果标签设置按钮
        diagnosis_label_action = QAction(QIcon.fromTheme("preferences-other", QIcon()), "诊断结果标签设置", self)
        diagnosis_label_action.setStatusTip("设置诊断结果标签")
        diagnosis_label_action.triggered.connect(self.open_diagnosis_label_settings)
        toolbar.addAction(diagnosis_label_action)
        
        # 帮助按钮
        help_action = QAction(QIcon.fromTheme("help-contents", QIcon()), "帮助", self)
        help_action.setStatusTip("查看软件使用帮助")
        help_action.triggered.connect(self.open_help)
        toolbar.addAction(help_action)
        
    def setup_connections(self):
        """设置信号连接"""
        # 关联视频片段标记信号
        self.video_player.segment_marked.connect(self.handle_segment_marked)
        
        # 关联标注管理器信号
        self.annotation_manager.annotation_changed.connect(self.update_annotation_list_from_manager)
        self.description_edit.textChanged.connect(self.mark_data_modified)
        self.thinking_chain_edit.textChanged.connect(self.mark_data_modified)
        self.ai_answer_edit.textChanged.connect(self.mark_data_modified)
        for checkbox in self.diagnosis_selector.checkboxes:
            checkbox.stateChanged.connect(self.mark_data_modified)
        self.diagnosis_selector.other_input.textChanged.connect(self.mark_data_modified)
        self.annotation_manager.annotation_changed.connect(self.mark_data_modified)

    def mark_data_modified(self):
        """标记数据已修改"""
        self.data_modified = True

    def update_ui_state(self, folder_loaded=False):
        """更新UI状态"""
        self.add_annotation_button.setEnabled(folder_loaded)
        self.edit_annotation_button.setEnabled(folder_loaded and self.annotation_list.count() > 0)
        self.delete_annotation_button.setEnabled(folder_loaded and self.annotation_list.count() > 0)
        self.generate_button.setEnabled(folder_loaded)
        self.save_button.setEnabled(folder_loaded)

        can_go_back = self.file_handler.output_jsonl and (self.viewing_history_index is None or self.viewing_history_index > 0)
        self.prev_folder_btn.setEnabled(bool(self.file_handler.output_jsonl) and len(self.file_handler.output_jsonl) > 0)
        self.current_folder_btn.setEnabled(self.viewing_history_index is not None)

    def reset_ui_to_initial_state(self):
        """重置UI到初始或完成状态"""
        self.current_folder_index = -1
        self.current_video_path = ""
        self.current_images = []
        self.annotations = []
        self.viewing_history_index = None
        self.data_modified = False

        self.video_player.clear()
        self.image_viewer.clear()
        self.annotation_manager.set_annotations([])
        self.annotation_list.clear()
        self.description_edit.clear()
        self.diagnosis_selector.set_selected_diagnoses([])
        self.thinking_chain_edit.clear()
        self.ai_answer_edit.clear()

        self.folder_info_label.setText("当前: 无")
        self.statusBar.clearMessage()
        self.update_ui_state(False)

    def import_folder(self):
        """导入数据文件夹"""

        self.reset_ui_to_initial_state()

        folders_list, start_index, loaded_jsonl = self.file_handler.import_folder(self)
        
        if folders_list:
            self.folders = folders_list
            
            if start_index >= len(self.folders):
                QMessageBox.information(self, "提示", "所有文件夹似乎都已处理完毕。您可以查看历史记录或重新导入。")
                self.reset_ui_to_initial_state()
                self.update_ui_state(False)
            else:
                self.load_folder(start_index)
        else:
             self.reset_ui_to_initial_state()

    def open_model_settings(self):
        """打开模型参数设置对话框"""
        dialog = ModelSettingsDialog(self.api_handler, self)
        dialog.exec_()
        
    def open_help(self):
        """打开帮助对话框"""
        dialog = HelpDialog(self)
        dialog.exec_()

    def open_diagnosis_label_settings(self):
        """打开诊断结果标签设置对话框"""
        dialog = DiagnosisLabelSettingsDialog(self)
        dialog.exec_()

    def load_folder(self, index_to_load, history_entry=None):
        """加载指定索引的文件夹及其数据"""
        if index_to_load < 0 or index_to_load >= len(self.folders):
            print(f"警告: 尝试加载无效索引 {index_to_load}")
            self.reset_ui_to_initial_state()
            return

        folder_idx, video_path, images, annotations, video_desc, final_diag = \
            self.file_handler.load_folder_by_index(index_to_load, self.folders, history_entry, self)

        if not video_path:
            QMessageBox.warning(self, "加载失败", f"无法加载文件夹索引 {index_to_load} 中的视频。")
            self.reset_ui_to_initial_state()
            return

        self.current_folder_index = folder_idx
        self.current_video_path = video_path
        self.current_images = images
        self.annotations = annotations

        self.video_player.load_video(video_path)
        if images:
            self.image_viewer.load_images(images)
        else:
            self.image_viewer.clear()

        self.annotation_manager.set_annotations(self.annotations)
        self.update_annotation_list()  # 添加这一行来直接更新UI
        self.description_edit.setPlainText(video_desc or "")
        diagnoses = [d.strip() for d in final_diag.split(',') if d.strip()]
        self.diagnosis_selector.set_selected_diagnoses(diagnoses)

        ai_thinking = ""
        ai_answer = ""
        if history_entry:
             conversations = history_entry.get('conversations', [])
             if len(conversations) > 1 and 'value' in conversations[1]:
                 content = conversations[1]['value']
                 if '<think>' in content and '</think>' in content:
                     ai_thinking = content.split('<think>', 1)[1].split('</think>', 1)[0].strip()
                 if '<answer>' in content and '</answer>' in content:
                     ai_answer = content.split('<answer>', 1)[1].split('</answer>', 1)[0].strip()
                 elif '<think>' not in content:
                     ai_answer = content.strip()

        self.thinking_chain_edit.setPlainText(ai_thinking)
        self.ai_answer_edit.setPlainText(ai_answer)

        folder_name = os.path.basename(self.folders[self.current_folder_index])
        status_prefix = ""
        if self.viewing_history_index is not None:
             history_count = len(self.file_handler.output_jsonl)
             status_prefix = f"历史记录 {self.viewing_history_index + 1}/{history_count}: "
        self.folder_info_label.setText(f"当前: {folder_name}")
        self.statusBar.showMessage(f"{status_prefix}{os.path.basename(video_path)}")

        self.data_modified = False
        self.update_ui_state(True)

    def save_and_load_next(self):
        """保存当前数据并加载下一个未处理的文件夹"""
        if self.current_folder_index < 0 or not self.current_video_path:
            QMessageBox.warning(self, "无数据", "没有加载有效的文件夹进行保存。")
            return

        video_description = self.description_edit.toPlainText().strip()
        final_diagnosis_list = self.diagnosis_selector.get_selected_diagnoses()
        final_diagnosis = ", ".join(final_diagnosis_list)
        ai_answer = self.ai_answer_edit.toPlainText().strip()
        thinking_chain = self.thinking_chain_edit.toPlainText().strip()

        if not video_description or len(video_description) < 10:
            QMessageBox.warning(self, "数据验证失败", "请输入视频总描述，不少于10个字。")
            return
        if not final_diagnosis_list:
            QMessageBox.warning(self, "数据验证失败", "请选择或输入诊断结果。")
            return
        if not ai_answer:
            QMessageBox.warning(self, "数据验证失败", "请确保已生成或输入大模型答案。")
            return

        current_entry_data = self.file_handler.generate_annotation_data(
            self.current_video_path,
            self.annotations,
            video_description,
            final_diagnosis,
            thinking_chain,
            ai_answer,
            self
        )

        if not current_entry_data:
            QMessageBox.critical(self, "错误", "无法生成标注数据结构，请检查日志。")
            return

        save_successful = self.file_handler.save_annotation_data(current_entry_data, self)

        if not save_successful:
            QMessageBox.critical(self, "保存失败", "保存标注数据或复制视频时出错，请检查日志。")
            return
        else:
             self.data_modified = False
            # 构建 JSONL 文件路径
             jsonl_path_save = os.path.join(self.file_handler.output_folder,
                                       self.file_handler.data_folder_name,
                                       f"{self.file_handler.data_folder_name}.jsonl")
             QMessageBox.information(self, "保存成功", f"标注数据已成功保存到: {jsonl_path_save}")

        current_logical_index = self.current_folder_index
        if self.viewing_history_index is not None:
            next_index = self.file_handler.load_next_folder(-1, self.folders, self)
            self.viewing_history_index = None
        else:
            next_index = self.file_handler.load_next_folder(self.current_folder_index, self.folders, self)

        if next_index >= len(self.folders):
            QMessageBox.information(self, "完成", "所有文件夹已处理完毕！")
            self.reset_ui_to_initial_state()
            self.update_ui_state(False)
        else:
            self.load_folder(next_index)

    def load_previous_history_entry(self):
        """加载上一个已保存的历史记录"""
        output_data_folder = os.path.join(self.file_handler.output_folder, self.file_handler.data_folder_name)
        jsonl_path = os.path.join(output_data_folder, f"{self.file_handler.data_folder_name}.jsonl")

        if not os.path.exists(jsonl_path):
            QMessageBox.information(self, "无历史记录", "未找到已保存的标注文件。")
            return

        try:
            with jsonlines.open(jsonl_path, mode='r') as reader:
                self.file_handler.output_jsonl = [entry for entry in reader]
                self.file_handler.output_jsonl.sort(key=lambda x: x.get("id", float('inf')))
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载历史记录文件失败: {str(e)}")
            return

        if not self.file_handler.output_jsonl:
            QMessageBox.information(self, "无历史记录", "标注文件为空。")
            return

        if self.viewing_history_index is None:
            self.viewing_history_index = len(self.file_handler.output_jsonl) - 1
        else:
            self.viewing_history_index -= 1

        if self.viewing_history_index < 0:
            self.viewing_history_index = 0
            QMessageBox.information(self, "提示", "已经是第一条历史记录。")

        history_entry = self.file_handler.output_jsonl[self.viewing_history_index]
        video_field = history_entry.get("video", "")
        if not video_field.startswith("videos/"):
            QMessageBox.warning(self, "错误", f"历史记录 {self.viewing_history_index + 1} 视频格式错误。")
            self.viewing_history_index = None
            self.update_ui_state(False)
            return
        video_name = video_field[7:]

        input_folder_index = -1
        for i, folder in enumerate(self.folders):
            if video_name in os.listdir(folder):
                input_folder_index = i
                break

        if input_folder_index == -1:
            QMessageBox.warning(self, "错误", f"未在输入文件夹中找到与历史记录视频 '{video_name}' 匹配的文件。")
            self.viewing_history_index = None
            self.update_ui_state(False)
            return

        self.load_folder(input_folder_index, history_entry=history_entry)

    def return_to_current_folder(self):
        """返回到当前逻辑上应该处理的文件夹"""
        if self.viewing_history_index is None:
            return

        if self.data_modified:
             reply = QMessageBox.question(self, "确认操作",
                                         "当前历史记录有未保存的修改，切换将丢失这些修改。是否继续？",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
             if reply == QMessageBox.No:
                 return

        next_index = self.file_handler.load_next_folder(-1, self.folders, self)

        self.viewing_history_index = None

        if next_index >= len(self.folders):
            QMessageBox.information(self, "提示", "所有文件夹似乎都已处理完毕。")
            self.reset_ui_to_initial_state()
            self.update_ui_state(False)
        else:
            self.load_folder(next_index)

    def handle_segment_marked(self, start_time, end_time, label):
        """处理视频片段标记信号"""
        if hasattr(self, 'is_handling_annotation') and self.is_handling_annotation:
            return
        self.is_handling_annotation = True
        
        try:
            dialog = AnnotationDialog(start_time, end_time, label, self)
            was_playing = False
            if hasattr(self.video_player, 'mediaPlayer') and self.video_player.mediaPlayer.state() == self.video_player.mediaPlayer.PlayingState:
                 was_playing = True
                 self.video_player.pause_video()

            if dialog.exec_() == QDialog.Accepted:
                annotation_data = dialog.get_annotation_data()
                if not annotation_data["end_time"] or not annotation_data["label"]:
                    QMessageBox.warning(self, "警告", "结束时间和标签描述不能为空")
                else:
                    self.annotation_manager.add_annotation(
                        annotation_data["start_time"],
                        annotation_data["end_time"],
                        annotation_data["label"]
                    )
            if was_playing:
                 self.video_player.play_video()
        finally:
            self.is_handling_annotation = False
            
    def update_annotation_list_from_manager(self, annotations):
        """从标注管理器更新标注列表UI和内部状态"""
        self.annotations = annotations
        self.update_annotation_list()
        self.mark_data_modified()
        self.update_ui_state(bool(self.current_video_path))

    def add_annotation(self):
        """手动添加标注"""
        if not self.current_video_path:
            return
        
        was_playing = False
        if hasattr(self.video_player, 'mediaPlayer') and self.video_player.mediaPlayer.state() == self.video_player.mediaPlayer.PlayingState:
             was_playing = True
             self.video_player.pause_video()
            
        dialog = AnnotationDialog("00:00:00", "", "", self)
        if dialog.exec_() == QDialog.Accepted:
            annotation_data = dialog.get_annotation_data()
            if not annotation_data["start_time"] or not annotation_data["end_time"] or not annotation_data["label"]:
                QMessageBox.warning(self, "警告", "开始时间、结束时间和标签描述不能为空")
            else:
                self.annotation_manager.add_annotation(
                    annotation_data["start_time"],
                    annotation_data["end_time"],
                    annotation_data["label"]
                )
        if was_playing:
             self.video_player.play_video()

    def edit_annotation(self, item):
        """编辑标注项"""
        index = self.annotation_list.row(item)
        self._edit_annotation_at_index(index)

    def edit_selected_annotation(self):
        """编辑选中的标注"""
        items = self.annotation_list.selectedItems()
        if items:
            index = self.annotation_list.row(items[0])
            self._edit_annotation_at_index(index)

    def _edit_annotation_at_index(self, index):
        """实际执行编辑标注的逻辑"""
        if index < 0 or index >= len(self.annotations):
             return

        was_playing = False
        if hasattr(self.video_player, 'mediaPlayer') and self.video_player.mediaPlayer.state() == self.video_player.mediaPlayer.PlayingState:
             was_playing = True
             self.video_player.pause_video()

        annotation = self.annotations[index]
        dialog = AnnotationDialog(
            annotation["start_time"],
            annotation["end_time"],
            annotation["label"],
            self
        )

        if dialog.exec_() == QDialog.Accepted:
            annotation_data = dialog.get_annotation_data()
            if not annotation_data["end_time"] or not annotation_data["label"]:
                QMessageBox.warning(self, "警告", "结束时间和标签描述不能为空")
            else:
                self.annotation_manager.edit_annotation(
                    index,
                    annotation_data["start_time"],
                    annotation_data["end_time"],
                    annotation_data["label"]
                )
        if was_playing:
             self.video_player.play_video()

    def delete_annotation(self):
        """删除标注"""
        items = self.annotation_list.selectedItems()
        if not items:
            return
            
        index = self.annotation_list.row(items[0])
        if index < 0 or index >= len(self.annotations):
            return
            
        reply = QMessageBox.question(self, "确认删除", 
                                    "确定要删除此标注吗？",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.annotation_manager.delete_annotation(index)
    
    def update_annotation_list(self):
        """更新标注列表UI"""
        self.annotation_list.clear()
        for annotation in self.annotations:
            start_time = annotation.get("start_time", "??:??:??")
            end_time = annotation.get("end_time", "??:??:??")
            label = annotation.get("label", "")
            
            item_text = f"【{start_time} → {end_time}】 : {label}"
            item = QListWidgetItem(item_text)
            item.setToolTip(f"开始: {start_time}\n结束: {end_time}\n标签: {label}")
            self.annotation_list.addItem(item)
    
    def generate_annotation_data(self):
        """生成标注数据（调用API填充AI结果，不保存）"""
        if hasattr(self, 'api_in_progress') and self.api_in_progress:
            QMessageBox.information(self, "提示", "正在调用API，请稍候...")
            return
            
        if not self.current_video_path:
            QMessageBox.warning(self, "警告", "请先加载视频")
            return
            
        video_description = self.description_edit.toPlainText().strip()
        final_diagnosis_list = self.diagnosis_selector.get_selected_diagnoses()
        final_diagnosis = ", ".join(final_diagnosis_list)
        
        if not video_description or len(video_description) < 10:
            QMessageBox.warning(self, "警告", "请输入视频总描述，不少于10个字")
            return
        if not final_diagnosis_list:
            QMessageBox.warning(self, "警告", "请选择或输入诊断结果")
            return

        formatted_annotations = "\n".join([
            f"{a['start_time']}-{a['end_time']}: {a['label']}" 
            for a in self.annotations
        ])
        
        description_parts = []
        if video_description:
            description_parts.append(f"视频总描述:\n{video_description}")
        if formatted_annotations:
            description_parts.append(f"标注片段:\n{formatted_annotations}")
        api_input_description = "\n\n".join(description_parts)

        try:
            self.api_in_progress = True
            self.statusBar.showMessage("正在调用AI分析...")
            QApplication.processEvents()
            
            api_response = self.api_handler.call_api(api_input_description, final_diagnosis, self)
            
            self.thinking_chain_edit.setPlainText(api_response.get("reasoning", ""))
            self.ai_answer_edit.setPlainText(api_response.get("answer", ""))
            
            self.statusBar.showMessage("AI分析完成", 3000)
            self.mark_data_modified()

        except Exception as e:
            QMessageBox.warning(self, "API调用失败", f"调用AI服务时出错: {str(e)}\n请检查网络和模型设置，或手动输入分析内容。")
            self.statusBar.showMessage("AI分析失败", 3000)
            traceback.print_exc()
        finally:
            self.api_in_progress = False
            QApplication.processEvents()

    def open_output_folder_settings(self):
        """打开输出文件夹设置对话框"""
        dialog = OutputFolderDialog(self.file_handler.output_folder, self)
        if dialog.exec_() == QDialog.Accepted:
            selected_folder = dialog.get_selected_folder()
            if dialog.save_settings(selected_folder):
                self.file_handler.output_folder = selected_folder
                QMessageBox.information(self, "设置成功", f"输出文件夹已设置为: {selected_folder}")
                try:
                    os.makedirs(selected_folder, exist_ok=True)
                except Exception as e:
                     QMessageBox.warning(self, "警告", f"创建输出文件夹时出错: {str(e)}")















