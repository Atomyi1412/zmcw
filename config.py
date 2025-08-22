# -*- coding: utf-8 -*-
"""
桌面宠物配置文件
定义窗口、图像、动画等配置参数
"""

class PetConfig:
    """宠物配置类"""
    
    # 窗口配置
    WINDOW_WIDTH = 100
    WINDOW_HEIGHT = 100
    INITIAL_X_OFFSET = 150  # 距离右边缘的距离
    INITIAL_Y_OFFSET = 150  # 距离底边缘的距离
    
    # 图像配置
    IMAGE_PATHS = {
        'normal': 'assets/pet_normal.png',
        'dragging': 'assets/pet_dragging.png',
        'falling': 'assets/pet_falling.png'
    }
    
    # 动画配置
    FALL_DURATION = 1000  # 下落动画时长（毫秒）
    BOUNCE_HEIGHT = 50    # 反弹高度（像素）
    GRAVITY_ACCELERATION = 9.8  # 重力加速度模拟

    # 叶子飘落效果（新增，可调）
    LEAF_FALL_DURATION = 3000       # 叶子飘落总时长（毫秒），越大越慢
    LEAF_SWAY_AMPLITUDE = 35        # 左右摆动幅度（像素）
    LEAF_SWAY_PERIOD_MS = 1200      # 左右摆动周期（毫秒），越小摆动越快
    
    # 交互配置
    DRAG_THRESHOLD = 5    # 拖拽触发阈值（像素）
    SCREEN_TOP_THRESHOLD = 0.5  # 屏幕上半部分阈值
    
    # 提醒功能配置（2.0版本新增）
    REMINDER_DIALOG_WIDTH = 300   # 提醒对话框宽度
    REMINDER_DIALOG_HEIGHT = 200  # 提醒对话框高度
    REMINDER_MESSAGE_DURATION = 5000  # 提醒消息显示时长（毫秒）
    PET_REMINDER_OFFSET = 50      # 宠物延迟提醒窗口的偏移距离
    
    # 循环提醒功能配置（2.1版本新增）
    DEFAULT_REPEAT_INTERVAL = 60  # 默认循环提醒间隔（分钟）
    MIN_REPEAT_INTERVAL = 1       # 最小循环提醒间隔（分钟）
    MAX_REPEAT_INTERVAL = 1440    # 最大循环提醒间隔（分钟，24小时）
    REPEAT_REMINDER_UNITS = ['分钟', '小时']  # 循环提醒时间单位选项
    
    # 设置功能配置（2.1版本新增）
    ALWAYS_ON_TOP = True          # 默认置顶显示
    SETTINGS_DIALOG_WIDTH = 460   # 设置对话框宽度（原为350，放大以容纳更宽的输入框）
    SETTINGS_DIALOG_HEIGHT = 360  # 设置对话框高度（加大以容纳更舒适的行间距）

    # 个性化配置（新增）
    DEFAULT_PET_NAME = '小乔治'   # 默认宠物名称
    
    # 宠物外观配置（新增）
    DEFAULT_PET_SCALE = 1.0       # 默认宠物缩放比例（1.0为原始大小）
    MIN_PET_SCALE = 0.5           # 最小缩放比例
    MAX_PET_SCALE = 2.0           # 最大缩放比例
    
    # 交互行为配置（新增）
    DEFAULT_AUTO_FALL = True      # 默认启用自动下落功能
    DEFAULT_AUTO_START = False    # 默认不开机自启动
    
    # 多提醒管理功能配置（2.2版本新增）
    REMINDER_LIST_DIALOG_WIDTH = 700    # 提醒列表对话框宽度
    REMINDER_LIST_DIALOG_HEIGHT = 500   # 提醒列表对话框高度
    REMINDER_EDIT_DIALOG_WIDTH = 400    # 提醒编辑对话框宽度
    REMINDER_EDIT_DIALOG_HEIGHT = 350   # 提醒编辑对话框高度
    REMINDER_DATA_FILE = 'reminders.json'  # 提醒数据文件名
    MAX_REMINDER_TITLE_LENGTH = 50      # 提醒标题最大长度
    MAX_REMINDER_CONTENT_LENGTH = 200   # 提醒内容最大长度
    AUTO_CLEANUP_EXPIRED_DAYS = 7       # 自动清理过期提醒的天数