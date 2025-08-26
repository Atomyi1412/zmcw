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
    QVBoxLayout, QHBoxLayout, QPushButton, QSizePolicy, QDesktopWidget
)
from PyQt5.QtCore import Qt, QPoint, QPropertyAnimation, QEasingCurve, pyqtSignal, QTimer, QTime, QStandardPaths, QRectF, QPointF
from PyQt5.QtGui import QPixmap, QPainter, QColor, QPainterPath, QFont, QCursor, QPen
from PyQt5.QtWidgets import QDesktopWidget

from pet_state import PetState
from config import PetConfig
from reminder_dialog import ReminderDialog
from reminder_list_dialog import ReminderListDialog
from reminder_manager import ReminderManager
from settings_dialog import SettingsDialog
from login_dialog import LoginDialog
from register_dialog import RegisterDialog
from user_auth import user_auth
from friends_dialog import FriendsDialog
from chat_window import ChatWindow
from friends_manager import friends_manager
from chat_database import chat_db

# PyInstaller资源路径辅助函数
def resource_path(relative_path: str) -> str:
    try:
        base_path = getattr(sys, '_MEIPASS')  # PyInstaller临时目录
    except Exception:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, relative_path)

class SpeechBubbleDialog(QDialog):
    """漫画人物说话气泡样式的提醒框"""
    def __init__(self, title: str, content: str, parent=None, button_text: str = "知道啦"): 
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

        # 移除标题显示

        content_label = QLabel(self.content)
        content_label.setWordWrap(True)
        content_font = QFont()
        content_font.setPointSize(14)  # 内容更大
        content_label.setFont(content_font)
        content_label.setStyleSheet("color: #4a4a4a;")
        content_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        content_label.setMaximumWidth(self.max_width - 36)

        btn = QPushButton(button_text)
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

        # 不再添加标题标签
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

    def paintEvent(self, a0):
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

        # 粗黑边框
        from PyQt5.QtGui import QPen
        from PyQt5.QtCore import Qt as QtCore
        pen = QPen(QColor(0, 0, 0), 3)  # 黑色，3像素粗
        pen.setJoinStyle(QtCore.RoundJoin)  # 圆角连接
        painter.setPen(pen)
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
        
        # 好友消息轮询属性（提前初始化，避免自动登录期间访问不存在的属性）
        self.message_check_timer = None
        self.friend_name_cache = {}
        self.notified_senders = set()
        # 创建消息检查定时器（未登录时不会启动）
        self.init_message_checker()
        
        # 初始化窗口
        self.init_window()
        
        # 初始化提醒管理器
        self.init_reminder_manager()
        
        # 初始化用户系统
        self.init_user_system()
        
        # 加载设置
        self.load_settings()
        
        # 应用置顶设置
        always_on_top = self.current_settings.get('always_on_top', PetConfig.ALWAYS_ON_TOP)
        if always_on_top:
            self.toggle_always_on_top(True)
        
        # 同步一次开机自启动状态（保证路径为当前版本/位置）
        try:
            self.update_auto_start(bool(self.current_settings.get('auto_start', getattr(PetConfig, 'DEFAULT_AUTO_START', False))))
        except Exception as e:
            print(f"同步开机自启动失败: {e}")
        
        # 加载图像
        self.load_images()
        
        # 若存在缩放设置，应用之
        scale = float(self.current_settings.get('pet_scale', getattr(PetConfig, 'DEFAULT_PET_SCALE', 1.0)))
        if abs(scale - 1.0) > 1e-6:
            self.apply_scale(scale)
        
        # 设置初始位置
        self.set_initial_position()
        
        # 消息轮询属性与定时器已在前面初始化
        
        # 显示宠物
        self.change_pet_state(PetState.NORMAL)
    
    def init_window(self):
        """初始化窗口属性"""
        # 设置窗口大小
        self.setFixedSize(PetConfig.WINDOW_WIDTH, PetConfig.WINDOW_HEIGHT)
        
        # 设置窗口标题
        self.setWindowTitle('桌面宠物')
        
        # 设置窗口标志：无边框、置顶、工具窗口（隐藏程序坞图标）
        self.setWindowFlags(
            Qt.FramelessWindowHint |  # 无边框
            Qt.WindowStaysOnTopHint |  # 置顶
            Qt.WindowDoesNotAcceptFocus |  # 不接受焦点，避免干扰其他程序
            Qt.Tool  # 工具窗口，不在程序坞显示
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
        self.reminder_manager = ReminderManager()
        # 连接提醒触发信号
        self.reminder_manager.reminder_triggered.connect(self.on_reminder_triggered)
    
    def init_user_system(self):
        """初始化用户系统"""
        # 用户系统相关的对话框
        self.login_dialog = None
        self.register_dialog = None
        
        # 应用启动时尝试自动登录（记住我）
        try:
            self.try_auto_login()
        except Exception as e:
            print(f"自动登录检查失败: {e}")
    
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
            # Mac特定处理：临时隐藏窗口以避免透明残影
            import platform
            is_macos = platform.system() == 'Darwin'
            
            if is_macos:
                # 临时隐藏窗口
                self.hide()
                QApplication.processEvents()
            
            # 彻底清除QLabel的内容和背景
            self.pet_label.clear()
            self.pet_label.setAutoFillBackground(False)
            self.pet_label.setScaledContents(False)
            
            # 强制处理事件循环，确保清除操作完成
            QApplication.processEvents()
            
            # 设置新的图像
            self.pet_label.setPixmap(self.images[state_key])
            
            if is_macos:
                # Mac特定：重新显示窗口
                self.show()
                # 额外的Mac刷新处理
                self.setAttribute(Qt.WA_TranslucentBackground, False)
                self.setAttribute(Qt.WA_TranslucentBackground, True)
            
            # 多重强制刷新机制
            self.pet_label.repaint()  # 强制重绘
            self.pet_label.update()   # 更新显示
            self.repaint()            # 强制重绘整个窗口
            self.update()             # 更新整个窗口
            
            # 再次处理事件循环，确保显示更新完成
            QApplication.processEvents()
        else:
            print(f"警告：状态 {state_key} 对应的图像不存在")
    
    def mousePressEvent(self, a0):
        """鼠标按下事件"""
        if a0.button() == Qt.LeftButton:
            # 若正在执行下落动画，立即停止
            if hasattr(self, 'leaf_fall_timer') and self.leaf_fall_timer and self.leaf_fall_timer.isActive():
                self.leaf_fall_timer.stop()
                self.leaf_fall_timer = None
                self.change_pet_state(PetState.NORMAL)
            self.is_dragging = True
            self.drag_start_position = a0.globalPos() - self.frameGeometry().topLeft()
            self.change_pet_state(PetState.DRAGGING)
            a0.accept()
    
    def mouseMoveEvent(self, a0):
        """鼠标移动事件"""
        if a0.buttons() == Qt.LeftButton and self.is_dragging:
            # 计算新位置
            new_position = a0.globalPos() - self.drag_start_position
            
            # 使用可用工作区，避免进入 Dock/任务栏
            rect = self._available_rect()
            new_x = max(rect.left(), min(new_position.x(), rect.right() - self.width()))
            new_y = max(rect.top(), min(new_position.y(), rect.bottom() - self.height()))
            
            self.move(new_x, new_y)
            a0.accept()
    
    def mouseReleaseEvent(self, a0):
        """鼠标释放事件"""
        if a0.button() == Qt.LeftButton and self.is_dragging:
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
            
            a0.accept()
    
    def contextMenuEvent(self, a0):
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
        
        # 添加用户系统菜单
        if user_auth.is_user_logged_in():
            # 已登录状态
            current_user = user_auth.get_current_user()
            user_info_action = QAction(f'用户: {current_user["username"]}', self)
            user_info_action.setEnabled(False)
            context_menu.addAction(user_info_action)
            
            # 好友管理
            friends_action = QAction('好友管理', self)
            friends_action.triggered.connect(self.show_friends_dialog)
            context_menu.addAction(friends_action)
            
            # 登出
            logout_action = QAction('登出', self)
            logout_action.triggered.connect(self.handle_logout)
            context_menu.addAction(logout_action)
        else:
            # 未登录状态
            login_action = QAction('登录', self)
            login_action.triggered.connect(self.show_login_dialog)
            context_menu.addAction(login_action)
        
        context_menu.addSeparator()
        
        # 添加设置选项
        settings_action = QAction('设置', self)
        settings_action.triggered.connect(self.show_settings_dialog)
        context_menu.addAction(settings_action)
        
        # 添加退出选项
        exit_action = QAction('退出', self)
        exit_action.triggered.connect(QApplication.quit)
        context_menu.addAction(exit_action)
        
        # 显示菜单
        context_menu.exec_(a0.globalPos())
    
    def update_menu(self):
        """更新菜单状态 - 由于菜单是动态创建的，此方法暂时为空"""
        # 菜单在 contextMenuEvent 中动态创建，无需额外更新
        pass
    
    def show_login_dialog(self):
        """显示登录对话框"""
        if self.login_dialog is None:
            self.login_dialog = LoginDialog(self)
            self.login_dialog.login_success.connect(self.on_login_success)
            self.login_dialog.switch_to_register.connect(self.show_register_dialog)
        
        # 设置对话框位置（在宠物附近）
        pet_pos = self.pos()
        dialog_x = pet_pos.x() + self.width() + 10
        dialog_y = pet_pos.y()
        
        # 确保对话框不会超出屏幕
        rect = self._available_rect()
        if dialog_x + self.login_dialog.width() > rect.right():
            dialog_x = pet_pos.x() - self.login_dialog.width() - 10
        if dialog_x < rect.left():
            dialog_x = rect.left() + 10
        if dialog_y + self.login_dialog.height() > rect.bottom():
            dialog_y = rect.bottom() - self.login_dialog.height() - 50
        if dialog_y < rect.top():
            dialog_y = rect.top() + 10
        
        self.login_dialog.move(dialog_x, dialog_y)
        self.login_dialog.show()
    
    def show_register_dialog(self):
        """显示注册对话框"""
        if self.register_dialog is None:
            self.register_dialog = RegisterDialog(self)
            self.register_dialog.register_success.connect(self.on_register_success)
            self.register_dialog.switch_to_login.connect(self.show_login_dialog)
        
        # 设置对话框位置（在宠物附近）
        pet_pos = self.pos()
        dialog_x = pet_pos.x() + self.width() + 10
        dialog_y = pet_pos.y()
        
        # 确保对话框不会超出屏幕
        rect = self._available_rect()
        if dialog_x + self.register_dialog.width() > rect.right():
            dialog_x = pet_pos.x() - self.register_dialog.width() - 10
        if dialog_x < rect.left():
            dialog_x = rect.left() + 10
        if dialog_y + self.register_dialog.height() > rect.bottom():
            dialog_y = rect.bottom() - self.register_dialog.height() - 50
        if dialog_y < rect.top():
            dialog_y = rect.top() + 10
        
        self.register_dialog.move(dialog_x, dialog_y)
        self.register_dialog.show()
    
    def on_login_success(self, user_info):
        """登录成功回调"""
        print(f"用户 {user_info['username']} 登录成功")
        
        # 关闭登录对话框
        if self.login_dialog:
            self.login_dialog.close()
        
        # 处理“记住我”
        try:
            if user_info.get('remember_me'):
                self.save_remember_session(user_info.get('user_id'), user_info.get('username'))
            else:
                self.clear_remember_session()
        except Exception as e:
            print(f"保存记住我状态失败: {e}")
        
        # 更新菜单状态
        self.update_menu()
        
        # 启动好友消息轮询并清空缓存
        try:
            self.friend_name_cache.clear()
            self.notified_senders.clear()
            if self.message_check_timer:
                self.message_check_timer.start()
            else:
                self.init_message_checker()
        except Exception as e:
            print(f"启动消息轮询失败: {e}")
        
        # 可以在这里添加登录成功后的处理逻辑
        # 比如显示欢迎消息等
    
    def on_register_success(self, user_info):
        """处理注册成功"""
        print(f"用户 {user_info['username']} 注册并登录成功")
        # 可以在这里添加注册成功后的处理逻辑
    
    def handle_logout(self):
        """处理登出操作"""
        # 立即更新UI状态，给用户即时反馈
        print("正在登出...")
        
        # 异步执行登出操作
        from async_worker import LogoutWorker, task_manager
        
        self.logout_worker = task_manager.run_task(LogoutWorker)
        self.logout_worker.progress.connect(lambda msg: print(msg))
        self.logout_worker.finished.connect(self.on_logout_finished)
        self.logout_worker.error.connect(self.on_logout_error)
    
    def on_logout_finished(self, result: dict):
        """登出完成回调"""
        if result.get('success'):
            # 清除所有缓存数据
            from cache_manager import user_cache
            user_cache.clear_all()
            
            # 停止消息轮询并清理相关缓存
            try:
                if self.message_check_timer and self.message_check_timer.isActive():
                    self.message_check_timer.stop()
                self.friend_name_cache.clear()
                self.notified_senders.clear()
            except Exception as e:
                print(f"停止消息轮询失败: {e}")
            
            # 清除记住我会话
            try:
                self.clear_remember_session()
            except Exception as e:
                print(f"清除记住我会话失败: {e}")
            
            # 关闭与登录状态相关的窗口（好友管理、聊天窗口等）
            try:
                self.close_login_related_windows()
            except Exception as e:
                print(f"关闭登录相关窗口时出错: {e}")
            
            # 更新菜单状态
            self.update_menu()
            print("用户已登出")
        else:
            print(f"登出失败: {result.get('message', '未知错误')}")
    
    def on_logout_error(self, error_message: str):
        """登出错误"""
        print(f"登出时出错: {error_message}")
    
    def show_friends_dialog(self):
        """显示好友管理对话框"""
        if not user_auth.is_user_logged_in():
            QMessageBox.warning(self, "提示", "请先登录")
            return
        
        # 如果已打开，置顶并返回
        try:
            if hasattr(self, 'friends_dialog') and self.friends_dialog is not None:
                if self.friends_dialog.isVisible():
                    self.friends_dialog.raise_()
                    self.friends_dialog.activateWindow()
                    return
        except Exception:
            pass
        
        # 创建新的对话框实例
        dialog = FriendsDialog(self)
        dialog.chat_requested.connect(self.on_chat_requested)
        
        # 设置对话框位置（在宠物附近）
        pet_pos = self.pos()
        dialog_x = pet_pos.x() + self.width() + 10
        dialog_y = pet_pos.y()
        
        # 确保对话框不会超出屏幕
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
        
        # 保持引用并以非模态方式显示
        self.friends_dialog = dialog
        dialog.setModal(False)
        dialog.show()
    
    def on_chat_requested(self, friend_id, username):
        """处理聊天请求"""
        if not user_auth.is_user_logged_in():
            QMessageBox.warning(self, "提示", "请先登录")
            return
        
        # 创建聊天窗口
        chat_window = ChatWindow(friend_id, username, self)
        
        # 设置聊天窗口位置（在宠物附近）
        pet_pos = self.pos()
        chat_x = pet_pos.x() + self.width() + 10
        chat_y = pet_pos.y()
        
        # 确保聊天窗口不会超出屏幕
        rect = self._available_rect()
        if chat_x + chat_window.width() > rect.right():
            chat_x = pet_pos.x() - chat_window.width() - 10
        if chat_x < rect.left():
            chat_x = rect.left() + 10
        if chat_y + chat_window.height() > rect.bottom():
            chat_y = rect.bottom() - chat_window.height() - 50
        if chat_y < rect.top():
            chat_y = rect.top() + 10
        
        chat_window.move(chat_x, chat_y)
        chat_window.show()
    
    def close_login_related_windows(self):
        """关闭与登录状态相关的所有窗口，如好友管理和聊天窗口。"""
        # 关闭好友管理对话框
        try:
            if hasattr(self, 'friends_dialog') and self.friends_dialog is not None:
                if self.friends_dialog.isVisible():
                    self.friends_dialog.close()
                self.friends_dialog = None
        except Exception as e:
            print(f"关闭好友管理对话框失败: {e}")
        
        # 关闭所有聊天窗口（作为当前窗口的子窗口）
        try:
            for w in self.findChildren(ChatWindow):
                if w.isVisible():
                    w.close()
        except Exception as e:
            print(f"关闭聊天窗口失败: {e}")
        
        # 关闭登录/注册对话框（如果存在）
        try:
            if hasattr(self, 'login_dialog') and self.login_dialog is not None:
                if self.login_dialog.isVisible():
                    self.login_dialog.close()
                self.login_dialog = None
        except Exception as e:
            print(f"关闭登录对话框失败: {e}")
        
        try:
            if hasattr(self, 'register_dialog') and self.register_dialog is not None:
                if self.register_dialog.isVisible():
                    self.register_dialog.close()
                self.register_dialog = None
        except Exception as e:
            print(f"关闭注册对话框失败: {e}")
    
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
        
        # 应用/同步开机自启动
        if 'auto_start' in new_settings:
            try:
                self.update_auto_start(bool(new_settings['auto_start']))
            except Exception as e:
                print(f"应用开机自启动失败: {e}")
        
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
                # 兼容旧版本：新增开机自启动
                if 'auto_start' not in self.current_settings:
                    self.current_settings['auto_start'] = getattr(PetConfig, 'DEFAULT_AUTO_START', False)
            else:
                # 使用默认设置（含宠物名称、缩放、自动下落与开机自启动）
                self.current_settings = {
                    'always_on_top': PetConfig.ALWAYS_ON_TOP,
                    'pet_name': PetConfig.DEFAULT_PET_NAME,
                    'pet_scale': getattr(PetConfig, 'DEFAULT_PET_SCALE', 1.0),
                    'auto_fall': getattr(PetConfig, 'DEFAULT_AUTO_FALL', True),
                    'auto_start': getattr(PetConfig, 'DEFAULT_AUTO_START', False)
                }
        except Exception as e:
            print(f"加载设置失败: {e}")
            # 使用默认设置（含宠物名称、缩放、自动下落与开机自启动）
            self.current_settings = {
                'always_on_top': PetConfig.ALWAYS_ON_TOP,
                'pet_name': PetConfig.DEFAULT_PET_NAME,
                'pet_scale': getattr(PetConfig, 'DEFAULT_PET_SCALE', 1.0),
                'auto_fall': getattr(PetConfig, 'DEFAULT_AUTO_FALL', True),
                'auto_start': getattr(PetConfig, 'DEFAULT_AUTO_START', False)
            }

    # =====================
    # 自启动（开机启动）实现
    # =====================
    def update_auto_start(self, enabled: bool):
        """根据平台启用/禁用开机自启动。"""
        try:
            if sys.platform.startswith('darwin'):
                self._macos_set_login_item(enabled)
            elif os.name == 'nt':
                self._windows_set_run_key(enabled)
            else:
                # 其他平台暂不实现（或按需扩展）
                pass
            self.current_settings['auto_start'] = bool(enabled)
        except Exception as e:
            print(f"更新开机自启动失败: {e}")

    def _windows_set_run_key(self, enabled: bool):
        """Windows: 使用注册表 Run 键实现开机自启动（HKCU）。"""
        try:
            import winreg
        except Exception as e:
            print(f"winreg 不可用，无法设置开机自启动: {e}")
            return
        run_key_path = r"Software\\Microsoft\\Windows\\CurrentVersion\\Run"
        app_name = "DesktopPet"
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, run_key_path, 0, winreg.KEY_SET_VALUE) as key:
                if enabled:
                    cmd = self._windows_start_command()
                    winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, cmd)
                else:
                    try:
                        winreg.DeleteValue(key, app_name)
                    except FileNotFoundError:
                        pass
        except Exception as e:
            print(f"设置 Windows 自启动失败: {e}")

    def _windows_start_command(self) -> str:
        """返回写入 Run 键的启动命令（带引号）。"""
        if getattr(sys, 'frozen', False):
            # PyInstaller 打包的 exe
            return f'"{sys.executable}"'
        else:
            # 开发环境：使用当前 Python 解释器 + main.py
            python_exe = sys.executable
            script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'main.py'))
            return f'"{python_exe}" "{script_path}"'

    def _macos_app_bundle_path(self):
        """尝试获取当前应用的 .app 包路径（仅在打包为 .app 时可用）。"""
        try:
            exe_path = os.path.abspath(sys.executable)
            # PyInstaller .app 内的可执行文件路径通常为 .../YourApp.app/Contents/MacOS/YourApp
            contents_dir = os.path.dirname(exe_path)  # .../Contents/MacOS
            app_dir = os.path.dirname(contents_dir)   # .../Contents
            bundle_dir = os.path.dirname(app_dir)     # .../YourApp.app
            if bundle_dir.endswith('.app') and os.path.isdir(bundle_dir):
                return bundle_dir
        except Exception:
            pass
        return None

    def _macos_add_login_item(self, app_path: str, hidden: bool = False) -> bool:
        """使用 AppleScript 将应用添加到系统“登录项”。返回是否成功。"""
        import subprocess
        try:
            # 使用 System Events 创建登录项
            # 指定 name 有助于后续删除；若系统已存在同名项，先尝试删除再创建
            name = 'DesktopPet'
            delete_cmd = f'tell application "System Events" to if exists login item "{name}" then delete login item "{name}"'
            create_cmd = (
                'tell application "System Events" to '
                f'make login item at end with properties {{path:"{app_path}", hidden:{str(hidden).lower()}, name:"{name}"}}'
            )
            subprocess.run(['osascript', '-e', delete_cmd], check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            result = subprocess.run(['osascript', '-e', create_cmd], check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return result.returncode == 0
        except Exception as e:
            print(f"添加登录项失败: {e}")
            return False

    def _macos_remove_login_item(self, name: str = 'DesktopPet') -> None:
        """使用 AppleScript 从系统“登录项”移除应用（忽略错误）。"""
        import subprocess
        try:
            delete_cmd = f'tell application "System Events" to if exists login item "{name}" then delete login item "{name}"'
            subprocess.run(['osascript', '-e', delete_cmd], check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except Exception as e:
            print(f"移除登录项失败: {e}")

    def _macos_set_login_item(self, enabled: bool):
        """macOS: 优先使用系统“登录项”（Login Items）；失败时回退到 LaunchAgents。"""
        import plistlib
        import subprocess

        # 统一的 LaunchAgent 路径与标签（作为回退方案以及清理遗留）
        plist_dir = os.path.expanduser('~/Library/LaunchAgents')
        os.makedirs(plist_dir, exist_ok=True)
        label = 'com.desktoppet.app'
        plist_path = os.path.join(plist_dir, f'{label}.plist')

        if enabled:
            # 优先尝试把 .app 写入“登录项”列表
            app_bundle = self._macos_app_bundle_path()
            if app_bundle:
                ok = self._macos_add_login_item(app_bundle, hidden=False)
                if ok:
                    # 登录项添加成功：清理可能存在的 LaunchAgent，避免显示在“允许在后台”
                    try:
                        subprocess.run(['launchctl', 'unload', plist_path], check=False)
                    except Exception:
                        pass
                    try:
                        if os.path.exists(plist_path):
                            os.remove(plist_path)
                    except Exception as e:
                        print(f"清理旧 LaunchAgent 失败: {e}")
                    return
                else:
                    print('未能添加到“登录项”，将回退到 LaunchAgent 方案。')
            else:
                print('未检测到 .app 包（可能在开发环境运行），将使用 LaunchAgent 方案。')

            # 回退：使用 LaunchAgent 方案（会显示在“允许在后台”）
            if getattr(sys, 'frozen', False):
                program_args = [sys.executable]
            else:
                program_args = [sys.executable, os.path.abspath(os.path.join(os.path.dirname(__file__), 'main.py'))]
            plist_data = {
                'Label': label,
                'ProgramArguments': program_args,
                'RunAtLoad': True,
                'KeepAlive': False,
                # 移除 ProcessType: 'Background'，尽量减少被归类为后台项目的概率（仍可能显示在“允许在后台”）
                'StandardOutPath': '/tmp/desktoppet.out',
                'StandardErrorPath': '/tmp/desktoppet.err'
            }
            try:
                with open(plist_path, 'wb') as f:
                    plistlib.dump(plist_data, f)
                try:
                    subprocess.run(['launchctl', 'unload', plist_path], check=False)
                except Exception:
                    pass
                try:
                    subprocess.run(['launchctl', 'load', plist_path], check=False)
                except Exception as e:
                    print(f"加载 LaunchAgent 失败: {e}")
            except Exception as e:
                print(f"写入 LaunchAgent 失败: {e}")
        else:
            # 关闭：删除登录项，同时卸载并删除 LaunchAgent
            self._macos_remove_login_item(name='DesktopPet')
            try:
                try:
                    subprocess.run(['launchctl', 'unload', plist_path], check=False)
                except Exception:
                    pass
                if os.path.exists(plist_path):
                    os.remove(plist_path)
            except Exception as e:
                print(f"移除 LaunchAgent 失败: {e}")

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
                if reminder_type == 'single':
                    reminder_time = dialog.get_reminder_time()
                    self.add_single_reminder(reminder_time, reminder_content)
                elif reminder_type == 'repeat':
                    reminder_interval = dialog.get_reminder_interval()
                    self.add_repeat_reminder(reminder_interval, reminder_content)
                elif reminder_type == 'relative':
                    relative_seconds = dialog.get_relative_seconds()
                    self.add_relative_reminder(relative_seconds, reminder_content)
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
        reminder_id = self.reminder_manager.add_reminder(
            title='',
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
        reminder_id = self.reminder_manager.add_reminder(
            title='',
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
    
    def add_relative_reminder(self, relative_seconds, content, title=None):
        """添加相对时间提醒"""
        if not self.reminder_manager:
            return
        
        reminder_id = self.reminder_manager.add_reminder(
            title='',
            content=content,
            reminder_type='relative',
            relative_seconds=relative_seconds
        )
        
        # 生成时间文本用于显示
        if relative_seconds < 60:
            time_text = f"{relative_seconds}秒"
        elif relative_seconds < 3600:
            minutes = relative_seconds // 60
            seconds = relative_seconds % 60
            if seconds == 0:
                time_text = f"{minutes}分钟"
            else:
                time_text = f"{minutes}分{seconds}秒"
        else:
            hours = relative_seconds // 3600
            minutes = (relative_seconds % 3600) // 60
            if minutes == 0:
                time_text = f"{hours}小时"
            else:
                time_text = f"{hours}小时{minutes}分钟"
        
        QMessageBox.information(
            self, 
            '延迟提醒设置成功', 
            f'延迟提醒已设置！\n延迟：{time_text}后\n内容：{content}'
        )
    
    def add_reminder_by_type(self, content, time, reminder_type, interval, relative_seconds):
        """根据类型添加提醒"""
        if reminder_type == 'single':
            self.add_single_reminder(time, content)
        elif reminder_type == 'repeat':
            self.add_repeat_reminder(interval, content)
        elif reminder_type == 'relative':
            self.add_relative_reminder(relative_seconds, content)
    
    def on_reminder_triggered(self, reminder_id, title, content):
        """处理提醒触发事件 -- 使用漫画气泡样式，从宠物正上方展示"""
        try:
            # 读取宠物名称并拼接到内容前，换行显示类似写信格式
            pet_name = self.current_settings.get('pet_name', PetConfig.DEFAULT_PET_NAME)
            display_content = f"{pet_name}：\n    {content}" if pet_name else content
            
            # 创建漫画气泡对话框
            bubble = SpeechBubbleDialog("", display_content, self)

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
    
    def closeEvent(self, a0):
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
        
        # 新增：停止消息轮询
        try:
            if self.message_check_timer and self.message_check_timer.isActive():
                self.message_check_timer.stop()
        except Exception:
            pass
        
        a0.accept()

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

    def _remember_file_path(self) -> str:
        """获取记住我会话文件路径"""
        import os
        base_dir = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
        if not base_dir:
            base_dir = os.path.expanduser('~/.desktop_pet')
        os.makedirs(base_dir, exist_ok=True)
        return os.path.join(base_dir, 'remember_me.json')

    def save_remember_session(self, user_id, username):
        """保存记住我会话信息"""
        import json, os
        if not user_id or not username:
            return
        data = {
            'user_id': str(user_id),
            'username': username,
            'ts': int(__import__('time').time())
        }
        path = self._remember_file_path()
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)

    def clear_remember_session(self):
        """清除记住我会话信息"""
        import os
        path = self._remember_file_path()
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception as e:
            print(f"删除remember_me文件失败: {e}")

    def try_auto_login(self):
        """尝试根据本地会话自动登录"""
        import json, os
        path = self._remember_file_path()
        if not os.path.exists(path):
            return
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            user_id = data.get('user_id')
            if not user_id:
                return
            # 调用用户系统恢复会话
            from user_auth import user_auth
            result = user_auth.restore_session(user_id)
            if result.get('success'):
                print(f"自动登录成功：{result.get('username')}")
                # 若登录框当前存在，关闭它
                if self.login_dialog:
                    self.login_dialog.close()
                # 刷新菜单以反映登录状态
                self.update_menu()
                
                # 自动登录成功后：启动消息轮询并清空相关缓存
                try:
                    if hasattr(self, 'friend_name_cache') and isinstance(self.friend_name_cache, dict):
                        self.friend_name_cache.clear()
                    if hasattr(self, 'notified_senders') and isinstance(self.notified_senders, set):
                        self.notified_senders.clear()
                    if hasattr(self, 'message_check_timer') and self.message_check_timer is not None:
                        self.message_check_timer.start()
                    # 立即检查一次，提升首次提醒的及时性
                    if hasattr(self, 'check_new_messages'):
                        self.check_new_messages()
                except Exception as e:
                    print(f"自动登录后启动消息轮询失败: {e}")
            else:
                # 恢复失败则清理会话文件，避免下次反复失败
                self.clear_remember_session()
                print(f"自动登录失败: {result.get('message')}")
        except Exception as e:
            print(f"读取自动登录信息失败: {e}")

    # ===== 新增：好友消息提醒相关 =====
    def init_message_checker(self):
        """初始化并启动好友消息轮询（登录后自动启动）"""
        try:
            if not self.message_check_timer:
                self.message_check_timer = QTimer(self)
                # 默认每5秒检查一次
                self.message_check_timer.setInterval(5000)
                self.message_check_timer.timeout.connect(self.check_new_messages)
            # 用户已登录时才启动
            if user_auth.get_current_user():
                self.message_check_timer.start()
        except Exception as e:
            print(f"初始化消息轮询失败: {e}")

    def _get_friend_name(self, friend_id: str) -> str:
        """根据好友ID获取用户名（带缓存）"""
        try:
            if friend_id in self.friend_name_cache:
                return self.friend_name_cache[friend_id]
            # 拉取好友列表并缓存
            result = friends_manager.get_friends_list()
            if result.get('success'):
                friends = result.get('friends', [])
                for f in friends:
                    fid = f.get('id') or f.get('user_id') or f.get('friend_id')
                    if fid:
                        self.friend_name_cache[fid] = f.get('username') or f.get('name') or fid
                if friend_id in self.friend_name_cache:
                    return self.friend_name_cache[friend_id]
        except Exception as e:
            print(f"获取好友昵称失败: {e}")
        # 兜底返回ID
        return friend_id

    def show_friend_message_bubble(self, friend_id: str, friend_username: str, message_content: str):
        """显示好友消息气泡，按钮为“回复”，点击后打开聊天窗口"""
        try:
            # 将宠物名字替换为好友昵称
            display_content = f"{friend_username}：\n    {message_content}" if friend_username else message_content
            # 创建漫画气泡对话框（按钮文案为“回复”）
            bubble = SpeechBubbleDialog("", display_content, self, button_text="回复")

            # 计算展示位置（宠物正上方）——与提醒一致
            pet_pos = self.pos()
            rect = self._available_rect()

            bubble_w, bubble_h = bubble.width(), bubble.height()

            # 计算宠物头顶中央位置
            pet_center_x = pet_pos.x() + self.width() // 2
            pet_top_y = pet_pos.y()

            # 气泡位置：以宠物头顶中央为锚点，气泡在正上方
            bx = pet_center_x - bubble_w // 2
            by = pet_top_y - bubble_h - 5

            # 边界处理
            if bx < rect.left() + 10:
                bx = rect.left() + 10
            elif bx + bubble_w > rect.right() - 10:
                bx = rect.right() - bubble_w - 10
            if by < rect.top() + 10:
                by = pet_pos.y() + self.height() + 5
            if by + bubble_h > rect.bottom() - 10:
                by = rect.bottom() - bubble_h - 10

            bubble.move(bx, by)
            res = bubble.exec_()
            if res == QDialog.Accepted:
                # 打开聊天窗口进行回复
                self.on_chat_requested(friend_id, friend_username)
        except Exception as e:
            print(f"show_friend_message_bubble error: {e}")

    def check_new_messages(self):
        """轮询检查是否有新的未读消息，如有则弹出气泡提醒"""
        try:
            current_user = user_auth.get_current_user()
            if not current_user:
                return
            user_id = current_user.get('id')
            if not user_id:
                return
            # 查询最近会话，包含未读数
            conversations = chat_db.get_recent_conversations(user_id, limit=20)
            # 遍历所有会话，找出未读且对方最近发来的消息
            for conv in conversations:
                other_id = conv.get('other_user_id')
                unread = int(conv.get('unread_count') or 0)
                is_last_sent = bool(conv.get('is_last_sent'))  # True表示我发的
                last_message = conv.get('last_message') or ""
                if not other_id or unread <= 0 or is_last_sent:
                    # 如果之前记录了通知但现在未读为0，则清理记录
                    if other_id in self.notified_senders and unread <= 0:
                        self.notified_senders.discard(other_id)
                    continue
                # 避免重复弹相同发送者的未读提醒（直到其未读清零）
                if other_id in self.notified_senders:
                    continue
                # 获取好友昵称
                friend_name = self._get_friend_name(other_id)
                # 弹出气泡
                self.show_friend_message_bubble(other_id, friend_name, last_message)
                # 标记为已通知，避免短时间重复打扰
                self.notified_senders.add(other_id)
                # 一次仅弹一个，避免堆叠
                break
        except Exception as e:
            print(f"check_new_messages error: {e}")