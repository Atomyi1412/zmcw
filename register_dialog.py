#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
注册对话框
提供用户注册界面和功能
"""

from typing import Optional
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QFrame, QProgressBar
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QColor
from user_auth import user_auth
from async_worker import RegisterWorker, task_manager

class RegisterDialog(QDialog):
    """注册对话框类"""
    
    # 信号定义
    register_success = pyqtSignal(dict)  # 注册成功信号，传递用户信息
    switch_to_login = pyqtSignal()  # 切换到登录界面信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.validation_timer = QTimer()
        self.validation_timer.setSingleShot(True)
        self.validation_timer.timeout.connect(self.validate_form)
        self.init_ui()
        self.setup_connections()
    
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle('用户注册')
        # 使用最小尺寸以适配不同DPI与字体度量
        self.setMinimumSize(440, 600)
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

        # 设置窗口样式（与登录界面保持一致）
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
            /* 使用动态属性 state 标识校验状态 */
            QLineEdit[state="error"] {
                border-color: #e74c3c;
            }
            QLineEdit[state="success"] {
                border-color: #27ae60;
            }
            QPushButton {
                padding: 12px 24px;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                min-height: 16px;
            }
            QPushButton#registerBtn {
                background-color: #4CAF50;
                color: white;
            }
            QPushButton#registerBtn:hover {
                background-color: #45a049;
            }
            QPushButton#registerBtn:pressed {
                background-color: #3d8b40;
            }
            QPushButton#registerBtn:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            QPushButton#loginBtn {
                background-color: transparent;
                color: #4CAF50;
            }
            QPushButton#loginBtn:hover {
                color: #45a049;
            }
            QProgressBar {
                border: 1px solid #ddd;
                border-radius: 3px;
                text-align: center;
                font-size: 10px;
                height: 18px;
            }
            QProgressBar::chunk {
                border-radius: 2px;
            }
        """)
        
        # 主布局（与登录界面保持一致的间距）
        main_layout = QVBoxLayout()
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(24, 24, 24, 24)
        
        # 标题
        title_label = QLabel('注册桌面宠物账户')
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
        username_label = QLabel('用户名 (3-20位字符):')
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('请输入用户名')
        self.username_status = QLabel('')
        self.username_status.setStyleSheet("font-size: 10px; margin-top: 2px;")
        form_layout.addWidget(username_label)
        form_layout.addWidget(self.username_input)
        form_layout.addWidget(self.username_status)
        
        # 邮箱输入（可选）
        email_label = QLabel('邮箱 (可选):')
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText('请输入邮箱地址')
        form_layout.addWidget(email_label)
        form_layout.addWidget(self.email_input)
        
        # 密码输入
        password_label = QLabel('密码 (5-20位，包含字母和数字):')
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('请输入密码')
        self.password_input.setEchoMode(QLineEdit.Password)
        
        # 密码强度指示器
        strength_layout = QHBoxLayout()
        strength_layout.setSpacing(5)
        self.password_strength = QProgressBar()
        self.password_strength.setRange(0, 100)
        self.password_strength.setValue(0)
        self.password_strength.setFixedHeight(18)
        self.strength_label = QLabel('密码强度: 无')
        self.strength_label.setStyleSheet("font-size: 10px; color: #666;")
        strength_layout.addWidget(self.password_strength)
        strength_layout.addWidget(self.strength_label)
        
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password_input)
        form_layout.addLayout(strength_layout)
        
        # 确认密码输入
        confirm_label = QLabel('确认密码:')
        self.confirm_input = QLineEdit()
        self.confirm_input.setPlaceholderText('请再次输入密码')
        self.confirm_input.setEchoMode(QLineEdit.Password)
        self.confirm_status = QLabel('')
        self.confirm_status.setStyleSheet("font-size: 10px; margin-top: 2px;")
        form_layout.addWidget(confirm_label)
        form_layout.addWidget(self.confirm_input)
        form_layout.addWidget(self.confirm_status)
        
        main_layout.addWidget(form_frame)
        
        # 按钮区域（与登录界面保持一致）
        button_layout = QVBoxLayout()
        button_layout.setSpacing(8)
        
        # 注册按钮
        self.register_btn = QPushButton('注册')
        self.register_btn.setObjectName('registerBtn')
        self.register_btn.setFixedHeight(40)
        self.register_btn.setEnabled(False)
        button_layout.addWidget(self.register_btn)
        
        # 登录链接
        login_layout = QHBoxLayout()
        login_layout.addStretch()
        
        has_account_label = QLabel('已有账户？')
        has_account_label.setStyleSheet("color: #666666;")
        login_layout.addWidget(has_account_label)
        
        self.login_btn = QPushButton('立即登录')
        self.login_btn.setObjectName('loginBtn')
        login_layout.addWidget(self.login_btn)
        
        login_layout.addStretch()
        button_layout.addLayout(login_layout)
        
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
        self.register_btn.clicked.connect(self.handle_register)
        self.login_btn.clicked.connect(self.handle_login)
        
        # 实时验证
        self.username_input.textChanged.connect(self.on_input_changed)
        self.password_input.textChanged.connect(self.on_input_changed)
        self.confirm_input.textChanged.connect(self.on_input_changed)
        
        # 回车键处理
        self.username_input.returnPressed.connect(self.handle_register)
        self.password_input.returnPressed.connect(self.handle_register)
        self.confirm_input.returnPressed.connect(self.handle_register)
    
    def on_input_changed(self):
        """输入内容改变时的处理"""
        # 延迟验证，避免频繁验证
        self.validation_timer.stop()
        self.validation_timer.start(500)  # 500ms后验证
    
    def _set_input_state(self, widget: QLineEdit, state: Optional[str]):
        """设置输入框校验状态并刷新样式。"""
        if state:
            widget.setProperty('state', state)
        else:
            widget.setProperty('state', None)
        # 强制刷新样式
        widget.style().unpolish(widget)
        widget.style().polish(widget)
        widget.update()
    
    def validate_form(self):
        """验证表单"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        confirm_password = self.confirm_input.text()
        
        is_valid = True
        
        # 验证用户名
        if not username:
            self.username_status.setText('')
            self._set_input_state(self.username_input, None)
        elif len(username) < 3 or len(username) > 20:
            self.username_status.setText('用户名长度应为3-20位字符')
            self.username_status.setStyleSheet("color: #e74c3c; font-size: 10px;")
            self._set_input_state(self.username_input, 'error')
            is_valid = False
        elif not username.replace('_', '').isalnum():
            self.username_status.setText('用户名只能包含字母、数字和下划线')
            self.username_status.setStyleSheet("color: #e74c3c; font-size: 10px;")
            self._set_input_state(self.username_input, 'error')
            is_valid = False
        else:
            self.username_status.setText('用户名格式正确')
            self.username_status.setStyleSheet("color: #27ae60; font-size: 10px;")
            self._set_input_state(self.username_input, 'success')
        
        # 验证密码强度
        if password:
            strength = self._calculate_password_strength(password)
            self.password_strength.setValue(strength)
            
            if strength < 30:
                self.strength_label.setText('密码强度: 弱')
                self.strength_label.setStyleSheet("color: #e74c3c; font-size: 10px;")
                self.password_strength.setStyleSheet("QProgressBar::chunk { background-color: #e74c3c; }")
                self._set_input_state(self.password_input, 'error')
                is_valid = False
            elif strength < 70:
                self.strength_label.setText('密码强度: 中等')
                self.strength_label.setStyleSheet("color: #f39c12; font-size: 10px;")
                self.password_strength.setStyleSheet("QProgressBar::chunk { background-color: #f39c12; }")
                self._set_input_state(self.password_input, None)
            else:
                self.strength_label.setText('密码强度: 强')
                self.strength_label.setStyleSheet("color: #27ae60; font-size: 10px;")
                self.password_strength.setStyleSheet("QProgressBar::chunk { background-color: #27ae60; }")
                self._set_input_state(self.password_input, 'success')
        else:
            self.password_strength.setValue(0)
            self.strength_label.setText('密码强度: 无')
            self.strength_label.setStyleSheet("color: #666; font-size: 10px;")
            self._set_input_state(self.password_input, None)
        
        # 验证确认密码
        if not confirm_password:
            self.confirm_status.setText('')
            self._set_input_state(self.confirm_input, None)
        elif password != confirm_password:
            self.confirm_status.setText('两次输入的密码不一致')
            self.confirm_status.setStyleSheet("color: #e74c3c; font-size: 10px;")
            self._set_input_state(self.confirm_input, 'error')
            is_valid = False
        else:
            self.confirm_status.setText('密码确认正确')
            self.confirm_status.setStyleSheet("color: #27ae60; font-size: 10px;")
            self._set_input_state(self.confirm_input, 'success')
        
        # 更新注册按钮状态
        self.register_btn.setEnabled(is_valid and len(username) >= 3 and len(password) >= 5)
    
    def _calculate_password_strength(self, password: str) -> int:
        """计算密码强度"""
        if len(password) < 5:
            return 0
        
        strength = 0
        
        # 长度加分
        if len(password) >= 8:
            strength += 25
        elif len(password) >= 6:
            strength += 15
        else:
            strength += 5
        
        # 包含小写字母
        if any(c.islower() for c in password):
            strength += 15
        
        # 包含大写字母
        if any(c.isupper() for c in password):
            strength += 15
        
        # 包含数字
        if any(c.isdigit() for c in password):
            strength += 15
        
        # 包含特殊字符
        if any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
            strength += 20
        
        # 字符种类多样性
        char_types = 0
        if any(c.islower() for c in password):
            char_types += 1
        if any(c.isupper() for c in password):
            char_types += 1
        if any(c.isdigit() for c in password):
            char_types += 1
        if any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
            char_types += 1
        
        if char_types >= 3:
            strength += 10
        
        return min(strength, 100)
    
    def handle_register(self):
        """处理注册"""
        if not self.register_btn.isEnabled():
            return
        
        username = self.username_input.text().strip()
        email = self.email_input.text().strip() or None
        password = self.password_input.text()
        
        # 开始异步注册
        self.start_async_register(username, password, email)
    
    def start_async_register(self, username: str, password: str, email: str = None):
        """开始异步注册"""
        # 禁用所有输入控件
        self.set_loading_state(True)
        
        # 创建注册工作线程
        self.register_worker = task_manager.run_task(RegisterWorker, username, password, email)
        
        # 连接信号
        self.register_worker.progress.connect(self.on_register_progress)
        self.register_worker.finished.connect(self.on_register_finished)
        self.register_worker.error.connect(self.on_register_error)
    
    def set_loading_state(self, loading: bool):
        """设置加载状态"""
        # 禁用/启用输入控件
        self.username_input.setEnabled(not loading)
        self.email_input.setEnabled(not loading)
        self.password_input.setEnabled(not loading)
        self.confirm_input.setEnabled(not loading)
        self.login_btn.setEnabled(not loading)
        
        if loading:
            # 显示加载状态
            self.register_btn.setEnabled(False)
            self.register_btn.setText('注册中...')
            
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
            self.register_btn.setEnabled(True)
            self.register_btn.setText('注册')
            
            # 隐藏进度条
            if hasattr(self, 'progress_bar'):
                self.progress_bar.hide()
    
    def on_register_progress(self, message: str):
        """注册进度更新"""
        self.show_status(message, is_error=False)
    
    def on_register_finished(self, result: dict):
        """注册完成"""
        self.set_loading_state(False)
        
        if result.get('success'):
            self.show_status('注册成功！', is_error=False)
            
            # 延迟一下再关闭，让用户看到成功消息
            QTimer.singleShot(500, lambda: (
                self.register_success.emit(result),
                self.accept()
            ))
        else:
            self.show_status(result.get('message', '注册失败'), is_error=True)
            # 重新聚焦到用户名输入框
            self.username_input.setFocus()
    
    def on_register_error(self, error_message: str):
        """注册错误"""
        self.set_loading_state(False)
        self.show_status(error_message, is_error=True)
        # 重新聚焦到用户名输入框
        self.username_input.setFocus()
    
    def handle_login(self):
        """处理登录按钮点击"""
        self.switch_to_login.emit()
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
        self.email_input.clear()
        self.password_input.clear()
        self.confirm_input.clear()
        self.username_status.clear()
        self.confirm_status.clear()
        self.password_strength.setValue(0)
        self.strength_label.setText('密码强度: 无')
        self.strength_label.setStyleSheet("color: #666; font-size: 10px;")
        self.status_label.clear()
        self.username_input.setFocus()
        
        # 清除输入框状态
        self._set_input_state(self.username_input, None)
        self._set_input_state(self.password_input, None)
        self._set_input_state(self.confirm_input, None)
    
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