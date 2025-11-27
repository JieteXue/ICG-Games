"""
通用按键重复管理器
为所有游戏提供一致的按键重复行为
"""

import pygame

class KeyRepeatManager:
    """管理按键重复行为的通用类"""
    
    def __init__(self):
        self.key_repeat_timer = 0
        self.initial_repeat_delay = 20  # 首次重复延迟（帧数）
        self.continuous_repeat_delay = 3  # 连续重复延迟（帧数）
        self.last_key = None
        self.is_initial_repeat = True  # 标记是否为首次重复
        self.enabled_keys = {
            pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN,
            pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d  # 添加WASD支持
        }
    
    def handle_key_event(self, event, callback_dict):
        """
        处理键盘事件
        
        Args:
            event: pygame键盘事件
            callback_dict: 按键到回调函数的映射字典
                {pygame.K_LEFT: left_callback, ...}
        """
        if event.type == pygame.KEYDOWN:
            if event.key in self.enabled_keys and event.key in callback_dict:
                # 立即执行一次回调
                callback_dict[event.key]()
                self.last_key = event.key
                self.key_repeat_timer = 0
                self.is_initial_repeat = True
        
        elif event.type == pygame.KEYUP:
            if event.key in self.enabled_keys and event.key == self.last_key:
                self._reset_state()
    
    def update(self, callback_dict):
        """
        更新按键重复状态（每帧调用）
        
        Args:
            callback_dict: 按键到回调函数的映射字典
        """
        if self.last_key is not None and self.last_key in callback_dict:
            self.key_repeat_timer += 1
            
            # 根据是否为首次重复选择不同的延迟
            current_delay = (self.initial_repeat_delay 
                           if self.is_initial_repeat 
                           else self.continuous_repeat_delay)
            
            if self.key_repeat_timer >= current_delay:
                # 执行重复动作
                callback_dict[self.last_key]()
                
                # 重置计时器，如果这是首次重复，则切换到连续重复模式
                self.key_repeat_timer = 0
                if self.is_initial_repeat:
                    self.is_initial_repeat = False
    
    def _reset_state(self):
        """重置状态"""
        self.last_key = None
        self.key_repeat_timer = 0
        self.is_initial_repeat = True
    
    def add_enabled_key(self, key):
        """添加支持的按键"""
        self.enabled_keys.add(key)
    
    def remove_enabled_key(self, key):
        """移除支持的按键"""
        self.enabled_keys.discard(key)
    
    def set_delays(self, initial_delay=20, continuous_delay=5):
        """设置延迟时间"""
        self.initial_repeat_delay = initial_delay
        self.continuous_repeat_delay = continuous_delay