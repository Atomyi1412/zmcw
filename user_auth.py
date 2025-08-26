#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户认证模块
提供用户注册、登录、密码验证等功能
"""

import os
import re
import bcrypt
import httpx
from typing import Optional, Dict, Any
from supabase import create_client, Client
from datetime import datetime
import time

class UserAuth:
    """用户认证管理类"""
    
    def __init__(self):
        """初始化Supabase客户端"""
        # Supabase配置
        self.supabase_url = "https://frxqpzjiddkrgpwxpfwz.supabase.co"
        self.supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZyeHFwemppZGRrcmdwd3hwZnd6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTU2NzUwNzAsImV4cCI6MjA3MTI1MTA3MH0.GxdpqhmTvuAWZiEKRRl7SdtQE4Gf1V_Bv3nML7D6oLc"
        
        # 创建带超时配置的HTTP客户端
        self.http_client = httpx.Client(
            timeout=httpx.Timeout(
                connect=30.0,  # 连接超时30秒
                read=60.0,     # 读取超时60秒
                write=30.0,    # 写入超时30秒
                pool=10.0      # 连接池超时10秒
            ),
            limits=httpx.Limits(
                max_keepalive_connections=5,
                max_connections=10
            ),
            retries=3  # 重试3次
        )
        
        # 创建Supabase客户端
        self.supabase: Client = create_client(
            self.supabase_url, 
            self.supabase_key,
            options={
                'postgrest': {
                    'client': self.http_client
                }
            }
        )
        
        # 当前登录用户信息
        self.current_user: Optional[Dict[str, Any]] = None
        self.is_logged_in = False
    
    def _handle_network_error(self, e: Exception, operation: str) -> Dict[str, Any]:
        """处理网络错误并返回用户友好的错误信息
        
        Args:
            e: 异常对象
            operation: 操作描述
            
        Returns:
            包含错误信息的字典
        """
        error_str = str(e)
        
        # 检查是否是连接被拒绝错误（WinError 10061）
        if "10061" in error_str or "Connection refused" in error_str:
            return {
                "success": False,
                "message": f"{operation}失败：无法连接到服务器\n\n可能的解决方案：\n1. 检查网络连接是否正常\n2. 确认防火墙没有阻止应用程序\n3. 尝试重启应用程序\n4. 如果使用代理，请检查代理设置"
            }
        
        # 检查是否是超时错误
        if "timeout" in error_str.lower() or "timed out" in error_str.lower():
            return {
                "success": False,
                "message": f"{operation}失败：网络连接超时\n\n请检查网络连接后重试"
            }
        
        # 检查是否是DNS解析错误
        if "Name or service not known" in error_str or "getaddrinfo failed" in error_str:
            return {
                "success": False,
                "message": f"{operation}失败：无法解析服务器地址\n\n请检查网络连接和DNS设置"
            }
        
        # 通用网络错误
        return {
            "success": False,
            "message": f"{operation}时出错: {error_str}\n\n请检查网络连接后重试"
        }
    
    def _retry_operation(self, operation_func, operation_name: str, max_retries: int = 3):
        """重试网络操作
        
        Args:
            operation_func: 要执行的操作函数
            operation_name: 操作名称
            max_retries: 最大重试次数
            
        Returns:
            操作结果
        """
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                return operation_func()
            except Exception as e:
                last_exception = e
                if attempt < max_retries:
                    # 等待一段时间后重试，使用指数退避
                    wait_time = (2 ** attempt) * 0.5  # 0.5, 1, 2 秒
                    time.sleep(wait_time)
                    continue
                else:
                    # 最后一次尝试失败，返回错误
                    return self._handle_network_error(e, operation_name)
        
        # 理论上不会到达这里
        return self._handle_network_error(last_exception, operation_name)
    
    def validate_username(self, username: str) -> Dict[str, Any]:
        """验证用户名格式和唯一性
        
        Args:
            username: 用户名
            
        Returns:
            验证结果字典，包含is_valid和message
        """
        # 检查用户名长度
        if len(username) < 3 or len(username) > 20:
            return {"is_valid": False, "message": "用户名长度必须在3-20位之间"}
        
        # 检查用户名格式（只允许字母、数字、下划线）
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return {"is_valid": False, "message": "用户名只能包含字母、数字和下划线"}
        
        # 检查用户名是否已存在
        def check_username():
            result = self.supabase.table('users').select('username').eq('username', username).execute()
            if result.data:
                return {"is_valid": False, "message": "用户名已存在"}
            return {"is_valid": True, "message": "用户名可用"}
        
        result = self._retry_operation(check_username, "验证用户名")
        if not result.get('success', True):  # 如果是网络错误
            return {"is_valid": False, "message": result['message']}
        
        return result
    
    def validate_password(self, password: str) -> Dict[str, Any]:
        """验证密码强度
        
        Args:
            password: 密码
            
        Returns:
            验证结果字典，包含is_valid、message和strength
        """
        # 检查密码长度
        if len(password) < 5 or len(password) > 20:
            return {
                "is_valid": False, 
                "message": "密码长度必须在5-20位之间",
                "strength": "弱"
            }
        
        # 检查是否包含数字和字母
        has_letter = bool(re.search(r'[a-zA-Z]', password))
        has_number = bool(re.search(r'\d', password))
        
        if not (has_letter and has_number):
            return {
                "is_valid": False,
                "message": "密码必须包含字母和数字",
                "strength": "弱"
            }
        
        # 计算密码强度
        strength_score = 0
        if len(password) >= 8:
            strength_score += 1
        if re.search(r'[a-z]', password):
            strength_score += 1
        if re.search(r'[A-Z]', password):
            strength_score += 1
        if re.search(r'\d', password):
            strength_score += 1
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            strength_score += 1
        
        if strength_score <= 2:
            strength = "弱"
        elif strength_score <= 3:
            strength = "中"
        else:
            strength = "强"
        
        return {
            "is_valid": True,
            "message": "密码格式正确",
            "strength": strength
        }
    
    def hash_password(self, password: str) -> str:
        """加密密码
        
        Args:
            password: 明文密码
            
        Returns:
            加密后的密码哈希
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """验证密码
        
        Args:
            password: 明文密码
            hashed: 加密后的密码哈希
            
        Returns:
            密码是否正确
        """
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def register(self, username: str, password: str, email: str = None) -> Dict[str, Any]:
        """用户注册
        
        Args:
            username: 用户名
            password: 密码
            email: 邮箱（可选）
            
        Returns:
            注册结果字典
        """
        # 验证用户名
        username_validation = self.validate_username(username)
        if not username_validation["is_valid"]:
            return {"success": False, "message": username_validation["message"]}
        
        # 验证密码
        password_validation = self.validate_password(password)
        if not password_validation["is_valid"]:
            return {"success": False, "message": password_validation["message"]}
        
        # 加密密码
        password_hash = self.hash_password(password)
        
        # 插入用户数据
        user_data = {
            "username": username,
            "password_hash": password_hash,
            "created_at": datetime.now().isoformat(),
            "last_active": datetime.now().isoformat(),
            "is_online": True
        }
        
        if email:
            user_data["email"] = email
        
        def register_user():
            result = self.supabase.table('users').insert(user_data).execute()
            
            if result.data:
                user_info = result.data[0]
                self.current_user = user_info
                self.is_logged_in = True
                
                return {
                    "success": True,
                    "message": "注册成功",
                    "user_id": user_info["id"],
                    "username": user_info["username"]
                }
            else:
                return {"success": False, "message": "注册失败，请重试"}
        
        return self._retry_operation(register_user, "用户注册")
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """用户登录
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            登录结果字典
        """
        def login_user():
            # 查询用户
            result = self.supabase.table('users').select('*').eq('username', username).execute()
            
            if not result.data:
                return {"success": False, "message": "用户名不存在"}
            
            user_info = result.data[0]
            
            # 验证密码
            if not self.verify_password(password, user_info["password_hash"]):
                return {"success": False, "message": "密码错误"}
            
            # 更新用户在线状态和最后活动时间
            self.supabase.table('users').update({
                "is_online": True,
                "last_active": datetime.now().isoformat()
            }).eq('id', user_info['id']).execute()
            
            # 设置当前用户
            self.current_user = user_info
            self.is_logged_in = True
            
            return {
                "success": True,
                "message": "登录成功",
                "user_id": user_info["id"],
                "username": user_info["username"]
            }
        
        return self._retry_operation(login_user, "用户登录")
    
    def logout(self) -> Dict[str, Any]:
        """用户登出
        
        Returns:
            登出结果字典
        """
        def logout_user():
            if self.current_user:
                # 更新用户离线状态
                self.supabase.table('users').update({
                    "is_online": False,
                    "last_active": datetime.now().isoformat()
                }).eq('id', self.current_user["id"]).execute()
            
            # 清除当前用户信息
            self.current_user = None
            self.is_logged_in = False
            
            return {"success": True, "message": "登出成功"}
        
        # 对于登出操作，即使网络失败也要清除本地状态
        result = self._retry_operation(logout_user, "用户登出")
        if not result.get('success'):
            # 即使网络请求失败，也要清除本地状态
            self.current_user = None
            self.is_logged_in = False
            return {"success": True, "message": "已离线登出（网络连接失败）"}
        
        return result
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """获取当前登录用户信息
        
        Returns:
            当前用户信息字典或None
        """
        return self.current_user
    
    def is_user_logged_in(self) -> bool:
        """检查用户是否已登录
        
        Returns:
            是否已登录
        """
        return self.is_logged_in
    
    def search_users(self, query: str) -> Dict[str, Any]:
        """搜索用户
        
        Args:
            query: 搜索关键词（用户名或ID）
            
        Returns:
            搜索结果字典
        """
        def search_operation():
            # 按用户名搜索
            result = self.supabase.table('users').select('id, username, created_at, last_active, is_online').ilike('username', f'%{query}%').limit(10).execute()
            
            users = []
            for user in result.data:
                # 排除当前用户
                if self.current_user and user["id"] != self.current_user["id"]:
                    users.append({
                        "id": user["id"],
                        "username": user["username"],
                        "is_online": user["is_online"],
                        "last_active": user["last_active"]
                    })
            
            return {
                "success": True,
                "users": users,
                "total": len(users)
            }
        
        result = self._retry_operation(search_operation, "搜索用户")
        if not result.get('success'):
            # 网络错误时返回空结果
            result["users"] = []
            result["total"] = 0
        
        return result
    
    def restore_session(self, user_id: str) -> Dict[str, Any]:
        """根据用户ID恢复会话（用于"记住我"自动登录）
        
        注意：此方法假定本地会话是可信的，仅用于在同一设备上恢复已登录状态，
        不需要再次输入密码。会同步更新服务端在线状态。
        """
        if not user_id:
            return {"success": False, "message": "无效的用户ID"}
        
        def restore_operation():
            # 查询用户
            result = self.supabase.table('users').select('*').eq('id', user_id).execute()
            if not result.data:
                return {"success": False, "message": "用户不存在或已被删除"}
            user_info = result.data[0]
            # 更新用户在线状态和最后活动时间
            self.supabase.table('users').update({
                "is_online": True,
                "last_active": datetime.now().isoformat()
            }).eq('id', user_info["id"]).execute()
            # 设置当前用户
            self.current_user = user_info
            self.is_logged_in = True
            return {
                "success": True,
                "message": "自动登录成功",
                "user_id": user_info["id"],
                "username": user_info["username"],
                "email": user_info.get("email"),
                "created_at": user_info["created_at"]
            }
        
        return self._retry_operation(restore_operation, "恢复会话")

# 全局用户认证实例
user_auth = UserAuth()