#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存管理模块
提供本地缓存机制，减少重复网络请求
"""

import json
import os
import time
from typing import Dict, Any, Optional
from PyQt5.QtCore import QStandardPaths

class CacheManager:
    """缓存管理器"""
    
    def __init__(self, cache_dir: str = None):
        """
        初始化缓存管理器
        
        Args:
            cache_dir: 缓存目录路径，默认使用系统缓存目录
        """
        if cache_dir is None:
            # 使用系统缓存目录
            base_dir = QStandardPaths.writableLocation(QStandardPaths.CacheLocation)
            if not base_dir:
                base_dir = os.path.expanduser('~/.cache/desktop_pet')
            self.cache_dir = base_dir
        else:
            self.cache_dir = cache_dir
        
        # 确保缓存目录存在
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # 缓存配置
        self.default_ttl = 300  # 默认缓存时间5分钟
        self.max_cache_size = 100  # 最大缓存条目数
        
        # 内存缓存
        self.memory_cache = {}
    
    def _get_cache_file_path(self, key: str) -> str:
        """获取缓存文件路径"""
        # 使用安全的文件名
        safe_key = key.replace('/', '_').replace('\\', '_').replace(':', '_')
        return os.path.join(self.cache_dir, f"{safe_key}.cache")
    
    def _is_expired(self, timestamp: float, ttl: int) -> bool:
        """检查缓存是否过期"""
        return time.time() - timestamp > ttl
    
    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """
        设置缓存
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 生存时间（秒），默认使用default_ttl
            
        Returns:
            是否设置成功
        """
        if ttl is None:
            ttl = self.default_ttl
        
        try:
            # 准备缓存数据
            cache_data = {
                'value': value,
                'timestamp': time.time(),
                'ttl': ttl
            }
            
            # 写入内存缓存
            self.memory_cache[key] = cache_data
            
            # 写入文件缓存
            cache_file = self._get_cache_file_path(key)
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            # 清理过期缓存
            self._cleanup_expired_cache()
            
            return True
            
        except Exception as e:
            print(f"设置缓存失败: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存
        
        Args:
            key: 缓存键
            
        Returns:
            缓存值，如果不存在或过期则返回None
        """
        try:
            # 先检查内存缓存
            if key in self.memory_cache:
                cache_data = self.memory_cache[key]
                if not self._is_expired(cache_data['timestamp'], cache_data['ttl']):
                    return cache_data['value']
                else:
                    # 过期，删除内存缓存
                    del self.memory_cache[key]
            
            # 检查文件缓存
            cache_file = self._get_cache_file_path(key)
            if os.path.exists(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                
                if not self._is_expired(cache_data['timestamp'], cache_data['ttl']):
                    # 加载到内存缓存
                    self.memory_cache[key] = cache_data
                    return cache_data['value']
                else:
                    # 过期，删除文件
                    os.remove(cache_file)
            
            return None
            
        except Exception as e:
            print(f"获取缓存失败: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """
        删除缓存
        
        Args:
            key: 缓存键
            
        Returns:
            是否删除成功
        """
        try:
            # 删除内存缓存
            if key in self.memory_cache:
                del self.memory_cache[key]
            
            # 删除文件缓存
            cache_file = self._get_cache_file_path(key)
            if os.path.exists(cache_file):
                os.remove(cache_file)
            
            return True
            
        except Exception as e:
            print(f"删除缓存失败: {e}")
            return False
    
    def clear(self) -> bool:
        """
        清空所有缓存
        
        Returns:
            是否清空成功
        """
        try:
            # 清空内存缓存
            self.memory_cache.clear()
            
            # 清空文件缓存
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.cache'):
                    file_path = os.path.join(self.cache_dir, filename)
                    os.remove(file_path)
            
            return True
            
        except Exception as e:
            print(f"清空缓存失败: {e}")
            return False
    
    def _cleanup_expired_cache(self):
        """清理过期缓存"""
        try:
            # 清理内存缓存
            expired_keys = []
            for key, cache_data in self.memory_cache.items():
                if self._is_expired(cache_data['timestamp'], cache_data['ttl']):
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.memory_cache[key]
            
            # 清理文件缓存
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.cache'):
                    file_path = os.path.join(self.cache_dir, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            cache_data = json.load(f)
                        
                        if self._is_expired(cache_data['timestamp'], cache_data['ttl']):
                            os.remove(file_path)
                    except:
                        # 文件损坏，直接删除
                        os.remove(file_path)
            
            # 限制缓存大小
            if len(self.memory_cache) > self.max_cache_size:
                # 删除最旧的缓存
                sorted_items = sorted(
                    self.memory_cache.items(),
                    key=lambda x: x[1]['timestamp']
                )
                
                for key, _ in sorted_items[:len(self.memory_cache) - self.max_cache_size]:
                    self.delete(key)
                    
        except Exception as e:
            print(f"清理缓存失败: {e}")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """
        获取缓存信息
        
        Returns:
            缓存信息字典
        """
        try:
            memory_count = len(self.memory_cache)
            
            file_count = 0
            total_size = 0
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.cache'):
                    file_count += 1
                    file_path = os.path.join(self.cache_dir, filename)
                    total_size += os.path.getsize(file_path)
            
            return {
                'memory_cache_count': memory_count,
                'file_cache_count': file_count,
                'total_size_bytes': total_size,
                'cache_dir': self.cache_dir
            }
            
        except Exception as e:
            print(f"获取缓存信息失败: {e}")
            return {}

class UserDataCache:
    """用户数据缓存"""
    
    def __init__(self):
        self.cache = CacheManager()
        
        # 不同数据类型的缓存时间
        self.ttl_config = {
            'friends_list': 300,      # 好友列表缓存5分钟
            'friend_requests': 180,   # 好友请求缓存3分钟
            'user_search': 600,       # 用户搜索缓存10分钟
            'user_profile': 1800,     # 用户资料缓存30分钟
        }
    
    def get_friends_list(self, user_id: str) -> Optional[Dict[str, Any]]:
        """获取好友列表缓存"""
        key = f"friends_list_{user_id}"
        return self.cache.get(key)
    
    def set_friends_list(self, user_id: str, friends_data: Dict[str, Any]) -> bool:
        """设置好友列表缓存"""
        key = f"friends_list_{user_id}"
        ttl = self.ttl_config['friends_list']
        return self.cache.set(key, friends_data, ttl)
    
    def get_friend_requests(self, user_id: str) -> Optional[Dict[str, Any]]:
        """获取好友请求缓存"""
        key = f"friend_requests_{user_id}"
        return self.cache.get(key)
    
    def set_friend_requests(self, user_id: str, requests_data: Dict[str, Any]) -> bool:
        """设置好友请求缓存"""
        key = f"friend_requests_{user_id}"
        ttl = self.ttl_config['friend_requests']
        return self.cache.set(key, requests_data, ttl)
    
    def get_user_search(self, query: str) -> Optional[Dict[str, Any]]:
        """获取用户搜索缓存"""
        key = f"user_search_{query}"
        return self.cache.get(key)
    
    def set_user_search(self, query: str, search_data: Dict[str, Any]) -> bool:
        """设置用户搜索缓存"""
        key = f"user_search_{query}"
        ttl = self.ttl_config['user_search']
        return self.cache.set(key, search_data, ttl)
    
    def invalidate_user_data(self, user_id: str):
        """使用户相关缓存失效"""
        keys_to_delete = [
            f"friends_list_{user_id}",
            f"friend_requests_{user_id}",
        ]
        
        for key in keys_to_delete:
            self.cache.delete(key)
    
    def clear_all(self) -> bool:
        """清空所有缓存"""
        return self.cache.clear()

# 全局缓存实例
user_cache = UserDataCache()