#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
聊天窗口
提供好友间聊天界面和功能
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QTextEdit, QScrollArea, QWidget, QFrame,
    QMessageBox, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QThread, pyqtSlot
from PyQt5.QtGui import QFont, QTextCursor, QPalette
from datetime import datetime
from user_auth import user_auth
from chat_database import chat_db
from typing import Dict, Any, List

class MessageBubble(QFrame):
    """消息气泡组件"""
    
    def __init__(self, message_data: Dict[str, Any], is_sent: bool, parent=None):
        super().__init__(parent)
        self.message_data = message_data
        self.is_sent = is_sent
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(2)
        
        # 消息内容
        content_label = QLabel(self.message_data['content'])
        content_label.setWordWrap(True)
        content_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        content_label.setStyleSheet("""
            QLabel {
                padding: 8px 12px;
                border-radius: 12px;
                font-size: 12px;
                line-height: 1.4;
            }
        """)
        
        # 时间标签
        try:
            created_time = datetime.fromisoformat(self.message_data['created_at'])
            time_text = created_time.strftime("%H:%M")
        except:
            time_text = "未知"
        
        time_label = QLabel(time_text)
        time_label.setStyleSheet("font-size: 10px; color: #95a5a6;")
        
        if self.is_sent:
            # 发送的消息（右对齐，绿色）
            content_label.setStyleSheet(content_label.styleSheet() + """
                QLabel {
                    background-color: #4CAF50;
                    color: white;
                }
            """)
            time_label.setAlignment(Qt.AlignRight)
            layout.addWidget(content_label)
            layout.addWidget(time_label)
            layout.setAlignment(Qt.AlignRight)
        else:
            # 接收的消息（左对齐，白色）
            content_label.setStyleSheet(content_label.styleSheet() + """
                QLabel {
                    background-color: white;
                    color: #333333;
                    border: 1px solid #e9ecef;
                }
            """)
            time_label.setAlignment(Qt.AlignLeft)
            layout.addWidget(content_label)
            layout.addWidget(time_label)
            layout.setAlignment(Qt.AlignLeft)
        
        self.setLayout(layout)
        self.setStyleSheet("background: transparent;")
        
        # 设置最大宽度
        content_label.setMaximumWidth(300)

