# -*- coding: utf-8 -*-
"""
提醒列表对话框类
用于显示、编辑和管理多个提醒
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QTimeEdit, QLineEdit, QRadioButton, QSpinBox, QComboBox,
    QButtonGroup, QGroupBox, QFormLayout, QCheckBox, QWidget, QScrollArea, QSizePolicy
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
        
        # 初始化组件引用
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
        # 新增：时间与间隔的label/容器，便于整体隐藏
        self.time_label = None
        self.interval_label = None
        self.interval_container = None
        
        self.init_dialog()
        self.setup_ui()
        
        if self.is_edit_mode:
            self.load_reminder_data()
    
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
        
        self.setWindowFlags(
            Qt.Dialog |
            Qt.WindowTitleHint |
            Qt.WindowCloseButtonHint
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
        title_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(title_label)
        
        # 标题输入
        title_group = QGroupBox('提醒标题')
        title_layout = QFormLayout()
        title_layout.setSpacing(10)
        title_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)
        title_layout.setLabelAlignment(Qt.AlignRight)
        title_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText('请输入提醒标题...')
        self.title_edit.setMinimumHeight(30)
        self.title_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        title_layout.addRow('标题:', self.title_edit)
        title_group.setLayout(title_layout)
        content_layout.addWidget(title_group)
        
        # 内容输入
        content_group = QGroupBox('提醒内容')
        form_content_layout = QFormLayout()
        form_content_layout.setSpacing(10)
        form_content_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)
        form_content_layout.setLabelAlignment(Qt.AlignRight)
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
        
        self.reminder_type_group.addButton(self.single_radio, 0)
        self.reminder_type_group.addButton(self.repeat_radio, 1)
        
        self.single_radio.setChecked(True)
        self.single_radio.toggled.connect(self.on_reminder_type_changed)
        
        type_layout.addWidget(self.single_radio)
        type_layout.addWidget(self.repeat_radio)
        type_group.setLayout(type_layout)
        content_layout.addWidget(type_group)
        
        # 时间设置
        time_group = QGroupBox('时间设置')
        time_layout = QFormLayout()
        time_layout.setSpacing(10)
        time_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)
        time_layout.setLabelAlignment(Qt.AlignRight)
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
        is_repeat = self.repeat_radio.isChecked()
        
        # 切换控件可见性（连同标签一起隐藏）
        if self.time_label:
            self.time_label.setVisible(not is_repeat)
        if self.time_edit:
            self.time_edit.setVisible(not is_repeat)
        if self.interval_label:
            self.interval_label.setVisible(is_repeat)
        if self.interval_container:
            self.interval_container.setVisible(is_repeat)
        
        try:
            self.adjustSize()
        except:
            pass
    
    def load_reminder_data(self):
        """加载提醒数据到界面"""
        if not self.reminder:
            return
        
        self.title_edit.setText(self.reminder.title)
        self.content_edit.setText(self.reminder.content)
        self.active_checkbox.setChecked(self.reminder.is_active)
        
        if self.reminder.type == 'single':
            self.single_radio.setChecked(True)
            if self.reminder.target_time:
                time = QTime(self.reminder.target_time.hour, self.reminder.target_time.minute)
                self.time_edit.setTime(time)
        else:
            self.repeat_radio.setChecked(True)
            if self.reminder.interval_minutes:
                if self.reminder.interval_minutes >= 60 and self.reminder.interval_minutes % 60 == 0:
                    self.interval_spinbox.setValue(self.reminder.interval_minutes // 60)
                    self.interval_unit_combo.setCurrentText('小时')
                else:
                    self.interval_spinbox.setValue(self.reminder.interval_minutes)
                    self.interval_unit_combo.setCurrentText('分钟')
        
        self.on_reminder_type_changed()
    
    def accept_reminder(self):
        """确认按钮处理"""
        try:
            # 验证输入
            title = self.title_edit.text().strip()
            content = self.content_edit.text().strip()
            
            if not title:
                QMessageBox.warning(self, '输入错误', '请输入提醒标题！')
                self.title_edit.setFocus()
                return
            
            if not content:
                QMessageBox.warning(self, '输入错误', '请输入提醒内容！')
                self.content_edit.setFocus()
                return
            
            # 验证时间设置
            if self.single_radio.isChecked():
                # 单次提醒：验证时间
                time = self.time_edit.time()
                today = datetime.now().date()
                target_time = datetime.combine(today, time.toPyTime())
                
                # 如果时间已过，设置为明天
                if target_time <= datetime.now():
                    target_time += timedelta(days=1)
            else:
                # 循环提醒：验证间隔
                interval = self.interval_spinbox.value()
                if interval < 1:
                    QMessageBox.warning(self, '输入错误', '提醒间隔不能小于1！')
                    self.interval_spinbox.setFocus()
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
        title = self.title_edit.text().strip()
        content = self.content_edit.text().strip()
        is_active = self.active_checkbox.isChecked()
        
        if self.single_radio.isChecked():
            # 单次提醒
            time = self.time_edit.time()
            today = datetime.now().date()
            target_time = datetime.combine(today, time.toPyTime())
            
            # 如果时间已过，设置为明天
            if target_time <= datetime.now():
                target_time += timedelta(days=1)
            
            return {
                'title': title,
                'content': content,
                'reminder_type': 'single',
                'target_time': target_time,
                'interval_minutes': None,
                'is_active': is_active
            }
        else:
            # 循环提醒
            interval = self.interval_spinbox.value()
            unit = self.interval_unit_combo.currentText()
            
            if unit == '小时':
                interval_minutes = interval * 60
            else:
                interval_minutes = interval
            
            return {
                'title': title,
                'content': content,
                'reminder_type': 'repeat',
                'target_time': None,
                'interval_minutes': interval_minutes,
                'is_active': is_active
            }
    
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
        
        self.setWindowFlags(
            Qt.Dialog |
            Qt.WindowTitleHint |
            Qt.WindowCloseButtonHint
        )
        
        self.setModal(True)
    
    def setup_ui(self):
        """设置界面布局"""
        main_layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel('提醒列表')
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 提醒列表表格
        self.reminder_table = QTableWidget()
        self.reminder_table.setColumnCount(6)
        self.reminder_table.setHorizontalHeaderLabels(['标题', '内容', '类型', '状态', '创建时间', '操作'])
        
        # 设置列宽
        header = self.reminder_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        header.setSectionResizeMode(5, QHeaderView.Fixed)
        
        self.reminder_table.setColumnWidth(0, 120)
        self.reminder_table.setColumnWidth(2, 80)
        self.reminder_table.setColumnWidth(3, 100)
        self.reminder_table.setColumnWidth(4, 120)
        self.reminder_table.setColumnWidth(5, 120)
        
        # 设置表格属性
        self.reminder_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.reminder_table.setAlternatingRowColors(True)
        
        main_layout.addWidget(self.reminder_table)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.edit_button = QPushButton('编辑提醒')
        self.edit_button.clicked.connect(self.edit_reminder)
        
        self.delete_button = QPushButton('删除提醒')
        self.delete_button.clicked.connect(self.delete_reminder)
        
        self.cleanup_button = QPushButton('清理过期')
        self.cleanup_button.clicked.connect(self.cleanup_expired)
        
        self.close_button = QPushButton('关闭')
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
            # 标题
            title_item = QTableWidgetItem(reminder.title)
            title_item.setData(Qt.UserRole, reminder.id)
            self.reminder_table.setItem(row, 0, title_item)
            
            # 内容
            content_item = QTableWidgetItem(reminder.content)
            self.reminder_table.setItem(row, 1, content_item)
            
            # 类型
            type_text = '单次提醒' if reminder.type == 'single' else '循环提醒'
            type_item = QTableWidgetItem(type_text)
            self.reminder_table.setItem(row, 2, type_item)
            
            # 状态
            status_item = QTableWidgetItem(reminder.get_status_text())
            self.reminder_table.setItem(row, 3, status_item)
            
            # 创建时间
            created_time = reminder.created_time.strftime('%m-%d %H:%M')
            time_item = QTableWidgetItem(created_time)
            self.reminder_table.setItem(row, 4, time_item)
            
            # 操作按钮
            action_layout = QHBoxLayout()
            
            toggle_button = QPushButton('停用' if reminder.is_active else '启用')
            toggle_button.clicked.connect(lambda checked, r_id=reminder.id: self.toggle_reminder(r_id))
            
            action_layout.addWidget(toggle_button)
            action_layout.setContentsMargins(5, 2, 5, 2)
            
            action_widget = QWidget()
            action_widget.setLayout(action_layout)
            self.reminder_table.setCellWidget(row, 5, action_widget)
    

    
    def edit_reminder(self):
        """编辑提醒"""
        current_row = self.reminder_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, '选择错误', '请先选择要编辑的提醒！')
            return
        
        reminder_id = self.reminder_table.item(current_row, 0).data(Qt.UserRole)
        reminder = self.reminder_manager.get_reminder(reminder_id)
        
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
        
        reminder_id = self.reminder_table.item(current_row, 0).data(Qt.UserRole)
        reminder = self.reminder_manager.get_reminder(reminder_id)
        
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
            self.reminder_manager.remove_reminder(reminder_id)
            self.refresh_reminder_list()
            self.reminders_changed.emit()
    
    def toggle_reminder(self, reminder_id):
        """切换提醒状态"""
        reminder = self.reminder_manager.get_reminder(reminder_id)
        if reminder:
            self.reminder_manager.update_reminder(reminder_id, is_active=not reminder.is_active)
            self.refresh_reminder_list()
            self.reminders_changed.emit()
    
    def cleanup_expired(self):
        """清理过期提醒"""
        count = self.reminder_manager.cleanup_expired_reminders()
        if count > 0:
            QMessageBox.information(self, '清理完成', f'已清理 {count} 个过期提醒！')
            self.refresh_reminder_list()
            self.reminders_changed.emit()
        else:
            QMessageBox.information(self, '清理完成', '没有过期的提醒需要清理。')