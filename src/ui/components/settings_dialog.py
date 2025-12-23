"""
设置对话框组件
包含游戏设置选项：背景音乐、音效、胜利指示器开关
"""

import pygame
from utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT

class SettingsDialog:
    """设置对话框"""
    
    def __init__(self, screen, font_manager, config_manager):
        self.screen = screen
        self.font_manager = font_manager
        self.config_manager = config_manager
        self.visible = False
        
        # 设置项
        self.settings = {
            'music_enabled': self.config_manager.get_preference('music_enabled', True),
            'sound_effects_enabled': self.config_manager.get_preference('sound_effects_enabled', True),
            'win_indicator_enabled': self.config_manager.get_preference('win_indicator_enabled', True),
            'show_creator_credit': self.config_manager.get_preference('show_creator_credit', True)
        }
        
        # 对话框尺寸
        self.width = 500
        self.height = 400
        self.x = (SCREEN_WIDTH - self.width) // 2
        self.y = (SCREEN_HEIGHT - self.height) // 2
        
        # 创建按钮
        self.create_buttons()
        
        # 标题
        self.title = "游戏设置"
        
        # 设置项标签
        self.setting_labels = [
            "背景音乐",
            "音效",
            "胜利/失败指示器",
            "显示创作者信息"
        ]
        
        # 设置项描述
        self.setting_descriptions = [
            "打开或关闭背景音乐",
            "打开或关闭游戏音效",
            "显示当前是否为必胜/必败位置的提示",
            "在游戏界面显示创作者信息"
        ]
        
        # 按钮样式
        self.button_on_color = (100, 200, 100)  # 绿色
        self.button_off_color = (200, 100, 100)  # 红色
        self.button_border_color = (50, 50, 70)
        self.button_text_color = (255, 255, 255)
        
    def create_buttons(self):
        """创建设置项按钮"""
        self.setting_buttons = []
        self.toggle_buttons = []
        
        # 每个设置项的位置
        start_y = self.y + 80
        spacing = 70
        
        for i in range(4):
            # 设置项标签区域
            label_rect = pygame.Rect(self.x + 30, start_y + i * spacing, 200, 40)
            self.setting_buttons.append(label_rect)
            
            # 开关按钮
            toggle_rect = pygame.Rect(self.x + self.width - 130, start_y + i * spacing, 100, 40)
            self.toggle_buttons.append(toggle_rect)
        
        # 关闭按钮
        self.close_button = pygame.Rect(
            self.x + self.width // 2 - 100,
            self.y + self.height - 60,
            200, 50
        )
    
    def handle_event(self, event):
        """处理事件"""
        if not self.visible:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # 检查开关按钮
            for i, toggle_rect in enumerate(self.toggle_buttons):
                if toggle_rect.collidepoint(mouse_pos):
                    self.toggle_setting(i)
                    return True
            
            # 检查关闭按钮
            if self.close_button.collidepoint(mouse_pos):
                self.visible = False
                self.save_settings()
                return True
            
            # 点击对话框外部关闭
            if not self.is_inside_dialog(mouse_pos):
                self.visible = False
                self.save_settings()
                return True
                
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.visible = False
                self.save_settings()
                return True
                
        return False
    
    def toggle_setting(self, setting_index):
        """切换设置"""
        settings_keys = ['music_enabled', 'sound_effects_enabled', 
                        'win_indicator_enabled', 'show_creator_credit']
        
        if setting_index < len(settings_keys):
            key = settings_keys[setting_index]
            self.settings[key] = not self.settings[key]
    
    def is_inside_dialog(self, pos):
        """检查点是否在对话框内"""
        return (self.x <= pos[0] <= self.x + self.width and
                self.y <= pos[1] <= self.y + self.height)
    
    def save_settings(self):
        """保存设置到配置文件"""
        for key, value in self.settings.items():
            self.config_manager.set_preference(key, value)
        self.config_manager.save_preferences()
    
    def get_setting(self, key):
        """获取设置值"""
        return self.settings.get(key, True)
    
    def show(self):
        """显示对话框"""
        self.visible = True
    
    def hide(self):
        """隐藏对话框"""
        self.visible = False
    
    def draw(self):
        """绘制对话框"""
        if not self.visible:
            return
        
        # 绘制半透明背景
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # 绘制对话框背景
        dialog_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(self.screen, (50, 45, 40), dialog_rect, border_radius=15)
        pygame.draw.rect(self.screen, (180, 150, 110), dialog_rect, 3, border_radius=15)
        
        # 绘制标题
        title_text = self.font_manager.large.render(self.title, True, (240, 230, 220))
        title_rect = title_text.get_rect(center=(self.x + self.width // 2, self.y + 40))
        self.screen.blit(title_text, title_rect)
        
        # 绘制设置项
        settings_keys = ['music_enabled', 'sound_effects_enabled', 
                        'win_indicator_enabled', 'show_creator_credit']
        
        for i in range(4):
            # 绘制设置标签
            label_text = self.font_manager.medium.render(
                self.setting_labels[i], True, (240, 230, 220)
            )
            self.screen.blit(label_text, (self.x + 40, self.y + 90 + i * 70))
            
            # 绘制设置描述
            desc_text = self.font_manager.small.render(
                self.setting_descriptions[i], True, (200, 190, 170)
            )
            self.screen.blit(desc_text, (self.x + 40, self.y + 120 + i * 70))
            
            # 绘制开关按钮
            toggle_rect = self.toggle_buttons[i]
            is_on = self.settings[settings_keys[i]]
            
            # 按钮背景
            button_color = self.button_on_color if is_on else self.button_off_color
            pygame.draw.rect(self.screen, button_color, toggle_rect, border_radius=8)
            pygame.draw.rect(self.screen, self.button_border_color, toggle_rect, 2, border_radius=8)
            
            # 按钮文本
            button_text = "开" if is_on else "关"
            text_color = self.button_text_color
            text_surface = self.font_manager.medium.render(button_text, True, text_color)
            text_rect = text_surface.get_rect(center=toggle_rect.center)
            self.screen.blit(text_surface, text_rect)
        
        # 绘制关闭按钮
        pygame.draw.rect(self.screen, (40, 50, 65), self.close_button, border_radius=10)
        pygame.draw.rect(self.screen, (180, 150, 110), self.close_button, 2, border_radius=10)
        
        close_text = self.font_manager.medium.render("关闭设置", True, (240, 230, 220))
        close_rect = close_text.get_rect(center=self.close_button.center)
        self.screen.blit(close_text, close_rect)
        
        # 绘制提示
        hint_text = self.font_manager.small.render(
            "提示：点击开关按钮切换状态，点击外部或按ESC关闭", 
            True, (200, 190, 170)
        )
        hint_rect = hint_text.get_rect(center=(self.x + self.width // 2, self.y + self.height - 20))
        self.screen.blit(hint_text, hint_rect)


class ToggleButton:
    """自定义开关按钮"""
    
    def __init__(self, x, y, width, height, initial_state=True):
        self.rect = pygame.Rect(x, y, width, height)
        self.state = initial_state
        self.on_color = (100, 200, 100)
        self.off_color = (200, 100, 100)
        self.knob_color = (255, 255, 255)
        self.border_color = (50, 50, 70)
        
    def handle_event(self, event):
        """处理点击事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.state = not self.state
                return True
        return False
    
    def draw(self, screen, font_manager):
        """绘制开关按钮"""
        # 绘制背景
        bg_color = self.on_color if self.state else self.off_color
        pygame.draw.rect(screen, bg_color, self.rect, border_radius=self.rect.height // 2)
        pygame.draw.rect(screen, self.border_color, self.rect, 2, border_radius=self.rect.height // 2)
        
        # 绘制滑块
        knob_radius = self.rect.height // 2 - 4
        if self.state:  # 开状态，滑块在右边
            knob_center = (self.rect.right - knob_radius - 4, self.rect.centery)
        else:  # 关状态，滑块在左边
            knob_center = (self.rect.left + knob_radius + 4, self.rect.centery)
        
        pygame.draw.circle(screen, self.knob_color, knob_center, knob_radius)
        
        # 绘制状态文本
        state_text = "开" if self.state else "关"
        text_color = (255, 255, 255)
        text_surface = font_manager.small.render(state_text, True, text_color)
        
        # 文本位置
        if self.state:
            text_x = self.rect.left + 15
        else:
            text_x = self.rect.right - 25
        
        text_rect = text_surface.get_rect(centery=self.rect.centery, x=text_x)
        screen.blit(text_surface, text_rect)