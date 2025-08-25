#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
登录对话框
提供用户登录界面和功能
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QCheckBox, QFrame, QProgressBar
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QColor
from user_auth import user_auth
from async_worker import LoginWorker, task_manager

class LoginDialog(QDialog):
    """登录对话框类"""
    
    # 信号定义
    login_success = pyqtSignal(dict)  # 登录成功信号，传递用户信息
    switch_to_register = pyqtSignal()  # 切换到注册界面信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.setup_connections()

    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle('用户登录')
        # self.setFixedSize(420, 400)
        # 改为设置最小尺寸，避免在高DPI/不同字体度量下被压缩导致重叠
        self.setMinimumSize(440, 500)
        self.setModal(True)
    
        # 为对话框启用背景填充，避免 macOS 上出现残影/叠印
        self.setAutoFillBackground(True)
        pal = self.palette()
        pal.setColor(self.backgroundRole(), QColor('#ffffff'))
        self.setPalette(pal)
        
        # Mac平台特殊处理
        import platform
        if platform.system() == 'Darwin':
            self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
            wa_attr = getattr(Qt, 'WA_MacShowFocusRect', None)
            if wa_attr is not None:
                self.setAttribute(wa_attr, False)
        
        # 设置窗口样式（避免为顶层 QDialog 设背景，仅限定子控件）
        self.setStyleSheet("""
            QLabel {
                color: #333333;
            }
            QLineEdit {
                padding: 8px 12px;
                border: 2px solid #e9ecef;
                border-radius: 6px;
                background-color: white;
                /* 保证文字与占位符在 macOS/高DPI 下不会被裁剪 */
                min-height: 36px;
            }
            QLineEdit:focus {
                border-color: #4CAF50;
                outline: none;
            }
            QPushButton {
                padding: 12px 24px;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                min-height: 16px;
            }
            QPushButton#loginBtn {
                background-color: #4CAF50;
                color: white;
            }
            QPushButton#loginBtn:hover {
                background-color: #45a049;
            }
            QPushButton#loginBtn:pressed {
                background-color: #3d8b40;
            }
            QPushButton#registerBtn {
                background-color: transparent;
                color: #4CAF50;
            }
            QPushButton#registerBtn:hover {
                color: #45a049;
            }
            QCheckBox {
                color: #666666;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid #ddd;
                border-radius: 3px;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #4CAF50;
                border-radius: 3px;
                background-color: #4CAF50;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xIDQuNUw0LjUgOEwxMSAxIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
            }
        """)

        # 主布局
        main_layout = QVBoxLayout()
        # 降低间距与边距，避免垂直空间不足
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(24, 24, 24, 24)
        # 防止窗口被调整得比内容建议尺寸还小
        # 移除 QLayout.SetMinimumSize 调用以避免 linter 报错
        # main_layout.setSizeConstraint(QLayout.SetMinimumSize)
        
        # 标题
        title_label = QLabel('登录到桌面宠物')
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 6px;")
        main_layout.addWidget(title_label)
        
        # 表单区域
        form_frame = QFrame()
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(12)
        form_layout.setContentsMargins(8, 8, 8, 8)
        
        # 用户名输入
        username_label = QLabel('用户名:')
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('请输入用户名')
        form_layout.addWidget(username_label)
        form_layout.addWidget(self.username_input)
        
        # 密码输入
        password_label = QLabel('密码:')
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('请输入密码')
        self.password_input.setEchoMode(QLineEdit.Password)
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password_input)
        
        # 记住我选项
        self.remember_checkbox = QCheckBox('记住我')
        form_layout.addWidget(self.remember_checkbox)
        
        main_layout.addWidget(form_frame)
        
        # 按钮区域
        button_layout = QVBoxLayout()
        button_layout.setSpacing(8)
        
        # 登录按钮
        self.login_btn = QPushButton('登录')
        self.login_btn.setObjectName('loginBtn')
        self.login_btn.setFixedHeight(40)
        button_layout.addWidget(self.login_btn)
        
        # 注册链接
        register_layout = QHBoxLayout()
        register_layout.addStretch()
        
        no_account_label = QLabel('还没有账户？')
        no_account_label.setStyleSheet("color: #666666;")
        register_layout.addWidget(no_account_label)
        
        self.register_btn = QPushButton('立即注册')
        self.register_btn.setObjectName('registerBtn')
        register_layout.addWidget(self.register_btn)
        
        register_layout.addStretch()
        button_layout.addLayout(register_layout)
        
        main_layout.addLayout(button_layout)
        
        # 状态标签
        self.status_label = QLabel('')
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #e74c3c;")
        main_layout.addWidget(self.status_label)
        
        self.setLayout(main_layout)
        # 依据内容调整窗口大小，保证控件不被压缩
        self.adjustSize()

    def setup_connections(self):
        """设置信号连接"""
        self.login_btn.clicked.connect(self.handle_login)
        self.register_btn.clicked.connect(self.handle_register)
        self.username_input.returnPressed.connect(self.handle_login)
        self.password_input.returnPressed.connect(self.handle_login)
    
    def handle_login(self):
        """处理登录"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        # 验证输入
        if not username:
            self.show_status('请输入用户名', is_error=True)
            self.username_input.setFocus()
            return
        
        if not password:
            self.show_status('请输入密码', is_error=True)
            self.password_input.setFocus()
            return
        
        # 开始异步登录
        self.start_async_login(username, password)
    
    def start_async_login(self, username: str, password: str):
        """开始异步登录"""
        # 禁用所有输入控件
        self.set_loading_state(True)
        
        # 创建登录工作线程
        self.login_worker = task_manager.run_task(LoginWorker, username, password)
        
        # 连接信号
        self.login_worker.progress.connect(self.on_login_progress)
        self.login_worker.finished.connect(self.on_login_finished)
        self.login_worker.error.connect(self.on_login_error)
    
    def set_loading_state(self, loading: bool):
        """设置加载状态"""
        # 禁用/启用输入控件
        self.username_input.setEnabled(not loading)
        self.password_input.setEnabled(not loading)
        self.remember_checkbox.setEnabled(not loading)
        self.register_btn.setEnabled(not loading)
        
        if loading:
            # 显示加载状态
            self.login_btn.setEnabled(False)
            self.login_btn.setText('登录中...')
            
            # 显示进度条
            if not hasattr(self, 'progress_bar'):
                self.progress_bar = QProgressBar()
                self.progress_bar.setRange(0, 0)  # 无限进度条
                self.progress_bar.setFixedHeight(4)
                self.progress_bar.setStyleSheet("""
                    QProgressBar {
                        border: none;
                        background-color: #f0f0f0;
                        border-radius: 2px;
                    }
                    QProgressBar::chunk {
                        background-color: #4CAF50;
                        border-radius: 2px;
                    }
                """)
                # 插入到状态标签上方
                layout = self.layout()
                layout.insertWidget(layout.count() - 1, self.progress_bar)
            
            self.progress_bar.show()
        else:
            # 恢复正常状态
            self.login_btn.setEnabled(True)
            self.login_btn.setText('登录')
            
            # 隐藏进度条
            if hasattr(self, 'progress_bar'):
                self.progress_bar.hide()
    
    def on_login_progress(self, message: str):
        """登录进度更新"""
        self.show_status(message, is_error=False)
    
    def on_login_finished(self, result: dict):
        """登录完成"""
        self.set_loading_state(False)
        
        if result.get('success'):
            self.show_status('登录成功！', is_error=False)
            
            # 清除缓存，确保数据一致性
            from cache_manager import user_cache
            user_cache.clear_all()
            
            # 发送登录成功信号（携带是否记住我标记）
            result['remember_me'] = self.remember_checkbox.isChecked()
            self.login_success.emit(result)
            
            # 延迟一下再关闭，让用户看到成功消息
            QTimer.singleShot(500, self.close)
        else:
            self.show_status(result.get('message', '登录失败'), is_error=True)
            # 重新聚焦到用户名输入框
            self.username_input.setFocus()
    
    def on_login_error(self, error_message: str):
        """登录错误"""
        self.set_loading_state(False)
        self.show_status(error_message, is_error=True)
        # 重新聚焦到用户名输入框
        self.username_input.setFocus()
    
    def handle_register(self):
        """处理注册按钮点击"""
        self.switch_to_register.emit()
        self.close()
    
    def show_status(self, message: str, is_error: bool = False):
        """显示状态信息
        
        Args:
            message: 状态消息
            is_error: 是否为错误信息
        """
        self.status_label.setText(message)
        if is_error:
            self.status_label.setStyleSheet("color: #e74c3c; font-size: 11px;")
        else:
            self.status_label.setStyleSheet("color: #27ae60; font-size: 11px;")
    
    def clear_form(self):
        """清空表单"""
        self.username_input.clear()
        self.password_input.clear()
        self.remember_checkbox.setChecked(False)
        self.status_label.clear()
        self.username_input.setFocus()
    
    def set_username(self, username: str):
        """设置用户名
        
        Args:
            username: 用户名
        """
        self.username_input.setText(username)
        self.password_input.setFocus()
    
    def showEvent(self, a0):
        """对话框显示时的事件"""
        super().showEvent(a0)
        self.username_input.setFocus()
        self.clear_form()