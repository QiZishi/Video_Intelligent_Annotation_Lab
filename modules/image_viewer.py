import os
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, 
                            QScrollArea, QHBoxLayout, QPushButton, QToolBar)
from PyQt5.QtGui import QImage, QPixmap, QTransform, QIcon

class ImageViewer(QWidget):
    """
    图片查看器模块，负责显示和浏览图片，支持缩放和旋转
    """
    
    # 自定义信号
    image_changed = pyqtSignal(int)  # 当前图片索引变化信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image_paths = []
        self.current_index = -1
        
        # 图片操作属性
        self.current_zoom = 0.5  # 默认缩放为0.5倍
        self.rotation_angle = 0
        self.original_pixmap = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # 创建布局
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # 添加工具栏
        toolbar = QToolBar()
        toolbar.setStyleSheet("""
            QToolBar {
                spacing: 8px; 
                background-color: #f0f0f0; 
                border-radius: 6px;
                border: 1px solid #ddd;
                padding: 3px;
            }
        """)
        
        # 放大按钮
        self.zoom_in_button = QPushButton()
        self.zoom_in_button.setIcon(QIcon.fromTheme("zoom-in", QIcon()))
        self.zoom_in_button.setToolTip("放大 (Ctrl++)")
        self.zoom_in_button.setStyleSheet("""
            QPushButton {
                min-width: 40px; 
                min-height: 40px; 
                border-radius: 20px; 
                background-color: #4CAF50; 
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3d8b40;
            }
        """)
        self.zoom_in_button.setText("放大🔍+")
        self.zoom_in_button.clicked.connect(self.zoom_in)
        toolbar.addWidget(self.zoom_in_button)

        # 缩小按钮
        self.zoom_out_button = QPushButton()
        self.zoom_out_button.setIcon(QIcon.fromTheme("zoom-out", QIcon()))
        self.zoom_out_button.setToolTip("缩小 (Ctrl+-)")
        self.zoom_out_button.setStyleSheet("""
            QPushButton {
                min-width: 40px; 
                min-height: 40px; 
                border-radius: 20px; 
                background-color: #2196F3; 
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
        """)
        self.zoom_out_button.setText("缩小🔍-")
        self.zoom_out_button.clicked.connect(self.zoom_out)
        toolbar.addWidget(self.zoom_out_button)

        # 旋转按钮
        self.rotate_button = QPushButton()
        self.rotate_button.setIcon(QIcon.fromTheme("object-rotate-right", QIcon()))
        self.rotate_button.setToolTip("旋转90度 (Ctrl+R)")
        self.rotate_button.setStyleSheet("""
            QPushButton {
                min-width: 40px; 
                min-height: 40px; 
                border-radius: 20px; 
                background-color: #FF9800; 
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e68900;
            }
        """)
        self.rotate_button.setText("旋转↻")
        self.rotate_button.clicked.connect(self.rotate_image)
        toolbar.addWidget(self.rotate_button)
        
        # 重置缩放按钮
        self.reset_button = QPushButton()
        self.reset_button.setToolTip("重置 (Ctrl+0)")
        self.reset_button.setStyleSheet("""
            QPushButton {
                min-width: 40px; 
                min-height: 40px; 
                border-radius: 20px; 
                background-color: #F44336; 
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        self.reset_button.setText("重置↺")
        self.reset_button.clicked.connect(self.reset_image)
        toolbar.addWidget(self.reset_button)

        layout.addWidget(toolbar)
        
        # 图片显示区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignCenter)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #f5f5f5; 
                border: 1px solid #ddd; 
                border-radius: 6px;
            }
        """)
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: #f8f8f8; 
                border-radius: 4px;
            }
        """)
        
        self.scroll_area.setWidget(self.image_label)
        layout.addWidget(self.scroll_area)
        
        # 控制区域
        controls_layout = QHBoxLayout()
        
        # 上一张按钮
        self.prev_button = QPushButton("上一张")
        self.prev_button.setStyleSheet("""
            QPushButton {
                min-height: 32px; 
                background-color: #2196F3; 
                color: white; 
                border-radius: 16px; 
                padding: 5px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #989898;
            }
        """)
        self.prev_button.clicked.connect(self.show_previous_image)
        controls_layout.addWidget(self.prev_button)
        
        # 图片计数标签
        self.count_label = QLabel("0/0")
        self.count_label.setAlignment(Qt.AlignCenter)
        self.count_label.setStyleSheet("""
            QLabel {
                font-weight: bold; 
                color: #333;
                font-size: 14px;
            }
        """)
        controls_layout.addWidget(self.count_label)
        
        # 下一张按钮
        self.next_button = QPushButton("下一张")
        self.next_button.setStyleSheet("""
            QPushButton {
                min-height: 32px; 
                background-color: #2196F3; 
                color: white; 
                border-radius: 16px; 
                padding: 5px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #989898;
            }
        """)
        self.next_button.clicked.connect(self.show_next_image)
        controls_layout.addWidget(self.next_button)
        
        layout.addLayout(controls_layout)
        self.setLayout(layout)
        
        # 初始状态下禁用按钮
        self.update_buttons()
        
        # 设置快捷键和鼠标滚轮事件
        self.setFocusPolicy(Qt.StrongFocus)
        self.scroll_area.viewport().installEventFilter(self)
        
    def eventFilter(self, source, event):
        """监听鼠标滚轮事件"""
        if (source is self.scroll_area.viewport() and 
            event.type() == event.Wheel and 
            event.modifiers() == Qt.ControlModifier):
            
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom_in()
            else:
                self.zoom_out()
            return True
            
        return super().eventFilter(source, event)
        
    def keyPressEvent(self, event):
        """处理键盘事件"""
        if event.key() == Qt.Key_Left:
            self.show_previous_image()
        elif event.key() == Qt.Key_Right:
            self.show_next_image()
        elif event.modifiers() & Qt.ControlModifier:
            if event.key() == Qt.Key_Plus or event.key() == Qt.Key_Equal:  # Ctrl++
                self.zoom_in()
            elif event.key() == Qt.Key_Minus:  # Ctrl+-
                self.zoom_out()
            elif event.key() == Qt.Key_0:  # Ctrl+0
                self.reset_image()
            elif event.key() == Qt.Key_R:  # Ctrl+R
                self.rotate_image()
        super().keyPressEvent(event)
        
    def load_images(self, image_paths):
        """加载图片列表"""
        self.image_paths = [path for path in image_paths if self.is_image_file(path)]
        self.current_index = -1
        
        if self.image_paths:
            self.current_index = 0
            self.show_current_image()
        else:
            self.image_label.clear()
            self.image_label.setText("没有可显示的图片")
            self.count_label.setText("0/0")
            
        self.update_buttons()
        return len(self.image_paths) > 0
        
    def is_image_file(self, file_path):
        """检查文件是否为图片格式"""
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif']
        ext = os.path.splitext(file_path)[1].lower()
        return ext in image_extensions
        
    def show_current_image(self):
        """显示当前索引的图片"""
        if 0 <= self.current_index < len(self.image_paths):
            image_path = self.image_paths[self.current_index]
            self.load_image(image_path)
            self.count_label.setText(f"{self.current_index + 1}/{len(self.image_paths)}")
            self.image_changed.emit(self.current_index)
            
    def load_image(self, image_path):
        """加载并显示图片"""
        # 重置缩放为默认值(0.5)和旋转角度
        self.current_zoom = 0.5
        self.rotation_angle = 0
        
        if not os.path.exists(image_path):
            self.image_label.setText(f"图片不存在: {image_path}")
            return
            
        # 加载图片
        self.original_pixmap = QPixmap(image_path)
        if self.original_pixmap.isNull():
            self.image_label.setText(f"无法加载图片: {image_path}")
            return
            
        # 显示图片
        self.update_image_display()
        
    def update_image_display(self):
        """根据当前的缩放和旋转更新图片显示"""
        if self.original_pixmap is None:
            return

        # 创建变换
        transform = QTransform()
        transform.rotate(self.rotation_angle)

        # 应用变换
        rotated_pixmap = self.original_pixmap.transformed(transform, Qt.SmoothTransformation)

        # 应用缩放
        scaled_size = rotated_pixmap.size() * self.current_zoom
        if scaled_size.width() > 0 and scaled_size.height() > 0:
            scaled_pixmap = rotated_pixmap.scaled(
                scaled_size, 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )

            self.image_label.setPixmap(scaled_pixmap)
            self.image_label.resize(scaled_pixmap.size())
            
    def zoom_in(self):
        """放大图片"""
        if self.original_pixmap is None:
            return
        self.current_zoom *= 1.25  # 放大25%
        self.update_image_display()

    def zoom_out(self):
        """缩小图片"""
        if self.original_pixmap is None:
            return
        self.current_zoom *= 0.8  # 缩小20%
        self.update_image_display()

    def rotate_image(self):
        """旋转图片90度"""
        if self.original_pixmap is None:
            return
        self.rotation_angle = (self.rotation_angle + 90) % 360
        self.update_image_display()
        
    def reset_image(self):
        """重置图片缩放和旋转"""
        if self.original_pixmap is None:
            return
        self.current_zoom = 0.5  # 重置为默认缩放比例(0.5倍)
        self.rotation_angle = 0
        self.update_image_display()
            
    def show_next_image(self):
        """显示下一张图片"""
        if self.current_index < len(self.image_paths) - 1:
            self.current_index += 1
            self.show_current_image()
            self.update_buttons()
            
    def show_previous_image(self):
        """显示上一张图片"""
        if self.current_index > 0:
            self.current_index -= 1
            self.show_current_image()
            self.update_buttons()
            
    def update_buttons(self):
        """更新按钮状态"""
        has_images = len(self.image_paths) > 0
        has_current_image = has_images and self.original_pixmap is not None
        
        self.prev_button.setEnabled(has_images and self.current_index > 0)
        self.next_button.setEnabled(has_images and self.current_index < len(self.image_paths) - 1)
        self.zoom_in_button.setEnabled(has_current_image)
        self.zoom_out_button.setEnabled(has_current_image)
        self.rotate_button.setEnabled(has_current_image)
        self.reset_button.setEnabled(has_current_image)
        
    def clear(self):
        """清除所有图片"""
        self.image_paths = []
        self.current_index = -1
        self.original_pixmap = None
        self.image_label.clear()
        self.count_label.setText("0/0")
        self.update_buttons()