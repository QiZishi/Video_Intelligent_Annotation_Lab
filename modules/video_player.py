import os
import cv2
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject, QSize
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QSlider, QPushButton, QFileDialog, QStyle, QMessageBox,
                            QComboBox, QButtonGroup, QRadioButton)
from PyQt5.QtGui import QImage, QPixmap, QIcon, QFont

class VideoPlayer(QWidget):
    """
    视频播放器模块，负责视频的播放、暂停、进度控制等功能
    """
    
    # 自定义信号
    position_changed = pyqtSignal(int)  # 视频位置变化信号
    duration_changed = pyqtSignal(int)  # 视频总时长变化信号
    end_reached = pyqtSignal()  # 视频播放结束信号
    segment_marked = pyqtSignal(str, str, str)  # 视频片段标记信号(start_time, end_time, label)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.video_path = ""
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.current_frame = 0
        self.total_frames = 0
        self.fps = 0
        self.is_playing = False
        self.mark_start_time = None  # 标记开始时间
        self.is_marking = False  # 标记状态
        
        # 新增：剪刀按钮点击次数计数器，用于解决连续点击问题
        self.scissors_click_count = 0
        
        # 新增：播放速度和音频状态
        self.play_speed = 1.0
        self.speed_options = [2.0,1.5,1.0,0.8,0.5,0.3,0.1]  # 播放速度选项
        
        # 视频步进大小（秒）
        self.step_size = 0.5
        
        # 缩放比例
        self.zoom_factor = 0.43
        
        self.setup_ui()
        
    def setup_ui(self):
        # 创建布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)
        
        # 视频显示区域
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("background-color: #161616; border-radius: 6px;")
        # 设置视频显示区域的固定大小，与图片中一致
        self.video_label.setFixedSize(1900, 800)
        main_layout.addWidget(self.video_label)
        
        # 控制区域
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(5, 5, 5, 5)
        
        # 缩放控制按钮 - 垂直布局
        zoom_button_layout = QVBoxLayout()
        zoom_button_layout.setSpacing(3) # 调整按钮间距

        zoom_in_btn = QPushButton("放大")
        zoom_in_btn.setStyleSheet("""
            QPushButton {
                background-color: #607d8b;
                color: white;
                border-radius: 4px;
                min-width: 50px; /* 调整宽度 */
                padding: 4px;
            }
            QPushButton:hover {
                background-color: #455a64;
            }
        """)
        zoom_in_btn.setToolTip("放大 (Ctrl+鼠标滚轮向上)")
        zoom_in_btn.clicked.connect(self.zoom_in)
        zoom_button_layout.addWidget(zoom_in_btn)

        zoom_out_btn = QPushButton("缩小")
        zoom_out_btn.setStyleSheet("""
            QPushButton {
                background-color: #607d8b;
                color: white;
                border-radius: 4px;
                min-width: 50px; /* 调整宽度 */
                padding: 4px;
            }
            QPushButton:hover {
                background-color: #455a64;
            }
        """)
        zoom_out_btn.setToolTip("缩小 (Ctrl+鼠标滚轮向下)")
        zoom_out_btn.clicked.connect(self.zoom_out)
        zoom_button_layout.addWidget(zoom_out_btn)
        
        zoom_reset_btn = QPushButton("重置")
        zoom_reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #607d8b;
                color: white;
                border-radius: 4px;
                min-width: 50px; /* 调整宽度 */
                padding: 4px;
            }
            QPushButton:hover {
                background-color: #455a64;
            }
        """)
        zoom_reset_btn.setToolTip("重置缩放 (Ctrl+鼠标中键)")
        zoom_reset_btn.clicked.connect(self.zoom_reset)
        zoom_button_layout.addWidget(zoom_reset_btn)
        
        # 将缩放按钮布局添加到主控制布局的开头
        controls_layout.addLayout(zoom_button_layout)
        
        # 播放/暂停按钮
        self.play_button = QPushButton()
        self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.play_button.setToolTip("播放/暂停")
        self.play_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                border-radius: 20px;
                min-width: 40px;
                min-height: 40px;
                padding: 0px;
                color: white;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.play_button.clicked.connect(self.toggle_play)
        controls_layout.addWidget(self.play_button)
        
        # 后退按钮
        self.backward_button = QPushButton()
        self.backward_button.setIcon(self.style().standardIcon(QStyle.SP_MediaSeekBackward))
        self.backward_button.setToolTip(f"后退 {self.step_size}秒")
        self.backward_button.setStyleSheet("""
            QPushButton {
                background-color: #7f8c8d;
                border-radius: 20px;
                min-width: 32px;
                min-height: 32px;
                padding: 0px;
                color: white;
            }
            QPushButton:hover {
                background-color: #95a5a6;
            }
        """)
        self.backward_button.clicked.connect(self.step_backward)
        controls_layout.addWidget(self.backward_button)
        
        # 前进按钮
        self.forward_button = QPushButton()
        self.forward_button.setIcon(self.style().standardIcon(QStyle.SP_MediaSeekForward))
        self.forward_button.setToolTip(f"前进 {self.step_size}秒")
        self.forward_button.setStyleSheet("""
            QPushButton {
                background-color: #7f8c8d;
                border-radius: 20px;
                min-width: 32px;
                min-height: 32px;
                padding: 0px;
                color: white;
            }
            QPushButton:hover {
                background-color: #95a5a6;
            }
        """)
        self.forward_button.clicked.connect(self.step_forward)
        controls_layout.addWidget(self.forward_button)
        
        # 添加剪刀按钮
        self.scissors_button = QPushButton("✂")
        self.scissors_button.setToolTip("标记视频片段 (Ctrl+D)")
        self.scissors_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                border-radius: 20px;
                min-width: 40px;
                min-height: 40px;
                padding: 0px;
                font-size: 16px;
                font-weight: bold;
                color: white;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.scissors_button.clicked.connect(self.mark_segment)
        controls_layout.addWidget(self.scissors_button)
        
        # 播放速度选择器
        self.speed_combo = QComboBox()
        self.speed_combo.addItems([f"{s}x" for s in self.speed_options])
        self.speed_combo.setCurrentIndex(2)  # 默认1.0x
        self.speed_combo.setStyleSheet("""
            QComboBox {
                background-color: #f0f0f0;
                border-radius: 4px;
                padding: 4px;
                min-width: 60px;
                border: 1px solid #ccc;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 16px;
                border-left: 1px solid #ccc;
            }
            QComboBox QAbstractItemView::item:hover { /* 添加下拉列表项悬停效果 */
                background-color: #d0e4f7; /* 高亮背景色 */
                color: yellow; /* 高亮文字颜色 - 确保为黑色 */
            }
            QComboBox:hover { /* 整体悬停效果（可选） */
                 border: 1px solid #3498db;
            }
        """)
        self.speed_combo.currentIndexChanged.connect(self.change_speed)
        controls_layout.addWidget(self.speed_combo)
        
        # 进度条
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 0)
        self.slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 10px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #B1B1B1, stop:1 #c4c4c4);
                margin: 2px 0;
                border-radius: 5px;
            }
            QSlider::handle:horizontal {
                background: #3498db;
                border: 1px solid #5c5c5c;
                width: 18px;
                height: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            QSlider::handle:horizontal:hover {
                background: #2980b9;
            }
        """)
        self.slider.sliderMoved.connect(self.set_position)
        self.slider.sliderPressed.connect(self.slider_pressed)
        self.slider.sliderReleased.connect(self.slider_released)
        controls_layout.addWidget(self.slider)
        
        # 时间标签
        self.time_label = QLabel("00:00.00 / 00:00.00")
        self.time_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #333333; min-width: 140px;")
        controls_layout.addWidget(self.time_label)
        
        main_layout.addLayout(controls_layout)
        self.setLayout(main_layout)
        
        # 设置键盘事件捕捉
        self.setFocusPolicy(Qt.StrongFocus)
    
    def zoom_in(self):
        """放大视频"""
        self.zoom_factor *= 1.2
        if self.cap:
            # 更新当前帧显示
            ret, frame = self.cap.read()
            if ret:
                self.display_frame(frame)
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)  # 重置位置
    
    def zoom_out(self):
        """缩小视频"""
        self.zoom_factor *= 0.8
        if self.cap:
            # 更新当前帧显示
            ret, frame = self.cap.read()
            if ret:
                self.display_frame(frame)
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)  # 重置位置
    
    def zoom_reset(self):
        """重置缩放"""
        self.zoom_factor = 0.43
        if self.cap:
            # 更新当前帧显示
            ret, frame = self.cap.read()
            if ret:
                self.display_frame(frame)
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)  # 重置位置
    
    def keyPressEvent(self, event):
        """处理键盘事件"""
        if event.key() == Qt.Key_Space:
            self.toggle_play()
        elif event.key() == Qt.Key_Left:
            self.step_backward()
        elif event.key() == Qt.Key_Right:
            self.step_forward()
        elif event.modifiers() & Qt.ControlModifier:  # 检查是否按下了 Ctrl 键
            if event.key() == Qt.Key_D:  # 检查是否是 D 键
                self.mark_segment()  # 调用标记片段功能
            elif event.key() == Qt.Key_Plus or event.key() == Qt.Key_Equal:
                self.zoom_in()
            elif event.key() == Qt.Key_Minus:
                self.zoom_out()
            elif event.key() == Qt.Key_0:
                self.zoom_reset()
            else:  # 如果是 Ctrl + 其他键，传递给父类处理
                super().keyPressEvent(event)
        else:  # 如果没有按下 Ctrl 键，传递给父类处理
            super().keyPressEvent(event)
    
    def wheelEvent(self, event):
        """处理鼠标滚轮事件"""
        # 检查是否按下Ctrl键
        if event.modifiers() & Qt.ControlModifier:
            delta = event.angleDelta().y()
            
            # 滚轮向上，放大视频
            if delta > 0:
                self.zoom_in()
            # 滚轮向下，缩小视频
            elif delta < 0:
                self.zoom_out()
                
            # 阻止事件传播
            event.accept()
        else:
            # 如果没有按Ctrl键，则传递事件给父类
            super().wheelEvent(event)
            
    def mousePressEvent(self, event):
        """处理鼠标按下事件"""
        # 检查是否是中键点击并且按下了Ctrl键
        if event.button() == Qt.MiddleButton and (event.modifiers() & Qt.ControlModifier):
            self.zoom_reset()
            event.accept()
        else:
            super().mousePressEvent(event)
    
    def change_speed(self, index):
        """改变播放速度"""
        if index >= 0 and index < len(self.speed_options):
            self.play_speed = self.speed_options[index]
            
            # 如果正在播放，调整播放速度
            if self.is_playing:
                self.timer.stop()
                interval = int(1000 / (self.fps * self.play_speed)) if self.fps > 0 else 100
                self.timer.start(max(1, interval))
        
    def step_backward(self):
        """后退指定秒数"""
        if not self.cap:
            return
            
        # 计算要后退的帧数
        frames_to_move = int(self.step_size * self.fps)
        new_position = max(0, self.current_frame - frames_to_move)
        
        # 设置新位置
        self.set_position(new_position)
        
    def step_forward(self):
        """前进指定秒数"""
        if not self.cap:
            return
            
        # 计算要前进的帧数
        frames_to_move = int(self.step_size * self.fps)
        new_position = min(self.total_frames - 1, self.current_frame + frames_to_move)
        
        # 设置新位置
        self.set_position(new_position)
        
    def load_video(self, video_path):
        """加载视频文件"""
        if not os.path.exists(video_path):
            print(f"文件不存在: {video_path}")
            return False
        
        # 关闭之前的视频
        self.stop_video()
        
        # 清除标记信息
        self.mark_start_time = None
        
        # 打开新视频
        self.video_path = video_path
        self.cap = cv2.VideoCapture(video_path)
        
        if not self.cap.isOpened():
            print(f"无法打开视频: {video_path}")
            return False
        
        # 获取视频信息
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.current_frame = 0
        
        # 更新UI
        self.slider.setRange(0, self.total_frames)
        self.update_time_label()
        self.duration_changed.emit(self.total_frames)
        
        # 显示第一帧
        ret, frame = self.cap.read()
        if ret:
            self.display_frame(frame)
        
        # 重置播放速度为默认值
        self.speed_combo.setCurrentIndex(2)  # 1.0x
        
        return True
        
    def toggle_play(self):
        """切换播放/暂停状态"""
        if not self.cap:
            return
            
        if self.is_playing:
            self.pause_video()
        else:
            self.play_video()
            
    def play_video(self):
        """播放视频"""
        if not self.cap:
            return
            
        self.is_playing = True
        self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        
        # 根据播放速度设置定时器间隔
        interval = int(1000 / (self.fps * self.play_speed)) if self.fps > 0 else 100
        self.timer.start(max(1, interval))
        
    def pause_video(self):
        """暂停视频"""
        if not self.cap:
            return
            
        self.is_playing = False
        self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.timer.stop()
        
    def stop_video(self):
        """停止视频"""
        self.pause_video()
        if self.cap:
            self.cap.release()
            self.cap = None
        self.current_frame = 0
        self.total_frames = 0
        self.fps = 0
        self.video_label.clear()
        self.slider.setRange(0, 0)
        self.time_label.setText("00:00.00 / 00:00.00")
        
    def update_frame(self):
        """更新视频帧"""
        if not self.cap or not self.is_playing:
            return

        ret, frame = self.cap.read()
        if not ret:
            # 当视频播放到末尾时，回到开头并暂停
            self.current_frame = 0
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.cap.read()
            
            # 如果不能获取帧，则停止播放
            if not ret:
                self.stop_video()
                return
                
            # 触发结束信号
            self.end_reached.emit()
            self.pause_video()

        self.current_frame += 1
        self.display_frame(frame)

        # 更新进度条，但避免触发滑动事件
        self.slider.blockSignals(True)
        self.slider.setValue(self.current_frame)
        self.slider.blockSignals(False)
        
        self.update_time_label()
            
    def display_frame(self, frame):
        """显示视频帧"""
        # 转换OpenCV格式(BGR)到Qt格式(RGB)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        
        # 创建QImage
        image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(image)
        
        # 应用缩放比例
        new_width = int(w * self.zoom_factor)
        new_height = int(h * self.zoom_factor)
        
        # 确保缩放后的尺寸有效
        if new_width <= 0 or new_height <= 0:
            # 如果缩放比例过小，使用原始尺寸或一个最小尺寸
            scaled_pixmap = pixmap.scaled(self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        else:
            scaled_pixmap = pixmap.scaled(new_width, new_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        self.video_label.setPixmap(scaled_pixmap)
            
    def slider_pressed(self):
        """滑块被按下时暂停视频并记录状态"""
        self.was_playing = self.is_playing
        self.pause_video()
            
    def set_position(self, position):
        """设置视频播放位置"""
        if not self.cap:
            return
            
        self.current_frame = position
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, position)
        self.position_changed.emit(position)
        self.update_time_label()
        
        # 更新当前帧显示
        ret, frame = self.cap.read()
        if ret:
            self.display_frame(frame)
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, position)  # 重置位置，因为读取帧会前进一帧
        
    def slider_released(self):
        """滑块释放后根据之前的状态决定是否恢复播放"""
        if hasattr(self, 'was_playing') and self.was_playing:
            self.play_video()
            
    def update_time_label(self):
        """更新时间标签，精确到毫秒"""
        if self.fps <= 0:
            return
            
        current_time = self.current_frame / self.fps
        total_time = self.total_frames / self.fps
        
        current_minutes = int(current_time // 60)
        current_seconds = int(current_time % 60)
        current_milliseconds = int((current_time * 100) % 100)
        
        total_minutes = int(total_time // 60)
        total_seconds = int(total_time % 60)
        total_milliseconds = int((total_time * 100) % 100)
        
        current_time_str = f"{current_minutes:02d}:{current_seconds:02d}.{current_milliseconds:02d}"
        total_time_str = f"{total_minutes:02d}:{total_seconds:02d}.{total_milliseconds:02d}"
        
        self.time_label.setText(f"{current_time_str} / {total_time_str}")
        
    def get_current_time_str(self):
        """获取当前时间字符串，精确到毫秒"""
        if not self.cap:
            return "00:00.000"

        current_time = self.current_frame / self.fps
        minutes = int(current_time // 60)
        seconds = int(current_time % 60)
        milliseconds = int((current_time * 1000) % 1000)
        return f"{minutes:02d}:{seconds:02d}.{milliseconds:03d}"
        
    def get_video_duration(self):
        """获取视频总时长（秒）"""
        if self.fps <= 0:
            return 0
        
        return self.total_frames / self.fps

    def mark_segment(self):
        """标记视频片段"""
        if not self.cap:
            return
            
        # 增加点击计数器
        self.scissors_click_count += 1
        
        # 只有当点击次数是单数时执行第一阶段，偶数时执行第二阶段
        current_time = self.get_current_time_str()
        
        if self.scissors_click_count % 2 == 1:
            # 第一次点击：设置开始时间
            self.mark_start_time = current_time
            self.is_marking = True
            self.scissors_button.setStyleSheet("""
                QPushButton {
                    background-color: #f39c12;
                    border-radius: 20px;
                    min-width: 40px;
                    min-height: 40px;
                    padding: 0px;
                    font-size: 16px;
                    font-weight: bold;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #e67e22;
                }
            """)
            self.scissors_button.setToolTip("点击标记片段结束时间 (Ctrl+D)")
        else:
            # 第二次点击：设置结束时间并发射信号
            end_time = current_time
            
            # 在发射信号前暂停视频
            self.pause_video() 
            
            # 重置剪刀按钮样式
            self.scissors_button.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    border-radius: 20px;
                    min-width: 40px;
                    min-height: 40px;
                    padding: 0px;
                    font-size: 16px;
                    font-weight: bold;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            self.scissors_button.setToolTip("标记视频片段 (Ctrl+D)")
            
            # 发射信号 - 发送空标签，让主程序处理标注对话框
            self.segment_marked.emit(self.mark_start_time, end_time, "")
            
            # 重置标记状态，为下一次标记做准备
            self.mark_start_time = None
            self.is_marking = False

    def clear(self):
        """清除视频显示和状态"""
        self.stop_video()
        self.video_label.clear()
        self.time_label.setText("00:00.00 / 00:00.00")
        self.slider.setValue(0)
        self.mark_start_time = None
        self.is_marking = False
        self.scissors_click_count = 0
        # 重置剪刀按钮样式
        self.scissors_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                border-radius: 20px;
                min-width: 40px;
                min-height: 40px;
                padding: 0px;
                font-size: 16px;
                font-weight: bold;
                color: white;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.scissors_button.setToolTip("标记视频片段 (Ctrl+D)")


