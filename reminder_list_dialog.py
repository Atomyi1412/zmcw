# -*- coding: utf-8 -*-
"""
提醒列表对话框类
用于显示、编辑和管理多个提醒
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QTimeEdit, QLineEdit, QRadioButton, QSpinBox, QComboBox,
    QButtonGroup, QGroupBox, QFormLayout, QCheckBox, QWidget, QScrollArea, QSizePolicy,
    QApplication
)
from PyQt5.QtCore import Qt, QTime, pyqtSignal
from PyQt5.QtGui import QFont
from datetime import datetime, timedelta
from config import PetConfig
from reminder_manager import Reminder


class ReminderEditDialog(QDialog):
    """提醒编辑对话框"""
    
    def __init__(self, parent=None, reminder=None):
        super().__init__(parent)
        self.reminder = reminder
        self.is_edit_mode = reminder is not None
        
        # 初始化所有UI组件
        self.content_edit = None
        self.single_radio = None
        self.repeat_radio = None
        self.relative_radio = None
        self.reminder_type_group = None
        self.time_edit = None
        self.time_label = None
        self.interval_spinbox = None
        self.interval_unit_combo = None
        self.interval_label = None
        self.interval_container = None
        self.relative_label = None
        self.relative_spinbox = None
        self.relative_unit_combo = None
        self.relative_container = None
        self.active_checkbox = None
        self.cancel_button = None
        self.confirm_button = None
        
        try:
            self.init_dialog()
            self.setup_ui()
            if self.is_edit_mode:
                self.load_reminder_data()
        except Exception as e:
            print(f"ReminderEditDialog initialization error: {e}")
            import traceback
            traceback.print_exc()
    
    def __del__(self):
        """析构函数，确保资源被正确清理"""
        try:
            # 清理所有组件引用
            self.title_edit = None
            self.content_edit = None
            self.single_radio = None
            self.repeat_radio = None
            self.time_edit = None
            self.interval_spinbox = None
            self.interval_unit_combo = None
            self.active_checkbox = None
            self.confirm_button = None
            self.cancel_button = None
            self.reminder_type_group = None
        except:
            pass
    
    def init_dialog(self):
        """初始化对话框属性"""
        title = '编辑提醒' if self.is_edit_mode else '添加提醒'
        self.setWindowTitle(title)
        # 由固定尺寸改为最小尺寸+可调整
        self.setMinimumSize(560, 520)
        self.resize(600, 560)
        self.setSizeGripEnabled(True)
        
        from PyQt5.QtCore import Qt as QtCore
        self.setWindowFlags(
            QtCore.Dialog |
            QtCore.WindowTitleHint |
            QtCore.WindowCloseButtonHint |
            QtCore.WindowStaysOnTopHint
        )
        
        self.setModal(True)
    
    def setup_ui(self):
        """设置界面布局"""
        # 外层主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 使用滚动区域承载主体内容，避免小屏或高DPI下超框
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(15)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # 对话框标题
        title_label = QLabel('编辑提醒' if self.is_edit_mode else '添加提醒')
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        from PyQt5.QtCore import Qt as QtCore
        title_label.setAlignment(QtCore.AlignCenter)
        content_layout.addWidget(title_label)
        
        # 移除标题输入区域
        
        # 内容输入
        content_group = QGroupBox('提醒内容')
        form_content_layout = QFormLayout()
        form_content_layout.setSpacing(10)
        from PyQt5.QtCore import Qt as QtCore
        form_content_layout.setFormAlignment(QtCore.AlignLeft | QtCore.AlignTop)
        form_content_layout.setLabelAlignment(QtCore.AlignRight)
        form_content_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        
        self.content_edit = QLineEdit()
        self.content_edit.setPlaceholderText('请输入提醒内容...')
        self.content_edit.setMinimumHeight(30)
        self.content_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        form_content_layout.addRow('内容:', self.content_edit)
        content_group.setLayout(form_content_layout)
        content_layout.addWidget(content_group)
        
        # 提醒类型选择
        type_group = QGroupBox('提醒类型')
        type_layout = QVBoxLayout()
        type_layout.setSpacing(10)
        
        self.reminder_type_group = QButtonGroup()
        self.single_radio = QRadioButton('单次提醒')
        self.repeat_radio = QRadioButton('循环提醒')
        self.relative_radio = QRadioButton('延迟提醒')
        
        self.reminder_type_group.addButton(self.single_radio, 0)
        self.reminder_type_group.addButton(self.repeat_radio, 1)
        self.reminder_type_group.addButton(self.relative_radio, 2)
        
        self.single_radio.setChecked(True)
        self.single_radio.toggled.connect(self.on_reminder_type_changed)
        self.repeat_radio.toggled.connect(self.on_reminder_type_changed)
        self.relative_radio.toggled.connect(self.on_reminder_type_changed)
        
        type_layout.addWidget(self.single_radio)
        type_layout.addWidget(self.repeat_radio)
        type_layout.addWidget(self.relative_radio)
        type_group.setLayout(type_layout)
        content_layout.addWidget(type_group)
        
        # 时间设置
        time_group = QGroupBox('时间设置')
        time_layout = QFormLayout()
        time_layout.setSpacing(10)
        from PyQt5.QtCore import Qt as QtCore
        time_layout.setFormAlignment(QtCore.AlignLeft | QtCore.AlignTop)
        time_layout.setLabelAlignment(QtCore.AlignRight)
        time_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        
        # 单次提醒时间
        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat('HH:mm')
        self.time_edit.setTime(QTime.currentTime().addSecs(300))
        self.time_edit.setMinimumHeight(30)
        self.time_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.time_label = QLabel('提醒时间:')
        time_layout.addRow(self.time_label, self.time_edit)
        
        # 循环提醒间隔
        interval_hbox = QHBoxLayout()
        interval_hbox.setSpacing(10)
        self.interval_spinbox = QSpinBox()
        self.interval_spinbox.setMinimum(1)
        self.interval_spinbox.setMaximum(999)
        self.interval_spinbox.setValue(1)
        self.interval_spinbox.setMinimumHeight(30)
        self.interval_spinbox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        
        self.interval_unit_combo = QComboBox()
        self.interval_unit_combo.addItems(['分钟', '小时'])
        self.interval_unit_combo.setMinimumHeight(30)
        self.interval_unit_combo.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        
        interval_hbox.addWidget(self.interval_spinbox)
        interval_hbox.addWidget(self.interval_unit_combo)
        interval_hbox.addStretch()
        
        self.interval_container = QWidget()
        self.interval_container.setLayout(interval_hbox)
        self.interval_label = QLabel('提醒间隔:')
        time_layout.addRow(self.interval_label, self.interval_container)
        
        # 延迟提醒时间设置
        relative_hbox = QHBoxLayout()
        relative_hbox.setSpacing(10)
        self.relative_spinbox = QSpinBox()
        self.relative_spinbox.setMinimum(1)
        self.relative_spinbox.setMaximum(999)
        self.relative_spinbox.setValue(5)
        self.relative_spinbox.setMinimumHeight(30)
        self.relative_spinbox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        
        self.relative_unit_combo = QComboBox()
        self.relative_unit_combo.addItems(['秒', '分钟', '小时'])
        self.relative_unit_combo.setMinimumHeight(30)
        self.relative_unit_combo.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        
        relative_hbox.addWidget(self.relative_spinbox)
        relative_hbox.addWidget(self.relative_unit_combo)
        relative_hbox.addStretch()
        
        self.relative_container = QWidget()
        self.relative_container.setLayout(relative_hbox)
        self.relative_label = QLabel('延迟时间:')
        time_layout.addRow(self.relative_label, self.relative_container)
        
        time_group.setLayout(time_layout)
        content_layout.addWidget(time_group)
        
        # 状态设置
        status_group = QGroupBox('状态设置')
        status_layout = QHBoxLayout()
        status_layout.setSpacing(10)
        
        self.active_checkbox = QCheckBox('启用提醒')
        self.active_checkbox.setChecked(True)
        
        status_layout.addWidget(self.active_checkbox)
        status_layout.addStretch()
        status_group.setLayout(status_layout)
        content_layout.addWidget(status_group)
        
        # 滚动区域装载内容
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)
        
        # 按钮区域（固定在底部，不随滚动）
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        button_layout.setContentsMargins(0, 10, 0, 0)
        
        button_layout.addStretch()
        
        self.cancel_button = QPushButton('取消')
        self.cancel_button.setMinimumSize(80, 35)
        self.cancel_button.clicked.connect(self.safe_reject)
        
        self.confirm_button = QPushButton('确认')
        self.confirm_button.setMinimumSize(80, 35)
        self.confirm_button.clicked.connect(self.accept_reminder)
        self.confirm_button.setDefault(True)
        
        # 设置按钮样式
        self.confirm_button.setStyleSheet("""
            QPushButton {
                background-color: #007ACC;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005A9E;
            }
            QPushButton:pressed {
                background-color: #004578;
            }
        """)
        
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #F0F0F0;
                color: #333333;
                border: 1px solid #CCCCCC;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #E0E0E0;
            }
            QPushButton:pressed {
                background-color: #D0D0D0;
            }
        """)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.confirm_button)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)
        
        # 初始状态设置
        self.on_reminder_type_changed()
    
    def on_reminder_type_changed(self):
        """提醒类型改变事件处理"""
        if not all([self.single_radio, self.repeat_radio, self.relative_radio]):
            return
            
        is_single = self.single_radio.isChecked()
        is_repeat = self.repeat_radio.isChecked()
        is_relative = self.relative_radio.isChecked()
        
        # 切换控件可见性（连同标签一起隐藏）
        if self.time_label:
            self.time_label.setVisible(is_single)
        if self.time_edit:
            self.time_edit.setVisible(is_single)
        if self.interval_label:
            self.interval_label.setVisible(is_repeat)
        if self.interval_container:
            self.interval_container.setVisible(is_repeat)
        if self.relative_label:
            self.relative_label.setVisible(is_relative)
        if self.relative_container:
            self.relative_container.setVisible(is_relative)
        
        try:
            self.adjustSize()
        except:
            pass
    
    def load_reminder_data(self):
        """加载提醒数据到界面"""
        if not self.reminder or not self.content_edit:
            return
        
        # 移除标题加载
        self.content_edit.setText(self.reminder.content)
        if self.active_checkbox:
            self.active_checkbox.setChecked(self.reminder.is_active)
        
        if self.reminder.type == 'single' and self.single_radio:
            self.single_radio.setChecked(True)
            if self.reminder.target_time and self.time_edit:
                time = QTime(self.reminder.target_time.hour, self.reminder.target_time.minute)
                self.time_edit.setTime(time)
        elif self.reminder.type == 'repeat' and self.repeat_radio:
            self.repeat_radio.setChecked(True)
            if self.reminder.interval_minutes and self.interval_spinbox and self.interval_unit_combo:
                if self.reminder.interval_minutes >= 60 and self.reminder.interval_minutes % 60 == 0:
                    self.interval_spinbox.setValue(self.reminder.interval_minutes // 60)
                    self.interval_unit_combo.setCurrentText('小时')
                else:
                    self.interval_spinbox.setValue(self.reminder.interval_minutes)
                    self.interval_unit_combo.setCurrentText('分钟')
        elif self.reminder.type == 'relative' and self.relative_radio:
            self.relative_radio.setChecked(True)
            if hasattr(self.reminder, 'relative_seconds') and self.reminder.relative_seconds and self.relative_spinbox and self.relative_unit_combo:
                seconds = self.reminder.relative_seconds
                if seconds >= 3600 and seconds % 3600 == 0:
                    self.relative_spinbox.setValue(seconds // 3600)
                    self.relative_unit_combo.setCurrentText('小时')
                elif seconds >= 60 and seconds % 60 == 0:
                    self.relative_spinbox.setValue(seconds // 60)
                    self.relative_unit_combo.setCurrentText('分钟')
                else:
                    self.relative_spinbox.setValue(seconds)
                    self.relative_unit_combo.setCurrentText('秒')
        
        self.on_reminder_type_changed()
    
    def accept_reminder(self):
        """确认按钮处理"""
        try:
            # 验证输入
            if not self.content_edit:
                return
                
            content = self.content_edit.text().strip()
            
            if not content:
                QMessageBox.warning(self, '输入错误', '请输入提醒内容！')
                self.content_edit.setFocus()
                return
            
            # 验证时间设置
            if self.single_radio and self.single_radio.isChecked():
                # 单次提醒：验证时间
                if self.time_edit:
                    time = self.time_edit.time()
                    today = datetime.now().date()
                    target_time = datetime.combine(today, time.toPyTime())
                    
                    # 如果时间已过，设置为明天
                    if target_time <= datetime.now():
                        target_time += timedelta(days=1)
            elif self.repeat_radio and self.repeat_radio.isChecked():
                # 循环提醒：验证间隔
                if self.interval_spinbox:
                    interval = self.interval_spinbox.value()
                    if interval < 1:
                        QMessageBox.warning(self, '输入错误', '提醒间隔不能小于1！')
                        self.interval_spinbox.setFocus()
                        return
            elif self.relative_radio and self.relative_radio.isChecked():
                # 延迟提醒：验证延迟时间
                if self.relative_spinbox:
                    relative_value = self.relative_spinbox.value()
                    if relative_value < 1:
                        QMessageBox.warning(self, '输入错误', '延迟时间不能小于1！')
                        self.relative_spinbox.setFocus()
                        return
            
            # 安全地接受对话框
            try:
                self.accept()
            except Exception as accept_error:
                print(f"Dialog accept error: {accept_error}")
                # 如果accept失败，尝试直接关闭
                self.close()
                
        except Exception as e:
            try:
                QMessageBox.critical(self, '错误', f'处理提醒数据时发生错误：{str(e)}')
            except:
                print(f"Failed to show error message: {e}")
            print(f"accept_reminder error: {e}")
            # 发生错误时安全关闭
            try:
                self.close()
            except:
                pass
    
    def safe_reject(self):
        """安全的取消操作"""
        try:
            self.reject()
        except Exception as e:
            print(f"safe_reject error: {e}")
            # 强制关闭对话框
            self.close()
    
    def get_reminder_data(self):
        """获取提醒数据"""
        if not self.content_edit:
            return None
            
        content = self.content_edit.text().strip()
        is_active = self.active_checkbox.isChecked() if self.active_checkbox else True
        
        if self.single_radio and self.single_radio.isChecked():
            # 单次提醒
            if self.time_edit:
                time = self.time_edit.time()
                today = datetime.now().date()
                target_time = datetime.combine(today, time.toPyTime())
                
                # 如果时间已过，设置为明天
                if target_time <= datetime.now():
                    target_time += timedelta(days=1)
                
                return {
                    'title': '',
                    'content': content,
                    'reminder_type': 'single',
                    'target_time': target_time,
                    'interval_minutes': None,
                    'is_active': is_active
                }
        elif self.repeat_radio and self.repeat_radio.isChecked():
            # 循环提醒
            if self.interval_spinbox and self.interval_unit_combo:
                interval = self.interval_spinbox.value()
                unit = self.interval_unit_combo.currentText()
                
                if unit == '小时':
                    interval_minutes = interval * 60
                else:
                    interval_minutes = interval
                
                return {
                    'title': '',
                    'content': content,
                    'reminder_type': 'repeat',
                    'target_time': None,
                    'interval_minutes': interval_minutes,
                    'is_active': is_active
                }
        elif self.relative_radio and self.relative_radio.isChecked():
            # 延迟提醒
            if self.relative_spinbox and self.relative_unit_combo:
                relative_value = self.relative_spinbox.value()
                unit = self.relative_unit_combo.currentText()
                
                # 转换为秒
                if unit == '小时':
                    relative_seconds = relative_value * 3600
                elif unit == '分钟':
                    relative_seconds = relative_value * 60
                else:
                    relative_seconds = relative_value
                
                return {
                    'title': '',
                    'content': content,
                    'reminder_type': 'relative',
                    'relative_seconds': relative_seconds,
                    'is_active': is_active
                }
        
        return None
    
    def keyPressEvent(self, event):
        """键盘事件处理"""
        try:
            from PyQt5.QtCore import Qt as QtCore
            # 按Enter键确认
            if event.key() == QtCore.Key_Return or event.key() == QtCore.Key_Enter:
                self.accept_reminder()
            # 按Escape键取消
            elif event.key() == QtCore.Key_Escape:
                self.safe_reject()
            else:
                super().keyPressEvent(event)
        except Exception as e:
            print(f"keyPressEvent error: {e}")
    
    def closeEvent(self, event):
        """窗口关闭事件处理"""
        try:
            # 清理资源
            if hasattr(self, 'reminder_type_group') and self.reminder_type_group:
                try:
                    self.reminder_type_group.deleteLater()
                except:
                    pass
            
            # 安全地断开信号连接
            try:
                if hasattr(self, 'single_radio') and self.single_radio:
                    self.single_radio.toggled.disconnect()
            except:
                pass
            
            try:
                if hasattr(self, 'repeat_radio') and self.repeat_radio:
                    self.repeat_radio.toggled.disconnect()
            except:
                pass
            
            try:
                if hasattr(self, 'confirm_button') and self.confirm_button:
                    self.confirm_button.clicked.disconnect()
            except:
                pass
            
            try:
                if hasattr(self, 'cancel_button') and self.cancel_button:
                    self.cancel_button.clicked.disconnect()
            except:
                pass
            
            event.accept()
        except Exception as e:
            print(f"closeEvent error: {e}")
            event.accept()


class ReminderListDialog(QDialog):
    """提醒列表对话框"""
    
    # 信号定义
    reminders_changed = pyqtSignal()
    
    def __init__(self, parent=None, reminder_manager=None):
        super().__init__(parent)
        self.reminder_manager = reminder_manager
        
        self.init_dialog()
        self.setup_ui()
        self.refresh_reminder_list()
    
    def init_dialog(self):
        """初始化对话框属性"""
        self.setWindowTitle('提醒管理')
        self.setFixedSize(700, 500)
        
        from PyQt5.QtCore import Qt as QtCore
        self.setWindowFlags(
            QtCore.Dialog |
            QtCore.WindowTitleHint |
            QtCore.WindowCloseButtonHint |
            QtCore.WindowStaysOnTopHint
        )
        
        self.setModal(True)
    
    def setup_ui(self):
        """设置界面布局"""
        # 设置全局样式
        self.setStyleSheet("""
            QDialog {
                background-color: #F8F9FA;
            }
            QLabel {
                font-family: "Microsoft YaHei";
                color: #333333;
                font-size: 14px;
            }
            QTableWidget {
                font-family: "Microsoft YaHei";
                font-size: 13px;
                border: 1px solid #DDDDDD;
                background-color: white;
                selection-background-color: #E3F2FD;
                selection-color: #333333;
                gridline-color: #EEEEEE;
            }
            QHeaderView::section {
                background-color: #F1F1F1;
                padding: 6px;
                border: none;
                border-bottom: 1px solid #DDDDDD;
                font-family: "Microsoft YaHei";
                font-size: 13px;
                font-weight: bold;
                color: #555555;
            }
            QPushButton {
                font-family: "Microsoft YaHei";
                font-size: 13px;
                border-radius: 4px;
                padding: 5px 12px;
                min-height: 24px;
            }
        """)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title_label = QLabel('提醒列表')
        title_font = QFont("Microsoft YaHei", 18, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #333333; margin-bottom: 10px;")
        main_layout.addWidget(title_label)
        
        # 提醒列表表格
        self.reminder_table = QTableWidget()
        self.reminder_table.setColumnCount(5)
        self.reminder_table.setHorizontalHeaderLabels(['内容', '类型', '状态', '创建时间', '操作'])
        
        # 设置列宽
        header = self.reminder_table.horizontalHeader()
        if header:
            header.setSectionResizeMode(0, QHeaderView.Stretch)
            header.setSectionResizeMode(1, QHeaderView.Fixed)
            header.setSectionResizeMode(2, QHeaderView.Fixed)
            header.setSectionResizeMode(3, QHeaderView.Fixed)
            header.setSectionResizeMode(4, QHeaderView.Fixed)
        
        self.reminder_table.setColumnWidth(1, 90)
        self.reminder_table.setColumnWidth(2, 80)
        self.reminder_table.setColumnWidth(3, 110)
        self.reminder_table.setColumnWidth(4, 80)
        
        # 设置表格属性
        self.reminder_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.reminder_table.setAlternatingRowColors(True)
        self.reminder_table.verticalHeader().setVisible(False)  # 隐藏行号
        self.reminder_table.setShowGrid(False)  # 隐藏网格线（使用交替行颜色）
        self.reminder_table.setFrameShape(QTableWidget.NoFrame)  # 无边框
        
        # 连接双击事件和项目改变事件
        self.reminder_table.cellDoubleClicked.connect(self.on_cell_double_clicked)
        self.reminder_table.itemChanged.connect(self.on_item_changed)
        
        # 设置状态和创建时间列不可编辑
        from PyQt5.QtWidgets import QAbstractItemView
        self.reminder_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        main_layout.addWidget(self.reminder_table)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        # 定义按钮样式
        primary_btn_style = """
            QPushButton {
                background-color: #5B9BD5;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #4A8AC4;
            }
            QPushButton:pressed {
                background-color: #376FC7;
            }
        """
        
        danger_btn_style = """
            QPushButton {
                background-color: #FF6B6B;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #FF5252;
            }
            QPushButton:pressed {
                background-color: #FF3838;
            }
        """
        
        default_btn_style = """
            QPushButton {
                background-color: #E0E0E0;
                color: #333333;
                border: none;
            }
            QPushButton:hover {
                background-color: #D0D0D0;
            }
            QPushButton:pressed {
                background-color: #C0C0C0;
            }
        """
        
        self.edit_button = QPushButton('编辑提醒')
        self.edit_button.setCursor(Qt.PointingHandCursor)
        self.edit_button.setStyleSheet(primary_btn_style)
        self.edit_button.clicked.connect(self.edit_reminder)
        
        self.delete_button = QPushButton('删除提醒')
        self.delete_button.setCursor(Qt.PointingHandCursor)
        self.delete_button.setStyleSheet(danger_btn_style)
        self.delete_button.clicked.connect(self.delete_reminder)
        
        self.cleanup_button = QPushButton('清理过期')
        self.cleanup_button.setCursor(Qt.PointingHandCursor)
        self.cleanup_button.setStyleSheet(default_btn_style)
        self.cleanup_button.clicked.connect(self.cleanup_expired)
        
        self.close_button = QPushButton('关闭')
        self.close_button.setCursor(Qt.PointingHandCursor)
        self.close_button.setStyleSheet(default_btn_style)
        self.close_button.clicked.connect(self.accept)
        
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.cleanup_button)
        button_layout.addStretch()
        button_layout.addWidget(self.close_button)
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
    
    def refresh_reminder_list(self):
        """刷新提醒列表"""
        if not self.reminder_manager:
            return
        
        reminders = self.reminder_manager.get_all_reminders()
        self.reminder_table.setRowCount(len(reminders))
        
        for row, reminder in enumerate(reminders):
            # 内容
            from PyQt5.QtCore import Qt as QtCore
            content_item = QTableWidgetItem(reminder.content)
            content_item.setData(QtCore.UserRole, reminder.id)
            self.reminder_table.setItem(row, 0, content_item)
            
            # 类型
            if reminder.type == 'single':
                type_text = '单次提醒'
            elif reminder.type == 'repeat':
                type_text = '循环提醒'
            elif reminder.type == 'relative':
                type_text = '延迟提醒'
            else:
                type_text = '未知类型'
            type_item = QTableWidgetItem(type_text)
            self.reminder_table.setItem(row, 1, type_item)
            
            # 状态
            status_item = QTableWidgetItem(reminder.get_status_text())
            self.reminder_table.setItem(row, 2, status_item)
            
            # 创建时间
            created_time = reminder.created_time.strftime('%m-%d %H:%M')
            time_item = QTableWidgetItem(created_time)
            self.reminder_table.setItem(row, 3, time_item)
            
            # 操作按钮
            action_layout = QHBoxLayout()
            
            toggle_button = QPushButton('停用' if reminder.is_active else '启用')
            toggle_button.clicked.connect(lambda checked, r_id=reminder.id: self.toggle_reminder(r_id))
            
            action_layout.addWidget(toggle_button)
            action_layout.setContentsMargins(5, 2, 5, 2)
            
            action_widget = QWidget()
            action_widget.setLayout(action_layout)
            self.reminder_table.setCellWidget(row, 4, action_widget)
    
    def on_cell_double_clicked(self, row, column):
        """处理表格单元格双击事件"""
        # 只允许编辑内容(列0)，禁止编辑类型(列1)、状态(列2)和创建时间(列3)
        if column != 0:
            return
        
        # 获取当前项
        item = self.reminder_table.item(row, column)
        if not item:
            return
        
        # 获取提醒ID
        from PyQt5.QtCore import Qt as QtCore
        reminder_id = self.reminder_table.item(row, 0).data(QtCore.UserRole)
        reminder = self.reminder_manager.get_reminder(reminder_id) if self.reminder_manager else None
        if not reminder:
            return
        
        # 设置项为可编辑
        original_flags = item.flags()
        item.setFlags(original_flags | QtCore.ItemIsEditable)
        
        # 内容列直接编辑
        self.reminder_table.editItem(item)
    
    def on_item_changed(self, item):
        """处理项目内容改变事件"""
        row = item.row()
        column = item.column()
        
        # 只处理内容列的改变
        if column == 0:
            from PyQt5.QtCore import Qt as QtCore
            reminder_id = self.reminder_table.item(row, 0).data(QtCore.UserRole)
            new_content = item.text()
            
            # 更新提醒内容
            if self.reminder_manager:
                self.reminder_manager.update_reminder(reminder_id, content=new_content)
                self.reminders_changed.emit()
    
    def edit_reminder(self):
        """编辑提醒"""
        current_row = self.reminder_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, '选择错误', '请先选择要编辑的提醒！')
            return
        
        from PyQt5.QtCore import Qt as QtCore
        reminder_id = self.reminder_table.item(current_row, 0).data(QtCore.UserRole)
        reminder = self.reminder_manager.get_reminder(reminder_id) if self.reminder_manager else None
        
        if not reminder:
            QMessageBox.warning(self, '错误', '提醒不存在！')
            return
        
        dialog = None
        try:
            dialog = ReminderEditDialog(self, reminder)
            result = dialog.exec_()
            if result == QDialog.Accepted:
                data = dialog.get_reminder_data()
                self.reminder_manager.update_reminder(reminder_id, **data)
                self.refresh_reminder_list()
                self.reminders_changed.emit()
        except Exception as e:
            print(f"edit_reminder error: {e}")
        finally:
            # 安全地销毁对话框
            if dialog:
                try:
                    dialog.deleteLater()
                except:
                    pass
    
    def delete_reminder(self):
        """删除提醒"""
        current_row = self.reminder_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, '选择错误', '请先选择要删除的提醒！')
            return
        
        from PyQt5.QtCore import Qt as QtCore
        reminder_id = self.reminder_table.item(current_row, 0).data(QtCore.UserRole)
        reminder = self.reminder_manager.get_reminder(reminder_id) if self.reminder_manager else None
        
        if not reminder:
            QMessageBox.warning(self, '错误', '提醒不存在！')
            return
        
        reply = QMessageBox.question(
            self, '确认删除', 
            f'确定要删除提醒 "{reminder.title}" 吗？',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.reminder_manager:
                self.reminder_manager.remove_reminder(reminder_id)
                self.refresh_reminder_list()
                self.reminders_changed.emit()
    
    def toggle_reminder(self, reminder_id):
        """切换提醒状态"""
        reminder = self.reminder_manager.get_reminder(reminder_id) if self.reminder_manager else None
        if reminder and self.reminder_manager:
            self.reminder_manager.update_reminder(reminder_id, is_active=not reminder.is_active)
            self.refresh_reminder_list()
            self.reminders_changed.emit()
    
    def cleanup_expired(self):
        """清理过期提醒"""
        if self.reminder_manager:
            count = self.reminder_manager.cleanup_expired_reminders()
            if count > 0:
                QMessageBox.information(self, '清理完成', f'已清理 {count} 个过期提醒！')
                self.refresh_reminder_list()
                self.reminders_changed.emit()
            else:
                QMessageBox.information(self, '清理完成', '没有过期的提醒需要清理。')