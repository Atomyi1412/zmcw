# -*- coding: utf-8 -*-
"""
桌面宠物主窗口类
实现宠物的显示、拖拽、动画等核心功能
"""

import sys
import os
import math
from PyQt5.QtWidgets import (
    QWidget, QLabel, QApplication, QMenu, QAction, QMessageBox, QDialog,
    QVBoxLayout, QHBoxLayout, QPushButton, QSizePolicy
)
from PyQt5.QtCore import Qt, QPoint, QPropertyAnimation, QEasingCurve, pyqtSignal, QTimer, QTime, QStandardPaths, QRectF, QPointF
from PyQt5.QtGui import QPixmap, QPainter, QColor, QPainterPath, QFont

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

class SpeechBubbleDialog(QDialog):
    """漫画人物说话气泡样式的提醒框"""
    def __init__(self, title: str, content: str, parent=None):
        super().__init__(parent)
        self.title = title
        self.content = content
        # 改为自适应尺寸：设定最小/最大宽度区间
        self.min_width = 240
        self.max_width = 360
        self.radius = 14
        self.tail_size = 16  # 小尾巴尺寸
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setModal(True)
        # 使用自适应策略而非固定大小
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.setMinimumWidth(self.min_width)
        self.setMaximumWidth(self.max_width)

        # 中心内容区域
        layout = QVBoxLayout()
        layout.setContentsMargins(18, 16, 18, 22)  # 底部增加边距为尾巴留空间
        layout.setSpacing(10)

        title_label = QLabel(f"{self.title}")
        title_font = QFont()
        title_font.setPointSize(16)  # 再增大标题
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #333;")
        # 允许标题在宽度不足时换行
        title_label.setWordWrap(True)
        title_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        title_label.setMaximumWidth(self.max_width - 36)  # 36=左右边距18*2

        content_label = QLabel(self.content)
        content_label.setWordWrap(True)
        content_font = QFont()
        content_font.setPointSize(14)  # 内容更大
        content_label.setFont(content_font)
        content_label.setStyleSheet("color: #4a4a4a;")
        content_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        content_label.setMaximumWidth(self.max_width - 36)

        btn = QPushButton("知道啦")
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedHeight(34)
        btn_font = QFont()
        btn_font.setPointSize(12)
        btn.setFont(btn_font)
        btn.setStyleSheet(
            """
            QPushButton { background: #4C9AFF; color: white; border: none; border-radius: 6px; padding: 8px 16px; }
            QPushButton:hover { background: #3F84E5; }
            QPushButton:pressed { background: #376FC7; }
            """
        )
        btn.clicked.connect(self.accept)

        layout.addWidget(title_label)
        layout.addWidget(content_label, 1)
        hl = QHBoxLayout()
        hl.addStretch()
        hl.addWidget(btn)
        layout.addLayout(hl)

        self.setLayout(layout)

        # 依据当前内容自适应尺寸
        self.adjustSize()
        # 保证宽度不小于最小值（短文本时不至于太窄）
        if self.width() < self.min_width:
            self.resize(self.min_width, self.height())

    def paintEvent(self, event):
        # 画气泡+小尾巴（现在在底部中央，指向宠物头顶）
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setOpacity(1.0)

        # 阴影层（稍大、透明）
        shadow_path = QPainterPath()
        rect = QRectF(self.rect()).adjusted(2, 2, -2, -2)
        # 主体区域（预留底部给尾巴）
        bubble_rect = rect.adjusted(0, 0, 0, -self.tail_size)
        shadow_path.addRoundedRect(bubble_rect, self.radius, self.radius)
        painter.fillPath(shadow_path, QColor(0, 0, 0, 50))

        # 真正的白色气泡
        bubble_path = QPainterPath()
        bubble_rect2 = QRectF(self.rect()).adjusted(0, 0, 0, -self.tail_size)  # 在底部留出尾巴区域
        bubble_path.addRoundedRect(bubble_rect2, self.radius, self.radius)
        
        # 小尾巴：位于底部中央，朝下指向宠物头顶
        tail = QPainterPath()
        center_x = self.width() // 2  # 底部中央位置
        tail_base_y = self.height() - self.tail_size
        tail_left = QPointF(center_x - 8, tail_base_y)
        tail_right = QPointF(center_x + 8, tail_base_y)
        tail_tip = QPointF(center_x, self.height() - 2)  # 尖端朝下
        tail.moveTo(tail_left)
        tail.lineTo(tail_right)
        tail.lineTo(tail_tip)
        tail.closeSubpath()

        painter.fillPath(bubble_path, QColor(255, 255, 255))
        painter.fillPath(tail, QColor(255, 255, 255))

        # 轮廓线
        painter.setPen(QColor(225, 225, 225))
        painter.drawRoundedRect(bubble_rect2, self.radius, self.radius)
        painter.drawPath(tail)

