import os
from PyQt5.QtCore import QObject, pyqtSignal, Qt
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                             QDialogButtonBox, QLineEdit, QMessageBox, QLabel)
from PyQt5.QtGui import QFont


class AnnotationDialog(QDialog):
    """标注对话框，用于添加视频片段标注"""
    
    def __init__(self, start_time, end_time="", label="", parent=None):
        super().__init__(parent)
        self.start_time = start_time
        self.end_time = end_time
        self.label = label
        
        self.setWindowTitle("添加片段标注")
        self.resize(500, 240)
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 8px;
            }
            QLabel {
                color: #333;
                font-weight: bold;
                font-size: 14px;
            }
            QLineEdit {
                border: 1px solid #aaa;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
                font-size: 13px;
                min-height: 20px;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
                background-color: #EFF8FB;
            }
            QPushButton {
                background-color: #4a86e8;
                color: white;
                border-radius: 6px;
                padding: 8px 15px;
                font-weight: bold;
                font-size: 13px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #3a76d8;
            }
            QPushButton:pressed {
                background-color: #2a66c8;
            }
        """)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(18)
        
        # 标题
        title_label = QLabel("视频片段标注")
        title_label.setStyleSheet("font-size: 16px; color: #2980b9; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # 表单布局
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        # 开始时间（只读）
        self.start_time_edit = QLineEdit(self.start_time)
        self.start_time_edit.setReadOnly(True)
        self.start_time_edit.setStyleSheet("background-color: #f0f0f0;")
        form_layout.addRow("开始时间:", self.start_time_edit)
        
        # 结束时间
        self.end_time_edit = QLineEdit(self.end_time)
        form_layout.addRow("结束时间:", self.end_time_edit)
        
        # 标签描述
        self.label_edit = QLineEdit(self.label)
        self.label_edit.setPlaceholderText("请输入该视频片段的描述")
        form_layout.addRow("标签描述:", self.label_edit)
        
        layout.addLayout(form_layout)
        
        # 提示信息
        tip_label = QLabel("提示: 标注片段将用于AI模型分析视频中的异常内容")
        tip_label.setStyleSheet("font-size: 12px; color: #7f8c8d; font-style: italic;")
        layout.addWidget(tip_label)
        
        # 按钮
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.button(QDialogButtonBox.Ok).setText("确定")
        self.button_box.button(QDialogButtonBox.Cancel).setText("取消")
        
        # 增强确定按钮的处理
        self.button_box.accepted.connect(self.validate_and_accept)
        self.button_box.rejected.connect(self.reject)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.button_box)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # 设置焦点
        if not self.end_time:
            self.end_time_edit.setFocus()
        else:
            self.label_edit.setFocus()
    
    def validate_and_accept(self):
        """验证输入并接受对话框"""
        self.end_time = self.end_time_edit.text().strip()
        self.label = self.label_edit.text().strip()
        
        # 检查必填字段
        if not self.end_time:
            QMessageBox.warning(self, "警告", "请输入结束时间")
            self.end_time_edit.setFocus()
            return
            
        if not self.label:
            QMessageBox.warning(self, "警告", "请输入标签描述")
            self.label_edit.setFocus()
            return
            
        # 当数据有效时，接受对话框并关闭
        self.accept()
        
    def get_annotation_data(self):
        """获取标注数据"""
        return {
            "start_time": self.start_time,
            "end_time": self.end_time,
            "label": self.label
        }


class AnnotationManager(QObject):
    """标注管理器，处理视频片段标注的相关操作"""
    
    annotation_changed = pyqtSignal(list)  # 标注变更信号，传递更新后的标注列表
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.annotations = []
        
    def clear_annotations(self):
        """清除所有标注"""
        self.annotations = []
        self.annotation_changed.emit(self.annotations)
    
    def add_annotation(self, start_time, end_time, label):
        """添加标注"""
        if not end_time or not label:
            return False
            
        annotation = {
            "start_time": start_time,
            "end_time": end_time,
            "label": label
        }
        
        self.annotations.append(annotation)
        self.annotation_changed.emit(self.annotations)
        return True
    
    def edit_annotation(self, index, start_time, end_time, label):
        """编辑标注"""
        if index < 0 or index >= len(self.annotations):
            return False
            
        if not end_time or not label:
            return False
            
        self.annotations[index] = {
            "start_time": start_time,
            "end_time": end_time,
            "label": label
        }
        
        self.annotation_changed.emit(self.annotations)
        return True
    
    def delete_annotation(self, index):
        """删除标注"""
        if index < 0 or index >= len(self.annotations):
            return False
            
        self.annotations.pop(index)
        self.annotation_changed.emit(self.annotations)
        return True
    
    def get_annotations(self):
        """获取所有标注"""
        return self.annotations
    
    def get_annotation(self, index):
        """获取指定索引的标注"""
        if 0 <= index < len(self.annotations):
            return self.annotations[index]
        return None
    
    def set_annotations(self, annotations):
        """设置标注列表"""
        self.annotations = annotations if annotations else []
        self.annotation_changed.emit(self.annotations)
    
    def get_annotations_text(self):
        """获取标注的文本表示"""
        return "\n".join([
            f"{a['start_time']}-{a['end_time']}: {a['label']}" 
            for a in self.annotations
        ])