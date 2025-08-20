# -*- coding: utf-8 -*-
"""
宠物状态枚举
定义宠物的三种状态：正面、拖拽、下落
"""

from enum import Enum

class PetState(Enum):
    """宠物状态枚举类"""
    
    NORMAL = "normal"      # 正面状态
    DRAGGING = "dragging"  # 拖拽状态
    FALLING = "falling"    # 下落状态
    
    def __str__(self):
        """返回状态的字符串表示"""
        return self.value
    
    @classmethod
    def get_all_states(cls):
        """获取所有状态列表"""
        return [state.value for state in cls]