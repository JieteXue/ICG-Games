"""
Base Button Components
"""

import pygame
import math
from abc import ABC, abstractmethod
from utils.constants import *
from utils.icon_renderer import IconRenderer
from utils.font_helper import FontHelper

class BaseButton(ABC):
    """Base button class"""
    
    def __init__(self, x, y, width, height, text, font_manager, tooltip=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font_manager = font_manager
        self.hovered = False
        self.enabled = True
        self.tooltip = tooltip
        self.tooltip_timer = 0
    
    @abstractmethod
    def draw(self, surface):
        """Draw the button - must be implemented by subclass"""
        pass
    
    def update_hover(self, mouse_pos):
        """Update hover state based on mouse position"""
        self.hovered = self.rect.collidepoint(mouse_pos) and self.enabled
    
    def is_clicked(self, event):
        """Check if button was clicked"""
        return (event.type == pygame.MOUSEBUTTONDOWN and 
                event.button == 1 and 
                self.hovered and 
                self.enabled)
    
    def _draw_tooltip(self, surface):
        """Draw tooltip if hovered long enough"""
        if not self.tooltip or not self.hovered or not self.enabled:
            return
        
        self.tooltip_timer += 1
        if self.tooltip_timer > 20:  # Show after 0.5 seconds
            tooltip_font = pygame.font.SysFont('Arial', 14)
            tooltip_text = tooltip_font.render(self.tooltip, True, (255, 255, 255))
            tooltip_rect = tooltip_text.get_rect()
            
            tooltip_x = self.rect.centerx - tooltip_rect.width // 2
            tooltip_y = self.rect.top - tooltip_rect.height - 8
            
            tooltip_bg = pygame.Rect(
                tooltip_x - 6, tooltip_y - 4,
                tooltip_rect.width + 12, tooltip_rect.height + 8
            )
            pygame.draw.rect(surface, (40, 40, 60), tooltip_bg, border_radius=6)
            pygame.draw.rect(surface, ACCENT_COLOR, tooltip_bg, 1, border_radius=6)
            surface.blit(tooltip_text, (tooltip_x, tooltip_y))
        else:
            self.tooltip_timer = 0

class GameButton(BaseButton):
    """Universal game button with enhanced styling"""
    
    def __init__(self, x, y, width, height, text, font_manager, icon=None, tooltip=""):
        super().__init__(x, y, width, height, text, font_manager, tooltip)
        self.icon = icon
        self.corner_radius = 12
        self.icon_surface = None
        
        if self.icon:
            self._load_icon()
    
    def _load_icon(self):
        """Load and cache icon surface"""
        if self.icon:
            icon_size = min(self.rect.width, self.rect.height) * 3 // 5
            icon_color = (255, 255, 255) if self.enabled else (150, 150, 150)
            self.icon_surface = IconRenderer.get_icon(self.icon, icon_size, icon_color)
    
    def draw(self, surface):
        """Draw the game button with icon"""
        FontHelper.ensure_initialized(self.font_manager)
        
        if hasattr(self.font_manager, 'ensure_initialized'):
            # 如果 font_manager 是 FontManager 且有这个方法
            self.font_manager.ensure_initialized()
        elif hasattr(self.font_manager, 'initialize_fonts'):
            # 如果 font_manager 是 FontManager 但有不同方法名
            if not hasattr(self.font_manager, 'small') or self.font_manager.small is None:
                self.font_manager.initialize_fonts()
        else:
            # 其他情况，假设字体已经初始化
            pass
        
        # 如果状态改变，重新加载图标
        if self.icon_surface is None and self.icon:
            self._load_icon()
        
        # Draw shadow
        shadow_rect = self.rect.move(4, 4)
        pygame.draw.rect(surface, SHADOW_COLOR, shadow_rect, border_radius=self.corner_radius)
        
        # Draw button
        color = BUTTON_HOVER_COLOR if self.hovered and self.enabled else BUTTON_COLOR
        if not self.enabled:
            color = (100, 100, 120)
        
        pygame.draw.rect(surface, color, self.rect, border_radius=self.corner_radius)
        
        # Draw border
        border_color = ACCENT_COLOR if self.hovered and self.enabled else (100, 140, 200)
        if not self.enabled:
            border_color = (80, 80, 100)
        pygame.draw.rect(surface, border_color, self.rect, 3, border_radius=self.corner_radius)
        
        # Draw icon and/or text
        if self.icon_surface and self.text:
            # Both icon and text
            self._draw_icon_and_text(surface)
        elif self.icon_surface:
            # Icon only
            self._draw_icon_only(surface)
        else:
            # Text only
            self._draw_text_only(surface)
        
        # Draw tooltip
        self._draw_tooltip(surface)
    
    def _draw_icon_and_text(self, surface):
        """Draw both icon and text"""
        if not self.icon_surface:
            return

        # 安全地获取小字体
        if hasattr(self.font_manager, 'small'):
            small_font = self.font_manager.small
        elif isinstance(self.font_manager, pygame.font.Font):
            # 如果是字体对象，计算小号字体
            small_font = pygame.font.Font(None, 20)  # 创建小号字体
        else:
            small_font = pygame.font.SysFont(None, 20)

        # Calculate positions
        total_height = self.icon_surface.get_height() + small_font.get_height() + 5
        icon_y = self.rect.centery - total_height // 2
        icon_x = self.rect.centerx - self.icon_surface.get_width() // 2

        # Draw icon
        surface.blit(self.icon_surface, (icon_x, icon_y))

        # Draw text
        text_color = (255, 255, 255) if self.enabled else (150, 150, 150)
        text_surface = small_font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=(self.rect.centerx, 
                                                icon_y + self.icon_surface.get_height() + 
                                                small_font.get_height()//2 + 5))

        # Text shadow
        if self.enabled:
            shadow_surface = small_font.render(self.text, True, (0, 0, 0, 100))
            shadow_rect = text_rect.move(1, 1)
            surface.blit(shadow_surface, shadow_rect)

        surface.blit(text_surface, text_rect)
    
    def _draw_icon_only(self, surface):
        """Draw icon only (centered)"""
        if not self.icon_surface:
            return
        
        icon_x = self.rect.centerx - self.icon_surface.get_width() // 2
        icon_y = self.rect.centery - self.icon_surface.get_height() // 2
        surface.blit(self.icon_surface, (icon_x, icon_y))
    
    def _draw_text_only(self, surface):
        """Draw text only (centered)"""
        text_color = (255, 255, 255) if self.enabled else (150, 150, 150)

        # 安全地获取字体
        if hasattr(self.font_manager, 'medium'):
            # font_manager 是 FontManager 实例
            font = self.font_manager.medium
        elif isinstance(self.font_manager, pygame.font.Font):
            # font_manager 是 pygame.font.Font 实例
            font = self.font_manager
        else:
            # 回退到系统字体
            font = pygame.font.SysFont(None, 32)

        text_surface = font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)

        # Text shadow
        if self.enabled:
            shadow_surface = font.render(self.text, True, (0, 0, 0, 100))
            shadow_rect = text_rect.move(2, 2)
            surface.blit(shadow_surface, shadow_rect)

        surface.blit(text_surface, text_rect)

class IconButton(GameButton):
    """Icon button for game selection"""
    
    def __init__(self, x, y, size, text, font_manager, icon_path=None, tooltip=""):
        super().__init__(x, y, size, size, text, font_manager, None, tooltip)
        self.icon_surface = None
        self.icon_path = icon_path
        self.corner_radius = 15
        
        # Load icon if provided
        if icon_path:
            self._load_icon()
    
    def _load_icon(self):
        """Load and process icon image"""
        try:
            import os
            if os.path.exists(self.icon_path):
                icon = pygame.image.load(self.icon_path).convert_alpha()
                # 创建带圆角的蒙版
                self.icon_surface = pygame.transform.smoothscale(icon, (self.rect.width, self.rect.height))
                # 创建圆角蒙版
                self.mask_surface = self._create_rounded_mask(self.rect.width, self.rect.height, self.corner_radius)
        except Exception as e:
            print(f"Error loading icon {self.icon_path}: {e}")
            self.icon_surface = None
            self.mask_surface = None
    
    def _create_rounded_mask(self, width, height, radius):
        """创建圆角蒙版表面"""
        mask_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        mask_surface.fill((0, 0, 0, 0))
        
        # 绘制四个圆角矩形填充
        pygame.draw.rect(mask_surface, (255, 255, 255, 255), 
                        (0, radius, width, height - 2*radius))
        pygame.draw.rect(mask_surface, (255, 255, 255, 255),
                        (radius, 0, width - 2*radius, height))
        
        # 绘制四个圆角
        for x, y in [(radius, radius), 
                     (width - radius - 1, radius),
                     (radius, height - radius - 1),
                     (width - radius - 1, height - radius - 1)]:
            # 绘制圆形
            pygame.draw.circle(mask_surface, (255, 255, 255, 255), (x, y), radius)
        
        return mask_surface
    
    def draw(self, surface):
        """Override draw for icon button"""
        # Draw shadow
        shadow_rect = self.rect.move(4, 4)
        pygame.draw.rect(surface, SHADOW_COLOR, shadow_rect, border_radius=self.corner_radius)
        
        # Draw button with icon
        if self.icon_surface:
            # 创建临时表面用于圆角裁剪
            temp_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            
            if not self.enabled:
                # 禁用状态：图标变灰并应用圆角
                gray_surface = self.icon_surface.copy()
                gray_overlay = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
                gray_overlay.fill((100, 100, 100, 150))
                gray_surface.blit(gray_overlay, (0, 0))
                
                # 应用圆角蒙版
                temp_surface.blit(gray_surface, (0, 0))
                temp_surface.blit(self.mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            else:
                # 正常状态：直接应用圆角蒙版
                temp_surface.blit(self.icon_surface, (0, 0))
                temp_surface.blit(self.mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            
            # 将处理后的图标绘制到屏幕上
            surface.blit(temp_surface, self.rect)
            
            # Hover overlay (在圆角图标上)
            if self.hovered and self.enabled:
                hover_overlay = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
                pygame.draw.rect(hover_overlay, (255, 255, 255, 40), 
                               (0, 0, self.rect.width, self.rect.height), 
                               border_radius=self.corner_radius)
                surface.blit(hover_overlay, self.rect)
        else:
            # Fallback to standard button (保持原有逻辑)
            color = BUTTON_HOVER_COLOR if self.hovered and self.enabled else BUTTON_COLOR
            if not self.enabled:
                color = (100, 100, 120)
            pygame.draw.rect(surface, color, self.rect, border_radius=self.corner_radius)
        
        # Draw border
        border_color = ACCENT_COLOR if self.hovered and self.enabled else (100, 140, 200)
        if not self.enabled:
            border_color = (80, 80, 100)
        pygame.draw.rect(surface, border_color, self.rect, 3, border_radius=self.corner_radius)
        
        # Draw text label at bottom
        if self.text:
            self._draw_text_label(surface)
        
        # Draw tooltip
        self._draw_tooltip(surface)
    
    def _draw_text_label(self, surface):
        """Draw text label at button bottom"""
        text_bg_height = 40
        text_bg_rect = pygame.Rect(
            self.rect.left, 
            self.rect.bottom - text_bg_height, 
            self.rect.width, 
            text_bg_height
        )
        
        # Create semi-transparent background
        text_bg_surface = pygame.Surface((text_bg_rect.width, text_bg_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(text_bg_surface, (30, 40, 60, 180), 
                        (0, 0, text_bg_rect.width, text_bg_rect.height),
                        border_radius=self.corner_radius)
        
        # Make bottom straight
        pygame.draw.rect(text_bg_surface, (30, 40, 60, 180),
                        (0, self.corner_radius, text_bg_rect.width, 
                         text_bg_rect.height - self.corner_radius))
        
        surface.blit(text_bg_surface, text_bg_rect)
        
        # Draw text with word wrapping
        words = self.text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_width = self.font_manager.small.size(test_line)[0]
            
            if test_width <= self.rect.width - 20:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw text lines
        total_text_height = len(lines) * 18
        start_y = text_bg_rect.centery - total_text_height // 2 + 2
        
        for i, line in enumerate(lines):
            text_color = (255, 255, 255) if self.enabled else (180, 180, 180)
            text_surface = self.font_manager.small.render(line, True, text_color)
            text_rect = text_surface.get_rect(center=(self.rect.centerx, start_y + i * 18))
            
            if self.enabled:
                shadow_surface = self.font_manager.small.render(line, True, (0, 0, 0, 150))
                shadow_rect = text_rect.move(1, 1)
                surface.blit(shadow_surface, shadow_rect)
            
            surface.blit(text_surface, text_rect)