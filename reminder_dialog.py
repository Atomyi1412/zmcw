# -*- coding: utf-8 -*-
"""
提醒对话框类
用于设置提醒时间和提醒内容
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QTimeEdit, QLineEdit, QPushButton, QMessageBox,
    QRadioButton, QButtonGroup, QSpinBox, QComboBox
)
from PyQt5.QtCore import QTime, Qt
from PyQt5.QtGui import QFont
from config import PetConfig

class ReminderDialog(QDialog):
    """提醒设置对话框类"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 初始化UI组件
        self.time_edit = None
        self.content_edit = None
        self.confirm_button = None
        self.cancel_button = None
        
        # 提醒类型相关组件
        self.single_radio = None
        self.repeat_radio = None
        self.reminder_type_group = None
        
        # 循环提醒相关组件
        self.interval_spinbox = None
        self.interval_unit_combo = None
        self.interval_label = None
        
        # 设置对话框属性
        self.init_dialog()
        
        # 设置界面布局
        self.setup_ui()
    
    def init_dialog(self):
        """初始化对话框属性"""
        self.setWindowTitle('设置提醒')
        self.setFixedSize(480, 420)  # 增加宽度和高度以容纳所有控件
        
        # 设置窗口标志：模态对话框
        self.setWindowFlags(
            Qt.Dialog |
            Qt.WindowTitleHint |
            Qt.WindowCloseButtonHint
        )
        
        # 设置为模态对话框
        self.setModal(True)
    
    def setup_ui(self):
        """设置界面布局"""
        # 创建主布局
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)  # 增加控件间距
        main_layout.setContentsMargins(25, 25, 25, 25)  # 增加边距
        
        # 标题标签
        title_label = QLabel('设置提醒')
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 提醒类型选择区域
        type_layout = QVBoxLayout()
        type_layout.setSpacing(10)
        type_title = QLabel('提醒类型:')
        type_title_font = QFont()
        type_title_font.setPointSize(12)
        type_title_font.setBold(True)
        type_title.setFont(type_title_font)
        type_layout.addWidget(type_title)
        
        # 创建单选按钮组
        self.reminder_type_group = QButtonGroup()
        
        radio_layout = QHBoxLayout()
        radio_layout.setSpacing(30)  # 增加单选按钮间距
        self.single_radio = QRadioButton('单次提醒')
        self.repeat_radio = QRadioButton('循环提醒')
        self.single_radio.setChecked(True)  # 默认选择单次提醒
        
        # 设置单选按钮字体
        radio_font = QFont()
        radio_font.setPointSize(11)
        self.single_radio.setFont(radio_font)
        self.repeat_radio.setFont(radio_font)
        
        self.reminder_type_group.addButton(self.single_radio, 0)
        self.reminder_type_group.addButton(self.repeat_radio, 1)
        
        radio_layout.addWidget(self.single_radio)
        radio_layout.addWidget(self.repeat_radio)
        radio_layout.addStretch()  # 添加弹性空间
        type_layout.addLayout(radio_layout)
        main_layout.addLayout(type_layout)
        
        # 时间选择区域（单次提醒）
        self.time_layout = QHBoxLayout()
        self.time_layout.setSpacing(15)
        time_label = QLabel('提醒时间:')
        time_label.setMinimumWidth(100)
        time_label_font = QFont()
        time_label_font.setPointSize(11)
        time_label.setFont(time_label_font)
        
        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat('HH:mm')
        self.time_edit.setTime(QTime.currentTime().addSecs(300))  # 默认5分钟后
        self.time_edit.setMinimumHeight(35)  # 设置最小高度
        self.time_edit.setMinimumWidth(120)  # 设置最小宽度
        
        self.time_layout.addWidget(time_label)
        self.time_layout.addWidget(self.time_edit)
        self.time_layout.addStretch()  # 添加弹性空间
        main_layout.addLayout(self.time_layout)
        
        # 循环提醒频率设置区域
        self.interval_layout = QHBoxLayout()
        self.interval_layout.setSpacing(15)
        self.interval_label = QLabel('提醒间隔:')
        self.interval_label.setMinimumWidth(100)
        interval_label_font = QFont()
        interval_label_font.setPointSize(11)
        self.interval_label.setFont(interval_label_font)
        
        self.interval_spinbox = QSpinBox()
        self.interval_spinbox.setMinimum(1)
        self.interval_spinbox.setMaximum(999)
        self.interval_spinbox.setValue(1)
        self.interval_spinbox.setMinimumHeight(35)
        self.interval_spinbox.setMinimumWidth(80)
        
        self.interval_unit_combo = QComboBox()
        self.interval_unit_combo.addItems(['分钟', '小时'])
        self.interval_unit_combo.setMinimumHeight(35)
        self.interval_unit_combo.setMinimumWidth(80)
        
        self.interval_layout.addWidget(self.interval_label)
        self.interval_layout.addWidget(self.interval_spinbox)
        self.interval_layout.addWidget(self.interval_unit_combo)
        self.interval_layout.addStretch()  # 添加弹性空间
        main_layout.addLayout(self.interval_layout)
        
        # 初始状态：隐藏循环提醒设置
        self.toggle_interval_controls(False)
        
        # 内容输入区域
        content_layout = QVBoxLayout()
        content_layout.setSpacing(10)
        content_label = QLabel('提醒内容:')
        content_label_font = QFont()
        content_label_font.setPointSize(11)
        content_label_font.setBold(True)
        content_label.setFont(content_label_font)
        
        self.content_edit = QLineEdit()
        self.content_edit.setPlaceholderText('请输入提醒内容...')
        self.content_edit.setText('该休息一下了！')
        self.content_edit.setMinimumHeight(40)  # 增加输入框高度
        content_edit_font = QFont()
        content_edit_font.setPointSize(11)
        self.content_edit.setFont(content_edit_font)
        
        content_layout.addWidget(content_label)
        content_layout.addWidget(self.content_edit)
        main_layout.addLayout(content_layout)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)
        button_layout.addStretch()  # 左侧弹性空间
        
        self.cancel_button = QPushButton('取消')
        self.cancel_button.clicked.connect(self.safe_reject)
        self.cancel_button.setMinimumSize(100, 40)  # 设置按钮尺寸
        cancel_button_font = QFont()
        cancel_button_font.setPointSize(11)
        self.cancel_button.setFont(cancel_button_font)
        
        self.confirm_button = QPushButton('确认')
        self.confirm_button.clicked.connect(self.accept_reminder)
        self.confirm_button.setDefault(True)  # 设为默认按钮
        self.confirm_button.setMinimumSize(100, 40)  # 设置按钮尺寸
        confirm_button_font = QFont()
        confirm_button_font.setPointSize(11)
        self.confirm_button.setFont(confirm_button_font)
        
        # 设置按钮样式
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """)
        
        self.confirm_button.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: white;
                border: 1px solid #005a9e;
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #004a7e;
            }
        """)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.confirm_button)
        button_layout.addStretch()  # 右侧弹性空间
        main_layout.addLayout(button_layout)
        
        # 设置主布局
        self.setLayout(main_layout)
        
        # 连接信号
        self.single_radio.toggled.connect(self.on_reminder_type_changed)
        self.repeat_radio.toggled.connect(self.on_reminder_type_changed)
    
    def get_reminder_time(self):
        """获取用户设置的提醒时间"""
        return self.time_edit.time()
    
    def get_reminder_content(self):
        """获取用户输入的提醒内容"""
        return self.content_edit.text().strip()
    
    def get_reminder_type(self):
        """获取提醒类型"""
        return 'single' if self.single_radio.isChecked() else 'repeat'
    
    def get_reminder_interval(self):
        """获取循环提醒间隔（分钟）"""
        if self.repeat_radio.isChecked():
            value = self.interval_spinbox.value()
            unit = self.interval_unit_combo.currentText()
            if unit == '小时':
                return value * 60  # 转换为分钟
            return value
        return 0
    
    def toggle_interval_controls(self, show):
        """切换循环提醒控件的显示状态"""
        self.interval_label.setVisible(show)
        self.interval_spinbox.setVisible(show)
        self.interval_unit_combo.setVisible(show)
    
    def on_reminder_type_changed(self):
        """提醒类型改变事件处理"""
        is_repeat = self.repeat_radio.isChecked()
        self.toggle_interval_controls(is_repeat)
        
        # 切换时间选择控件的可见性
        time_label = self.time_layout.itemAt(0).widget()
        time_label.setVisible(not is_repeat)
        self.time_edit.setVisible(not is_repeat)
    
    def accept_reminder(self):
        """确认按钮处理"""
        try:
            # 验证输入
            content = self.get_reminder_content()
            if not content:
                QMessageBox.warning(self, '输入错误', '请输入提醒内容！')
                if hasattr(self, 'content_edit') and self.content_edit:
                    self.content_edit.setFocus()
                return
            
            reminder_type = self.get_reminder_type()
            
            if reminder_type == 'single':
                # 单次提醒：验证时间（确保不是过去的时间）
                current_time = QTime.currentTime()
                reminder_time = self.get_reminder_time()
                
                if reminder_time <= current_time:
                    QMessageBox.warning(self, '时间错误', '提醒时间不能是过去的时间！')
                    if hasattr(self, 'time_edit') and self.time_edit:
                        self.time_edit.setFocus()
                    return
            else:
                # 循环提醒：验证间隔
                interval = self.get_reminder_interval()
                if interval < 1:
                    QMessageBox.warning(self, '间隔错误', '提醒间隔不能小于1分钟！')
                    if hasattr(self, 'interval_spinbox') and self.interval_spinbox:
                        self.interval_spinbox.setFocus()
                    return
            
            # 验证通过，安全接受对话框
            self.safe_accept()
        except Exception as e:
            print(f"accept_reminder error: {e}")
            # 发生异常时安全关闭
            self.safe_reject()
    
    def safe_accept(self):
        """安全的确认操作"""
        try:
            self.accept()
        except Exception as e:
            print(f"safe_accept error: {e}")
            # 强制关闭对话框
            self.close()
    
    def safe_reject(self):
        """安全的取消操作"""
        try:
            self.reject()
        except Exception as e:
            print(f"safe_reject error: {e}")
            # 强制关闭对话框
            self.close()
    
    def keyPressEvent(self, event):
        """键盘事件处理"""
        try:
            # 按Enter键确认
            if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                self.accept_reminder()
            # 按Escape键取消
            elif event.key() == Qt.Key_Escape:
                self.safe_reject()
            else:
                super().keyPressEvent(event)
        except Exception as e:
            print(f"keyPressEvent error: {e}")
    
    def closeEvent(self, event):
        """窗口关闭事件处理"""
        try:
            # 清理资源
            if hasattr(self, 'reminder_type_group'):
                self.reminder_type_group.deleteLater()
            
            # 断开所有信号连接
            if hasattr(self, 'single_radio'):
                self.single_radio.toggled.disconnect()
            if hasattr(self, 'repeat_radio'):
                self.repeat_radio.toggled.disconnect()
            if hasattr(self, 'confirm_button'):
                self.confirm_button.clicked.disconnect()
            if hasattr(self, 'cancel_button'):
                self.cancel_button.clicked.disconnect()
            
            event.accept()
        except Exception as e:
            print(f"closeEvent error: {e}")
            event.accept()
    
    def __del__(self):
        """析构函数"""
        try:
            # 清理所有组件引用
            self.time_edit = None
            self.content_edit = None
            self.confirm_button = None
            self.cancel_button = None
            self.single_radio = None
            self.repeat_radio = None
            self.reminder_type_group = None
            self.interval_spinbox = None
            self.interval_unit_combo = None
            self.interval_label = None
        except Exception as e:
            print(f"__del__ error: {e}")