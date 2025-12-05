# [file name]: utils/key_repeat.py
"""
通用按键重复管理器 - 添加双击支持
"""

import pygame

class KeyRepeatManager:
    """管理按键重复行为和双击检测的通用类"""
    
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
        
        # 双击支持
        self.last_click_time = 0
        self.double_click_delay = 500  # 双击延迟（毫秒）
        self.last_click_position = None
    
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
    
    def handle_mouse_click(self, event, position, callback_dict):
        """
        处理鼠标点击事件，支持双击
        
        Args:
            event: pygame鼠标事件
            position: 点击位置标识（如位置索引）
            callback_dict: 回调函数字典
                {'single_click': single_callback, 'double_click': double_callback}
        """
        if (event.type == pygame.MOUSEBUTTONDOWN and 
            event.button == 1 and 
            'single_click' in callback_dict):
            
            current_time = pygame.time.get_ticks()
            
            # 检查是否为双击（相同位置且在时间窗口内）
            is_double_click = (current_time - self.last_click_time < self.double_click_delay and 
                             position == self.last_click_position)
            
            if is_double_click and 'double_click' in callback_dict:
                # 执行双击回调
                callback_dict['double_click']()
                self.last_click_time = 0  # 重置双击计时器
                self.last_click_position = None
            else:
                # 执行单点击回调
                callback_dict['single_click']()
                self.last_click_time = current_time
                self.last_click_position = position
    
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