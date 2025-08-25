#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
好友管理对话框
提供好友列表、添加好友、处理好友请求等界面
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QListWidget, QListWidgetItem, QTabWidget,
    QWidget, QMessageBox, QFrame, QScrollArea, QTextEdit, QProgressBar, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPixmap, QPainter, QColor
from friends_manager import friends_manager
from user_auth import user_auth
from datetime import datetime
from async_worker import FriendsListWorker, FriendRequestsWorker, SearchUsersWorker, task_manager

class FriendItemWidget(QWidget):
    """好友列表项组件"""
    
    chat_requested = pyqtSignal(str, str)  # 聊天请求信号(friend_id, username)
    remove_requested = pyqtSignal(str, str)  # 删除好友信号(friend_id, username)
    
    def __init__(self, friend_data, parent=None):
        super().__init__(parent)
        self.friend_data = friend_data
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 8, 10, 8)
        
        # 好友信息
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        
        # 用户名
        username_label = QLabel(self.friend_data['username'])
        username_label.setStyleSheet("font-weight: bold; font-size: 13px; color: #2c3e50;")
        info_layout.addWidget(username_label)
        
        # 在线状态
        status_text = "在线" if self.friend_data['is_online'] else "离线"
        status_color = "#27ae60" if self.friend_data['is_online'] else "#95a5a6"
        
        if not self.friend_data['is_online'] and self.friend_data['last_active']:
            try:
                last_active = datetime.fromisoformat(self.friend_data['last_active'].replace('Z', '+00:00'))
                now = datetime.now(last_active.tzinfo)
                diff = now - last_active
                
                if diff.days > 0:
                    status_text = f"离线 {diff.days}天前"
                elif diff.seconds > 3600:
                    hours = diff.seconds // 3600
                    status_text = f"离线 {hours}小时前"
                elif diff.seconds > 60:
                    minutes = diff.seconds // 60
                    status_text = f"离线 {minutes}分钟前"
                else:
                    status_text = "刚刚离线"
            except:
                status_text = "离线"
        
        status_label = QLabel(status_text)
        status_label.setStyleSheet(f"font-size: 11px; color: {status_color};")
        info_layout.addWidget(status_label)
        
        layout.addLayout(info_layout)
        layout.addStretch()
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(5)
        
        # 聊天按钮
        chat_btn = QPushButton("聊天")
        chat_btn.setFixedSize(50, 25)
        chat_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 3px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        chat_btn.clicked.connect(self.on_chat_clicked)
        button_layout.addWidget(chat_btn)
        
        # 删除按钮
        remove_btn = QPushButton("删除")
        remove_btn.setFixedSize(50, 25)
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 3px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        remove_btn.clicked.connect(self.on_remove_clicked)
        button_layout.addWidget(remove_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # 设置样式
        self.setStyleSheet("""
            FriendItemWidget {
                background-color: white;
                border: 1px solid #e9ecef;
                border-radius: 6px;
                margin: 2px;
            }
            FriendItemWidget:hover {
                background-color: #f8f9fa;
                border-color: #4CAF50;
            }
        """)
        self.setFixedHeight(60)
    
    def on_chat_clicked(self):
        """聊天按钮点击"""
        self.chat_requested.emit(self.friend_data['id'], self.friend_data['username'])
    
    def on_remove_clicked(self):
        """删除按钮点击"""
        self.remove_requested.emit(self.friend_data['id'], self.friend_data['username'])

class FriendRequestWidget(QWidget):
    """好友请求列表项组件"""
    
    request_responded = pyqtSignal(str, str)  # 请求回应信号(request_id, action)
    
    def __init__(self, request_data, parent=None):
        super().__init__(parent)
        self.request_data = request_data
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 8, 10, 8)
        
        # 请求信息
        info_layout = QHBoxLayout()
        
        # 发送者信息
        sender_label = QLabel(f"来自: {self.request_data['sender_username']}")
        sender_label.setStyleSheet("font-weight: bold; font-size: 12px; color: #2c3e50;")
        info_layout.addWidget(sender_label)
        
        info_layout.addStretch()
        
        # 时间
        try:
            created_time = datetime.fromisoformat(self.request_data['created_at'].replace('Z', '+00:00'))
            time_text = created_time.strftime("%m-%d %H:%M")
        except:
            time_text = "未知时间"
        
        time_label = QLabel(time_text)
        time_label.setStyleSheet("font-size: 10px; color: #95a5a6;")
        info_layout.addWidget(time_label)
        
        layout.addLayout(info_layout)
        
        # 请求消息
        if self.request_data['message']:
            message_label = QLabel(self.request_data['message'])
            message_label.setStyleSheet("font-size: 11px; color: #666666; margin: 5px 0;")
            message_label.setWordWrap(True)
            message_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            layout.addWidget(message_label)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # 拒绝按钮
        reject_btn = QPushButton("拒绝")
        reject_btn.setFixedSize(60, 28)
        reject_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        reject_btn.clicked.connect(lambda: self.request_responded.emit(self.request_data['id'], 'reject'))
        button_layout.addWidget(reject_btn)
        
        # 接受按钮
        accept_btn = QPushButton("接受")
        accept_btn.setFixedSize(60, 28)
        accept_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        accept_btn.clicked.connect(lambda: self.request_responded.emit(self.request_data['id'], 'accept'))
        button_layout.addWidget(accept_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # 设置样式
        self.setStyleSheet("""
            FriendRequestWidget {
                background-color: #fff3cd;
                border: 1px solid #ffeaa7;
                border-radius: 6px;
                margin: 2px;
            }
        """)
        
        # 关键：取消固定高度，改为根据内容自适应
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        # self.setFixedHeight(80)

class AddFriendDialog(QDialog):
    """添加好友对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.setup_connections()
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle('添加好友')
        self.setFixedSize(400, 300)
        self.setModal(True)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 搜索区域
        search_layout = QHBoxLayout()
        
        search_label = QLabel('搜索用户:')
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('输入用户名搜索')
        self.search_btn = QPushButton('搜索')
        self.search_btn.setFixedWidth(60)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_btn)
        
        layout.addLayout(search_layout)
        
        # 搜索结果
        self.result_list = QListWidget()
        self.result_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:hover {
                background-color: #f5f5f5;
            }
        """)
        layout.addWidget(self.result_list)
        
        # 状态标签
        self.status_label = QLabel('')
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #666; font-size: 11px;")
        layout.addWidget(self.status_label)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.close_btn = QPushButton('关闭')
        self.close_btn.clicked.connect(self.close)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def setup_connections(self):
        """设置信号连接"""
        self.search_btn.clicked.connect(self.search_users)
        self.search_input.returnPressed.connect(self.search_users)
        self.result_list.itemDoubleClicked.connect(self.send_friend_request)
    
    def search_users(self):
        """搜索用户"""
        query = self.search_input.text().strip()
        if not query:
            self.status_label.setText('请输入搜索关键词')
            return
        
        self.search_btn.setEnabled(False)
        self.search_btn.setText('搜索中...')
        self.status_label.setText('正在搜索...')
        
        try:
            result = friends_manager.search_users(query)
            
            self.result_list.clear()
            
            if result['success'] and result['users']:
                for user in result['users']:
                    item_text = f"{user['username']} - {user['last_active'][:10] if user['last_active'] else '未知'}"
                    item = QListWidgetItem(item_text)
                    item.setData(Qt.UserRole, user)
                    self.result_list.addItem(item)
                
                self.status_label.setText(f'找到 {len(result["users"])} 个用户，双击发送好友请求')
            else:
                self.status_label.setText('未找到匹配的用户')
        
        except Exception as e:
            self.status_label.setText(f'搜索失败: {str(e)}')
        
        finally:
            self.search_btn.setEnabled(True)
            self.search_btn.setText('搜索')
    
    def send_friend_request(self, item):
        """发送好友请求"""
        user_data = item.data(Qt.UserRole)
        if not user_data:
            return
        
        reply = QMessageBox.question(
            self, '确认添加好友', 
            f'确定要向 {user_data["username"]} 发送好友请求吗？',
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            result = friends_manager.send_friend_request(user_data['username'])
            
            if result['success']:
                QMessageBox.information(self, '成功', result['message'])
                self.close()
            else:
                QMessageBox.warning(self, '失败', result['message'])

class FriendsDialog(QDialog):
    """好友管理对话框"""
    
    chat_requested = pyqtSignal(str, str)  # 聊天请求信号(friend_id, username)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_user = user_auth.get_current_user()
        
        if not self.current_user:
            QMessageBox.warning(self, "错误", "请先登录")
            self.close()
            return
        
        # 初始化加载状态
        self.friends_loading = False
        self.requests_loading = False
        self.search_loading = False
        
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.init_ui()
        self.setup_connections()
        
        # 异步加载数据
        self.load_friends_list_async()
        self.load_friend_requests_async()
        
        # 每30秒刷新一次数据
        self.refresh_timer.start(30000)
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle('好友管理')
        self.setFixedSize(450, 500)
        self.setModal(False)
        
        # 设置样式
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
            QTabWidget::pane {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e9ecef;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 1px solid white;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        
        # 标题
        title_label = QLabel('好友管理')
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # 选项卡
        self.tab_widget = QTabWidget()
        
        # 好友列表选项卡
        self.friends_tab = QWidget()
        self.init_friends_tab()
        self.tab_widget.addTab(self.friends_tab, "好友列表")
        
        # 好友请求选项卡
        self.requests_tab = QWidget()
        self.init_requests_tab()
        self.tab_widget.addTab(self.requests_tab, "好友请求")
        
        layout.addWidget(self.tab_widget)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.add_friend_btn = QPushButton('添加好友')
        self.add_friend_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        button_layout.addWidget(self.add_friend_btn)
        
        button_layout.addStretch()
        
        self.refresh_btn = QPushButton('刷新')
        self.close_btn = QPushButton('关闭')
        
        button_layout.addWidget(self.refresh_btn)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def init_friends_tab(self):
        """初始化好友列表选项卡"""
        layout = QVBoxLayout()
        
        # 好友列表滚动区域
        self.friends_scroll = QScrollArea()
        self.friends_scroll.setWidgetResizable(True)
        self.friends_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        self.friends_container = QWidget()
        self.friends_layout = QVBoxLayout(self.friends_container)
        self.friends_layout.setSpacing(5)
        self.friends_layout.addStretch()
        
        self.friends_scroll.setWidget(self.friends_container)
        layout.addWidget(self.friends_scroll)
        
        self.friends_tab.setLayout(layout)
    
    def init_requests_tab(self):
        """初始化好友请求选项卡"""
        layout = QVBoxLayout()
        
        # 好友请求滚动区域
        self.requests_scroll = QScrollArea()
        self.requests_scroll.setWidgetResizable(True)
        self.requests_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        self.requests_container = QWidget()
        self.requests_layout = QVBoxLayout(self.requests_container)
        self.requests_layout.setSpacing(5)
        self.requests_layout.addStretch()
        
        self.requests_scroll.setWidget(self.requests_container)
        layout.addWidget(self.requests_scroll)
        
        self.requests_tab.setLayout(layout)
    
    def setup_connections(self):
        """设置信号连接"""
        self.add_friend_btn.clicked.connect(self.show_add_friend_dialog)
        self.refresh_btn.clicked.connect(self.refresh_data)
        self.close_btn.clicked.connect(self.close)
    
    def refresh_data(self):
        """刷新数据"""
        self.load_friends_list()
        self.load_friend_requests()
    
    def load_friends_list_async(self):
        """异步加载好友列表"""
        if self.friends_loading:
            return
        
        self.friends_loading = True
        self.set_friends_loading_state(True)
        
        # 创建好友列表工作线程
        self.friends_worker = task_manager.run_task(FriendsListWorker)
        
        # 连接信号
        self.friends_worker.progress.connect(self.on_friends_progress)
        self.friends_worker.finished.connect(self.on_friends_loaded)
        self.friends_worker.error.connect(self.on_friends_error)
    
    def set_friends_loading_state(self, loading: bool):
        """设置好友列表加载状态"""
        # 清空现有列表
        for i in reversed(range(self.friends_layout.count() - 1)):
            child = self.friends_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        if loading:
            # 显示加载提示
            if not hasattr(self, 'friends_loading_label'):
                self.friends_loading_label = QLabel('正在加载好友列表...')
                self.friends_loading_label.setAlignment(Qt.AlignCenter)
                self.friends_loading_label.setStyleSheet("color: #666666; font-size: 12px; padding: 20px;")
            
            self.friends_layout.insertWidget(self.friends_layout.count() - 1, self.friends_loading_label)
    
    def on_friends_progress(self, message: str):
        """好友列表加载进度"""
        if hasattr(self, 'friends_loading_label'):
            self.friends_loading_label.setText(message)
    
    def on_friends_loaded(self, result: dict):
        """好友列表加载完成"""
        self.friends_loading = False
        
        # 清空现有列表
        for i in reversed(range(self.friends_layout.count() - 1)):
            child = self.friends_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        if result.get('success'):
            friends = result.get('friends', [])
            
            if friends:
                for friend in friends:
                    friend_widget = FriendItemWidget(friend)
                    friend_widget.chat_requested.connect(self.on_chat_requested)
                    friend_widget.remove_requested.connect(self.on_remove_friend)
                    self.friends_layout.insertWidget(self.friends_layout.count() - 1, friend_widget)
            else:
                # 显示空状态
                empty_label = QLabel('暂无好友\n点击"添加好友"开始添加吧！')
                empty_label.setAlignment(Qt.AlignCenter)
                empty_label.setStyleSheet("color: #95a5a6; font-size: 12px; padding: 40px;")
                self.friends_layout.insertWidget(self.friends_layout.count() - 1, empty_label)
        else:
            QMessageBox.warning(self, "错误", f"加载好友列表失败: {result.get('message', '未知错误')}")
    
    def on_friends_error(self, error_message: str):
        """好友列表加载错误"""
        self.friends_loading = False
        
        # 清空现有列表
        for i in reversed(range(self.friends_layout.count() - 1)):
            child = self.friends_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # 显示错误状态
        error_label = QLabel('加载失败\n请检查网络连接后重试')
        error_label.setAlignment(Qt.AlignCenter)
        error_label.setStyleSheet("color: #e74c3c; font-size: 12px; padding: 40px;")
        self.friends_layout.insertWidget(self.friends_layout.count() - 1, error_label)
        
        QMessageBox.critical(self, "错误", f"加载好友列表时出错: {error_message}")
    
    def load_friends_list(self):
        """同步加载好友列表（保持兼容性）"""
        self.load_friends_list_async()
    
    def load_friend_requests_async(self):
        """异步加载好友请求"""
        if self.requests_loading:
            return
        
        self.requests_loading = True
        self.set_requests_loading_state(True)
        
        # 创建好友请求工作线程
        self.requests_worker = task_manager.run_task(FriendRequestsWorker)
        
        # 连接信号
        self.requests_worker.progress.connect(self.on_requests_progress)
        self.requests_worker.finished.connect(self.on_requests_loaded)
        self.requests_worker.error.connect(self.on_requests_error)
    
    def set_requests_loading_state(self, loading: bool):
        """设置好友请求加载状态"""
        # 清空现有列表
        for i in reversed(range(self.requests_layout.count() - 1)):
            child = self.requests_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        if loading:
            # 显示加载提示
            if not hasattr(self, 'requests_loading_label'):
                self.requests_loading_label = QLabel('正在加载好友请求...')
                self.requests_loading_label.setAlignment(Qt.AlignCenter)
                self.requests_loading_label.setStyleSheet("color: #666666; font-size: 12px; padding: 20px;")
            
            self.requests_layout.insertWidget(self.requests_layout.count() - 1, self.requests_loading_label)
    
    def on_requests_progress(self, message: str):
        """好友请求加载进度"""
        if hasattr(self, 'requests_loading_label'):
            self.requests_loading_label.setText(message)
    
    def on_requests_loaded(self, result: dict):
        """好友请求加载完成"""
        self.requests_loading = False
        
        # 清空现有列表
        for i in reversed(range(self.requests_layout.count() - 1)):
            child = self.requests_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        if result.get('success'):
            requests = result.get('requests', [])
            
            if requests:
                for request in requests:
                    request_widget = FriendRequestWidget(request)
                    request_widget.request_responded.connect(self.on_request_responded)
                    self.requests_layout.insertWidget(self.requests_layout.count() - 1, request_widget)
                
                # 更新选项卡标题显示未读数量
                count = len(requests)
                self.tab_widget.setTabText(1, f"好友请求 ({count})")
            else:
                # 显示空状态
                empty_label = QLabel('暂无好友请求')
                empty_label.setAlignment(Qt.AlignCenter)
                empty_label.setStyleSheet("color: #95a5a6; font-size: 12px; padding: 40px;")
                self.requests_layout.insertWidget(self.requests_layout.count() - 1, empty_label)
                
                # 重置选项卡标题
                self.tab_widget.setTabText(1, "好友请求")
        else:
            QMessageBox.warning(self, "错误", f"加载好友请求失败: {result.get('message', '未知错误')}")
    
    def on_requests_error(self, error_message: str):
        """好友请求加载错误"""
        self.requests_loading = False
        
        # 清空现有列表
        for i in reversed(range(self.requests_layout.count() - 1)):
            child = self.requests_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # 显示错误状态
        error_label = QLabel('加载失败\n请检查网络连接后重试')
        error_label.setAlignment(Qt.AlignCenter)
        error_label.setStyleSheet("color: #e74c3c; font-size: 12px; padding: 40px;")
        self.requests_layout.insertWidget(self.requests_layout.count() - 1, error_label)
        
        QMessageBox.critical(self, "错误", f"加载好友请求时出错: {error_message}")
    
    def load_friend_requests(self):
        """同步加载好友请求（保持兼容性）"""
        self.load_friend_requests_async()
    
    def show_add_friend_dialog(self):
        """显示添加好友对话框"""
        dialog = AddFriendDialog(self)
        dialog.setWindowModality(Qt.WindowModal)  # 仅阻塞本对话框，不阻塞整个应用
        dialog.exec_()
        # 刷新好友列表
        self.refresh_data()
    
    def on_chat_requested(self, friend_id, username):
        """处理聊天请求"""
        self.chat_requested.emit(friend_id, username)
    
    def on_remove_friend(self, friend_id, username):
        """处理删除好友"""
        reply = QMessageBox.question(
            self, '确认删除', 
            f'确定要删除好友 {username} 吗？',
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            result = friends_manager.remove_friend(friend_id)
            
            if result['success']:
                QMessageBox.information(self, '成功', result['message'])
                self.refresh_data()
            else:
                QMessageBox.warning(self, '失败', result['message'])
    
    def on_request_responded(self, request_id, action):
        """处理好友请求回应"""
        result = friends_manager.respond_to_friend_request(request_id, action)
        
        if result['success']:
            QMessageBox.information(self, '成功', result['message'])
            self.refresh_data()
        else:
            QMessageBox.warning(self, '失败', result['message'])
    
    def closeEvent(self, event):
        """关闭事件"""
        self.refresh_timer.stop()
        super().closeEvent(event)