class ChatWindow(QDialog):
    """聊天窗口类"""
    
    def __init__(self, friend_id: str, friend_username: str, parent=None):
        super().__init__(parent)
        self.friend_id = friend_id
        self.friend_username = friend_username
        self.current_user = user_auth.get_current_user()
        
        if not self.current_user:
            QMessageBox.warning(self, "错误", "请先登录")
            self.close()
            return
        
        self.message_widgets = []
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.load_messages)
        
        self.init_ui()
        self.setup_connections()
        self.load_messages()
        
        # 标记消息为已读
        chat_db.mark_messages_as_read(self.friend_id, self.current_user['id'])
        
        # 每5秒刷新一次消息
        self.refresh_timer.start(5000)
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle(f'与 {self.friend_username} 聊天')
        self.setFixedSize(400, 500)
        self.setModal(False)  # 允许多个聊天窗口
        
        # 设置样式
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QLineEdit {
                padding: 8px 12px;
                border: 2px solid #e9ecef;
                border-radius: 20px;
                font-size: 12px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #4CAF50;
                outline: none;
            }
            QPushButton#sendBtn {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 18px;
                font-size: 12px;
                font-weight: bold;
                padding: 8px 16px;
            }
            QPushButton#sendBtn:hover {
                background-color: #45a049;
            }
            QPushButton#sendBtn:pressed {
                background-color: #3d8b40;
            }
            QPushButton#sendBtn:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 标题栏
        title_layout = QHBoxLayout()
        
        title_label = QLabel(f'与 {self.friend_username} 聊天')
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #2c3e50;")
        title_layout.addWidget(title_label)
        
        title_layout.addStretch()
        
        # 关闭按钮
        close_btn = QPushButton('×')
        close_btn.setFixedSize(25, 25)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        close_btn.clicked.connect(self.close)
        title_layout.addWidget(close_btn)
        
        layout.addLayout(title_layout)
        
        # 消息显示区域
        self.messages_scroll = QScrollArea()
        self.messages_scroll.setWidgetResizable(True)
        self.messages_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.messages_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.messages_container = QWidget()
        self.messages_layout = QVBoxLayout(self.messages_container)
        self.messages_layout.setSpacing(8)
        self.messages_layout.addStretch()
        
        self.messages_scroll.setWidget(self.messages_container)
        layout.addWidget(self.messages_scroll)
        
        # 输入区域
        input_layout = QHBoxLayout()
        input_layout.setSpacing(8)
        
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText('输入消息...')
        self.message_input.setFixedHeight(36)
        input_layout.addWidget(self.message_input)
        
        self.send_btn = QPushButton('发送')
        self.send_btn.setObjectName('sendBtn')
        self.send_btn.setFixedSize(60, 36)
        input_layout.addWidget(self.send_btn)
        
        layout.addLayout(input_layout)
        
        # 状态标签
        self.status_label = QLabel('')
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #95a5a6; font-size: 10px;")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
    
    def setup_connections(self):
        """设置信号连接"""
        self.send_btn.clicked.connect(self.send_message)
        self.message_input.returnPressed.connect(self.send_message)
        self.message_input.textChanged.connect(self.on_input_changed)
    
    def on_input_changed(self, text):
        """输入框内容改变"""
        self.send_btn.setEnabled(bool(text.strip()))
    
    def send_message(self):
        """发送消息"""
        content = self.message_input.text().strip()
        if not content:
            return
        
        # 禁用发送按钮
        self.send_btn.setEnabled(False)
        self.send_btn.setText('发送中...')
        
        try:
            # 保存到本地数据库
            message_id = chat_db.save_message(
                sender_id=self.current_user['id'],
                receiver_id=self.friend_id,
                content=content
            )
            
            if message_id:
                # 清空输入框
                self.message_input.clear()
                
                # 立即显示发送的消息
                message_data = {
                    'id': message_id,
                    'sender_id': self.current_user['id'],
                    'receiver_id': self.friend_id,
                    'content': content,
                    'created_at': datetime.now().isoformat(),
                    'is_read': False
                }
                
                self.add_message_bubble(message_data, is_sent=True)
                self.scroll_to_bottom()
                
                self.status_label.setText('消息已发送')
                QTimer.singleShot(2000, lambda: self.status_label.setText(''))
            else:
                self.status_label.setText('发送失败')
                QTimer.singleShot(2000, lambda: self.status_label.setText(''))
        
        except Exception as e:
            self.status_label.setText(f'发送失败: {str(e)}')
            QTimer.singleShot(3000, lambda: self.status_label.setText(''))
        
        finally:
            # 恢复发送按钮
            self.send_btn.setEnabled(True)
            self.send_btn.setText('发送')
            self.message_input.setFocus()
    
    def load_messages(self):
        """加载聊天记录"""
        try:
            messages = chat_db.get_conversation_history(
                self.current_user['id'], 
                self.friend_id, 
                limit=50
            )
            
            # 检查是否有新消息
            if len(messages) != len(self.message_widgets):
                self.refresh_messages(messages)
                
                # 标记新收到的消息为已读
                chat_db.mark_messages_as_read(self.friend_id, self.current_user['id'])
        
        except Exception as e:
            print(f"加载聊天记录失败: {e}")
    
    def refresh_messages(self, messages: List[Dict[str, Any]]):
        """刷新消息列表"""
        # 清空现有消息
        for widget in self.message_widgets:
            widget.setParent(None)
        self.message_widgets.clear()
        
        # 添加新消息
        for message in messages:
            is_sent = message['sender_id'] == self.current_user['id']
            self.add_message_bubble(message, is_sent)
        
        self.scroll_to_bottom()
    
    def add_message_bubble(self, message_data: Dict[str, Any], is_sent: bool):
        """添加消息气泡"""
        bubble = MessageBubble(message_data, is_sent)
        
        # 创建容器来控制对齐
        container = QWidget()
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        
        if is_sent:
            container_layout.addStretch()
            container_layout.addWidget(bubble)
        else:
            container_layout.addWidget(bubble)
            container_layout.addStretch()
        
        # 插入到消息列表中（在stretch之前）
        self.messages_layout.insertWidget(self.messages_layout.count() - 1, container)
        self.message_widgets.append(container)
    
    def scroll_to_bottom(self):
        """滚动到底部"""
        QTimer.singleShot(100, lambda: (
            self.messages_scroll.verticalScrollBar().setValue(
                self.messages_scroll.verticalScrollBar().maximum()
            )
        ))
    
    def closeEvent(self, event):
        """关闭事件"""
        self.refresh_timer.stop()
        super().closeEvent(event)
    
    def showEvent(self, event):
        """显示事件"""
        super().showEvent(event)
        self.message_input.setFocus()
        self.scroll_to_bottom()