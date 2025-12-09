"""
UI Panel Components
"""

import pygame
from abc import ABC, abstractmethod
from utils.constants import *

class Panel(ABC):
    """Base panel class"""
    
    def __init__(self, x, y, width, height, corner_radius=15):
        self.rect = pygame.Rect(x, y, width, height)
        self.corner_radius = corner_radius
        self.visible = True
    
    @abstractmethod
    def draw(self, surface):
        """Draw the panel - must be implemented by subclass"""
        pass
    
    def contains(self, point):
        """Check if point is inside panel"""
        return self.rect.collidepoint(point)

class InfoPanel(Panel):
    """Information panel for displaying game info"""
    
    def __init__(self, x, y, width, height, font_manager, title="", bg_color=(35, 45, 60), border_color=ACCENT_COLOR):
        super().__init__(x, y, width, height)
        self.font_manager = font_manager
        self.title = title
        self.bg_color = bg_color
        self.border_color = border_color
        self.content = []
    
    def add_content(self, text, color=TEXT_COLOR, font_size='medium'):
        """Add content to panel"""
        self.content.append({
            'text': text,
            'color': color,
            'font_size': font_size
        })
    
    def clear_content(self):
        """Clear all content"""
        self.content = []
    
    def draw(self, surface):
        """Draw the info panel"""
        if not self.visible:
            return
        
        # Draw panel background
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=self.corner_radius)
        pygame.draw.rect(surface, self.border_color, self.rect, 3, border_radius=self.corner_radius)
        
        # Draw title
        if self.title:
            title_font = getattr(self.font_manager, 'large', self.font_manager.medium)
            title_text = title_font.render(self.title, True, TEXT_COLOR)
            title_rect = title_text.get_rect(center=(self.rect.centerx, self.rect.top + 30))
            surface.blit(title_text, title_rect)
        
        # Draw content
        y_offset = self.rect.top + 60 if self.title else self.rect.top + 20
        for item in self.content:
            font = getattr(self.font_manager, item['font_size'], self.font_manager.small)
            text_surface = font.render(item['text'], True, item['color'])
            text_rect = text_surface.get_rect(midleft=(self.rect.left + 20, y_offset))
            surface.blit(text_surface, text_rect)
            y_offset += 25

class ControlPanel(Panel):
    """Control panel for game controls"""
    
    def __init__(self, x, y, width, height, font_manager, title="Controls"):
        super().__init__(x, y, width, height)
        self.font_manager = font_manager
        self.title = title
        self.buttons = []
        self.labels = []
    
    def add_button(self, button):
        """Add a button to the panel"""
        self.buttons.append(button)
    
    def add_label(self, text, x, y, color=TEXT_COLOR, font_size='small'):
        """Add a label to the panel"""
        self.labels.append({
            'text': text,
            'x': x,
            'y': y,
            'color': color,
            'font_size': font_size
        })
    
    def draw(self, surface):
        """Draw the control panel"""
        # Draw panel background
        pygame.draw.rect(surface, (35, 45, 60), self.rect, border_radius=self.corner_radius)
        pygame.draw.rect(surface, ACCENT_COLOR, self.rect, 3, border_radius=self.corner_radius)
        
        # Draw title
        if self.title:
            title_text = self.font_manager.medium.render(self.title, True, TEXT_COLOR)
            title_rect = title_text.get_rect(center=(self.rect.centerx, self.rect.top + 25))
            surface.blit(title_text, title_rect)
        
        # Draw labels
        for label in self.labels:
            font = getattr(self.font_manager, label['font_size'], self.font_manager.small)
            text_surface = font.render(label['text'], True, label['color'])
            surface.blit(text_surface, (label['x'], label['y']))
        
        # Draw buttons
        for button in self.buttons:
            button.draw(surface)