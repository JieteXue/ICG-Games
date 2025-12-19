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
    
class ScrollablePanel:
    """Scrollable panel for displaying text content"""
    
    def __init__(self, x, y, width, height, font_manager, bg_color=(25, 30, 45)):
        self.rect = pygame.Rect(x, y, width, height)
        self.font_manager = font_manager
        self.bg_color = bg_color
        
        # Content management
        self.lines = []  # List of (text, color, font_size)
        self.line_heights = []  # Pre-calculated line heights
        self.content_height = 0
        self.scroll_offset = 0
        self.max_scroll = 0
        
        # Scrollbar properties
        self.scrollbar_width = 10
        self.scrollbar_rect = pygame.Rect(
            x + width - self.scrollbar_width,
            y,
            self.scrollbar_width,
            height
        )
        self.scrollbar_handle_height = 100
        self.is_dragging = False
        
        # Performance optimization
        self.cached_surface = None
        self.needs_redraw = True
    
    def add_line(self, text, color, font_size='medium', centered=False):
        """Add a line of text to the panel"""
        self.lines.append({
            'text': text,
            'color': color,
            'font_size': font_size,
            'centered': centered
        })
        self.needs_redraw = True
        self._calculate_content_height()
    
    def add_spacing(self, pixels):
        """Add empty spacing"""
        self.lines.append({
            'text': '',
            'color': (0, 0, 0),
            'font_size': 'small',
            'spacing': pixels,
            'centered': False
        })
        self.needs_redraw = True
        self._calculate_content_height()
    
    def clear_content(self):
        """Clear all content from the panel"""
        self.lines = []
        self.line_heights = []
        self.content_height = 0
        self.scroll_offset = 0
        self.max_scroll = 0
        self.needs_redraw = True
    
    def _calculate_content_height(self):
        """Calculate total content height and line positions"""
        self.line_heights = []
        self.content_height = 0
        
        for line in self.lines:
            if 'spacing' in line:
                height = line['spacing']
            else:
                font = self._get_font(line['font_size'])
                _, line_height = font.size(line['text'])
                height = line_height + 5  # Add some padding
            
            self.line_heights.append(height)
            self.content_height += height
        
        self.max_scroll = max(0, self.content_height - self.rect.height)
    
    def _get_font(self, font_size):
        """Get font object based on size name"""
        if font_size == 'small':
            return self.font_manager.small
        elif font_size == 'medium':
            return self.font_manager.medium
        elif font_size == 'large':
            return self.font_manager.large
        else:
            return self.font_manager.medium
    
    def handle_event(self, event):
        """Handle events for the scrollable panel"""
        mouse_pos = pygame.mouse.get_pos()
        
        if event.type == pygame.MOUSEWHEEL:
            # Scroll with mouse wheel
            self.scroll_offset = max(0, min(
                self.max_scroll,
                self.scroll_offset - event.y * 20
            ))
            self.needs_redraw = True
            return True
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                # Check if clicking on scrollbar
                scrollbar_handle = self._get_scrollbar_handle_rect()
                if scrollbar_handle.collidepoint(mouse_pos):
                    self.is_dragging = True
                    self.drag_start_y = mouse_pos[1]
                    self.drag_start_offset = self.scroll_offset
                    return True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.is_dragging = False
                return True
        
        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging:
                # Calculate new scroll offset based on drag
                delta_y = mouse_pos[1] - self.drag_start_y
                scroll_ratio = delta_y / self.rect.height
                new_offset = self.drag_start_offset + (scroll_ratio * self.content_height)
                self.scroll_offset = max(0, min(self.max_scroll, new_offset))
                self.needs_redraw = True
                return True
        
        return False
    
    def _get_scrollbar_handle_rect(self):
        """Get rectangle for scrollbar handle"""
        if self.max_scroll == 0:
            return pygame.Rect(0, 0, 0, 0)
        
        # Calculate handle position based on scroll offset
        handle_y_ratio = self.scroll_offset / self.max_scroll
        handle_y = self.rect.y + (handle_y_ratio * (self.rect.height - self.scrollbar_handle_height))
        
        return pygame.Rect(
            self.scrollbar_rect.x,
            handle_y,
            self.scrollbar_width,
            self.scrollbar_handle_height
        )
    
    def draw(self, screen):
        """Draw the scrollable panel"""
        # Draw background
        pygame.draw.rect(screen, self.bg_color, self.rect, border_radius=8)
        pygame.draw.rect(screen, (60, 70, 100), self.rect, 1, border_radius=8)
        
        # Create clipping area
        clip_rect = screen.get_clip()
        screen.set_clip(self.rect)
        
        # Draw content
        current_y = self.rect.y - self.scroll_offset
        
        for i, line in enumerate(self.lines):
            line_height = self.line_heights[i]
            
            # Only draw if line is visible
            if (current_y + line_height >= self.rect.y and 
                current_y <= self.rect.y + self.rect.height):
                
                if 'spacing' in line:
                    # This is just spacing, skip drawing
                    pass
                else:
                    # Draw text line
                    font = self._get_font(line['font_size'])
                    text_surface = font.render(line['text'], True, line['color'])
                    
                    if line['centered']:
                        text_x = self.rect.x + (self.rect.width - text_surface.get_width()) // 2
                    else:
                        text_x = self.rect.x + 10
                    
                    screen.blit(text_surface, (text_x, current_y))
            
            current_y += line_height
        
        # Reset clipping
        screen.set_clip(clip_rect)
        
        # Draw scrollbar if needed
        if self.max_scroll > 0:
            # Scrollbar background
            pygame.draw.rect(screen, (40, 45, 65), self.scrollbar_rect, border_radius=5)
            
            # Scrollbar handle
            handle_rect = self._get_scrollbar_handle_rect()
            pygame.draw.rect(screen, (80, 90, 130), handle_rect, border_radius=5)
            pygame.draw.rect(screen, (100, 110, 150), handle_rect, 1, border_radius=5)