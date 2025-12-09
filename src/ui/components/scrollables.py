"""
Scrollable UI Components
"""

import pygame
from utils.constants import *

class ScrollableList:
    """Scrollable list component"""
    
    def __init__(self, x, y, width, height, item_height=40, max_visible_items=8):
        self.rect = pygame.Rect(x, y, width, height)
        self.item_height = item_height
        self.max_visible_items = max_visible_items
        self.items = []
        self.scroll_offset = 0
        self.scrollbar_width = 10
        
    def add_item(self, item):
        """Add item to the list"""
        self.items.append(item)
    
    def clear_items(self):
        """Clear all items"""
        self.items = []
    
    def draw(self, surface):
        """Draw the scrollable list"""
        # Draw list background
        pygame.draw.rect(surface, (35, 45, 60), self.rect, border_radius=10)
        pygame.draw.rect(surface, ACCENT_COLOR, self.rect, 2, border_radius=10)
        
        # Draw visible items
        start_index = self.scroll_offset
        end_index = min(start_index + self.max_visible_items, len(self.items))
        
        for i in range(start_index, end_index):
            item_y = self.rect.top + 10 + (i - start_index) * (self.item_height + 5)
            item_rect = pygame.Rect(self.rect.left + 10, item_y, 
                                  self.rect.width - 20 - self.scrollbar_width, 
                                  self.item_height)
            
            # Draw item background
            pygame.draw.rect(surface, (50, 65, 85), item_rect, border_radius=8)
            pygame.draw.rect(surface, (80, 100, 130), item_rect, 1, border_radius=8)
            
            # Draw item content (to be implemented by subclass)
            self._draw_item_content(surface, item_rect, self.items[i], i)
        
        # Draw scrollbar if needed
        if len(self.items) > self.max_visible_items:
            self._draw_scrollbar(surface)
    
    def _draw_item_content(self, surface, rect, item, index):
        """Draw item content - to be overridden by subclass"""
        pass
    
    def _draw_scrollbar(self, surface):
        """Draw scrollbar"""
        scrollbar_rect = pygame.Rect(
            self.rect.right - self.scrollbar_width - 5,
            self.rect.top + 5,
            self.scrollbar_width,
            self.rect.height - 10
        )
        
        # Scrollbar background
        pygame.draw.rect(surface, (50, 60, 80), scrollbar_rect, border_radius=5)
        
        # Scrollbar thumb
        visible_ratio = self.max_visible_items / len(self.items)
        thumb_height = max(20, scrollbar_rect.height * visible_ratio)
        max_scroll = len(self.items) - self.max_visible_items
        
        if max_scroll > 0:
            scroll_ratio = self.scroll_offset / max_scroll
            thumb_y = scrollbar_rect.top + scroll_ratio * (scrollbar_rect.height - thumb_height)
        else:
            thumb_y = scrollbar_rect.top
        
        thumb_rect = pygame.Rect(
            scrollbar_rect.left,
            thumb_y,
            scrollbar_rect.width,
            thumb_height
        )
        pygame.draw.rect(surface, ACCENT_COLOR, thumb_rect, border_radius=5)
    
    def handle_scroll(self, event):
        """Handle mouse wheel scrolling"""
        if event.type == pygame.MOUSEWHEEL and self.rect.collidepoint(pygame.mouse.get_pos()):
            if event.y > 0:  # Scroll up
                self.scroll_offset = max(0, self.scroll_offset - 1)
            elif event.y < 0:  # Scroll down
                self.scroll_offset = min(len(self.items) - self.max_visible_items, 
                                       self.scroll_offset + 1)
            return True
        return False

class Scrollbar:
    """Simple scrollbar component"""
    
    def __init__(self, x, y, width, height, total_items, visible_items):
        self.rect = pygame.Rect(x, y, width, height)
        self.total_items = total_items
        self.visible_items = visible_items
        self.scroll_offset = 0
        self.dragging = False
    
    def draw(self, surface):
        """Draw the scrollbar"""
        if self.total_items <= self.visible_items:
            return
        
        # Scrollbar background
        pygame.draw.rect(surface, (50, 60, 80), self.rect, border_radius=5)
        
        # Scrollbar thumb
        visible_ratio = self.visible_items / self.total_items
        thumb_height = max(20, self.rect.height * visible_ratio)
        max_scroll = self.total_items - self.visible_items
        
        if max_scroll > 0:
            scroll_ratio = self.scroll_offset / max_scroll
            thumb_y = self.rect.top + scroll_ratio * (self.rect.height - thumb_height)
        else:
            thumb_y = self.rect.top
        
        self.thumb_rect = pygame.Rect(
            self.rect.left,
            thumb_y,
            self.rect.width,
            thumb_height
        )
        pygame.draw.rect(surface, ACCENT_COLOR, self.thumb_rect, border_radius=5)
    
    def handle_event(self, event):
        """Handle scrollbar events"""
        mouse_pos = pygame.mouse.get_pos()
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.thumb_rect.collidepoint(mouse_pos):
                self.dragging = True
                self.drag_offset = mouse_pos[1] - self.thumb_rect.top
                return True
            elif self.rect.collidepoint(mouse_pos):
                # Click on scrollbar track
                if mouse_pos[1] < self.thumb_rect.top:
                    self.scroll_offset = max(0, self.scroll_offset - self.visible_items)
                else:
                    self.scroll_offset = min(self.total_items - self.visible_items,
                                          self.scroll_offset + self.visible_items)
                return True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
            return False
        
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            # Calculate new scroll position based on drag
            new_thumb_y = mouse_pos[1] - self.drag_offset
            new_thumb_ratio = (new_thumb_y - self.rect.top) / (self.rect.height - self.thumb_rect.height)
            self.scroll_offset = int(new_thumb_ratio * (self.total_items - self.visible_items))
            self.scroll_offset = max(0, min(self.scroll_offset, self.total_items - self.visible_items))
            return True
        
        return False