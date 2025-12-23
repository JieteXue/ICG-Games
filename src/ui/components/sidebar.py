"""
Sidebar Component with toggle functionality and settings integration
"""

import pygame
from utils.constants import *

# 添加SettingsDialog类（内联以避免导入问题）
class SettingsDialog:
    """设置对话框"""
    
    def __init__(self, screen, font_manager, config_manager=None):
        self.screen = screen
        self.font_manager = font_manager
        self.config_manager = config_manager
        self.visible = False
        
        # 设置项 - 如果没有配置管理器，使用默认值
        self.settings = {
            'music_enabled': True,
            'sound_effects_enabled': True,
            'win_indicator_enabled': True,
            'show_creator_credit': True
        }
        
        # 如果有配置管理器，从配置加载
        if config_manager:
            for key in self.settings.keys():
                value = config_manager.get_preference(key)
                if value is not None:
                    self.settings[key] = value
        
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
    
    def handle_event(self, event, mouse_pos=None):
        """处理事件"""
        if not self.visible:
            return False
            
        if mouse_pos is None:
            mouse_pos = pygame.mouse.get_pos()
        
        if event.type == pygame.MOUSEBUTTONDOWN:
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
        if self.config_manager:
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
        self.save_settings()
    
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


class Sidebar:
    """Expandable sidebar with toggle button only visible when collapsed"""
    
    def __init__(self, screen, font_manager, config_manager=None):
        self.screen = screen
        self.font_manager = font_manager
        self.config_manager = config_manager
        self.expanded = False  # 默认不展开
        self.current_width = 0  # 默认宽度为0，完全隐藏
        self.target_width = 0

        # 添加设置对话框
        self.settings_dialog = SettingsDialog(screen, font_manager, config_manager)

        # 假设这些常量存在，如果没有，我们使用默认值
        # 定义侧边栏相关常量（如果constants.py中没有）
        self.SIDEBAR_EXPANDED_WIDTH = getattr(globals(), 'SIDEBAR_EXPANDED_WIDTH', 200)
        self.SIDEBAR_ANIMATION_SPEED = getattr(globals(), 'SIDEBAR_ANIMATION_SPEED', 20)
        self.SIDEBAR_EXPANDED_COLOR = getattr(globals(), 'SIDEBAR_EXPANDED_COLOR', (40, 35, 30))

        # Sidebar position - 初始宽度为0
        self.rect = pygame.Rect(0, 0, 0, SCREEN_HEIGHT)

        # 折叠状态下的切换按钮（独立显示）
        self.toggle_button_rect = pygame.Rect(
            10, 20,  # x=10 向右移动了10像素，y=20 距离顶部20像素
            40, 40  # 增加了切换按钮大小
        )

        # Buttons (only visible when expanded)
        self.buttons = []
        self.button_width = 160  # 增加了按钮宽度
        self.button_height = 45  # 增加了按钮高度
        self.button_spacing = 15  # 增加了按钮间距
        self.create_buttons()

        # Animation state
        self.is_animating = False

        self.key_shortcuts = {
            pygame.K_r: "refresh",  # R键对应Restart
            pygame.K_i: "info",     # I键对应Info
            pygame.K_b: "back",     # B键对应Back
            pygame.K_h: "home",     # H键对应Home
            pygame.K_s: "settings", # S键对应Settings
            pygame.K_t: "toggle",   # T键对应Toggle侧边栏
            pygame.K_ESCAPE: "toggle"  # ESC键也可以切换侧边栏
        }
        
    def create_buttons(self):
        """Create sidebar buttons with text"""
        button_configs = [
            {"name": "back", "display_text": "Back (B)", "tooltip": "Back to mode selection (B键)"},
            {"name": "home", "display_text": "Home (H)", "tooltip": "Back to main menu (H键)"},
            {"name": "refresh", "display_text": "Restart (R)", "tooltip": "Restart current game (R键)"},
            {"name": "info", "display_text": "Info (I)", "tooltip": "Game instructions (I键)"},
            {"name": "settings", "display_text": "Settings (S)", "tooltip": "Game settings (S键)"}
        ]

        start_y = 90  # 提高了起始位置，给标题留更多空间

        for i, config in enumerate(button_configs):
            button_y = start_y + i * (self.button_height + self.button_spacing)
            button = SidebarButton(
                x=10,
                y=button_y,
                width=self.button_width,
                height=self.button_height,
                name=config["name"],
                display_text=config["display_text"],
                tooltip=config["tooltip"],
                font_manager=self.font_manager
            )
            self.buttons.append(button)
    
    def toggle(self):
        """Toggle sidebar expansion"""
        self.expanded = not self.expanded
        self.target_width = self.SIDEBAR_EXPANDED_WIDTH if self.expanded else 0
        self.is_animating = True
        return "toggle"
    
    def update(self):
        """Update sidebar animation"""
        if self.is_animating:
            if self.current_width < self.target_width:
                # 展开动画
                self.current_width = min(self.current_width + self.SIDEBAR_ANIMATION_SPEED, self.target_width)
            elif self.current_width > self.target_width:
                # 折叠动画
                self.current_width = max(self.current_width - self.SIDEBAR_ANIMATION_SPEED, self.target_width)
            else:
                self.is_animating = False
            
            self.rect.width = self.current_width
            
            # 动画期间动态更新切换按钮位置
            if self.expanded:
                # 展开时按钮从左侧逐渐移到右侧
                # 计算动画进度比例
                if self.SIDEBAR_EXPANDED_WIDTH > 0:  # 避免除以0
                    progress = self.current_width / self.SIDEBAR_EXPANDED_WIDTH
                    start_x = 10  # 折叠时的位置
                    end_x = self.SIDEBAR_EXPANDED_WIDTH - 50  # 展开时的位置
                    self.toggle_button_rect.x = start_x + (end_x - start_x) * progress
            else:
                # 折叠时按钮从右侧逐渐移到左侧
                if self.SIDEBAR_EXPANDED_WIDTH > 0:  # 避免除以0
                    progress = (self.SIDEBAR_EXPANDED_WIDTH - self.current_width) / self.SIDEBAR_EXPANDED_WIDTH
                    start_x = self.SIDEBAR_EXPANDED_WIDTH - 50  # 展开时的位置
                    end_x = 10  # 折叠时的位置
                    self.toggle_button_rect.x = start_x + (end_x - start_x) * progress
        
        # Update button positions based on sidebar width
        for button in self.buttons:
            # 只在展开且宽度足够时才显示按钮
            button.set_visible(self.expanded and self.current_width >= self.SIDEBAR_EXPANDED_WIDTH - 10)
            if self.expanded and self.current_width >= self.SIDEBAR_EXPANDED_WIDTH - 10:
                button.update_position(self.current_width)
    
    def handle_event(self, event, mouse_pos):
        """Handle sidebar events"""
        mouse_pos = pygame.mouse.get_pos()
        
        # 首先检查设置对话框事件（如果可见）
        if self.settings_dialog.visible:
            if self.settings_dialog.handle_event(event, mouse_pos):
                return "settings_handled"
        
        # Check keyboard shortcuts
        if event.type == pygame.KEYDOWN:
            if event.key in self.key_shortcuts:
                action = self.key_shortcuts[event.key]
                if action == "toggle":
                    return self.toggle()
                elif action == "settings":
                    # 按下S键打开设置
                    self.settings_dialog.show()
                    return "settings"
                return action

        # Check toggle button
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.toggle_button_rect.collidepoint(mouse_pos):
                return self.toggle()

            # Check sidebar buttons if expanded and visible
            if self.expanded and self.current_width >= self.SIDEBAR_EXPANDED_WIDTH - 10:
                for button in self.buttons:
                    if button.is_clicked(event):
                        if button.name == "settings":
                            # 点击设置按钮，显示设置对话框
                            self.settings_dialog.show()
                            return "settings"
                        return button.name

        # Handle hover
        if event.type == pygame.MOUSEMOTION:
            for button in self.buttons:
                button.update_hover(mouse_pos)

        return None
    
    def draw(self):
        """Draw the sidebar"""
        # 只有在展开或动画过程中且宽度大于0时才绘制侧边栏背景
        if (self.expanded or self.is_animating) and self.current_width > 0:
            # 绘制背景（宽度会动画变化）
            color = self.SIDEBAR_EXPANDED_COLOR if self.expanded else (self.SIDEBAR_EXPANDED_COLOR[0], self.SIDEBAR_EXPANDED_COLOR[1], self.SIDEBAR_EXPANDED_COLOR[2], 150)
            pygame.draw.rect(self.screen, color, self.rect)
            
            # 绘制边框
            if self.expanded:
                pygame.draw.rect(self.screen, ACCENT_COLOR, self.rect, 2)
            
            # Draw buttons if expanded and wide enough
            if self.expanded and self.current_width >= self.SIDEBAR_EXPANDED_WIDTH - 10:
                for button in self.buttons:
                    button.draw(self.screen)
                
                # Draw sidebar title
                if self.current_width >= 120:
                    title_font = pygame.font.SysFont('Arial', 18, bold=True)  # 增加了标题字体大小
                    title_text = title_font.render("NAVIGATION", True, ACCENT_COLOR)
                    title_rect = title_text.get_rect(center=(self.current_width // 2, 50))  # 调整了标题位置
                    self.screen.blit(title_text, title_rect)
        
        # 总是绘制切换按钮
        self._draw_toggle_button()
        
        # 绘制设置对话框（如果可见）
        self.settings_dialog.draw()
    
    def _draw_toggle_button(self):
        """Draw the toggle button"""
        # Button background (总是显示)
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.toggle_button_rect.collidepoint(mouse_pos)
        
        # Button background with shadow effect
        if is_hovered:
            # Shadow for hover effect
            shadow_rect = self.toggle_button_rect.move(2, 2)
            pygame.draw.rect(self.screen, (0, 0, 0, 100), shadow_rect, border_radius=8)  # 增加了圆角半径
        
        # Button background
        button_color = BUTTON_HOVER_COLOR if is_hovered else ACCENT_COLOR
        pygame.draw.rect(self.screen, button_color, self.toggle_button_rect, border_radius=8)  # 增加了圆角半径
        
        # Hamburger or X icon
        center_x = self.toggle_button_rect.centerx
        center_y = self.toggle_button_rect.centery
        
        icon_color = (255, 255, 255)
        
        if self.expanded:
            # Draw X icon when expanded
            offset = 10  # 增加了X图标的大小
            pygame.draw.line(self.screen, icon_color, 
                           (center_x - offset, center_y - offset),
                           (center_x + offset, center_y + offset), 4)  # 增加了线宽
            pygame.draw.line(self.screen, icon_color,
                           (center_x - offset, center_y + offset),
                           (center_x + offset, center_y - offset), 4)  # 增加了线宽
        else:
            # Draw hamburger icon when collapsed (三条横线)
            bar_height = 3  # 增加了线条高度
            bar_spacing = 5  # 增加了线条间距
            for i in range(-1, 2):
                y = center_y + i * bar_spacing
                pygame.draw.line(self.screen, icon_color,
                               (center_x - 10, y),  # 增加了线条长度
                               (center_x + 10, y), bar_height)  # 增加了线条长度
    
    def is_mouse_over(self, mouse_pos):
        """Check if mouse is over sidebar area"""
        # 检查侧边栏区域
        if self.current_width > 0 and self.rect.collidepoint(mouse_pos):
            return True
        # 检查切换按钮
        if self.toggle_button_rect.collidepoint(mouse_pos):
            return True
        return False
    
    def get_button_position(self, button_name):
        """Get position of a specific button"""
        for button in self.buttons:
            if button.name == button_name:
                return button.rect
        return None
    
    def is_settings_dialog_visible(self):
        """检查设置对话框是否可见"""
        return self.settings_dialog.visible
    
    def get_win_indicator_enabled(self):
        """获取胜利指示器是否启用"""
        return self.settings_dialog.get_setting('win_indicator_enabled')


class SidebarButton:
    """Button for sidebar - now shows text instead of icons"""
    
    def __init__(self, x, y, width, height, name, display_text, tooltip, font_manager):
        self.rect = pygame.Rect(x, y, width, height)
        self.name = name
        self.display_text = display_text  # 要显示的文字
        self.tooltip = tooltip
        self.font_manager = font_manager
        self.hovered = False
        self.visible = False
        self.tooltip_timer = 0
        
    def set_visible(self, visible):
        """Set button visibility"""
        self.visible = visible
    
    def update_position(self, sidebar_width):
        """Update button position based on sidebar width"""
        self.rect.x = (sidebar_width - self.rect.width) // 2
    
    def update_hover(self, mouse_pos):
        """Update hover state"""
        self.hovered = self.visible and self.rect.collidepoint(mouse_pos)
    
    def is_clicked(self, event):
        """Check if button was clicked"""
        return (event.type == pygame.MOUSEBUTTONDOWN and 
                event.button == 1 and 
                self.hovered and 
                self.visible)
    
    def draw(self, surface):
        """Draw the button with text"""
        if not self.visible:
            return
        
        # Button background
        color = BUTTON_HOVER_COLOR if self.hovered else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect, border_radius=10)  # 增加了圆角半径
        
        # Button border
        border_color = ACCENT_COLOR if self.hovered else (100, 140, 200)
        pygame.draw.rect(surface, border_color, self.rect, 2, border_radius=10)  # 增加了圆角半径
        
        # Draw text
        self._draw_text(surface)
        
        # Draw tooltip
        self._draw_tooltip(surface)
    
    def _draw_text(self, surface):
        """Draw button text"""
        text_color = (255, 255, 255) if self.hovered else (220, 230, 240)

        text_surface = None
        if hasattr(self.font_manager, 'medium'):
            text_surface = self.font_manager.medium.render(self.display_text, True, text_color)
        else:
            text_surface = pygame.font.SysFont('Arial', 18, bold=True).render(self.display_text, True, text_color)

        if text_surface is not None:
            text_rect = text_surface.get_rect(center=self.rect.center)

            if self.hovered:
                shadow_color = (50, 70, 100)
                shadow_surface = None
                if hasattr(self.font_manager, 'medium'):
                    shadow_surface = self.font_manager.medium.render(self.display_text, True, shadow_color)
                else:
                    shadow_surface = pygame.font.SysFont('Arial', 18, bold=True).render(self.display_text, True, shadow_color)

                if shadow_surface is not None:
                    shadow_rect = text_rect.move(1, 1)
                    surface.blit(shadow_surface, shadow_rect)

            surface.blit(text_surface, text_rect)
    
    def _draw_tooltip(self, surface):
        """Draw tooltip if hovered"""
        if not self.hovered or not self.tooltip:
            return
        
        self.tooltip_timer += 1
        if self.tooltip_timer > 20:  # Show after 0.5 seconds
            tooltip_font = pygame.font.SysFont('Arial', 14)
            tooltip_text = tooltip_font.render(self.tooltip, True, (255, 255, 255))
            tooltip_rect = tooltip_text.get_rect()
            
            tooltip_x = self.rect.right + 10
            tooltip_y = self.rect.centery - tooltip_rect.height // 2
            
            # Adjust if tooltip goes off screen
            if tooltip_x + tooltip_rect.width > SCREEN_WIDTH:
                tooltip_x = self.rect.left - tooltip_rect.width - 10
            
            tooltip_bg = pygame.Rect(
                tooltip_x - 6, tooltip_y - 4,
                tooltip_rect.width + 12, tooltip_rect.height + 8
            )
            pygame.draw.rect(surface, (40, 40, 60), tooltip_bg, border_radius=6)
            pygame.draw.rect(surface, ACCENT_COLOR, tooltip_bg, 1, border_radius=6)
            surface.blit(tooltip_text, (tooltip_x, tooltip_y))
        else:
            self.tooltip_timer = 0