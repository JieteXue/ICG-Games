"""
UI Button components
"""

import pygame
from utils.constants import *

class Button:
    """Represents a clickable button"""
    def __init__(self, x, y, width, height, text, font_manager, icon=None, tooltip=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font_manager = font_manager
        self.hovered = False
        self.enabled = True
        self.icon = icon
        self.tooltip = tooltip  # 添加提示文本
        self.tooltip_timer = 0  # 提示显示计时器
        self.show_tooltip = False  # 是否显示提示
    
    def draw(self, surface):
        """Draw the button on the surface with enhanced styling"""
        # 确保字体已初始化
        self.font_manager.ensure_initialized()
        
        # Draw shadow
        shadow_rect = self.rect.move(4, 4)
        pygame.draw.rect(surface, SHADOW_COLOR, shadow_rect, border_radius=12)
        
        # Draw button
        color = BUTTON_HOVER_COLOR if self.hovered and self.enabled else BUTTON_COLOR
        if not self.enabled:
            color = (100, 100, 120)  # Disabled color
        
        pygame.draw.rect(surface, color, self.rect, border_radius=12)
        
        # Draw border
        border_color = ACCENT_COLOR if self.hovered and self.enabled else (100, 140, 200)
        if not self.enabled:
            border_color = (80, 80, 100)
        pygame.draw.rect(surface, border_color, self.rect, 3, border_radius=12)
        
        # Draw icon or text
        if self.icon:
            self._draw_icon(surface)
        else:
            self._draw_text(surface)
        
        # 绘制提示（如果悬停时间足够长）
        if self.hovered and self.tooltip and self.enabled:
            self.tooltip_timer += 1
            if self.tooltip_timer > 20:  # 悬停0.5秒后显示提示
                self._draw_tooltip(surface)
        else:
            self.tooltip_timer = 0
    
    def _draw_tooltip(self, surface):
        """绘制提示"""
        if not self.tooltip:
            return
            
        # 创建提示文本
        tooltip_font = pygame.font.SysFont('Arial', 14)
        tooltip_text = tooltip_font.render(self.tooltip, True, (255, 255, 255))
        tooltip_rect = tooltip_text.get_rect()
        
        # 计算提示位置（在按钮上方）
        tooltip_x = self.rect.centerx - tooltip_rect.width // 2
        tooltip_y = self.rect.top - tooltip_rect.height - 8
        
        # 绘制提示背景
        tooltip_bg = pygame.Rect(
            tooltip_x - 6, tooltip_y - 4,
            tooltip_rect.width + 12, tooltip_rect.height + 8
        )
        pygame.draw.rect(surface, (40, 40, 60), tooltip_bg, border_radius=6)
        pygame.draw.rect(surface, ACCENT_COLOR, tooltip_bg, 1, border_radius=6)
        
        # 绘制提示文本
        surface.blit(tooltip_text, (tooltip_x, tooltip_y))
        
        # 绘制小三角形指向按钮
        points = [
            (self.rect.centerx, self.rect.top - 2),
            (self.rect.centerx - 6, self.rect.top - 8),
            (self.rect.centerx + 6, self.rect.top - 8)
        ]
        pygame.draw.polygon(surface, (40, 40, 60), points)
        pygame.draw.polygon(surface, ACCENT_COLOR, points, 1)
    
    def _draw_icon(self, surface):
        """Draw button icon"""
        icon_color = (255, 255, 255) if self.enabled else (150, 150, 150)
        if self.icon == 'back':
            # Draw back arrow (←)
            pygame.draw.polygon(surface, icon_color, [
                (self.rect.centerx - 8, self.rect.centery),
                (self.rect.centerx + 2, self.rect.centery - 8),
                (self.rect.centerx + 2, self.rect.centery - 4),
                (self.rect.centerx + 8, self.rect.centery - 4),
                (self.rect.centerx + 8, self.rect.centery + 4),
                (self.rect.centerx + 2, self.rect.centery + 4),
                (self.rect.centerx + 2, self.rect.centery + 8)
            ])
        elif self.icon == 'home':
            # Draw home icon (house shape)
            pygame.draw.polygon(surface, icon_color, [
                (self.rect.centerx, self.rect.centery - 8),  # Top
                (self.rect.centerx - 10, self.rect.centery + 2),  # Bottom left
                (self.rect.centerx - 6, self.rect.centery + 2),  # Left inner
                (self.rect.centerx - 6, self.rect.centery + 8),  # Left bottom
                (self.rect.centerx + 6, self.rect.centery + 8),  # Right bottom
                (self.rect.centerx + 6, self.rect.centery + 2),  # Right inner
                (self.rect.centerx + 10, self.rect.centery + 2)   # Bottom right
            ])
        elif self.icon == 'info':
            # Draw info icon (circle with 'i')
            # Draw circle
            pygame.draw.circle(surface, icon_color, self.rect.center, min(self.rect.width, self.rect.height) // 2 - 5, 3)
            # Draw 'i'
            i_font = pygame.font.SysFont('Arial', 20, bold=True)
            i_text = i_font.render("i", True, icon_color)
            i_rect = i_text.get_rect(center=self.rect.center)
            surface.blit(i_text, i_rect)
    
    def _draw_text(self, surface):
        """Draw button text"""
        text_color = (255, 255, 255) if self.enabled else (150, 150, 150)
        text_surface = self.font_manager.medium.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        
        # Text shadow
        if self.enabled:
            shadow_surface = self.font_manager.medium.render(self.text, True, (0, 0, 0, 100))
            shadow_rect = text_rect.move(2, 2)
            surface.blit(shadow_surface, shadow_rect)
        
        surface.blit(text_surface, text_rect)
    
    def update_hover(self, mouse_pos):
        """Update hover state based on mouse position"""
        self.hovered = self.rect.collidepoint(mouse_pos) and self.enabled
    
    def is_clicked(self, event):
        """Check if button was clicked"""
        return (event.type == pygame.MOUSEBUTTONDOWN and 
                event.button == 1 and 
                self.hovered and 
                self.enabled)

class InfoButton(Button):
    """Specialized info button with tooltip"""
    def __init__(self, x, y, size, font_manager):
        super().__init__(x, y, size, size, "", font_manager, icon='info')
        self.showing_tooltip = False
    
    def draw(self, surface):
        """Override draw method to use softer colors"""
        # 确保字体已初始化
        self.font_manager.ensure_initialized()
        
        # 使用更柔和的颜色
        soft_shadow = (25, 35, 45)  # 更暗的阴影
        soft_button = (60, 90, 130)  # 更柔和的按钮颜色
        soft_hover = (80, 110, 160)  # 更柔和的悬停颜色
        soft_accent = (80, 130, 200)  # 更柔和的高亮颜色
        
        # Draw shadow
        shadow_rect = self.rect.move(3, 3)
        pygame.draw.rect(surface, soft_shadow, shadow_rect, border_radius=10)
        
        # Draw button with softer colors
        color = soft_hover if self.hovered and self.enabled else soft_button
        if not self.enabled:
            color = (70, 70, 90)  # 更柔和的禁用颜色
        
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        
        # Draw border with softer accent
        border_color = soft_accent if self.hovered and self.enabled else (70, 100, 150)
        if not self.enabled:
            border_color = (60, 60, 80)
        pygame.draw.rect(surface, border_color, self.rect, 2, border_radius=10)
        
        # Draw info icon with softer white
        self._draw_soft_icon(surface)
    
    def _draw_soft_icon(self, surface):
        """Draw info icon with softer colors"""
        # 使用更柔和的白色
        soft_white = (200, 220, 240) if self.enabled else (120, 140, 160)
        
        # Draw circle with softer color
        circle_radius = min(self.rect.width, self.rect.height) // 2 - 6
        pygame.draw.circle(surface, soft_white, self.rect.center, circle_radius, 2)
        
        # Draw 'i' with softer color and smaller size
        i_font = pygame.font.SysFont('Arial', 18, bold=True)  # 更小的字体
        i_text = i_font.render("i", True, soft_white)
        i_rect = i_text.get_rect(center=self.rect.center)
        surface.blit(i_text, i_rect)
    
    def draw_tooltip(self, surface, games_info):
        """Draw tooltip with game information"""
        if not self.showing_tooltip:
            return
        
        # 使用更柔和的工具提示颜色
        soft_tooltip_bg = (45, 55, 75)  # 更暗的背景
        soft_tooltip_border = (80, 130, 200)  # 更柔和的边框
        soft_title_color = (220, 230, 240)  # 更柔和的标题颜色
        soft_text_color = (180, 200, 220)  # 更柔和的文本颜色
        soft_accent_color = (100, 160, 220)  # 更柔和的重点颜色
        
        # Tooltip dimensions
        tooltip_width = 600
        tooltip_height = 400
        tooltip_x = SCREEN_WIDTH - tooltip_width - 20
        tooltip_y = 80
        
        # Draw tooltip background with softer colors
        tooltip_rect = pygame.Rect(tooltip_x, tooltip_y, tooltip_width, tooltip_height)
        pygame.draw.rect(surface, soft_tooltip_bg, tooltip_rect, border_radius=12)
        pygame.draw.rect(surface, soft_tooltip_border, tooltip_rect, 2, border_radius=12)  # 更细的边框
        
        # Draw title with softer color
        title = self.font_manager.large.render("Game Information", True, soft_title_color)
        surface.blit(title, (tooltip_x + 20, tooltip_y + 20))
        
        # Draw separator line
        separator_y = tooltip_y + 60
        pygame.draw.line(surface, soft_tooltip_border, 
                        (tooltip_x + 20, separator_y), 
                        (tooltip_x + tooltip_width - 20, separator_y), 1)
        
        # Draw game information
        y_offset = tooltip_y + 80
        for game_info in games_info:
            # Game name with softer accent color
            name_text = self.font_manager.medium.render(game_info['name'], True, soft_accent_color)
            surface.blit(name_text, (tooltip_x + 20, y_offset))
            
            # Game description with wrapping and softer color
            desc_lines = self._wrap_text(game_info['description'], self.font_manager.small, tooltip_width - 40)
            for line in desc_lines:
                desc_text = self.font_manager.small.render(line, True, soft_text_color)
                surface.blit(desc_text, (tooltip_x + 20, y_offset + 30))
                y_offset += 22  # 更紧凑的行距
            
            # Players info with softer color
            players_text = self.font_manager.small.render(
                f"Players: {game_info['min_players']}-{game_info['max_players']}", 
                True, (140, 160, 180)  # 更柔和的次要文本颜色
            )
            surface.blit(players_text, (tooltip_x + 20, y_offset + 10))
            
            y_offset += 40  # 游戏之间的间距
    
    def _wrap_text(self, text, font, max_width):
        """Wrap text for tooltip"""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_width = font.size(test_line)[0]
            
            if test_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines