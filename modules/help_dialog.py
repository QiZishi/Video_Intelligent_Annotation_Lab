import os
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QTabWidget, QWidget,
                             QScrollArea, QSizePolicy, QApplication)
from PyQt5.QtGui import QIcon, QPixmap, QFont, QColor

class HelpDialog(QDialog):
    """帮助对话框，用于展示软件使用说明"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("使用说明")
        self.resize(1100, 900)  # 增大对话框尺寸
        base_font_size = QApplication.font().pointSizeF()
        help_font_size = base_font_size * 1.3
        title_font_size = base_font_size * 1.5

        self.setStyleSheet(f"""
            QDialog {{
                background-color: #f8f9fa;
            }}
            QLabel {{
                color: #333;
                font-size: {help_font_size}pt;
                line-height: 1.5;
            }}
            QLabel[isTitle="true"] {{
                 font-size: {title_font_size}pt;
                 font-weight: bold;
                 color: #2980b9;
                 padding: 8px;
            }}
            QLabel[isSectionTitle="true"] {{
                 font-weight: bold;
                 font-size: {help_font_size * 1.1}pt;
                 color: #2c3e50;
                 padding-top: 15px;
                 margin-bottom: 5px;
            }}
            QLabel[isNoteTitle="true"] {{
                 font-weight: bold;
                 font-size: {help_font_size * 1.1}pt;
                 color: #e74c3c;
                 padding-top: 20px;
                 margin-bottom: 5px;
            }}
            QLabel[isShortcutKey="true"] {{
                 font-size: {help_font_size}pt;
                 color: #34495e;
                 padding-left: 15px;
                 margin-bottom: 5px;
            }}
            QPushButton {{
                background-color: #4a86e8;
                color: white;
                border-radius: 4px;
                padding: 8px 15px;
                font-size: {base_font_size * 1.1}pt;
            }}
            QPushButton:hover {{
                background-color: #3a76d8;
            }}
        """)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)

        title_label = QLabel("智能视频标注分析平台使用说明")
        title_label.setProperty("isTitle", True)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        self.tab_widget = QTabWidget()

        basic_tab = self.create_basic_tab()
        self.tab_widget.addTab(basic_tab, "基本使用")

        features_tab = self.create_features_tab()
        self.tab_widget.addTab(features_tab, "功能详解")

        shortcuts_tab = self.create_shortcuts_tab()
        self.tab_widget.addTab(shortcuts_tab, "快捷键")

        faq_tab = self.create_faq_tab()
        self.tab_widget.addTab(faq_tab, "常见问题")

        layout.addWidget(self.tab_widget)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        close_button = QPushButton("关闭")
        close_button.clicked.connect(self.accept)
        close_button.setMinimumWidth(120)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def create_basic_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)

        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setSpacing(10)

        steps = [
            ("1. 导入数据", "点击工具栏上的 \"导入数据文件夹\" 按钮 (文件夹图标)，选择包含多个样本子文件夹的根目录。程序会自动扫描所有子文件夹。每个子文件夹应包含一个视频文件和相关的图片文件。"),
            ("2. 视频播放和标注", "程序会自动加载第一个待处理子文件夹中的视频和图片。\n- 使用播放器下方的按钮控制视频的播放/暂停 (空格键)、前进/后退 (左右箭头键)。\n- 使用下拉菜单选择播放速度。\n- 在需要标注的位置点击红色的剪刀按钮(✂)或按 Ctrl+D 两次，标记一个视频片段。第一次点击标记开始时间，第二次点击标记结束时间。"),
            ("3. 添加/编辑片段标注", "- 标记视频片段后，会弹出对话框，输入该片段的文字描述，然后点击 \"确定\"。\n- 已添加的标注会显示在视频下方的 \"视频片段标注\" 列表中。\n- 您可以双击列表中的标注，或选中后点击 \"编辑\" 按钮来修改它。\n- 选中标注后点击 \"删除\" 按钮可将其移除。\n- 点击 \"添加\" 按钮可以手动输入开始、结束时间和描述来添加标注。"),
            ("4. 图片查看", "切换到 \"图片\" 选项卡可以查看当前文件夹中的图片。\n- 使用下方的按钮或快捷键 (Ctrl+ +/-/0/R, Ctrl+鼠标滚轮, Ctrl+鼠标中键) 放大、缩小、旋转或重置图片。\n- 如果有多张图片，使用左右箭头按钮或键盘左右箭头键进行翻页。"),
            ("5. 添加视频总描述", "在右侧的 \"视频总描述\" 区域输入对整个视频的综合性描述，**必须不少于10个字** 。"),
            ("6. 选择诊断结果", "在 \"诊断结果\" 区域，勾选一个或多个符合视频表现的诊断标签。**必须至少选择一项**。\n- 如果列表中没有合适的选项，勾选 \"其他\" 并在下方输入框中输入自定义诊断。\n- 您可以在 \"模型参数设置\" -> \"诊断结果标签设置\" 中管理这些标签。"),
            ("7. 生成AI分析数据", "点击右下角的 \"生成标注数据\" 按钮。程序会将视频描述、片段标注和诊断结果发送给AI模型进行分析，生成思维链和答案。这个过程可能需要几十秒到一分钟，请耐心等待。"),
            ("8. 查看与修改AI结果", "AI分析完成后，\"思维链\" 和 \"大模型答案\" 区域会显示结果。您可以根据需要手动编辑这两个区域的内容。"),
            ("9. 保存并处理下一个", "确认所有信息无误后，点击 \"确定保存\" 按钮。\n- 程序会将当前视频的所有标注信息（包括描述、诊断、AI结果等）保存到输出文件夹对应的 JSONL 文件中，并自动加载下一个未处理的子文件夹。\n- 如果所有文件夹都已处理，程序会提示完成。"),
            ("10. 查看历史记录", "点击工具栏上的 \"查看上一条已存数据\" 按钮，可以回溯查看已保存的标注记录。此时界面会加载对应视频和已保存的标注信息。您可以修改后再次点击 \"确定保存\" 来更新记录。\n- 点击 \"返回当前待处理数据\" 按钮可以跳回到最新的未处理文件夹。")
        ]

        for title, desc in steps:
            step_title = QLabel(title)
            step_title.setProperty("isSectionTitle", True)
            content_layout.addWidget(step_title)

            step_desc = QLabel(desc)
            step_desc.setWordWrap(True)
            step_desc.setStyleSheet(f"padding-left: 15px; margin-bottom: 10px; font-size: {self.font().pointSizeF()}pt;")
            content_layout.addWidget(step_desc)

        note_title = QLabel("注意事项")
        note_title.setProperty("isNoteTitle", True)
        content_layout.addWidget(note_title)

        note = QLabel("- **视频总描述** (不少于10字) 和 **诊断结果** 是必须填写的，否则无法保存。\n"
                      "- 片段标注不是必须的，但有助于AI更准确地分析。\n"
                      "- 生成AI分析数据需要连接互联网，并确保API设置正确。\n"
                      "- 保存操作会覆盖之前对同一视频的标注数据。\n"
                      "- 输出文件夹和API参数可以在工具栏的设置中修改。\n"
                      "- 诊断标签列表也可以在设置中自定义。")
        note.setStyleSheet(f"padding-left: 15px; font-size: {self.font().pointSizeF()}pt;")
        note.setWordWrap(True)
        content_layout.addWidget(note)

        content_layout.addStretch()
        content_widget.setLayout(content_layout)
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)

        tab.setLayout(layout)
        return tab

    def create_features_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)

        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setSpacing(10)

        features = [
            ("视频播放控制", "- **播放/暂停**: 点击播放按钮或按空格键。\n"
                          "- **步进**: 点击前进/后退按钮或按左右箭头键 (默认0.5秒)。\n"
                          "- **进度条**: 拖动滑块跳转到视频任意位置。\n"
                          "- **变速播放**: 使用下拉菜单选择 0.1x 到 2.0x 的播放速度。\n"
                          "- **缩放**: 使用按钮或 Ctrl+鼠标滚轮/Ctrl+ +/- 键进行缩放，Ctrl+鼠标中键/Ctrl+0 重置。"),

            ("片段标注", "- **标记**: 使用剪刀按钮(✂)或按 Ctrl+D 两次标记片段起止时间。\n"
                      "- **添加/编辑/删除**: 在弹窗或列表中进行操作。\n"
                      "- **时间格式**: 时间精确到毫秒 (HH:MM:SS.fff)。"),

            ("图片查看", "- **多图浏览**: 若文件夹含多张图片，可通过按钮或左右箭头键翻页。\n"
                      "- **缩放/旋转/重置**: 提供多种操作方式，包括快捷键。"),

            ("数据管理", "- **导入**: 支持导入包含多层子文件夹的数据集。\n"
                       "- **输出**: 自动在指定的输出文件夹下创建与导入文件夹同名的子目录，存放处理后的视频 (videos/ 目录) 和 JSONL 标注文件。\n"
                       "- **自动续标**: 程序会记录已处理的视频，\"确定保存\" 后自动加载下一个未处理的。\n"
                       "- **历史回溯**: 可以方便地查看和修改已保存的标注记录。"),

            ("AI集成", "- **模型调用**: 点击 \"生成标注数据\" 按钮，调用配置的AI模型进行分析。\n"
                     "- **结果展示**: 思维链和最终答案会显示在对应文本框中，并可编辑。\n"
                     "- **数据保存**: AI结果会随其他标注信息一同保存在 JSONL 文件中。"),

            ("参数设置", "- **模型参数**: 在工具栏设置 (齿轮图标) 中配置 API Base URL、模型名称、API密钥、系统提示语、用户提示语模板 (用于AI分析) 和人类提问模板 (用于JSONL输出)。\n"
                        "- **输出文件夹**: 在工具栏设置 (文件夹图标) 中指定保存结果的位置。\n"
                        "- **诊断标签**: 在工具栏设置 (扳手图标) 中添加、编辑、删除或恢复默认的诊断标签列表。")
        ]

        for title, desc in features:
            section_title = QLabel(title)
            section_title.setProperty("isSectionTitle", True)
            content_layout.addWidget(section_title)

            section_desc = QLabel(desc)
            section_desc.setWordWrap(True)
            section_desc.setStyleSheet(f"padding-left: 15px; margin-bottom: 15px; font-size: {self.font().pointSizeF()}pt;")
            content_layout.addWidget(section_desc)

        content_layout.addStretch()
        content_widget.setLayout(content_layout)
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)

        tab.setLayout(layout)
        return tab

    def create_shortcuts_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)

        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setSpacing(10)

        title = QLabel("键盘与鼠标快捷键")
        title.setProperty("isSectionTitle", True)
        title.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(title)

        video_title = QLabel("视频播放器")
        video_title.setProperty("isSectionTitle", True)
        content_layout.addWidget(video_title)

        video_shortcuts = [
            ("空格键", "播放 / 暂停 视频"),
            ("左箭头", f"视频后退 {self.parent().video_player.step_size if self.parent() else 0.5} 秒"),
            ("右箭头", f"视频前进 {self.parent().video_player.step_size if self.parent() else 0.5} 秒"),
            ("Ctrl + D", "标记视频片段开始 / 结束时间 (点击两次)"),
            ("Ctrl + 鼠标滚轮向上", "放大视频"),
            ("Ctrl + +", "放大视频"),
            ("Ctrl + 鼠标滚轮向下", "缩小视频"),
            ("Ctrl + -", "缩小视频"),
            ("Ctrl + 鼠标中键点击", "重置视频缩放"),
            ("Ctrl + 0", "重置视频缩放"),
        ]

        for key, desc in video_shortcuts:
            shortcut = QLabel(f"<b>{key}</b>: {desc}")
            shortcut.setProperty("isShortcutKey", True)
            content_layout.addWidget(shortcut)

        image_title = QLabel("图片查看器")
        image_title.setProperty("isSectionTitle", True)
        content_layout.addWidget(image_title)

        image_shortcuts = [
            ("Ctrl + 鼠标滚轮", "放大 / 缩小 图片"),
            ("Ctrl + +", "放大图片"),
            ("Ctrl + -", "缩小图片"),
            ("Ctrl + 鼠标中键点击", "重置图片大小和旋转"),
            ("Ctrl + 0", "重置图片大小和旋转"),
            ("Ctrl + R", "向右旋转图片 90 度"),
            ("左箭头", "显示上一张图片 (若有多张)"),
            ("右箭头", "显示下一张图片 (若有多张)"),
        ]

        for key, desc in image_shortcuts:
            shortcut = QLabel(f"<b>{key}</b>: {desc}")
            shortcut.setProperty("isShortcutKey", True)
            content_layout.addWidget(shortcut)

        content_layout.addStretch()
        content_widget.setLayout(content_layout)
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)

        tab.setLayout(layout)
        return tab

    def create_faq_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)

        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setSpacing(10)

        faqs = [
            ("Q: 点击 \"生成标注数据\" 时提示 API 调用失败怎么办？",
             "A: 请检查以下几点：\n"
             "  - 电脑是否已连接到互联网。\n"
             "  - 工具栏 -> 模型参数设置 -> API密钥 是否已正确添加。\n"
             "  - API Base URL 和模型名称是否适用于您添加的密钥。\n"
             "  - 您的API账户是否有效或有足够余额。\n"
             "  - 尝试在设置中 \"恢复默认设置\"，然后重新添加您的密钥。\n"
             "  - 如果使用本地模型或代理，请确保服务正在运行且地址正确。"),

            ("Q: 视频无法播放或显示黑屏？",
             "A: 请尝试：\n"
             "  - 确认视频文件本身没有损坏，可以用其他播放器打开。\n"
             "  - 确认视频格式是常见的格式 (如 .mp4, .avi, .mov, .mkv)。\n"
             "  - 可能是缺少视频解码器。对于 Windows 系统，安装 K-Lite Codec Pack 等解码器包可能会有帮助。"),

            ("Q: 如何提高标注效率？",
             "A: - 熟练使用快捷键进行播放控制和片段标记 (空格, 左右箭头, Ctrl+D)。\n"
             "  - 使用变速播放功能快速浏览视频。\n"
             "  - 对于常见的片段描述，可以先在别处写好，然后复制粘贴到标签描述框中。\n"
             "  - 提前在设置中配置好常用的诊断标签。"),

            ("Q: 生成的标注数据保存在哪里？",
             "A: - 数据保存在您通过工具栏设置的 \"输出文件夹\" 中。\n"
             "  - 程序会在输出文件夹内创建一个与您导入的根文件夹同名的子目录。\n"
             "  - 该子目录内包含一个 `videos` 文件夹 (存放复制过来的视频文件) 和一个与子目录同名的 `.jsonl` 文件 (包含所有标注信息)。"),

            ("Q: 如何修改已经保存的标注数据？",
             "A: - **推荐方式**: 使用程序的回溯功能。点击 \"查看上一条已存数据\" 找到要修改的记录，修改完成后点击 \"确定保存\" 即可覆盖更新。\n"
             "  - **手动方式**: 直接用文本编辑器打开对应的 `.jsonl` 文件进行修改。请注意 JSONL 格式要求，每行是一个完整的 JSON 对象。修改后程序下次加载会读取修改后的内容。"),

            ("Q: 如何自定义诊断标签？",
             "A: - 在工具栏点击 \"诊断结果标签设置\" (扳手图标)。\n"
             "  - 在弹出的对话框中，您可以 \"新增\"、\"编辑\" 或 \"删除\" 标签。\n"
             "  - 也可以 \"恢复默认设置\"。\n"
             "  - 修改后的标签列表将在下次程序启动时或重新加载数据时生效。\n"
             "  - \"其他\" 选项始终存在，用于输入不在列表中的诊断。"),

            ("Q: 为什么有时候点击剪刀按钮(✂)或按 Ctrl+D 没反应？",
             "A: - 标记片段需要点击两次：第一次标记开始，第二次标记结束。请确保您点击了两次。\n"
             "  - 第一次点击后，剪刀按钮会变色 (橙色)，提示您需要再次点击以标记结束。\n"
             "  - 如果正在进行其他操作（如API调用），按钮可能会暂时禁用。")
        ]

        for q, a in faqs:
            question = QLabel(q)
            question.setProperty("isSectionTitle", True)
            question.setWordWrap(True)
            content_layout.addWidget(question)

            answer = QLabel(a)
            answer.setWordWrap(True)
            answer.setStyleSheet(f"padding-left: 15px; margin-bottom: 15px; font-size: {self.font().pointSizeF()}pt;")
            content_layout.addWidget(answer)

        content_layout.addStretch()
        content_widget.setLayout(content_layout)
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)

        tab.setLayout(layout)
        return tab