"""
UI Button components
"""

import pygame
from utils.constants import *

class Button:
    """Represents a clickable button"""
    def __init__(self, x, y, width, height, text, font_manager, icon=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font_manager = font_manager
        self.hovered = False
        self.enabled = True
        self.icon = icon
    
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