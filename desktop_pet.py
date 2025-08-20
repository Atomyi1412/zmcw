# -*- coding: utf-8 -*-
"""
桌面宠物主窗口类
实现宠物的显示、拖拽、动画等核心功能
"""

import sys
import os
import math
from PyQt5.QtWidgets import (
    QWidget, QLabel, QApplication, QMenu, QAction, QMessageBox, QDialog
)
from PyQt5.QtCore import Qt, QPoint, QPropertyAnimation, QEasingCurve, pyqtSignal, QTimer, QTime, QStandardPaths
from PyQt5.QtGui import QPixmap, QPainter, QColor

from pet_state import PetState
from config import PetConfig
from reminder_dialog import ReminderDialog
from reminder_list_dialog import ReminderListDialog
from reminder_manager import ReminderManager
from settings_dialog import SettingsDialog

# PyInstaller资源路径辅助函数
def resource_path(relative_path: str) -> str:
    try:
        base_path = getattr(sys, '_MEIPASS')  # PyInstaller临时目录
    except Exception:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, relative_path)

class DesktopPet(QWidget):
    """桌面宠物主窗口类"""
    
    def __init__(self):
        super().__init__()
        
        # 初始化属性
        self.current_state = PetState.NORMAL
        self.is_dragging = False
        self.drag_start_position = QPoint()
        self.images = {}
        self.pet_label = None
        self.fall_animation = None
        # 叶子下落动画相关
        self.leaf_fall_timer = None
        self.leaf_fall_start_time = None
        self.leaf_fall_start_pos = None
        self.leaf_base_x = 0
        
        # 提醒功能相关属性（使用新的ReminderManager）
        self.reminder_manager = None
        self.original_position = QPoint()
        self.current_settings = {}  # 当前设置
        
        # 初始化窗口
        self.init_window()
        
        # 初始化提醒管理器
        self.init_reminder_manager()
        
        # 加载设置
        self.load_settings()
        
        # 应用置顶设置
        always_on_top = self.current_settings.get('always_on_top', PetConfig.ALWAYS_ON_TOP)
        if always_on_top:
            self.toggle_always_on_top(True)
        
        # 加载图像
        self.load_images()
        
        # 设置初始位置
        self.set_initial_position()
        
        # 显示宠物
        self.change_pet_state(PetState.NORMAL)
    
    def init_window(self):
        """初始化窗口属性"""
        # 设置窗口大小
        self.setFixedSize(PetConfig.WINDOW_WIDTH, PetConfig.WINDOW_HEIGHT)
        
        # 设置窗口标题
        self.setWindowTitle('桌面宠物')
        
        # 设置窗口标志：无边框、置顶（移除Qt.Tool以修复macOS置顶问题）
        self.setWindowFlags(
            Qt.FramelessWindowHint |  # 无边框
            Qt.WindowStaysOnTopHint |  # 置顶
            Qt.WindowDoesNotAcceptFocus  # 不接受焦点，避免干扰其他程序
        )
        
        # 设置透明背景
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 创建宠物标签
        self.pet_label = QLabel(self)
        self.pet_label.setAlignment(Qt.AlignCenter)
        self.pet_label.setGeometry(0, 0, PetConfig.WINDOW_WIDTH, PetConfig.WINDOW_HEIGHT)
        
        # 设置标签透明背景，避免显示白色背景
        self.pet_label.setStyleSheet("background: transparent;")
    
    def init_reminder_manager(self):
        """初始化提醒管理器"""
        self.reminder_manager = ReminderManager(self)
        # 连接提醒触发信号
        self.reminder_manager.reminder_triggered.connect(self.on_reminder_triggered)
    
    def load_images(self):
        """加载宠物图像"""
        for state, image_path in PetConfig.IMAGE_PATHS.items():
            resolved_path = resource_path(image_path)
            if os.path.exists(resolved_path):
                # 加载图像并确保透明度保持
                pixmap = QPixmap(resolved_path)
                if not pixmap.isNull():
                    # 确保图像具有alpha通道
                    if not pixmap.hasAlphaChannel():
                        # 如果没有alpha通道，创建一个新的带alpha通道的pixmap
                        new_pixmap = QPixmap(pixmap.size())
                        new_pixmap.fill(QColor(0, 0, 0, 0))  # 透明背景
                        painter = QPainter(new_pixmap)
                        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
                        painter.drawPixmap(0, 0, pixmap)
                        painter.end()
                        pixmap = new_pixmap
                    
                    # 缩放图像保持比例和透明度
                    scaled_pixmap = pixmap.scaled(
                        PetConfig.WINDOW_WIDTH - 10,
                        PetConfig.WINDOW_HEIGHT - 10,
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                    self.images[state] = scaled_pixmap
                else:
                    print(f"警告：无法加载图像 {image_path}")
                    self.images[state] = self.create_placeholder_image()
            else:
                print(f"警告：图像文件不存在 {image_path}，使用占位图像")
                self.images[state] = self.create_placeholder_image()
    
    def create_placeholder_image(self):
        """创建占位图像"""
        pixmap = QPixmap(80, 80)
        pixmap.fill(QColor(0, 0, 0, 0))  # 完全透明的背景
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
        painter.setBrush(QColor(100, 150, 255, 200))  # 半透明蓝色
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(10, 10, 60, 60)
        painter.end()
        
        return pixmap
    
    def set_initial_position(self):
        """设置初始位置在屏幕右下角"""
        screen = QApplication.desktop().screenGeometry()
        x = screen.width() - PetConfig.WINDOW_WIDTH - PetConfig.INITIAL_X_OFFSET
        y = screen.height() - PetConfig.WINDOW_HEIGHT - PetConfig.INITIAL_Y_OFFSET
        self.move(x, y)
    
    def change_pet_state(self, new_state):
        """切换宠物状态"""
        self.current_state = new_state
        state_key = new_state.value
        
        if state_key in self.images:
            # 彻底清除QLabel的内容和背景
            self.pet_label.clear()
            self.pet_label.setAutoFillBackground(False)
            self.pet_label.setScaledContents(False)
            
            # 强制处理事件循环，确保清除操作完成
            QApplication.processEvents()
            
            # 设置新的图像
            self.pet_label.setPixmap(self.images[state_key])
            
            # 多重强制刷新机制
            self.pet_label.repaint()  # 强制重绘
            self.pet_label.update()   # 更新显示
            self.repaint()            # 强制重绘整个窗口
            self.update()             # 更新整个窗口
            
            # 再次处理事件循环，确保显示更新完成
            QApplication.processEvents()
        else:
            print(f"警告：状态 {state_key} 对应的图像不存在")
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            # 若正在执行下落动画，立即停止
            if hasattr(self, 'leaf_fall_timer') and self.leaf_fall_timer and self.leaf_fall_timer.isActive():
                self.leaf_fall_timer.stop()
                self.leaf_fall_timer = None
                self.change_pet_state(PetState.NORMAL)
            self.is_dragging = True
            self.drag_start_position = event.globalPos() - self.frameGeometry().topLeft()
            self.change_pet_state(PetState.DRAGGING)
            event.accept()
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if event.buttons() == Qt.LeftButton and self.is_dragging:
            # 计算新位置
            new_position = event.globalPos() - self.drag_start_position
            
            # 确保窗口不会移出屏幕
            screen = QApplication.desktop().screenGeometry()
            new_position.setX(max(0, min(new_position.x(), screen.width() - self.width())))
            new_position.setY(max(0, min(new_position.y(), screen.height() - self.height())))
            
            self.move(new_position)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.LeftButton and self.is_dragging:
            self.is_dragging = False
            
            # 检查是否在屏幕上半部分
            screen = QApplication.desktop().screenGeometry()
            current_y = self.y()
            screen_middle = screen.height() * PetConfig.SCREEN_TOP_THRESHOLD
            
            if current_y < screen_middle:
                # 在上半部分，触发下落动画
                self.start_fall_animation()
            else:
                # 在下半部分，直接回到正常状态
                self.change_pet_state(PetState.NORMAL)
            
            event.accept()
    
    def contextMenuEvent(self, event):
        """右键菜单事件"""
        # 创建右键菜单
        context_menu = QMenu(self)
        
        # 添加设置提醒选项
        reminder_action = QAction('添加提醒', self)
        reminder_action.triggered.connect(self.show_reminder_dialog)
        context_menu.addAction(reminder_action)
        
        # 添加查看提醒列表选项
        list_action = QAction('查看提醒', self)
        list_action.triggered.connect(self.show_reminder_list)
        context_menu.addAction(list_action)
        
        # 如果有活动的提醒，添加停止所有提醒选项
        if self.reminder_manager and self.reminder_manager.has_active_reminders():
            stop_all_action = QAction('停止所有提醒', self)
            stop_all_action.triggered.connect(self.stop_all_reminders_with_message)
            context_menu.addAction(stop_all_action)
            
            # 添加提醒状态显示
            status_text = self.reminder_manager.get_status_summary()
            status_action = QAction(status_text, self)
            status_action.setEnabled(False)  # 只显示，不可点击
            context_menu.addSeparator()
            context_menu.addAction(status_action)
        
        context_menu.addSeparator()
        
        # 添加设置选项
        settings_action = QAction('设置', self)
        settings_action.triggered.connect(self.show_settings_dialog)
        context_menu.addAction(settings_action)
        
        # 添加退出选项
        exit_action = QAction('退出', self)
        exit_action.triggered.connect(self.close)
        context_menu.addAction(exit_action)
        
        # 显示菜单
        context_menu.exec_(event.globalPos())
    
    def show_settings_dialog(self):
        """显示设置对话框"""
        dialog = SettingsDialog(self, self.current_settings)
        
        # 设置对话框位置（在宠物附近）
        pet_pos = self.pos()
        dialog_x = pet_pos.x() + self.width() + 10
        dialog_y = pet_pos.y()
        
        # 确保对话框不会超出屏幕
        screen = QApplication.desktop().screenGeometry()
        if dialog_x + dialog.width() > screen.width():
            dialog_x = pet_pos.x() - dialog.width() - 10
        if dialog_y + dialog.height() > screen.height():
            dialog_y = screen.height() - dialog.height() - 50
        
        dialog.move(dialog_x, dialog_y)
        
        # 连接设置改变信号
        dialog.settings_changed.connect(self.apply_settings)
        
        # 显示对话框
        dialog.exec_()
    
    def apply_settings(self, new_settings):
        """应用新设置"""
        self.current_settings.update(new_settings)
        
        # 应用置顶设置
        if 'always_on_top' in new_settings:
            self.toggle_always_on_top(new_settings['always_on_top'])
        
        # 保存设置到文件
        self.save_settings()
    
    def toggle_always_on_top(self, always_on_top):
        """切换窗口置顶状态"""
        # 保存当前位置
        current_pos = self.pos()
        
        # 设置基础窗口标志
        base_flags = Qt.FramelessWindowHint | Qt.WindowDoesNotAcceptFocus
        
        if always_on_top:
            # 添加置顶标志
            new_flags = base_flags | Qt.WindowStaysOnTopHint
        else:
            # 不添加置顶标志
            new_flags = base_flags
        
        # 应用新的窗口标志
        self.setWindowFlags(new_flags)
        
        # 重新显示窗口（setWindowFlags会隐藏窗口）
        self.show()
        
        # 恢复位置
        self.move(current_pos)
        
        # 更新当前设置
        self.current_settings['always_on_top'] = always_on_top
    
    def save_settings(self):
        """保存设置到文件"""
        import json
        import os
        
        # 使用用户数据目录，适配打包后的不可写目录问题
        base_dir = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
        if not base_dir:
            base_dir = os.path.expanduser('~/.desktop_pet')
        os.makedirs(base_dir, exist_ok=True)
        settings_file = os.path.join(base_dir, 'settings.json')
        try:
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存设置失败: {e}")
    
    def load_settings(self):
        """从文件加载设置"""
        import json
        import os
        
        # 使用用户数据目录
        base_dir = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
        if not base_dir:
            base_dir = os.path.expanduser('~/.desktop_pet')
        os.makedirs(base_dir, exist_ok=True)
        settings_file = os.path.join(base_dir, 'settings.json')
        try:
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    self.current_settings = json.load(f)
            else:
                # 使用默认设置
                self.current_settings = {
                    'always_on_top': PetConfig.ALWAYS_ON_TOP
                }
        except Exception as e:
            print(f"加载设置失败: {e}")
            # 使用默认设置
            self.current_settings = {
                'always_on_top': PetConfig.ALWAYS_ON_TOP
            }
    
    def show_reminder_dialog(self):
        """显示提醒设置对话框"""
        dialog = None
        try:
            dialog = ReminderDialog(self)
            
            # 设置对话框位置（在宠物附近）
            pet_pos = self.pos()
            dialog_x = pet_pos.x() + self.width() + 10
            dialog_y = pet_pos.y()
            
            # 确保对话框不会超出屏幕
            screen = QApplication.desktop().screenGeometry()
            if dialog_x + dialog.width() > screen.width():
                dialog_x = pet_pos.x() - dialog.width() - 10
            if dialog_y + dialog.height() > screen.height():
                dialog_y = screen.height() - dialog.height() - 50
            
            dialog.move(dialog_x, dialog_y)
            
            # 显示对话框并处理结果
            result = dialog.exec_()
            if result == QDialog.Accepted:
                reminder_type = dialog.get_reminder_type()
                reminder_content = dialog.get_reminder_content()
                
                if reminder_type == 'single':
                    reminder_time = dialog.get_reminder_time()
                    self.add_single_reminder(reminder_time, reminder_content)
                else:
                    reminder_interval = dialog.get_reminder_interval()
                    self.add_repeat_reminder(reminder_interval, reminder_content)
        except Exception as e:
            print(f"show_reminder_dialog error: {e}") 
        finally:
            # 安全地销毁对话框
            if dialog:
                try:
                    dialog.deleteLater()
                except:
                    pass
    
    def show_reminder_list(self):
        """显示提醒列表对话框"""
        if not self.reminder_manager:
            return
        
        dialog = None
        try:
            dialog = ReminderListDialog(self, self.reminder_manager)
            
            # 设置对话框位置（在宠物附近）
            pet_pos = self.pos()
            dialog_x = pet_pos.x() + self.width() + 10
            dialog_y = pet_pos.y()
            
            # 确保对话框不会超出屏幕
            screen = QApplication.desktop().screenGeometry()
            if dialog_x + dialog.width() > screen.width():
                dialog_x = pet_pos.x() - dialog.width() - 10
            if dialog_y + dialog.height() > screen.height():
                dialog_y = screen.height() - dialog.height() - 50
            
            dialog.move(dialog_x, dialog_y)
            
            # 显示对话框
            dialog.exec_()
        except Exception as e:
            print(f"show_reminder_list error: {e}")
        finally:
            # 安全地销毁对话框
            if dialog:
                try:
                    dialog.deleteLater()
                except:
                    pass
    
    def add_single_reminder(self, reminder_time, content):
        """添加单次提醒"""
        if not self.reminder_manager:
            return
        
        # 计算目标时间
        from datetime import datetime, timedelta
        today = datetime.now().date()
        target_time = datetime.combine(today, reminder_time.toPyTime())
        
        # 如果时间已过，设置为明天
        if target_time <= datetime.now():
            target_time += timedelta(days=1)
        
        # 生成提醒标题
        title = f"定时提醒 {reminder_time.toString('HH:mm')}"
        
        # 添加提醒
        reminder_id = self.reminder_manager.add_reminder(
            title=title,
            content=content,
            reminder_type='single',
            target_time=target_time
        )
        
        # 显示设置成功消息
        QMessageBox.information(
            self, 
            '提醒设置成功', 
            f'提醒已设置！\n时间：{reminder_time.toString("HH:mm")}\n内容：{content}'
        )
    
    def add_repeat_reminder(self, interval_minutes, content):
        """添加循环提醒"""
        if not self.reminder_manager:
            return
        
        # 生成提醒标题
        if interval_minutes < 60:
            title = f"循环提醒 每{interval_minutes}分钟"
        else:
            hours = interval_minutes // 60
            minutes = interval_minutes % 60
            if minutes == 0:
                title = f"循环提醒 每{hours}小时"
            else:
                title = f"循环提醒 每{hours}小时{minutes}分钟"
        
        # 添加提醒
        reminder_id = self.reminder_manager.add_reminder(
            title=title,
            content=content,
            reminder_type='repeat',
            interval_minutes=interval_minutes
        )
        
        # 显示设置成功消息
        interval_text = f"{interval_minutes}分钟" if interval_minutes < 60 else f"{interval_minutes//60}小时{interval_minutes%60}分钟" if interval_minutes % 60 != 0 else f"{interval_minutes//60}小时"
        QMessageBox.information(
            self, 
            '循环提醒设置成功', 
            f'循环提醒已设置！\n间隔：{interval_text}\n内容：{content}'
        )
    
    def on_reminder_triggered(self, reminder_id, title, content):
        """处理提醒触发事件"""
        # 保存当前位置
        self.original_position = self.pos()
        
        # 调整宠物位置
        self.adjust_position_for_reminder()
        
        # 创建提醒消息框
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle('提醒')
        msg_box.setText(f'⏰ {title}\n\n{content}')
        msg_box.setIcon(QMessageBox.Information)
        
        # 设置按钮
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.setDefaultButton(QMessageBox.Ok)
        
        # 设置消息框位置（在宠物上方）
        pet_pos = self.pos()
        msg_x = pet_pos.x() - 50
        msg_y = pet_pos.y() - 150
        
        # 确保消息框不会超出屏幕
        screen = QApplication.desktop().screenGeometry()
        if msg_x < 0:
            msg_x = 10
        if msg_y < 0:
            msg_y = 10
        if msg_x + 300 > screen.width():
            msg_x = screen.width() - 310
        
        msg_box.move(msg_x, msg_y)
        
        # 显示消息框
        msg_box.exec_()
        
        # 恢复宠物原始位置
        if not self.original_position.isNull():
            self.move(self.original_position)
    
    def stop_all_reminders_with_message(self):
        """停止所有提醒并显示消息"""
        if self.reminder_manager and self.reminder_manager.has_active_reminders():
            self.reminder_manager.stop_all_reminders()
            QMessageBox.information(self, '提醒已停止', '所有提醒已成功停止！')
    
    def adjust_position_for_reminder(self):
        """调整宠物位置以配合提醒窗口显示"""
        # 获取屏幕尺寸
        screen = QApplication.desktop().screenGeometry()
        
        # 计算新位置（移动到屏幕中央上方）
        new_x = (screen.width() - self.width()) // 2
        new_y = screen.height() // 3
        
        # 确保不超出屏幕边界
        new_x = max(0, min(new_x, screen.width() - self.width()))
        new_y = max(0, min(new_y, screen.height() - self.height()))
        
        # 移动宠物到新位置
        self.move(new_x, new_y)
    
    def start_fall_animation(self):
        """开始下落动画（叶子飘落效果）"""
        self.change_pet_state(PetState.FALLING)
    
        # 若存在旧的属性动画或计时器，先停止
        if self.fall_animation:
            try:
                self.fall_animation.stop()
            except Exception:
                pass
            self.fall_animation = None
        if self.leaf_fall_timer and self.leaf_fall_timer.isActive():
            self.leaf_fall_timer.stop()
    
        # 屏幕与目标位置
        screen = QApplication.desktop().screenGeometry()
        start_pos = self.pos()
        target_y = screen.height() - self.height()
    
        # 记录初始参数
        self.leaf_fall_start_time = QTime.currentTime()
        self.leaf_fall_start_pos = start_pos
        self.leaf_base_x = start_pos.x()
    
        duration = getattr(PetConfig, 'LEAF_FALL_DURATION', PetConfig.FALL_DURATION * 3)
        sway_amp = getattr(PetConfig, 'LEAF_SWAY_AMPLITUDE', 35)
        sway_period = getattr(PetConfig, 'LEAF_SWAY_PERIOD_MS', 1200)
    
        # 使用计时器逐帧更新位置，产生左右摆动的缓慢下落效果
        self.leaf_fall_timer = QTimer(self)
        self.leaf_fall_timer.setInterval(16)  # ~60FPS
    
        def update_position():
            elapsed = self.leaf_fall_start_time.msecsTo(QTime.currentTime())
            progress = max(0.0, min(1.0, elapsed / float(duration)))
    
            # 垂直线性缓慢下降，可适度做Ease-Out
            ease_out = progress * (2 - progress)  # Quadratic ease-out
            new_y = int(self.leaf_fall_start_pos.y() + ease_out * (target_y - self.leaf_fall_start_pos.y()))
    
            # 左右摆动：正弦波，可随进度略微衰减
            decay = 0.85 - 0.35 * progress  # 从0.85衰减到0.5
            dx = int(sway_amp * decay * math.sin(2 * math.pi * (elapsed % sway_period) / float(sway_period)))
            new_x = self.leaf_base_x + dx
    
            # 保证不越界
            new_x = max(0, min(new_x, screen.width() - self.width()))
            new_y = max(0, min(new_y, screen.height() - self.height()))
    
            self.move(new_x, new_y)
    
            if progress >= 1.0 or new_y >= target_y:
                self.leaf_fall_timer.stop()
                self.change_pet_state(PetState.NORMAL)
    
        self.leaf_fall_timer.timeout.connect(update_position)
        self.leaf_fall_timer.start()
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        # 停止动画
        if self.fall_animation:
            self.fall_animation.stop()
        if hasattr(self, 'leaf_fall_timer') and self.leaf_fall_timer:
            try:
                self.leaf_fall_timer.stop()
            except Exception:
                pass
        
        # 停止所有提醒定时器
        if self.reminder_manager:
            self.reminder_manager.stop_all_reminders()
        
        event.accept()