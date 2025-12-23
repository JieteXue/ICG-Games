"""
Sidebar Component with toggle functionality
"""

import pygame
from abc import ABC, abstractmethod
from utils.constants import *

class Sidebar:
    """Expandable sidebar with toggle button only visible when collapsed"""
    
    def __init__(self, screen, font_manager):
        self.screen = screen
        self.font_manager = font_manager
        self.expanded = False  # 默认不展开
        self.current_width = 0  # 默认宽度为0，完全隐藏
        self.target_width = 0

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
        # Check keyboard shortcuts
        if event.type == pygame.KEYDOWN:
            if event.key in self.key_shortcuts:
                action = self.key_shortcuts[event.key]
                if action == "toggle":
                    return self.toggle()
                return action

        # Check toggle button
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.toggle_button_rect.collidepoint(mouse_pos):
                return self.toggle()

            # Check sidebar buttons if expanded and visible
            if self.expanded and self.current_width >= SIDEBAR_EXPANDED_WIDTH - 10:
                for button in self.buttons:
                    if button.is_clicked(event):
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

"""
侧边栏组件 - 更新以支持设置对话框
"""

import pygame
import math
from utils.constants import *

class Sidebar:
    """侧边栏组件，包含导航按钮和设置功能"""
    
    def __init__(self, screen, font_manager, config_manager=None):
        self.screen = screen
        self.font_manager = font_manager
        self.config_manager = config_manager
        
        # 侧边栏状态
        self.expanded = True
        self.width = SIDEBAR_WIDTH if self.expanded else SIDEBAR_COLLAPSED_WIDTH
        self.height = SCREEN_HEIGHT
        self.x = SCREEN_WIDTH - self.width
        self.y = 0
        
        # 按钮参数
        self.button_height = 60
        self.button_spacing = 10
        self.icon_size = 30
        
        # 创建按钮
        self.buttons = self.create_buttons()
        
        # 导入设置对话框
        try:
            from .settings_dialog import SettingsDialog
            self.settings_dialog = SettingsDialog(screen, font_manager, config_manager)
        except ImportError:
            self.settings_dialog = None
            print("注意：设置对话框组件未找到，设置功能将不可用")
    
    def create_buttons(self):
        """创建侧边栏按钮"""
        buttons = {}
        
        # 按钮定义：图标, 文本, 工具提示, 颜色
        button_defs = [
            ('home', '主菜单', '返回主菜单', (100, 200, 100)),
            ('back', '返回', '返回上一级', (255, 200, 50)),
            ('refresh', '重玩', '重新开始游戏', (100, 150, 255)),
            ('info', '帮助', '显示游戏说明', (255, 150, 100)),
            ('settings', '设置', '游戏设置', (180, 150, 110))
        ]
        
        # 起始Y位置
        start_y = 120
        
        for i, (icon, text, tooltip, color) in enumerate(button_defs):
            y_pos = start_y + i * (self.button_height + self.button_spacing)
            
            # 按钮矩形
            button_rect = pygame.Rect(
                self.x + 10,
                y_pos,
                self.width - 20,
                self.button_height
            )
            
            buttons[icon] = {
                'rect': button_rect,
                'icon': icon,
                'text': text,
                'tooltip': tooltip,
                'color': color,
                'hovered': False
            }
        
        # 展开/收起按钮
        toggle_rect = pygame.Rect(
            self.x - 15,
            SCREEN_HEIGHT // 2 - 25,
            30, 50
        )
        buttons['toggle'] = {
            'rect': toggle_rect,
            'icon': 'toggle',
            'text': '',
            'tooltip': '展开/收起侧边栏',
            'color': (180, 150, 110),
            'hovered': False
        }
        
        return buttons
    
    def handle_event(self, event, mouse_pos):
        """处理事件"""
        # 首先检查设置对话框
        if self.settings_dialog and self.settings_dialog.visible:
            if self.settings_dialog.handle_event(event):
                return "settings_dialog"
        
        # 检查按钮点击
        if event.type == pygame.MOUSEBUTTONDOWN:
            for button_name, button_info in self.buttons.items():
                if button_info['rect'].collidepoint(mouse_pos):
                    return self.handle_button_click(button_name)
        
        # 更新按钮悬停状态
        self.update_hover_states(mouse_pos)
        
        return None
    
    def handle_button_click(self, button_name):
        """处理按钮点击"""
        if button_name == 'toggle':
            self.toggle_expanded()
            return "toggle"
        
        elif button_name == 'settings':
            if self.settings_dialog:
                self.settings_dialog.show()
                return "settings"
        
        else:
            # 返回按钮名称供游戏管理器处理
            return button_name
    
    def toggle_expanded(self):
        """切换侧边栏展开/收起状态"""
        self.expanded = not self.expanded
        self.width = SIDEBAR_WIDTH if self.expanded else SIDEBAR_COLLAPSED_WIDTH
        self.x = SCREEN_WIDTH - self.width
        
        # 重新创建按钮
        self.buttons = self.create_buttons()
    
    def update_hover_states(self, mouse_pos):
        """更新按钮悬停状态"""
        for button_info in self.buttons.values():
            button_info['hovered'] = button_info['rect'].collidepoint(mouse_pos)
    
    def update(self):
        """更新侧边栏状态"""
        if self.settings_dialog:
            # 更新设置对话框（如果需要）
            pass
    
    def draw(self):
        """绘制侧边栏"""
        # 绘制侧边栏背景
        sidebar_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(self.screen, (40, 35, 30), sidebar_rect)
        
        # 绘制侧边栏边框
        pygame.draw.line(self.screen, (180, 150, 110), 
                        (self.x, 0), (self.x, self.height), 3)
        
        # 绘制标题（仅当展开时）
        if self.expanded:
            title = self.font_manager.medium.render("游戏控制", True, (240, 230, 220))
            title_rect = title.get_rect(center=(self.x + self.width // 2, 60))
            self.screen.blit(title, title_rect)
            
            # 绘制版本信息
            version = self.font_manager.small.render("ICG Games v1.0", True, (200, 190, 170))
            version_rect = version.get_rect(center=(self.x + self.width // 2, SCREEN_HEIGHT - 40))
            self.screen.blit(version, version_rect)
        
        # 绘制按钮
        for button_name, button_info in self.buttons.items():
            if button_name == 'toggle':
                self.draw_toggle_button(button_info)
            else:
                self.draw_sidebar_button(button_info)
        
        # 绘制设置对话框（如果需要）
        if self.settings_dialog:
            self.settings_dialog.draw()
    
    def draw_sidebar_button(self, button_info):
        """绘制侧边栏按钮"""
        rect = button_info['rect']
        color = button_info['color']
        hovered = button_info['hovered']
        
        # 按钮背景
        button_color = color if hovered else tuple(c * 0.7 for c in color)
        pygame.draw.rect(self.screen, button_color, rect, border_radius=10)
        
        # 按钮边框
        border_color = tuple(min(c + 50, 255) for c in color) if hovered else color
        pygame.draw.rect(self.screen, border_color, rect, 2, border_radius=10)
        
        if self.expanded:
            # 绘制图标和文本
            icon = button_info['icon']
            text = button_info['text']
            
            # 绘制图标
            self.draw_icon(rect, icon, hovered)
            
            # 绘制文本
            text_color = (255, 255, 255) if hovered else (240, 230, 220)
            text_surface = self.font_manager.small.render(text, True, text_color)
            text_rect = text_surface.get_rect(
                center=(rect.centerx, rect.centery + 15)
            )
            self.screen.blit(text_surface, text_rect)
        else:
            # 只绘制图标（收起状态）
            icon = button_info['icon']
            self.draw_icon(rect, icon, hovered)
    
    def draw_toggle_button(self, button_info):
        """绘制展开/收起按钮"""
        rect = button_info['rect']
        hovered = button_info['hovered']
        
        # 按钮背景
        button_color = (180, 150, 110) if hovered else (150, 120, 90)
        pygame.draw.rect(self.screen, button_color, rect, border_radius=8)
        
        # 按钮边框
        border_color = (210, 180, 150) if hovered else (180, 150, 110)
        pygame.draw.rect(self.screen, border_color, rect, 2, border_radius=8)
        
        # 绘制箭头图标
        arrow_color = (255, 255, 255) if hovered else (240, 230, 220)
        
        if self.expanded:
            # 向左箭头（表示可以收起）
            points = [
                (rect.centerx - 5, rect.centery - 8),
                (rect.centerx + 3, rect.centery),
                (rect.centerx - 5, rect.centery + 8)
            ]
        else:
            # 向右箭头（表示可以展开）
            points = [
                (rect.centerx + 5, rect.centery - 8),
                (rect.centerx - 3, rect.centery),
                (rect.centerx + 5, rect.centery + 8)
            ]
        
        pygame.draw.polygon(self.screen, arrow_color, points)
    
    def draw_icon(self, rect, icon_name, hovered):
        """绘制按钮图标"""
        icon_color = (255, 255, 255) if hovered else (240, 230, 220)
        icon_size = self.icon_size
        
        if icon_name == 'home':
            # 房屋图标
            pygame.draw.polygon(self.screen, icon_color, [
                (rect.centerx, rect.centery - 10),
                (rect.centerx - 8, rect.centery - 2),
                (rect.centerx - 6, rect.centery - 2),
                (rect.centerx - 6, rect.centery + 6),
                (rect.centerx + 6, rect.centery + 6),
                (rect.centerx + 6, rect.centery - 2),
                (rect.centerx + 8, rect.centery - 2)
            ])
        
        elif icon_name == 'back':
            # 返回箭头
            pygame.draw.polygon(self.screen, icon_color, [
                (rect.centerx - 5, rect.centery),
                (rect.centerx + 3, rect.centery - 7),
                (rect.centerx + 3, rect.centery - 3),
                (rect.centerx + 7, rect.centery - 3),
                (rect.centerx + 7, rect.centery + 3),
                (rect.centerx + 3, rect.centery + 3),
                (rect.centerx + 3, rect.centery + 7)
            ])
        
        elif icon_name == 'refresh':
            # 刷新图标
            pygame.draw.circle(self.screen, icon_color, (rect.centerx, rect.centery), 8, 2)
            
            # 绘制箭头
            pygame.draw.polygon(self.screen, icon_color, [
                (rect.centerx + 6, rect.centery - 6),
                (rect.centerx + 10, rect.centery - 6),
                (rect.centerx + 6, rect.centery - 10)
            ])
        
        elif icon_name == 'info':
            # 信息图标
            pygame.draw.circle(self.screen, icon_color, (rect.centerx, rect.centery), 8, 2)
            
            # 绘制"i"
            font = pygame.font.SysFont('Arial', 12, bold=True)
            info_text = font.render("i", True, icon_color)
            info_rect = info_text.get_rect(center=(rect.centerx, rect.centery))
            self.screen.blit(info_text, info_rect)
        
        elif icon_name == 'settings':
            # 设置齿轮图标
            center_x, center_y = rect.centerx, rect.centery
            radius = 8
            
            # 齿轮外圈
            pygame.draw.circle(self.screen, icon_color, (center_x, center_y), radius, 2)
            
            # 齿轮齿
            for i in range(6):
                angle = i * 60
                rad = math.radians(angle)
                x1 = center_x + (radius - 2) * math.cos(rad)
                y1 = center_y + (radius - 2) * math.sin(rad)
                x2 = center_x + (radius + 3) * math.cos(rad)
                y2 = center_y + (radius + 3) * math.sin(rad)
                pygame.draw.line(self.screen, icon_color, (x1, y1), (x2, y2), 2)
    
    def is_settings_dialog_visible(self):
        """检查设置对话框是否可见"""
        return self.settings_dialog and self.settings_dialog.visible
    
    def get_win_indicator_enabled(self):
        """获取胜利指示器是否启用"""
        if self.settings_dialog:
            return self.settings_dialog.get_setting('win_indicator_enabled')
        return True  # 默认启用