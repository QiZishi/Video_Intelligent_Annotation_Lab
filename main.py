#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import traceback
from PyQt5.QtWidgets import QApplication
from modules.main_window import MainWindow
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon

def resource_path(relative_path):
    """获取资源的绝对路径，兼容开发环境和打包后的环境"""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def ensure_config_directories():
    """确保配置目录存在"""
    config_dir = resource_path("config")
    os.makedirs(config_dir, exist_ok=True)

def exception_hook(exctype, value, traceback_obj):
    """全局异常捕获处理"""
    traceback_str = ''.join(traceback.format_exception(exctype, value, traceback_obj))
    print(f"Error: {traceback_str}")

def main():
    """程序入口函数"""
    # 设置异常捕获器
    sys.excepthook = exception_hook
    
    # 确保配置目录存在
    ensure_config_directories()
    
    # 创建应用实例
    app = QApplication(sys.argv)
    app.setApplicationName("智能视频标注分析平台（慧影）")
    app.setStyle('Fusion')  # 使用Fusion风格，在不同平台上保持一致外观
    icon_path = resource_path("logo.ico")
    if os.path.exists(icon_path):
        app_icon = QIcon(icon_path)
        app.setWindowIcon(app_icon)
    
    # 创建主窗口
    main_window = MainWindow()
    main_window.setWindowTitle("智能视频标注分析平台（慧影）- VIAL (Video Intelligent Annotation Lab)")
    
    # 使用QTimer确保界面元素初始化后再最大化显示
    QTimer.singleShot(100, main_window.showMaximized)
    
    # 显示主窗口
    main_window.show()
    
    # 运行应用
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()