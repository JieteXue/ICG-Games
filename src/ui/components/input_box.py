
"""
通用文本输入框组件
支持手动输入数字，带验证功能
"""

import pygame
from utils.constants import *

class InputBox:
    """通用文本输入框组件"""
    
    def __init__(self, x, y, width, height, font_manager, 
                 initial_value="1", max_length=4, 
                 validate_func=None, is_numeric=True):
        """
        初始化输入框
        
        Args:
            x, y: 位置
            width, height: 尺寸
            font_manager: 字体管理器
            initial_value: 初始值
            max_length: 最大长度
            validate_func: 验证函数，返回(验证结果, 处理后的值)
            is_numeric: 是否为数字输入框
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.font_manager = font_manager
        self.value = initial_value
        self.active = False
        self.max_length = max_length
        self.validate_func = validate_func
        self.is_numeric = is_numeric
        
        # 输入框样式
        self.bg_color = (40, 50, 65)
        self.active_bg_color = (60, 70, 85)
        self.border_color = ACCENT_COLOR
        self.text_color = TEXT_COLOR
        self.cursor_color = (255, 255, 255)
        
        # 光标状态
        self.cursor_visible = True
        self.cursor_timer = 0
        self.cursor_blink_rate = 30  # 光标闪烁速度
        
        # 文本渲染
        self.text_surface = None
        self._update_text_surface()
        
        # 历史值（用于取消编辑）
        self.original_value = initial_value
        
        # 工具提示
        self.tooltip = "点击输入数字，回车确认，ESC取消"
    
    def handle_event(self, event):
        """处理事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            # 点击输入框激活/取消激活
            if self.rect.collidepoint(event.pos):
                self.active = True
                self.original_value = self.value  # 保存原始值
                return True
            elif self.active:
                self.active = False
                self._apply_validation()
                return True
                
        elif event.type == pygame.KEYDOWN and self.active:
            # 处理键盘输入
            if event.key == pygame.K_RETURN:
                self.active = False
                self._apply_validation()
                return True
            elif event.key == pygame.K_ESCAPE:
                # 取消编辑，恢复原始值
                self.active = False
                self.value = self.original_value
                self._update_text_surface()
                return True
            elif event.key == pygame.K_BACKSPACE:
                # 退格键
                self.value = self.value[:-1]
                self._update_text_surface()
                return True
            else:
                # 输入字符
                char = event.unicode
                if self._is_valid_char(char):
                    if len(self.value) < self.max_length:
                        self.value += char
                        self._update_text_surface()
                        return True
        return False
    
    def _is_valid_char(self, char):
        """检查字符是否有效"""
        if not char:
            return False
            
        if self.is_numeric:
            # 数字输入框只接受数字
            return char.isdigit()
        return True  # 非数字输入框接受任何字符
    
    def _apply_validation(self):
        """应用验证"""
        if self.validate_func:
            is_valid, validated_value = self.validate_func(self.value)
            if is_valid:
                self.value = validated_value
            else:
                # 验证失败，使用默认值
                self.value = "1"
        elif self.is_numeric:
            # 默认的数字验证
            try:
                num = int(self.value)
                if num < 1:
                    self.value = "1"
            except ValueError:
                self.value = "1"
        
        self._update_text_surface()
    
    def _update_text_surface(self):
        """更新文本表面"""
        self.text_surface = self.font_manager.medium.render(
            self.value, True, self.text_color
        )
    
    def update(self):
        """更新状态（光标闪烁）"""
        if self.active:
            self.cursor_timer += 1
            if self.cursor_timer >= self.cursor_blink_rate:
                self.cursor_timer = 0
                self.cursor_visible = not self.cursor_visible
    
    def draw(self, screen):
        """绘制输入框"""
        # 绘制背景
        bg_color = self.active_bg_color if self.active else self.bg_color
        pygame.draw.rect(screen, bg_color, self.rect, border_radius=8)
        
        # 绘制边框
        border_width = 3 if self.active else 2
        pygame.draw.rect(screen, self.border_color, self.rect, border_width, border_radius=8)
        
        # 绘制文本
        text_rect = self.text_surface.get_rect(
            center=(self.rect.centerx, self.rect.centery)
        )
        screen.blit(self.text_surface, text_rect)
        
        # 绘制光标
        if self.active and self.cursor_visible:
            cursor_x = text_rect.right + 2
            if text_rect.right > self.rect.right - 10:
                cursor_x = text_rect.left - 2
            cursor_rect = pygame.Rect(
                cursor_x, self.rect.y + 5, 2, self.rect.height - 10
            )
            pygame.draw.rect(screen, self.cursor_color, cursor_rect)
    
    def get_int_value(self):
        """获取整数值"""
        try:
            return int(self.value)
        except ValueError:
            return 1
    
    def set_value(self, value):
        """设置值"""
        self.value = str(value)
        self._update_text_surface()
    
    def is_active(self):
        """检查是否激活"""
        return self.active


class InputBoxManager:
    """输入框管理器，用于管理多个输入框"""
    
    def __init__(self):
        self.input_boxes = []
    
    def add_input_box(self, input_box):
        """添加输入框"""
        self.input_boxes.append(input_box)
    
    def handle_events(self, event):
        """处理所有输入框的事件"""
        for input_box in self.input_boxes:
            if input_box.handle_event(event):
                # 如果事件被处理，停用其他输入框
                for other_box in self.input_boxes:
                    if other_box != input_box and other_box.active:
                        other_box.active = False
                        other_box._apply_validation()
                return input_box
        return None
    
    def update(self):
        """更新所有输入框"""
        for input_box in self.input_boxes:
            input_box.update()
    
    def draw(self, screen):
        """绘制所有输入框"""
        for input_box in self.input_boxes:
            input_box.draw(screen)
    
    def get_active_box(self):
        """获取当前激活的输入框"""
        for input_box in self.input_boxes:
            if input_box.active:
                return input_box
        return None
    
    def deactivate_all(self):
        """停用所有输入框"""
        for input_box in self.input_boxes:
            if input_box.active:
                input_box.active = False
                input_box._apply_validation()