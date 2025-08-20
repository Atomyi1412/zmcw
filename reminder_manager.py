# -*- coding: utf-8 -*-
"""
提醒管理器类
用于管理多个提醒的添加、删除、编辑和执行
"""

import json
import uuid
import os
from datetime import datetime, timedelta
from PyQt5.QtCore import QTimer, QObject, pyqtSignal, QStandardPaths
from PyQt5.QtWidgets import QMessageBox


class Reminder:
    """单个提醒类"""
    
    def __init__(self, reminder_id=None, title="", content="", reminder_type="single", 
                 target_time=None, interval_minutes=None, is_active=True):
        self.id = reminder_id or str(uuid.uuid4())
        self.title = title
        self.content = content
        self.type = reminder_type  # 'single' 或 'repeat'
        self.target_time = target_time  # datetime对象，用于单次提醒
        self.interval_minutes = interval_minutes  # 循环提醒间隔（分钟）
        self.is_active = is_active
        self.created_time = datetime.now()
        self.last_triggered = None
        
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'type': self.type,
            'target_time': self.target_time.isoformat() if self.target_time else None,
            'interval_minutes': self.interval_minutes,
            'is_active': self.is_active,
            'created_time': self.created_time.isoformat(),
            'last_triggered': self.last_triggered.isoformat() if self.last_triggered else None
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建提醒对象"""
        reminder = cls(
            reminder_id=data['id'],
            title=data['title'],
            content=data['content'],
            reminder_type=data['type'],
            interval_minutes=data.get('interval_minutes'),
            is_active=data['is_active']
        )
        
        if data.get('target_time'):
            reminder.target_time = datetime.fromisoformat(data['target_time'])
        if data.get('created_time'):
            reminder.created_time = datetime.fromisoformat(data['created_time'])
        if data.get('last_triggered'):
            reminder.last_triggered = datetime.fromisoformat(data['last_triggered'])
            
        return reminder
    
    def get_status_text(self):
        """获取提醒状态文本"""
        if not self.is_active:
            return "已停用"
        
        if self.type == 'single':
            if self.target_time:
                if datetime.now() > self.target_time:
                    return "已过期"
                else:
                    return f"定时提醒：{self.target_time.strftime('%H:%M')}"
            return "单次提醒"
        else:
            if self.interval_minutes < 60:
                return f"循环提醒：每{self.interval_minutes}分钟"
            else:
                hours = self.interval_minutes // 60
                minutes = self.interval_minutes % 60
                if minutes == 0:
                    return f"循环提醒：每{hours}小时"
                else:
                    return f"循环提醒：每{hours}小时{minutes}分钟"


class ReminderManager(QObject):
    """提醒管理器类"""
    
    # 信号定义
    reminder_triggered = pyqtSignal(str, str, str)  # reminder_id, title, content
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.reminders = {}  # 存储所有提醒 {id: Reminder}
        self.timers = {}     # 存储定时器 {id: QTimer}
        
        # 使用用户数据目录存放提醒数据文件
        base_dir = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
        if not base_dir:
            base_dir = os.path.expanduser('~/.desktop_pet')
        os.makedirs(base_dir, exist_ok=True)
        self.data_file = os.path.join(base_dir, 'reminders.json')
        
        # 加载已保存的提醒
        self.load_reminders()
        
        # 启动所有活动的提醒
        self.start_all_active_reminders()
    
    def add_reminder(self, title, content, reminder_type, target_time=None, interval_minutes=None):
        """添加新提醒"""
        reminder = Reminder(
            title=title,
            content=content,
            reminder_type=reminder_type,
            target_time=target_time,
            interval_minutes=interval_minutes
        )
        
        self.reminders[reminder.id] = reminder
        self.save_reminders()
        
        # 启动提醒
        if reminder.is_active:
            self.start_reminder(reminder.id)
        
        return reminder.id
    
    def remove_reminder(self, reminder_id):
        """删除提醒"""
        if reminder_id in self.reminders:
            # 停止定时器
            self.stop_reminder(reminder_id)
            # 删除提醒
            del self.reminders[reminder_id]
            self.save_reminders()
            return True
        return False
    
    def update_reminder(self, reminder_id, title=None, content=None, 
                       reminder_type=None, target_time=None, interval_minutes=None, is_active=None):
        """更新提醒"""
        if reminder_id not in self.reminders:
            return False
        
        reminder = self.reminders[reminder_id]
        
        # 更新属性
        if title is not None:
            reminder.title = title
        if content is not None:
            reminder.content = content
        if reminder_type is not None:
            reminder.type = reminder_type
        if target_time is not None:
            reminder.target_time = target_time
        if interval_minutes is not None:
            reminder.interval_minutes = interval_minutes
        if is_active is not None:
            reminder.is_active = is_active
        
        self.save_reminders()
        
        # 重新启动提醒
        self.stop_reminder(reminder_id)
        if reminder.is_active:
            self.start_reminder(reminder_id)
        
        return True
    
    def get_reminder(self, reminder_id):
        """获取提醒"""
        return self.reminders.get(reminder_id)
    
    def get_all_reminders(self):
        """获取所有提醒"""
        return list(self.reminders.values())
    
    def get_active_reminders(self):
        """获取所有活动的提醒"""
        return [r for r in self.reminders.values() if r.is_active]
    
    def start_reminder(self, reminder_id):
        """启动单个提醒"""
        if reminder_id not in self.reminders:
            return False
        
        reminder = self.reminders[reminder_id]
        if not reminder.is_active:
            return False
        
        # 停止现有定时器
        self.stop_reminder(reminder_id)
        
        if reminder.type == 'single':
            self._start_single_reminder(reminder)
        else:
            self._start_repeat_reminder(reminder)
        
        return True
    
    def _start_single_reminder(self, reminder):
        """启动单次提醒"""
        if not reminder.target_time:
            return
        
        now = datetime.now()
        if now >= reminder.target_time:
            # 时间已过，直接触发
            self._trigger_reminder(reminder)
            return
        
        # 计算延迟时间
        delay_ms = int((reminder.target_time - now).total_seconds() * 1000)
        
        # 创建定时器
        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(lambda: self._trigger_reminder(reminder))
        timer.start(delay_ms)
        
        self.timers[reminder.id] = timer
    
    def _start_repeat_reminder(self, reminder):
        """启动循环提醒"""
        if not reminder.interval_minutes or reminder.interval_minutes <= 0:
            return
        
        # 创建定时器
        timer = QTimer()
        timer.timeout.connect(lambda: self._trigger_reminder(reminder))
        timer.start(reminder.interval_minutes * 60 * 1000)  # 转换为毫秒
        
        self.timers[reminder.id] = timer
    
    def _trigger_reminder(self, reminder):
        """触发提醒"""
        reminder.last_triggered = datetime.now()
        self.save_reminders()
        
        # 发送信号
        self.reminder_triggered.emit(reminder.id, reminder.title, reminder.content)
        
        # 如果是单次提醒，设置为非活动状态
        if reminder.type == 'single':
            reminder.is_active = False
            self.stop_reminder(reminder.id)
            self.save_reminders()
    
    def stop_reminder(self, reminder_id):
        """停止单个提醒"""
        if reminder_id in self.timers:
            self.timers[reminder_id].stop()
            del self.timers[reminder_id]
    
    def stop_all_reminders(self):
        """停止所有提醒"""
        for timer in self.timers.values():
            timer.stop()
        self.timers.clear()
        
        # 设置所有提醒为非活动状态
        for reminder in self.reminders.values():
            reminder.is_active = False
        self.save_reminders()
    
    def start_all_active_reminders(self):
        """启动所有活动的提醒"""
        for reminder in self.reminders.values():
            if reminder.is_active:
                self.start_reminder(reminder.id)
    
    def has_active_reminders(self):
        """检查是否有活动的提醒"""
        return any(r.is_active for r in self.reminders.values())
    
    def get_status_summary(self):
        """获取提醒状态摘要"""
        active_count = len(self.get_active_reminders())
        total_count = len(self.reminders)
        
        if active_count == 0:
            return "无活动提醒"
        elif active_count == 1:
            return "1个活动提醒"
        else:
            return f"{active_count}个活动提醒"
    
    def save_reminders(self):
        """保存提醒到文件"""
        try:
            data = [reminder.to_dict() for reminder in self.reminders.values()]
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存提醒失败: {e}")
    
    def load_reminders(self):
        """从文件加载提醒"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.reminders = {}
            for item in data:
                reminder = Reminder.from_dict(item)
                self.reminders[reminder.id] = reminder
                
        except FileNotFoundError:
            # 文件不存在，使用空的提醒列表
            self.reminders = {}
        except Exception as e:
            print(f"加载提醒失败: {e}")
            self.reminders = {}
    
    def cleanup_expired_reminders(self):
        """清理过期的单次提醒"""
        now = datetime.now()
        expired_ids = []
        
        for reminder_id, reminder in self.reminders.items():
            if (reminder.type == 'single' and 
                reminder.target_time and 
                now > reminder.target_time and 
                not reminder.is_active):
                expired_ids.append(reminder_id)
        
        for reminder_id in expired_ids:
            self.remove_reminder(reminder_id)
        
        return len(expired_ids)