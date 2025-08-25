#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
异步工作线程模块
提供后台处理网络请求和数据库操作的工作线程
"""

from PyQt5.QtCore import QThread, pyqtSignal, QObject
from typing import Dict, Any, Callable, Optional
import traceback
from cache_manager import user_cache

class AsyncWorker(QThread):
    """异步工作线程基类"""
    
    # 信号定义
    finished = pyqtSignal(dict)  # 完成信号，传递结果
    error = pyqtSignal(str)      # 错误信号，传递错误信息
    progress = pyqtSignal(str)   # 进度信号，传递进度信息
    
    def __init__(self, task_func: Callable, *args, **kwargs):
        """
        初始化异步工作线程
        
        Args:
            task_func: 要执行的任务函数
            *args: 任务函数的位置参数
            **kwargs: 任务函数的关键字参数
        """
        super().__init__()
        self.task_func = task_func
        self.args = args
        self.kwargs = kwargs
        self.result = None
    
    def run(self):
        """执行任务"""
        try:
            # 执行任务函数
            self.result = self.task_func(*self.args, **self.kwargs)
            
            # 发送完成信号
            if isinstance(self.result, dict):
                self.finished.emit(self.result)
            else:
                self.finished.emit({"success": True, "data": self.result})
                
        except Exception as e:
            # 发送错误信号
            error_msg = f"任务执行失败: {str(e)}"
            print(f"AsyncWorker error: {error_msg}")
            print(traceback.format_exc())
            self.error.emit(error_msg)
    
    def emit_progress(self, message: str):
        """发送进度信息"""
        self.progress.emit(message)

class LoginWorker(AsyncWorker):
    """登录工作线程"""
    
    def __init__(self, username: str, password: str):
        from user_auth import user_auth
        super().__init__(user_auth.login, username, password)
    
    def run(self):
        """执行登录任务"""
        try:
            self.progress.emit("正在验证用户信息...")
            
            # 执行登录
            result = self.task_func(*self.args, **self.kwargs)
            
            if result.get('success'):
                self.progress.emit("登录成功！")
            else:
                self.progress.emit("登录失败")
            
            self.finished.emit(result)
            
        except Exception as e:
            error_msg = f"登录失败: {str(e)}"
            print(f"LoginWorker error: {error_msg}")
            print(traceback.format_exc())
            self.error.emit(error_msg)

class RegisterWorker(AsyncWorker):
    """注册工作线程"""
    
    def __init__(self, username: str, password: str, email: str = None):
        from user_auth import user_auth
        super().__init__(user_auth.register, username, password, email)
    
    def run(self):
        """执行注册任务"""
        try:
            self.progress.emit("正在创建账户...")
            
            # 执行注册
            result = self.task_func(*self.args, **self.kwargs)
            
            if result.get('success'):
                self.progress.emit("注册成功！")
            else:
                self.progress.emit("注册失败")
            
            self.finished.emit(result)
            
        except Exception as e:
            error_msg = f"注册失败: {str(e)}"
            print(f"RegisterWorker error: {error_msg}")
            print(traceback.format_exc())
            self.error.emit(error_msg)

class LogoutWorker(AsyncWorker):
    """登出工作线程"""
    
    def __init__(self):
        from user_auth import user_auth
        super().__init__(user_auth.logout)
    
    def run(self):
        """执行登出任务"""
        try:
            self.progress.emit("正在登出...")
            
            # 执行登出
            result = self.task_func(*self.args, **self.kwargs)
            
            if result.get('success'):
                self.progress.emit("登出成功")
            else:
                self.progress.emit("登出失败")
            
            self.finished.emit(result)
            
        except Exception as e:
            error_msg = f"登出失败: {str(e)}"
            print(f"LogoutWorker error: {error_msg}")
            print(traceback.format_exc())
            self.error.emit(error_msg)

class FriendsListWorker(AsyncWorker):
    """好友列表加载工作线程"""
    
    def __init__(self):
        from friends_manager import friends_manager
        from user_auth import user_auth
        self.friends_manager = friends_manager
        self.current_user = user_auth.get_current_user()
        super().__init__(self._load_friends_with_cache)
    
    def _load_friends_with_cache(self):
        """带缓存的加载好友列表"""
        if not self.current_user:
            return {"success": False, "message": "用户未登录"}
        
        user_id = str(self.current_user['id'])
        
        # 先尝试从缓存获取
        cached_data = user_cache.get_friends_list(user_id)
        if cached_data:
            self.progress.emit("从缓存加载好友列表...")
            return cached_data
        
        # 缓存未命中，从服务器获取
        self.progress.emit("正在从服务器加载好友列表...")
        result = self.friends_manager.get_friends_list()
        
        # 缓存成功的结果
        if result.get('success'):
            user_cache.set_friends_list(user_id, result)
        
        return result
    
    def run(self):
        """执行加载好友列表任务"""
        try:
            # 执行加载好友列表
            result = self.task_func(*self.args, **self.kwargs)
            
            if result.get('success'):
                friend_count = len(result.get('friends', []))
                self.progress.emit(f"加载完成，共 {friend_count} 个好友")
            else:
                self.progress.emit("加载失败")
            
            self.finished.emit(result)
            
        except Exception as e:
            error_msg = f"加载好友列表失败: {str(e)}"
            print(f"FriendsListWorker error: {error_msg}")
            print(traceback.format_exc())
            self.error.emit(error_msg)

class FriendRequestsWorker(AsyncWorker):
    """好友请求加载工作线程"""
    
    def __init__(self):
        from friends_manager import friends_manager
        from user_auth import user_auth
        self.friends_manager = friends_manager
        self.current_user = user_auth.get_current_user()
        super().__init__(self._load_requests_with_cache)
    
    def _load_requests_with_cache(self):
        """带缓存的加载好友请求"""
        if not self.current_user:
            return {"success": False, "message": "用户未登录"}
        
        user_id = str(self.current_user['id'])
        
        # 先尝试从缓存获取
        cached_data = user_cache.get_friend_requests(user_id)
        if cached_data:
            self.progress.emit("从缓存加载好友请求...")
            return cached_data
        
        # 缓存未命中，从服务器获取
        self.progress.emit("正在从服务器加载好友请求...")
        result = self.friends_manager.get_friend_requests()
        
        # 缓存成功的结果
        if result.get('success'):
            user_cache.set_friend_requests(user_id, result)
        
        return result
    
    def run(self):
        """执行加载好友请求任务"""
        try:
            # 执行加载好友请求
            result = self.task_func(*self.args, **self.kwargs)
            
            if result.get('success'):
                request_count = len(result.get('requests', []))
                self.progress.emit(f"加载完成，共 {request_count} 个请求")
            else:
                self.progress.emit("加载失败")
            
            self.finished.emit(result)
            
        except Exception as e:
            error_msg = f"加载好友请求失败: {str(e)}"
            print(f"FriendRequestsWorker error: {error_msg}")
            print(traceback.format_exc())
            self.error.emit(error_msg)

class SearchUsersWorker(AsyncWorker):
    """搜索用户工作线程"""
    
    def __init__(self, query: str):
        from user_auth import user_auth
        self.user_auth = user_auth
        self.query = query
        super().__init__(self._search_users_with_cache, query)
    
    def _search_users_with_cache(self, query: str):
        """带缓存的搜索用户"""
        # 先尝试从缓存获取
        cached_data = user_cache.get_user_search(query)
        if cached_data:
            self.progress.emit("从缓存获取搜索结果...")
            return cached_data
        
        # 缓存未命中，从服务器搜索
        self.progress.emit("正在搜索用户...")
        result = self.user_auth.search_users(query)
        
        # 缓存成功的结果
        if result.get('success'):
            user_cache.set_user_search(query, result)
        
        return result
    
    def run(self):
        """执行搜索用户任务"""
        try:
            # 执行搜索用户
            result = self.task_func(*self.args, **self.kwargs)
            
            if result.get('success'):
                user_count = result.get('total', 0)
                self.progress.emit(f"搜索完成，找到 {user_count} 个用户")
            else:
                self.progress.emit("搜索失败")
            
            self.finished.emit(result)
            
        except Exception as e:
            error_msg = f"搜索用户失败: {str(e)}"
            print(f"SearchUsersWorker error: {error_msg}")
            print(traceback.format_exc())
            self.error.emit(error_msg)

class AsyncTaskManager(QObject):
    """异步任务管理器"""
    
    def __init__(self):
        super().__init__()
        self.active_workers = []
    
    def run_task(self, worker_class, *args, **kwargs) -> AsyncWorker:
        """运行异步任务
        
        Args:
            worker_class: 工作线程类
            *args: 工作线程构造参数
            **kwargs: 工作线程构造关键字参数
            
        Returns:
            工作线程实例
        """
        worker = worker_class(*args, **kwargs)
        
        # 连接完成信号，自动清理
        worker.finished.connect(lambda: self._cleanup_worker(worker))
        worker.error.connect(lambda: self._cleanup_worker(worker))
        
        # 添加到活动列表
        self.active_workers.append(worker)
        
        # 启动线程
        worker.start()
        
        return worker
    
    def _cleanup_worker(self, worker: AsyncWorker):
        """清理工作线程"""
        if worker in self.active_workers:
            self.active_workers.remove(worker)
        
        # 确保线程正确结束
        if worker.isRunning():
            worker.quit()
            worker.wait()
    
    def cleanup_all(self):
        """清理所有工作线程"""
        for worker in self.active_workers[:]:
            self._cleanup_worker(worker)

# 全局任务管理器实例
task_manager = AsyncTaskManager()