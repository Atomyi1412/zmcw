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
from PyQt5.QtCore import QTime, pyqtSignal, Qt
from PyQt5.QtGui import QFont
from config import PetConfig

class ReminderDialog(QDialog):
    """提醒设置对话框类"""
    
    # 定义信号
    reminder_added = pyqtSignal(str, QTime, str, int, int)  # 内容, 时间, 类型, 间隔, 相对秒数
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 初始化UI组件
        self.time_edit = None
        self.content_edit = None
        self.confirm_button = None
        self.cancel_button = None
        
        # 移除标题相关变量
        
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
        # 延后固定尺寸，构建完UI后按内容自适应
        
        # 设置窗口标志：模态对话框
        self.setWindowFlags(
            Qt.Dialog |
            Qt.WindowTitleHint |
            Qt.WindowCloseButtonHint |
            Qt.WindowStaysOnTopHint
        )
        
        # 设置为模态对话框
        self.setModal(True)

    def setup_ui(self):
        """设置界面布局"""
        # 创建主布局
        main_layout = QVBoxLayout()
        main_layout.setSpacing(4)  # 更紧凑的行间距
        main_layout.setContentsMargins(8, 6, 8, 6)  # 左右8，上下6，进一步减少留白
        
        # 标题标签
        title_label = QLabel('设置提醒')
        title_font = QFont()
        title_font.setPointSize(15)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        # main_layout.addWidget(title_label)
        
        # 提醒类型选择区域（单行：标签 + 单选按钮）
        type_layout = QHBoxLayout()
        type_layout.setSpacing(6)
        type_title = QLabel('提醒类型:')
        type_title_font = QFont()
        type_title_font.setPointSize(15)
        type_title.setFont(type_title_font)
        type_title.setMinimumWidth(72)
        
        # 创建单选按钮组
        self.reminder_type_group = QButtonGroup()
        self.single_radio = QRadioButton('单次提醒')
        self.repeat_radio = QRadioButton('循环提醒')
        self.relative_radio = QRadioButton('延迟提醒')
        self.single_radio.setChecked(True)
        radio_font = QFont(); radio_font.setPointSize(15)
        self.single_radio.setFont(radio_font)
        self.repeat_radio.setFont(radio_font)
        self.relative_radio.setFont(radio_font)
        self.reminder_type_group.addButton(self.single_radio, 0)
        self.reminder_type_group.addButton(self.repeat_radio, 1)
        self.reminder_type_group.addButton(self.relative_radio, 2)
        
        type_layout.addWidget(type_title)
        type_layout.addWidget(self.single_radio)
        type_layout.addWidget(self.repeat_radio)
        type_layout.addWidget(self.relative_radio)
        type_layout.addStretch()
        main_layout.addLayout(type_layout)
        
        # 移除标题输入区域
        
        # 时间选择区域（单次提醒）
        self.time_layout = QHBoxLayout()
        self.time_layout.setSpacing(4)
        time_label = QLabel('提醒时间:')
        time_label.setMinimumWidth(72)
        time_label_font = QFont()
        time_label_font.setPointSize(15)
        time_label.setFont(time_label_font)
        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat('HH:mm')
        self.time_edit.setTime(QTime.currentTime().addSecs(300))
        self.time_edit.setMinimumHeight(32)
        self.time_edit.setMinimumWidth(112)
        time_edit_font = QFont(); time_edit_font.setPointSize(15)
        self.time_edit.setFont(time_edit_font)
        self.time_layout.addWidget(time_label)
        self.time_layout.addWidget(self.time_edit)
        self.time_layout.addStretch()
        main_layout.addLayout(self.time_layout)
        
        # 循环提醒频率设置区域
        self.interval_layout = QHBoxLayout()
        self.interval_layout.setSpacing(4)
        self.interval_label = QLabel('提醒间隔:')
        self.interval_label.setMinimumWidth(72)
        interval_label_font = QFont()
        interval_label_font.setPointSize(15)
        self.interval_label.setFont(interval_label_font)
        self.interval_spinbox = QSpinBox()
        self.interval_spinbox.setRange(1, 999)
        self.interval_spinbox.setValue(1)
        self.interval_spinbox.setMinimumHeight(32)
        self.interval_spinbox.setMinimumWidth(72)
        interval_spin_font = QFont(); interval_spin_font.setPointSize(15)
        self.interval_spinbox.setFont(interval_spin_font)
        self.interval_unit_combo = QComboBox()
        self.interval_unit_combo.addItems(['分钟', '小时'])
        self.interval_unit_combo.setMinimumHeight(32)
        self.interval_unit_combo.setMinimumWidth(72)
        interval_unit_font = QFont(); interval_unit_font.setPointSize(15)
        self.interval_unit_combo.setFont(interval_unit_font)
        self.interval_layout.addWidget(self.interval_label)
        self.interval_layout.addWidget(self.interval_spinbox)
        self.interval_layout.addWidget(self.interval_unit_combo)
        self.interval_layout.addStretch()
        main_layout.addLayout(self.interval_layout)
        
        # 相对时间提醒设置区域
        self.relative_layout = QHBoxLayout()
        self.relative_layout.setSpacing(4)
        self.relative_label = QLabel('延迟时间:')
        self.relative_label.setMinimumWidth(72)
        relative_label_font = QFont()
        relative_label_font.setPointSize(15)
        self.relative_label.setFont(relative_label_font)
        self.relative_spinbox = QSpinBox()
        self.relative_spinbox.setRange(1, 999)
        self.relative_spinbox.setValue(5)
        self.relative_spinbox.setMinimumHeight(32)
        self.relative_spinbox.setMinimumWidth(72)
        relative_spin_font = QFont(); relative_spin_font.setPointSize(15)
        self.relative_spinbox.setFont(relative_spin_font)
        self.relative_unit_combo = QComboBox()
        self.relative_unit_combo.addItems(['秒', '分钟', '小时'])
        self.relative_unit_combo.setMinimumHeight(32)
        self.relative_unit_combo.setMinimumWidth(72)
        relative_unit_font = QFont(); relative_unit_font.setPointSize(15)
        self.relative_unit_combo.setFont(relative_unit_font)
        self.relative_layout.addWidget(self.relative_label)
        self.relative_layout.addWidget(self.relative_spinbox)
        self.relative_layout.addWidget(self.relative_unit_combo)
        self.relative_layout.addStretch()
        main_layout.addLayout(self.relative_layout)
        
        # 初始状态：隐藏循环提醒和相对时间设置
        self.toggle_interval_controls(False)
        self.toggle_relative_controls(False)
        
        # 内容输入区域 -> 横向单行：标签 + 输入框
        content_layout = QHBoxLayout()
        content_layout.setSpacing(6)
        content_label = QLabel('提醒内容:')
        content_label_font = QFont()
        content_label_font.setPointSize(15)
        content_label.setFont(content_label_font)
        content_label.setMinimumWidth(72)
        self.content_edit = QLineEdit()
        self.content_edit.setPlaceholderText('请输入提醒内容...')
        content_font = QFont(); content_font.setPointSize(15)
        self.content_edit.setFont(content_font)
        self.content_edit.setMinimumHeight(32)
        content_layout.addWidget(content_label)
        content_layout.addWidget(self.content_edit)
        main_layout.addLayout(content_layout)
        
        # 确认和取消按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        button_layout.addStretch()
        self.cancel_button = QPushButton('取消')
        self.cancel_button.setMinimumSize(86, 32)
        self.confirm_button = QPushButton('确定')
        self.confirm_button.setMinimumSize(86, 32)
        
        # 新增：连接按钮信号
        self.cancel_button.clicked.connect(self.safe_reject)
        self.confirm_button.clicked.connect(self.accept_reminder)
        self.confirm_button.setDefault(True)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.confirm_button)
        main_layout.addLayout(button_layout)
        
        # 连接信号
        self.single_radio.toggled.connect(self.on_reminder_type_changed)
        self.repeat_radio.toggled.connect(self.on_reminder_type_changed)
        self.relative_radio.toggled.connect(self.on_reminder_type_changed)
        
        self.setLayout(main_layout)
        
        # 构建完成
    
    def get_reminder_time(self):
        """获取用户设置的提醒时间"""
        return self.time_edit.time()
    
    def get_reminder_content(self):
        """获取用户输入的提醒内容"""
        return self.content_edit.text().strip()
    
    # 移除get_reminder_title方法
    
    def get_reminder_type(self):
        """获取提醒类型"""
        if self.single_radio.isChecked():
            return 'single'
        elif self.repeat_radio.isChecked():
            return 'repeat'
        else:
            return 'relative'
    
    def get_reminder_interval(self):
        """获取循环提醒间隔（分钟）"""
        if self.repeat_radio.isChecked():
            value = self.interval_spinbox.value()
            unit = self.interval_unit_combo.currentText()
            if unit == '小时':
                return value * 60  # 转换为分钟
            return value
        return 0
    
    def get_relative_seconds(self):
        """获取相对时间（秒）"""
        value = self.relative_spinbox.value()
        unit = self.relative_unit_combo.currentText()
        if unit == '秒':
            return value
        elif unit == '分钟':
            return value * 60
        else:  # 小时
            return value * 3600
    
    def toggle_interval_controls(self, show):
        """切换循环提醒控件的显示状态"""
        self.interval_label.setVisible(show)
        self.interval_spinbox.setVisible(show)
        self.interval_unit_combo.setVisible(show)
    
    def toggle_relative_controls(self, show):
        """切换相对时间提醒控件的显示状态"""
        self.relative_label.setVisible(show)
        self.relative_spinbox.setVisible(show)
        self.relative_unit_combo.setVisible(show)
    
    def on_reminder_type_changed(self):
        """提醒类型改变事件处理"""
        is_single = self.single_radio.isChecked()
        is_repeat = self.repeat_radio.isChecked()
        is_relative = self.relative_radio.isChecked()
        
        # 控制各种控件的显示
        self.toggle_interval_controls(is_repeat)
        self.toggle_relative_controls(is_relative)
        
        # 切换时间选择控件的可见性（只有单次提醒显示）
        time_label = self.time_layout.itemAt(0).widget()
        time_label.setVisible(is_single)
        self.time_edit.setVisible(is_single)
        
        # 类型切换完成
    
    # 移除标题相关方法
    
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
            elif reminder_type == 'repeat':
                # 循环提醒：验证间隔
                interval = self.get_reminder_interval()
                if interval < 1:
                    QMessageBox.warning(self, '间隔错误', '提醒间隔不能小于1分钟！')
                    if hasattr(self, 'interval_spinbox') and self.interval_spinbox:
                        self.interval_spinbox.setFocus()
                    return
            else:
                # 相对时间提醒：验证延迟时间
                relative_seconds = self.get_relative_seconds()
                if relative_seconds < 1:
                    QMessageBox.warning(self, '时间错误', '延迟时间不能小于1秒！')
                    if hasattr(self, 'relative_spinbox') and self.relative_spinbox:
                        self.relative_spinbox.setFocus()
                    return
            
            # 验证通过，发送信号给主窗口
            if self.get_reminder_type() == 'relative':
                self.reminder_added.emit(
                    self.get_reminder_content(),
                    QTime.currentTime(),  # 相对时间提醒使用当前时间作为占位符
                    self.get_reminder_type(),
                    0,  # 相对时间提醒不需要间隔
                    self.get_relative_seconds()  # 添加相对秒数参数
                )
            else:
                self.reminder_added.emit(
                    self.get_reminder_content(),
                    self.get_reminder_time(),
                    self.get_reminder_type(),
                    self.get_reminder_interval(),
                    0  # 非相对时间提醒的相对秒数为0
                )
            
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
    
    def keyPressEvent(self, a0):
        """键盘事件处理"""
        try:
            # 按Enter键确认
            if a0.key() == Qt.Key_Return or a0.key() == Qt.Key_Enter:
                self.accept_reminder()
            # 按Escape键取消
            elif a0.key() == Qt.Key_Escape:
                self.safe_reject()
            else:
                super().keyPressEvent(a0)
        except Exception as e:
            print(f"keyPressEvent error: {e}")
    
    def closeEvent(self, a0):
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
            
            a0.accept()
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