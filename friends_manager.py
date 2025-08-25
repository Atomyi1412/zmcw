#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
好友管理模块
提供好友添加、删除、搜索等功能
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from user_auth import user_auth

class FriendsManager:
    """好友管理类"""
    
    def __init__(self):
        """初始化好友管理器"""
        self.supabase = user_auth.supabase
    
    def send_friend_request(self, target_username: str, message: str = None) -> Dict[str, Any]:
        """发送好友请求
        
        Args:
            target_username: 目标用户名
            message: 请求消息
            
        Returns:
            请求结果字典
        """
        try:
            current_user = user_auth.get_current_user()
            if not current_user:
                return {"success": False, "message": "请先登录"}
            
            # 查找目标用户
            target_result = self.supabase.table('users').select('id, username').eq('username', target_username).execute()
            if not target_result.data:
                return {"success": False, "message": "用户不存在"}
            
            target_user = target_result.data[0]
            
            # 检查是否是自己
            if target_user['id'] == current_user['id']:
                return {"success": False, "message": "不能添加自己为好友"}
            
            # 检查是否已经是好友
            friendship_check = self.supabase.table('friendships').select('id').or_(
                f'and(user1_id.eq.{current_user["id"]},user2_id.eq.{target_user["id"]}),'
                f'and(user1_id.eq.{target_user["id"]},user2_id.eq.{current_user["id"]})'
            ).execute()
            
            if friendship_check.data:
                return {"success": False, "message": "你们已经是好友了"}
            
            # 检查是否已经发送过请求
            existing_request = self.supabase.table('friend_requests').select('id, status').eq(
                'sender_id', current_user['id']
            ).eq('receiver_id', target_user['id']).eq('status', 'pending').execute()
            
            if existing_request.data:
                return {"success": False, "message": "已经发送过好友请求，请等待对方回应"}
            
            # 发送好友请求
            request_data = {
                "sender_id": current_user['id'],
                "receiver_id": target_user['id'],
                "message": message or f"{current_user['username']} 想要添加你为好友",
                "status": "pending",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            result = self.supabase.table('friend_requests').insert(request_data).execute()
            
            if result.data:
                return {
                    "success": True,
                    "message": f"已向 {target_username} 发送好友请求",
                    "request_id": result.data[0]['id']
                }
            else:
                return {"success": False, "message": "发送好友请求失败"}
                
        except Exception as e:
            return {"success": False, "message": f"发送好友请求时出错: {str(e)}"}
    
    def get_friend_requests(self, request_type: str = "received") -> Dict[str, Any]:
        """获取好友请求列表
        
        Args:
            request_type: 请求类型，"received"(收到的) 或 "sent"(发送的)
            
        Returns:
            请求列表字典
        """
        try:
            current_user = user_auth.get_current_user()
            if not current_user:
                return {"success": False, "message": "请先登录", "requests": []}
            
            if request_type == "received":
                # 获取收到的好友请求
                result = self.supabase.table('friend_requests').select(
                    'id, sender_id, message, status, created_at, users!friend_requests_sender_id_fkey(username)'
                ).eq('receiver_id', current_user['id']).eq('status', 'pending').order('created_at', desc=True).execute()
            else:
                # 获取发送的好友请求
                result = self.supabase.table('friend_requests').select(
                    'id, receiver_id, message, status, created_at, users!friend_requests_receiver_id_fkey(username)'
                ).eq('sender_id', current_user['id']).order('created_at', desc=True).execute()
            
            requests = []
            for req in result.data:
                if request_type == "received":
                    requests.append({
                        "id": req['id'],
                        "sender_id": req['sender_id'],
                        "sender_username": req['users']['username'],
                        "message": req['message'],
                        "status": req['status'],
                        "created_at": req['created_at']
                    })
                else:
                    requests.append({
                        "id": req['id'],
                        "receiver_id": req['receiver_id'],
                        "receiver_username": req['users']['username'],
                        "message": req['message'],
                        "status": req['status'],
                        "created_at": req['created_at']
                    })
            
            return {
                "success": True,
                "requests": requests,
                "total": len(requests)
            }
            
        except Exception as e:
            return {"success": False, "message": f"获取好友请求时出错: {str(e)}", "requests": []}
    
    def respond_to_friend_request(self, request_id: str, action: str) -> Dict[str, Any]:
        """回应好友请求
        
        Args:
            request_id: 请求ID
            action: 操作类型，"accept"(接受) 或 "reject"(拒绝)
            
        Returns:
            操作结果字典
        """
        try:
            current_user = user_auth.get_current_user()
            if not current_user:
                return {"success": False, "message": "请先登录"}
            
            if action not in ["accept", "reject"]:
                return {"success": False, "message": "无效的操作类型"}
            
            # 获取好友请求信息
            request_result = self.supabase.table('friend_requests').select(
                'id, sender_id, receiver_id, status'
            ).eq('id', request_id).eq('receiver_id', current_user['id']).eq('status', 'pending').execute()
            
            if not request_result.data:
                return {"success": False, "message": "好友请求不存在或已处理"}
            
            friend_request = request_result.data[0]
            
            # 更新请求状态
            status = "accepted" if action == "accept" else "rejected"
            self.supabase.table('friend_requests').update({
                "status": status,
                "updated_at": datetime.now().isoformat()
            }).eq('id', request_id).execute()
            
            if action == "accept":
                # 创建好友关系
                friendship_data = {
                    "user1_id": friend_request['sender_id'],
                    "user2_id": friend_request['receiver_id'],
                    "created_at": datetime.now().isoformat()
                }
                
                self.supabase.table('friendships').insert(friendship_data).execute()
                
                return {"success": True, "message": "已接受好友请求"}
            else:
                return {"success": True, "message": "已拒绝好友请求"}
                
        except Exception as e:
            return {"success": False, "message": f"处理好友请求时出错: {str(e)}"}
    
    def get_friends_list(self) -> Dict[str, Any]:
        """获取好友列表
        
        Returns:
            好友列表字典
        """
        try:
            current_user = user_auth.get_current_user()
            if not current_user:
                return {"success": False, "message": "请先登录", "friends": []}
            
            # 获取好友关系
            result = self.supabase.table('friendships').select(
                'id, user1_id, user2_id, created_at'
            ).or_(
                f'user1_id.eq.{current_user["id"]},user2_id.eq.{current_user["id"]}'
            ).execute()
            
            friends = []
            friend_ids = []
            
            for friendship in result.data:
                # 确定好友ID
                friend_id = friendship['user2_id'] if friendship['user1_id'] == current_user['id'] else friendship['user1_id']
                friend_ids.append(friend_id)
            
            if friend_ids:
                # 获取好友详细信息
                friends_result = self.supabase.table('users').select(
                    'id, username, is_online, last_active'
                ).in_('id', friend_ids).execute()
                
                for friend in friends_result.data:
                    friends.append({
                        "id": friend['id'],
                        "username": friend['username'],
                        "is_online": friend['is_online'],
                        "last_active": friend['last_active']
                    })
            
            return {
                "success": True,
                "friends": friends,
                "total": len(friends)
            }
            
        except Exception as e:
            return {"success": False, "message": f"获取好友列表时出错: {str(e)}", "friends": []}
    
    def remove_friend(self, friend_id: str) -> Dict[str, Any]:
        """删除好友
        
        Args:
            friend_id: 好友用户ID
            
        Returns:
            删除结果字典
        """
        try:
            current_user = user_auth.get_current_user()
            if not current_user:
                return {"success": False, "message": "请先登录"}
            
            # 删除好友关系
            result = self.supabase.table('friendships').delete().or_(
                f'and(user1_id.eq.{current_user["id"]},user2_id.eq.{friend_id}),'
                f'and(user1_id.eq.{friend_id},user2_id.eq.{current_user["id"]})'
            ).execute()
            
            if result.data:
                return {"success": True, "message": "已删除好友"}
            else:
                return {"success": False, "message": "好友关系不存在"}
                
        except Exception as e:
            return {"success": False, "message": f"删除好友时出错: {str(e)}"}
    
    def search_users(self, query: str) -> Dict[str, Any]:
        """搜索用户（用于添加好友）
        
        Args:
            query: 搜索关键词
            
        Returns:
            搜索结果字典
        """
        return user_auth.search_users(query)

# 全局好友管理实例
friends_manager = FriendsManager()