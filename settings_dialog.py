# -*- coding: utf-8 -*-
"""
设置对话框模块
提供桌面宠物的各种设置选项，包括置顶显示等功能
"""

import sys
import json
import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QCheckBox, 
    QPushButton, QLabel, QGroupBox, QApplication
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from config import PetConfig


class SettingsDialog(QDialog):
    """
    设置对话框类
    
    提供用户设置界面，包括：
    - 是否置顶显示
    - 其他设置选项（可扩展）
    """
    
    # 设置改变信号
    settings_changed = pyqtSignal(dict)
    
    def __init__(self, parent=None, current_settings=None):
        """
        初始化设置对话框
        
        Args:
            parent: 父窗口
            current_settings: 当前设置字典
        """
        super().__init__(parent)
        self.current_settings = current_settings or {}
        self.setup_ui()
        self.load_current_settings()
        
    def setup_ui(self):
        """
        设置用户界面
        """
        self.setWindowTitle("桌面宠物设置")
        self.setFixedSize(PetConfig.SETTINGS_DIALOG_WIDTH, PetConfig.SETTINGS_DIALOG_HEIGHT)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title_label = QLabel("桌面宠物设置")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 显示设置组
        display_group = QGroupBox("显示设置")
        display_layout = QVBoxLayout()
        
        # 置顶选项
        self.always_on_top_checkbox = QCheckBox("始终置顶显示")
        self.always_on_top_checkbox.setToolTip("勾选后，桌面宠物将始终显示在其他程序窗口之上")
        display_layout.addWidget(self.always_on_top_checkbox)
        
        display_group.setLayout(display_layout)
        main_layout.addWidget(display_group)
        
        # 添加弹性空间
        main_layout.addStretch()
        
        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # 取消按钮
        cancel_button = QPushButton("取消")
        cancel_button.setFixedSize(80, 30)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        # 确定按钮
        ok_button = QPushButton("确定")
        ok_button.setFixedSize(80, 30)
        ok_button.setDefault(True)
        ok_button.clicked.connect(self.accept_settings)
        button_layout.addWidget(ok_button)
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
        
        # 设置样式
        self.setStyleSheet("""
            QDialog {
                background-color: #f0f0f0;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QCheckBox {
                font-size: 12px;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid #cccccc;
                background-color: white;
                border-radius: 3px;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #4CAF50;
                background-color: #4CAF50;
                border-radius: 3px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        
    def load_current_settings(self):
        """
        加载当前设置到界面
        """
        always_on_top = self.current_settings.get('always_on_top', PetConfig.ALWAYS_ON_TOP)
        self.always_on_top_checkbox.setChecked(always_on_top)
        
    def get_settings(self):
        """
        获取当前设置
        
        Returns:
            dict: 设置字典
        """
        return {
            'always_on_top': self.always_on_top_checkbox.isChecked()
        }
        
    def accept_settings(self):
        """
        确认设置并关闭对话框
        """
        new_settings = self.get_settings()
        self.settings_changed.emit(new_settings)
        self.accept()
        
    def keyPressEvent(self, event):
        """
        处理键盘事件
        
        Args:
            event: 键盘事件
        """
        if event.key() == Qt.Key_Escape:
            self.reject()
        elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.accept_settings()
        else:
            super().keyPressEvent(event)


if __name__ == "__main__":
    # 测试代码
    app = QApplication(sys.argv)
    
    # 测试设置
    test_settings = {
        'always_on_top': True
    }
    
    dialog = SettingsDialog(current_settings=test_settings)
    
    def on_settings_changed(settings):
        print(f"设置已更改: {settings}")
    
    dialog.settings_changed.connect(on_settings_changed)
    
    if dialog.exec_() == QDialog.Accepted:
        print("用户确认了设置")
    else:
        print("用户取消了设置")
    
    sys.exit(app.exec_())