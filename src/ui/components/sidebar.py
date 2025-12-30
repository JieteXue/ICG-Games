"""
Sidebar Component with toggle functionality
"""

import pygame
from utils.constants import *
from ui.components.settings_panel import SettingsPanel
from ui.components.music_panel import MusicPanel
from utils.music_manager import music_manager

class Sidebar:
    """Expandable sidebar with toggle button only visible when collapsed"""
    
    def __init__(self, screen, font_manager):
        self.screen = screen
        self.font_manager = font_manager
        self.expanded = False  # 默认不展开
        self.current_width = 0  # 默认宽度为0，完全隐藏
        self.target_width = 0
        self.settings_panel = SettingsPanel(screen, font_manager)
        self.music_panel = MusicPanel(screen, font_manager, music_manager)#新增音乐面板
        
        # 从设置面板获取初始设置
        self.settings = self.settings_panel.get_settings()
        
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
            pygame.K_m: "music",    # M键对应Music
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
            {"name": "settings", "display_text": "Settings (S)", "tooltip": "Game settings (S键)"},
            {"name": "music", "display_text": "Music (M)", "tooltip": "Music selection (M键)"}  # 新增音乐按钮
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
        self.target_width = SIDEBAR_EXPANDED_WIDTH if self.expanded else 0
        self.is_animating = True
        return "toggle"
    
    def update(self):
        """Update sidebar animation"""
        if self.is_animating:
            if self.current_width < self.target_width:
                # 展开动画
                self.current_width = min(self.current_width + SIDEBAR_ANIMATION_SPEED, self.target_width)
            elif self.current_width > self.target_width:
                # 折叠动画
                self.current_width = max(self.current_width - SIDEBAR_ANIMATION_SPEED, self.target_width)
            else:
                self.is_animating = False
            
            self.rect.width = self.current_width
            
            # 动画期间动态更新切换按钮位置
            if self.expanded:
                # 展开时按钮从左侧逐渐移到右侧
                # 计算动画进度比例
                if SIDEBAR_EXPANDED_WIDTH > 0:  # 避免除以0
                    progress = self.current_width / SIDEBAR_EXPANDED_WIDTH
                    start_x = 10  # 折叠时的位置
                    end_x = SIDEBAR_EXPANDED_WIDTH - 50  # 展开时的位置
                    self.toggle_button_rect.x = start_x + (end_x - start_x) * progress
            else:
                # 折叠时按钮从右侧逐渐移到左侧
                if SIDEBAR_EXPANDED_WIDTH > 0:  # 避免除以0
                    progress = (SIDEBAR_EXPANDED_WIDTH - self.current_width) / SIDEBAR_EXPANDED_WIDTH
                    start_x = SIDEBAR_EXPANDED_WIDTH - 50  # 展开时的位置
                    end_x = 10  # 折叠时的位置
                    self.toggle_button_rect.x = start_x + (end_x - start_x) * progress
        
        # Update button positions based on sidebar width
        for button in self.buttons:
            # 只在展开且宽度足够时才显示按钮
            button.set_visible(self.expanded and self.current_width >= SIDEBAR_EXPANDED_WIDTH - 10)
            if self.expanded and self.current_width >= SIDEBAR_EXPANDED_WIDTH - 10:
                button.update_position(self.current_width)
    
    def handle_event(self, event, mouse_pos):
        """Handle sidebar events"""
        # 如果音乐面板可见，优先处理音乐面板事件
        if self.music_panel.visible:
            result = self.music_panel.handle_event(event, mouse_pos)
            if result:
                if result.startswith("music_selected_"):
                    # 音乐被选中
                    music_id = int(result.replace("music_selected_", ""))
                    print(f"Music selected: {music_id}")
                elif result == "music_locked":
                    print("This music is locked!")
                elif result == "music_panel_closed":
                    self.music_panel.hide()
                return result
            return None
        # 如果设置面板可见，优先处理设置面板事件
        if self.settings_panel.visible:
            result = self.settings_panel.handle_event(event, mouse_pos)
            if result:
                if result.startswith("setting_changed_"):
                    # 更新本地设置
                    setting_name = result.replace("setting_changed_", "")
                    self.settings[setting_name] = self.settings_panel.settings.get(setting_name, False)
                    # 传递设置变化事件给游戏
                    return result
                elif result == "back_from_settings":
                    return "settings_closed"  # 返回特定事件表示设置面板已关闭
                elif result == "sponsor_clicked":
                    return "sponsor_clicked"
                elif result == "sponsor_error":
                    return "sponsor_error"
            return None  # 设置面板可见时，不处理其他事件

        # 原有的键盘快捷键检查
        if event.type == pygame.KEYDOWN:
            if event.key in self.key_shortcuts:
                action = self.key_shortcuts[event.key]
                if action == "toggle":
                    return self.toggle()
                elif action == "settings":
                    # 按S键打开设置面板
                    self.settings_panel.show()
                    return "settings_opened"
                elif action == "music":  # 新增：按M键打开音乐面板
                    self.music_panel.toggle_visibility()
                    return "music_panel_toggled"
                return action
            # ESC键处理
            if event.key == pygame.K_ESCAPE:
                if self.music_panel.visible:
                    self.music_panel.hide()
                    return "music_panel_closed"
                elif self.settings_panel.visible:
                    self.settings_panel.hide()
                    return "settings_closed"


        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # 如果侧边栏展开，点击外部区域则收起侧边栏
            if self.expanded and not self.is_mouse_over(mouse_pos):
                # 检查是否点击了其他UI元素（比如游戏区域）
                # 这里可以根据需要添加额外检查
                return self.toggle()  # 收起侧边栏

            # 检查切换按钮
            if self.toggle_button_rect.collidepoint(mouse_pos):
                return self.toggle()

            # 检查侧边栏按钮（如果展开且可见）
            if self.expanded and self.current_width >= SIDEBAR_EXPANDED_WIDTH - 10:
                for button in self.buttons:
                    if button.is_clicked(event):
                        if button.name == "settings":
                            # 点击settings按钮时，显示设置面板
                            self.settings_panel.show()
                            return "settings_opened"
                        elif button.name == "music":  # 新增：音乐按钮
                            self.music_panel.toggle_visibility()
                            return "music_panel_toggled"
                        return button.name

        # 处理悬停
        if event.type == pygame.MOUSEMOTION:
            for button in self.buttons:
                button.update_hover(mouse_pos)

        return None
    
    def draw(self):
        """Draw the sidebar"""
        # 如果音乐面板可见，先绘制音乐面板
        if self.music_panel.visible:
            self.music_panel.draw()
            return
        # 如果设置面板可见，先绘制设置面板
        if self.settings_panel.visible:
            self.settings_panel.draw()
            return  # 绘制设置面板后，不绘制侧边栏背景
        
        # 只有在展开或动画过程中且宽度大于0时才绘制侧边栏背景
        if (self.expanded or self.is_animating) and self.current_width > 0:
            # 绘制背景（宽度会动画变化）
            color = SIDEBAR_EXPANDED_COLOR if self.expanded else (SIDEBAR_EXPANDED_COLOR[0], SIDEBAR_EXPANDED_COLOR[1], SIDEBAR_EXPANDED_COLOR[2], 150)
            pygame.draw.rect(self.screen, color, self.rect)
            
            # 绘制边框
            if self.expanded:
                pygame.draw.rect(self.screen, ACCENT_COLOR, self.rect, 2)
            
            # Draw buttons if expanded and wide enough
            if self.expanded and self.current_width >= SIDEBAR_EXPANDED_WIDTH - 10:
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
        # 检查切换按钮（无论是否展开都检查）
        if self.toggle_button_rect.collidepoint(mouse_pos):
            return True
        # 检查侧边栏按钮（如果展开且可见）
        if self.expanded and self.current_width >= SIDEBAR_EXPANDED_WIDTH - 10:
            for button in self.buttons:
                if button.rect.collidepoint(mouse_pos):
                    return True
        return False
    
    def get_button_position(self, button_name):
        """Get position of a specific button"""
        for button in self.buttons:
            if button.name == button_name:
                return button.rect
        return None
    
    def get_settings(self):
        """获取当前设置"""
        return self.settings_panel.get_settings()
    
    def set_settings(self, settings):
        """更新设置"""
        self.settings_panel.set_settings(settings)
        self.settings = settings


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