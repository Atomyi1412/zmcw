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
    QPushButton, QLabel, QGroupBox, QApplication, QLineEdit, QSizePolicy, QSlider, QSpinBox, QWidget
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from config import PetConfig


class SettingsDialog(QDialog):
    """
    设置对话框类
    
    提供用户设置界面，包括：
    - 是否置顶显示
    - 宠物名称
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
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint | Qt.WindowStaysOnTopHint)
        
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setSpacing(14)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # （移除与窗口标题重复的居中标题标签）
        
        # 显示设置组
        display_group = QGroupBox("显示设置")
        display_layout = QVBoxLayout()
        display_layout.setSpacing(12)
        display_layout.setContentsMargins(12, 14, 12, 12)
        
        # 置顶选项
        self.always_on_top_checkbox = QCheckBox("始终置顶显示")
        self.always_on_top_checkbox.setToolTip("勾选后，桌面宠物将始终显示在其他程序窗口之上")
        display_layout.addWidget(self.always_on_top_checkbox)
        
        # 自动下落选项
        self.auto_fall_checkbox = QCheckBox("自动下落（松手后从上半区下落）")
        self.auto_fall_checkbox.setToolTip("关闭后，松手将不触发自动下落动画")
        display_layout.addWidget(self.auto_fall_checkbox)
        
        # 宠物大小（缩放）
        size_widget = QWidget()
        size_layout = QVBoxLayout(size_widget)
        size_layout.setSpacing(6)
        size_layout.setContentsMargins(0, 0, 0, 0)
        # 顶部信息行：说明 + 右侧百分比
        info_row = QHBoxLayout()
        info_row.setSpacing(8)
        self.size_help_label = QLabel("大小调整（当前 100%）")
        help_font = QFont()
        help_font.setPointSize(11)
        self.size_help_label.setFont(help_font)
        self.size_help_label.setWordWrap(True)
        info_row.addWidget(self.size_help_label)
        info_row.addStretch(1)
        self.pet_scale_value_label = QLabel("100%")
        self.pet_scale_value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.pet_scale_value_label.setMinimumWidth(48)
        info_row.addWidget(self.pet_scale_value_label)
        size_layout.addLayout(info_row)

        # 第二行：仅放滑块
        slider_row = QHBoxLayout()
        slider_row.setContentsMargins(0, 0, 0, 0)
        self.pet_scale_slider = QSlider(Qt.Horizontal)
        self.pet_scale_slider.setMinimum(int(PetConfig.MIN_PET_SCALE * 100))
        self.pet_scale_slider.setMaximum(int(PetConfig.MAX_PET_SCALE * 100))
        self.pet_scale_slider.setSingleStep(5)
        self.pet_scale_slider.setPageStep(10)
        self.pet_scale_slider.setTickPosition(QSlider.TicksBelow)
        self.pet_scale_slider.setTickInterval(10)
        self.pet_scale_slider.setFixedHeight(22)
        self.pet_scale_slider.setToolTip(f"拖动以调整宠物显示比例（{int(PetConfig.MIN_PET_SCALE * 100)}% - {int(PetConfig.MAX_PET_SCALE * 100)}%）")
        slider_row.addWidget(self.pet_scale_slider)
        size_layout.addLayout(slider_row)
        display_layout.addWidget(size_widget)
        
        # 将显示设置组加入主布局
        display_group.setLayout(display_layout)
        main_layout.addWidget(display_group)
        
        # 个性化设置组：宠物名称
        personalize_group = QGroupBox("个性化")
        personalize_layout = QVBoxLayout()
        personalize_layout.setContentsMargins(15, 18, 15, 15)
        personalize_layout.setSpacing(10)
        
        name_row = QHBoxLayout()
        name_row.setContentsMargins(0, 8, 0, 8)
        name_row.setSpacing(12)
        name_label = QLabel("宠物名称：")
        self.pet_name_edit = QLineEdit()
        self.pet_name_edit.setPlaceholderText("给你的宠物取个名字吧，例如：小乔治")
        # 本段使用的通用字体
        font = QFont()
        font.setPointSize(12)
        # 设置输入框字体
        self.pet_name_edit.setFont(font)
        name_label.setFont(font)
        name_label.setFixedWidth(72)
        self.pet_name_edit.setMinimumWidth(260)
        self.pet_name_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.pet_name_edit.setMinimumHeight(30)
        self.pet_name_edit.setStyleSheet("QLineEdit { padding: 4px 8px; }")  # 避免在部分主题中背景异常
        name_row.addWidget(name_label)
        name_row.addWidget(self.pet_name_edit, 1)
        personalize_layout.addLayout(name_row)
        personalize_group.setLayout(personalize_layout)
        main_layout.addWidget(personalize_group)
        
        # 弹性空间和按钮行
        main_layout.addStretch()
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.addStretch()
        cancel_button = QPushButton("取消")
        cancel_button.setFixedSize(80, 30)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        ok_button = QPushButton("确定")
        ok_button.setFixedSize(80, 30)
        ok_button.setDefault(True)
        ok_button.clicked.connect(self.accept_settings)
        button_layout.addWidget(ok_button)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)
        
        # 样式：使用系统原生样式避免控件不可见
        self.setStyleSheet("")
        
    def on_scale_changed(self, v: int):
        """滑块变化时，更新百分比标签、说明文字与 tooltip。"""
        try:
            percent_text = f"{int(v)}%"
            self.pet_scale_value_label.setText(percent_text)
            self.size_help_label.setText(f"大小调整（当前 {percent_text}）")
            self.pet_scale_slider.setToolTip(f"拖动以调整宠物显示比例（当前 {percent_text}）")
        except Exception:
            pass
        
    def load_current_settings(self):
        """
        加载当前设置到界面
        """
        always_on_top = self.current_settings.get('always_on_top', PetConfig.ALWAYS_ON_TOP)
        self.always_on_top_checkbox.setChecked(always_on_top)
    
        pet_name = self.current_settings.get('pet_name', PetConfig.DEFAULT_PET_NAME)
        self.pet_name_edit.setText(str(pet_name))
    
        # 加载缩放
        pet_scale = float(self.current_settings.get('pet_scale', PetConfig.DEFAULT_PET_SCALE))
        slider_value = int(max(PetConfig.MIN_PET_SCALE, min(PetConfig.MAX_PET_SCALE, pet_scale)) * 100)
        self.pet_scale_slider.setValue(slider_value)
        # 同步更新两个标签
        self.on_scale_changed(slider_value)
        # 连接信号（先断开可能的旧连接）
        try:
            self.pet_scale_slider.valueChanged.disconnect()
        except Exception:
            pass
        self.pet_scale_slider.valueChanged.connect(self.on_scale_changed)
    
        # 加载自动下落设置
        auto_fall = bool(self.current_settings.get('auto_fall', PetConfig.DEFAULT_AUTO_FALL))
        self.auto_fall_checkbox.setChecked(auto_fall)
    
    def get_settings(self):
        """
        获取当前设置
    
        Returns:
            dict: 设置字典
        """
        name = self.pet_name_edit.text().strip()
        if not name:
            name = PetConfig.DEFAULT_PET_NAME
        # 限制长度，避免过长撑破布局
        if len(name) > 20:
            name = name[:20]
        pet_scale = max(PetConfig.MIN_PET_SCALE, min(PetConfig.MAX_PET_SCALE, self.pet_scale_slider.value() / 100.0))
        return {
            'always_on_top': self.always_on_top_checkbox.isChecked(),
            'pet_name': name,
            'pet_scale': pet_scale,
            'auto_fall': self.auto_fall_checkbox.isChecked()
        }
    
    def accept_settings(self):
        """
        确认设置并关闭对话框
        """
        new_settings = self.get_settings()
        self.settings_changed.emit(new_settings)
        self.accept()
    
    def keyPressEvent(self, a0):
        """
        处理键盘事件
    
        Args:
            a0: 键盘事件
        """
        if a0.key() == Qt.Key_Escape:
            self.reject()
        elif a0.key() == Qt.Key_Return or a0.key() == Qt.Key_Enter:
            self.accept_settings()
        else:
            super().keyPressEvent(a0)
    
    
if __name__ == "__main__":
    # 测试代码
    app = QApplication(sys.argv)
    
    # 测试设置
    test_settings = {
        'always_on_top': True,
        'pet_name': '小可爱'
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