class DesktopPet(QWidget):
    """桌面宠物主窗口类"""
    
    # 新增：获取当前屏幕可用区域（排除 Dock/任务栏）
    def _available_rect(self):
        desktop = QApplication.desktop()
        try:
            return desktop.availableGeometry(self)
        except Exception:
            return desktop.availableGeometry()
    
    def __init__(self):
        super().__init__()
        
        # 初始化属性
        self.current_state = PetState.NORMAL
        self.is_dragging = False
        self.drag_start_position = QPoint()
        self.images = {}
        self.original_images = {}  # 新增：保留原始图像，便于缩放
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
        
        # 若存在缩放设置，应用之
        scale = float(self.current_settings.get('pet_scale', getattr(PetConfig, 'DEFAULT_PET_SCALE', 1.0)))
        if abs(scale - 1.0) > 1e-6:
            self.apply_scale(scale)
        
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
                    
                    # 保存原始图像
                    self.original_images[state] = pixmap
                    
                    # 按当前窗口大小缩放图像保持比例和透明度
                    target_w = max(1, self.width() - 10)
                    target_h = max(1, self.height() - 10)
                    scaled_pixmap = pixmap.scaled(
                        target_w,
                        target_h,
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                    self.images[state] = scaled_pixmap
                else:
                    print(f"警告：无法加载图像 {image_path}")
                    placeholder = self.create_placeholder_image()
                    self.original_images[state] = placeholder
                    self.images[state] = placeholder.scaled(
                        max(1, self.width() - 10),
                        max(1, self.height() - 10),
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
            else:
                print(f"警告：图像文件不存在 {image_path}，使用占位图像")
                placeholder = self.create_placeholder_image()
                self.original_images[state] = placeholder
                self.images[state] = placeholder.scaled(
                    max(1, self.width() - 10),
                    max(1, self.height() - 10),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
    
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
        """设置初始位置在屏幕右下角（使用可用工作区）"""
        rect = self._available_rect()
        x = rect.right() - PetConfig.WINDOW_WIDTH - PetConfig.INITIAL_X_OFFSET
        y = rect.bottom() - PetConfig.WINDOW_HEIGHT - PetConfig.INITIAL_Y_OFFSET
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
            
            # 使用可用工作区，避免进入 Dock/任务栏
            rect = self._available_rect()
            new_x = max(rect.left(), min(new_position.x(), rect.right() - self.width()))
            new_y = max(rect.top(), min(new_position.y(), rect.bottom() - self.height()))
            
            self.move(new_x, new_y)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.LeftButton and self.is_dragging:
            self.is_dragging = False
            
            # 检查是否在屏幕上半部分（基于可用工作区）
            rect = self._available_rect()
            current_y = self.y()
            screen_middle = rect.top() + rect.height() * PetConfig.SCREEN_TOP_THRESHOLD
            
            auto_fall_enabled = bool(self.current_settings.get('auto_fall', getattr(PetConfig, 'DEFAULT_AUTO_FALL', True)))
            if current_y < screen_middle and auto_fall_enabled:
                # 在上半部分，触发下落动画
                self.start_fall_animation()
            else:
                # 在下半部分或关闭自动下落时，直接回到正常状态
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
        
        # 确保对话框不会超出屏幕（使用可用工作区）
        rect = self._available_rect()
        if dialog_x + dialog.width() > rect.right():
            dialog_x = pet_pos.x() - dialog.width() - 10
        if dialog_x < rect.left():
            dialog_x = rect.left() + 10
        if dialog_y + dialog.height() > rect.bottom():
            dialog_y = rect.bottom() - dialog.height() - 50
        if dialog_y < rect.top():
            dialog_y = rect.top() + 10
        
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
        
        # 应用缩放
        if 'pet_scale' in new_settings:
            try:
                self.apply_scale(float(new_settings['pet_scale']))
            except Exception as e:
                print(f"应用缩放失败: {e}")
        
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
                # 兼容旧版本：没有宠物名称时填充默认值
                if 'pet_name' not in self.current_settings:
                    self.current_settings['pet_name'] = PetConfig.DEFAULT_PET_NAME
                # 兼容旧版本：新增缩放与自动下落
                if 'pet_scale' not in self.current_settings:
                    self.current_settings['pet_scale'] = getattr(PetConfig, 'DEFAULT_PET_SCALE', 1.0)
                if 'auto_fall' not in self.current_settings:
                    self.current_settings['auto_fall'] = getattr(PetConfig, 'DEFAULT_AUTO_FALL', True)
            else:
                # 使用默认设置（含宠物名称、缩放与自动下落）
                self.current_settings = {
                    'always_on_top': PetConfig.ALWAYS_ON_TOP,
                    'pet_name': PetConfig.DEFAULT_PET_NAME,
                    'pet_scale': getattr(PetConfig, 'DEFAULT_PET_SCALE', 1.0),
                    'auto_fall': getattr(PetConfig, 'DEFAULT_AUTO_FALL', True)
                }
        except Exception as e:
            print(f"加载设置失败: {e}")
            # 使用默认设置（含宠物名称、缩放与自动下落）
            self.current_settings = {
                'always_on_top': PetConfig.ALWAYS_ON_TOP,
                'pet_name': PetConfig.DEFAULT_PET_NAME,
                'pet_scale': getattr(PetConfig, 'DEFAULT_PET_SCALE', 1.0),
                'auto_fall': getattr(PetConfig, 'DEFAULT_AUTO_FALL', True)
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
            # 确保对话框不会超出屏幕（使用可用工作区）
            rect = self._available_rect()
            if dialog_x + dialog.width() > rect.right():
                dialog_x = pet_pos.x() - dialog.width() - 10
            if dialog_x < rect.left():
                dialog_x = rect.left() + 10
            if dialog_y + dialog.height() > rect.bottom():
                dialog_y = rect.bottom() - dialog.height() - 50
            if dialog_y < rect.top():
                dialog_y = rect.top() + 10
            dialog.move(dialog_x, dialog_y)
            # 显示对话框并处理结果
            result = dialog.exec_()
            if result == QDialog.Accepted:
                reminder_type = dialog.get_reminder_type()
                reminder_content = dialog.get_reminder_content()
                reminder_title = dialog.get_reminder_title()
                if reminder_type == 'single':
                    reminder_time = dialog.get_reminder_time()
                    self.add_single_reminder(reminder_time, reminder_content, title=reminder_title)
                else:
                    reminder_interval = dialog.get_reminder_interval()
                    self.add_repeat_reminder(reminder_interval, reminder_content, title=reminder_title)
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
            
            # 确保对话框不会超出屏幕（使用可用工作区）
            rect = self._available_rect()
            if dialog_x + dialog.width() > rect.right():
                dialog_x = pet_pos.x() - dialog.width() - 10
            if dialog_x < rect.left():
                dialog_x = rect.left() + 10
            if dialog_y + dialog.height() > rect.bottom():
                dialog_y = rect.bottom() - dialog.height() - 50
            if dialog_y < rect.top():
                dialog_y = rect.top() + 10
            
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
    
    def add_single_reminder(self, reminder_time, content, title=None):
        """添加单次提醒"""
        if not self.reminder_manager:
            return
        from datetime import datetime, timedelta
        today = datetime.now().date()
        target_time = datetime.combine(today, reminder_time.toPyTime())
        if target_time <= datetime.now():
            target_time += timedelta(days=1)
        # 使用传入标题或生成默认标题
        if not title:
            title = f"定时提醒 {reminder_time.toString('HH:mm')}"
        reminder_id = self.reminder_manager.add_reminder(
            title=title,
            content=content,
            reminder_type='single',
            target_time=target_time
        )
        QMessageBox.information(
            self, 
            '提醒设置成功', 
            f'提醒已设置！\n时间：{reminder_time.toString("HH:mm")}\n内容：{content}'
        )
    
    def add_repeat_reminder(self, interval_minutes, content, title=None):
        """添加循环提醒"""
        if not self.reminder_manager:
            return
        # 使用传入标题或生成默认标题
        if not title:
            if interval_minutes < 60:
                title = f"循环提醒 每{interval_minutes}分钟"
            else:
                hours = interval_minutes // 60
                minutes = interval_minutes % 60
                if minutes == 0:
                    title = f"循环提醒 每{hours}小时"
                else:
                    title = f"循环提醒 每{hours}小时{minutes}分钟"
        reminder_id = self.reminder_manager.add_reminder(
            title=title,
            content=content,
            reminder_type='repeat',
            interval_minutes=interval_minutes
        )
        interval_text = f"{interval_minutes}分钟" if interval_minutes < 60 else f"{interval_minutes//60}小时{interval_minutes%60}分钟" if interval_minutes % 60 != 0 else f"{interval_minutes//60}小时"
        QMessageBox.information(
            self, 
            '循环提醒设置成功', 
            f'循环提醒已设置！\n间隔：{interval_text}\n内容：{content}'
        )
    
    def on_reminder_triggered(self, reminder_id, title, content):
        """处理提醒触发事件 -- 使用漫画气泡样式，从宠物正上方展示"""
        try:
            # 读取宠物名称并拼接到内容前
            pet_name = self.current_settings.get('pet_name', PetConfig.DEFAULT_PET_NAME)
            display_content = f"{pet_name}：{content}" if pet_name else content
            
            # 创建漫画气泡对话框
            bubble = SpeechBubbleDialog(f"⏰ {title}", display_content, self)

            # 计算展示位置（宠物正上方）
            pet_pos = self.pos()
            rect = self._available_rect()

            bubble_w, bubble_h = bubble.width(), bubble.height()
            
            # 计算宠物头顶中央位置
            pet_center_x = pet_pos.x() + self.width() // 2
            pet_top_y = pet_pos.y()
            
            # 气泡位置：以宠物头顶中央为锚点，气泡在正上方
            bx = pet_center_x - bubble_w // 2  # 水平居中对齐
            by = pet_top_y - bubble_h - 5  # 垂直在宠物上方，留5px间距

            # 边界处理（使用可用工作区）
            if bx < rect.left() + 10:
                bx = rect.left() + 10
            elif bx + bubble_w > rect.right() - 10:
                bx = rect.right() - bubble_w - 10
            # 上边界（如果气泡超出屏幕顶部，改为显示在宠物下方）
            if by < rect.top() + 10:
                by = pet_pos.y() + self.height() + 5
            # 下边界
            if by + bubble_h > rect.bottom() - 10:
                by = rect.bottom() - bubble_h - 10

            bubble.move(bx, by)
            bubble.exec_()
        except Exception as e:
            print(f"on_reminder_triggered error: {e}")

    def stop_all_reminders_with_message(self):
        """停止所有提醒并显示消息"""
        if self.reminder_manager and self.reminder_manager.has_active_reminders():
            self.reminder_manager.stop_all_reminders()
            QMessageBox.information(self, '提醒已停止', '所有提醒已成功停止！')
    
    def adjust_position_for_reminder(self):
        """调整宠物位置以配合提醒窗口显示（使用可用工作区）"""
        rect = self._available_rect()
        
        # 计算新位置（移动到屏幕中央上方）
        new_x = rect.left() + (rect.width() - self.width()) // 2
        new_y = rect.top() + rect.height() // 3
        
        # 确保不超出屏幕边界
        new_x = max(rect.left(), min(new_x, rect.right() - self.width()))
        new_y = max(rect.top(), min(new_y, rect.bottom() - self.height()))
        
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
    
        # 使用可用工作区
        rect = self._available_rect()
        start_pos = self.pos()
        target_y = rect.bottom() - self.height()
    
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
    
            # 边界约束（可用工作区）
            new_x = max(rect.left(), min(new_x, rect.right() - self.width()))
            new_y = max(rect.top(), min(new_y, rect.bottom() - self.height()))
    
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

    def apply_scale(self, scale: float):
        """根据缩放比例调整窗口大小并重建缩放图像"""
        try:
            min_s = getattr(PetConfig, 'MIN_PET_SCALE', 0.5)
            max_s = getattr(PetConfig, 'MAX_PET_SCALE', 2.0)
            s = max(min_s, min(max_s, float(scale)))
        except Exception:
            s = 1.0
        
        # 计算新尺寸（以配置的基础尺寸为基准）
        base_w = getattr(PetConfig, 'WINDOW_WIDTH', 100)
        base_h = getattr(PetConfig, 'WINDOW_HEIGHT', 100)
        new_w = max(30, int(base_w * s))
        new_h = max(30, int(base_h * s))
        
        # 应用窗口与标签尺寸
        self.setFixedSize(new_w, new_h)
        if self.pet_label:
            self.pet_label.setGeometry(0, 0, new_w, new_h)
        
        # 重新按新尺寸缩放图像
        self.rescale_images()
        
        # 更新当前显示
        if self.current_state and self.current_state.value in self.images:
            self.pet_label.setPixmap(self.images[self.current_state.value])
        
        # 确保窗口在屏幕内
        rect = self._available_rect()
        nx = min(max(rect.left(), self.x()), rect.right() - self.width())
        ny = min(max(rect.top(), self.y()), rect.bottom() - self.height())
        self.move(nx, ny)
        
        # 记录设置
        self.current_settings['pet_scale'] = s

    def rescale_images(self):
        """按照当前窗口大小重新缩放所有图像"""
        try:
            target_w = max(1, self.width() - 10)
            target_h = max(1, self.height() - 10)
            for state, pix in self.original_images.items():
                self.images[state] = pix.scaled(
                    target_w,
                    target_h,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
        except Exception as e:
            print(f"重建缩放图像失败: {e}")