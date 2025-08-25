#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
聊天数据库模块
提供本地SQLite数据库存储聊天记录功能
"""

import sqlite3
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from PyQt5.QtCore import QStandardPaths

class ChatDatabase:
    """聊天数据库管理类"""
    
    def __init__(self):
        """初始化数据库连接"""
        # 使用用户数据目录存储数据库
        base_dir = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
        if not base_dir:
            base_dir = os.path.expanduser('~/.desktop_pet')
        os.makedirs(base_dir, exist_ok=True)
        
        self.db_path = os.path.join(base_dir, 'chat.db')
        self.init_database()
    
    def init_database(self):
        """初始化数据库表结构"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 创建聊天消息表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS chat_messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        sender_id TEXT NOT NULL,
                        receiver_id TEXT NOT NULL,
                        content TEXT NOT NULL,
                        message_type TEXT DEFAULT 'text',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_read BOOLEAN DEFAULT 0,
                        sync_status TEXT DEFAULT 'local'
                    )
                """)
                
                # 创建索引
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_chat_messages_conversation 
                    ON chat_messages(sender_id, receiver_id, created_at)
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_chat_messages_unread 
                    ON chat_messages(receiver_id, is_read)
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_chat_messages_sync 
                    ON chat_messages(sync_status)
                """)
                
                conn.commit()
                
        except Exception as e:
            print(f"初始化聊天数据库失败: {e}")
    
    def save_message(self, sender_id: str, receiver_id: str, content: str, 
                    message_type: str = 'text') -> Optional[int]:
        """保存聊天消息
        
        Args:
            sender_id: 发送者ID
            receiver_id: 接收者ID
            content: 消息内容
            message_type: 消息类型
            
        Returns:
            消息ID或None
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO chat_messages (sender_id, receiver_id, content, message_type, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (sender_id, receiver_id, content, message_type, datetime.now().isoformat()))
                
                conn.commit()
                return cursor.lastrowid
                
        except Exception as e:
            print(f"保存聊天消息失败: {e}")
            return None
    
    def get_conversation_history(self, user1_id: str, user2_id: str, 
                               limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """获取两个用户之间的聊天记录
        
        Args:
            user1_id: 用户1 ID
            user2_id: 用户2 ID
            limit: 消息数量限制
            offset: 偏移量
            
        Returns:
            聊天记录列表
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT id, sender_id, receiver_id, content, message_type, created_at, is_read
                    FROM chat_messages
                    WHERE (sender_id = ? AND receiver_id = ?) OR (sender_id = ? AND receiver_id = ?)
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                """, (user1_id, user2_id, user2_id, user1_id, limit, offset))
                
                messages = []
                for row in cursor.fetchall():
                    messages.append({
                        'id': row[0],
                        'sender_id': row[1],
                        'receiver_id': row[2],
                        'content': row[3],
                        'message_type': row[4],
                        'created_at': row[5],
                        'is_read': bool(row[6])
                    })
                
                # 按时间正序返回（最新的在最后）
                return list(reversed(messages))
                
        except Exception as e:
            print(f"获取聊天记录失败: {e}")
            return []
    
    def mark_messages_as_read(self, sender_id: str, receiver_id: str) -> bool:
        """标记消息为已读
        
        Args:
            sender_id: 发送者ID
            receiver_id: 接收者ID（当前用户）
            
        Returns:
            是否成功
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE chat_messages 
                    SET is_read = 1 
                    WHERE sender_id = ? AND receiver_id = ? AND is_read = 0
                """, (sender_id, receiver_id))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"标记消息已读失败: {e}")
            return False
    
    def get_unread_count(self, user_id: str) -> int:
        """获取用户的未读消息数量
        
        Args:
            user_id: 用户ID
            
        Returns:
            未读消息数量
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT COUNT(*) FROM chat_messages 
                    WHERE receiver_id = ? AND is_read = 0
                """, (user_id,))
                
                result = cursor.fetchone()
                return result[0] if result else 0
                
        except Exception as e:
            print(f"获取未读消息数量失败: {e}")
            return 0
    
    def get_unread_count_by_sender(self, receiver_id: str, sender_id: str) -> int:
        """获取特定发送者的未读消息数量
        
        Args:
            receiver_id: 接收者ID（当前用户）
            sender_id: 发送者ID
            
        Returns:
            未读消息数量
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT COUNT(*) FROM chat_messages 
                    WHERE receiver_id = ? AND sender_id = ? AND is_read = 0
                """, (receiver_id, sender_id))
                
                result = cursor.fetchone()
                return result[0] if result else 0
                
        except Exception as e:
            print(f"获取特定发送者未读消息数量失败: {e}")
            return 0
    
    def get_recent_conversations(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """获取用户的最近聊天会话
        
        Args:
            user_id: 用户ID
            limit: 会话数量限制
            
        Returns:
            最近会话列表
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 获取最近的聊天对象和最后一条消息
                cursor.execute("""
                    SELECT 
                        CASE 
                            WHEN sender_id = ? THEN receiver_id 
                            ELSE sender_id 
                        END as other_user_id,
                        content,
                        created_at,
                        sender_id = ? as is_sent
                    FROM chat_messages 
                    WHERE sender_id = ? OR receiver_id = ?
                    GROUP BY other_user_id
                    ORDER BY MAX(created_at) DESC
                    LIMIT ?
                """, (user_id, user_id, user_id, user_id, limit))
                
                conversations = []
                for row in cursor.fetchall():
                    other_user_id = row[0]
                    unread_count = self.get_unread_count_by_sender(user_id, other_user_id)
                    
                    conversations.append({
                        'other_user_id': other_user_id,
                        'last_message': row[1],
                        'last_message_time': row[2],
                        'is_last_sent': row[3],
                        'unread_count': unread_count
                    })
                
                return conversations
                
        except Exception as e:
            print(f"获取最近会话失败: {e}")
            return []
    
    def delete_conversation(self, user1_id: str, user2_id: str) -> bool:
        """删除两个用户之间的所有聊天记录
        
        Args:
            user1_id: 用户1 ID
            user2_id: 用户2 ID
            
        Returns:
            是否成功
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    DELETE FROM chat_messages
                    WHERE (sender_id = ? AND receiver_id = ?) OR (sender_id = ? AND receiver_id = ?)
                """, (user1_id, user2_id, user2_id, user1_id))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"删除聊天记录失败: {e}")
            return False
    
    def search_messages(self, user_id: str, keyword: str, limit: int = 50) -> List[Dict[str, Any]]:
        """搜索聊天消息
        
        Args:
            user_id: 用户ID
            keyword: 搜索关键词
            limit: 结果数量限制
            
        Returns:
            搜索结果列表
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT id, sender_id, receiver_id, content, message_type, created_at
                    FROM chat_messages
                    WHERE (sender_id = ? OR receiver_id = ?) AND content LIKE ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (user_id, user_id, f'%{keyword}%', limit))
                
                messages = []
                for row in cursor.fetchall():
                    messages.append({
                        'id': row[0],
                        'sender_id': row[1],
                        'receiver_id': row[2],
                        'content': row[3],
                        'message_type': row[4],
                        'created_at': row[5]
                    })
                
                return messages
                
        except Exception as e:
            print(f"搜索聊天消息失败: {e}")
            return []
    
    def close(self):
        """关闭数据库连接"""
        # SQLite连接在with语句中自动关闭，这里不需要特别处理
        pass

# 全局聊天数据库实例
chat_db = ChatDatabase()