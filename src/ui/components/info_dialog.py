"""
Information Dialog Component
"""

import pygame
from utils.constants import *

class InfoDialog:
    """Game instructions dialog"""
    
    def __init__(self, screen, font_manager, game_name="", instructions=""):
        self.screen = screen
        self.font_manager = font_manager
        self.game_name = game_name
        self.instructions = instructions
        self.visible = False
        self.scroll_offset = 0
        self.max_scroll = 0
        
        # Dialog dimensions
        self.width = min(800, SCREEN_WIDTH - 100)
        self.height = min(600, SCREEN_HEIGHT - 100)
        self.rect = pygame.Rect(
            (SCREEN_WIDTH - self.width) // 2,
            (SCREEN_HEIGHT - self.height) // 2,
            self.width,
            self.height
        )
        
        # Close button
        close_size = 40
        self.close_button_rect = pygame.Rect(
            self.rect.right - close_size - 15,
            self.rect.top + 15,
            close_size,
            close_size
        )
        
        # Scrollbar
        self.scrollbar_width = 10
        self.scrollbar_rect = pygame.Rect(
            self.rect.right - self.scrollbar_width - 10,
            self.rect.top + 80,
            self.scrollbar_width,
            self.height - 160
        )
        
    def show(self, game_name="", instructions=""):
        """Show the info dialog"""
        if game_name:
            self.game_name = game_name
        if instructions:
            self.instructions = instructions
        self.visible = True
        self.scroll_offset = 0
        self.calculate_scroll()
    
    def hide(self):
        """Hide the info dialog"""
        self.visible = False
    
    def toggle(self):
        """Toggle dialog visibility"""
        self.visible = not self.visible
        if self.visible:
            self.scroll_offset = 0
            self.calculate_scroll()
    
    def calculate_scroll(self):
        """Calculate maximum scroll offset"""
        # This is a simplified calculation
        # In a real implementation, you'd calculate based on text height
        self.max_scroll = max(0, len(self.instructions.split('\n')) * 25 - (self.height - 160))
    
    def handle_event(self, event, mouse_pos):
        """Handle dialog events"""
        if not self.visible:
            return None
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check close button
            if self.close_button_rect.collidepoint(mouse_pos):
                self.hide()
                return "close"
            
            # Check if click is inside dialog
            if self.rect.collidepoint(mouse_pos):
                return "click_inside"
            
            # Click outside dialog to close
            self.hide()
            return "close_outside"
        
        elif event.type == pygame.MOUSEWHEEL and self.rect.collidepoint(mouse_pos):
            # Handle scrolling
            if event.y > 0:  # Scroll up
                self.scroll_offset = max(0, self.scroll_offset - 3)
            elif event.y < 0:  # Scroll down
                self.scroll_offset = min(self.max_scroll, self.scroll_offset + 3)
            return "scroll"
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.hide()
                return "close"
        
        return None
    
    def draw(self):
        """Draw the info dialog"""
        if not self.visible:
            return
        
        # Draw semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Draw dialog background
        pygame.draw.rect(self.screen, (35, 45, 60), self.rect, border_radius=15)
        pygame.draw.rect(self.screen, ACCENT_COLOR, self.rect, 3, border_radius=15)
        
        # Draw header
        header_rect = pygame.Rect(self.rect.left, self.rect.top, self.rect.width, 60)
        pygame.draw.rect(self.screen, (45, 55, 75), header_rect, border_top_left_radius=15, border_top_right_radius=15)
        
        # Draw title
        title = self.font_manager.large.render(f"{self.game_name} - Instructions", True, TEXT_COLOR)
        title_rect = title.get_rect(center=(self.rect.centerx, self.rect.top + 30))
        self.screen.blit(title, title_rect)
        
        # Draw close button
        pygame.draw.rect(self.screen, (200, 70, 70), self.close_button_rect, border_radius=8)
        pygame.draw.rect(self.screen, (255, 255, 255), self.close_button_rect, 2, border_radius=8)
        
        # Draw X icon
        offset = 12
        pygame.draw.line(self.screen, (255, 255, 255),
                       (self.close_button_rect.centerx - offset, self.close_button_rect.centery - offset),
                       (self.close_button_rect.centerx + offset, self.close_button_rect.centery + offset), 3)
        pygame.draw.line(self.screen, (255, 255, 255),
                       (self.close_button_rect.centerx - offset, self.close_button_rect.centery + offset),
                       (self.close_button_rect.centerx + offset, self.close_button_rect.centery - offset), 3)
        
        # Draw content area
        content_rect = pygame.Rect(
            self.rect.left + 20,
            self.rect.top + 80 - self.scroll_offset,
            self.rect.width - 40 - (self.scrollbar_width if self.max_scroll > 0 else 0),
            self.rect.height - 100
        )
        
        # Draw instructions with word wrapping
        y = content_rect.top
        instructions_text = self.instructions if self.instructions else "No instructions available."
        
        # Split into paragraphs
        paragraphs = instructions_text.split('\n\n')
        
        for paragraph in paragraphs:
            # Split paragraph into lines
            words = paragraph.split()
            lines = []
            current_line = []
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                test_width = self.font_manager.small.size(test_line)[0]
                
                if test_width <= content_rect.width - 20:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                    current_line = [word]
            
            if current_line:
                lines.append(' '.join(current_line))
            
            # Draw each line
            for line in lines:
                if y < content_rect.bottom and y > self.rect.top + 80 - 30:
                    text_surface = self.font_manager.small.render(line, True, (220, 230, 240))
                    text_rect = text_surface.get_rect(topleft=(content_rect.left + 10, y))
                    self.screen.blit(text_surface, text_rect)
                y += 25
            
            # Add spacing between paragraphs
            y += 10
        
        # Draw scrollbar if needed
        if self.max_scroll > 0:
            # Scrollbar background
            pygame.draw.rect(self.screen, (50, 60, 80), self.scrollbar_rect, border_radius=5)
            
            # Scrollbar thumb
            visible_ratio = (self.height - 160) / (y - content_rect.top + self.scroll_offset)
            thumb_height = max(20, self.scrollbar_rect.height * visible_ratio)
            
            if self.max_scroll > 0:
                scroll_ratio = self.scroll_offset / self.max_scroll
                thumb_y = self.scrollbar_rect.top + scroll_ratio * (self.scrollbar_rect.height - thumb_height)
            else:
                thumb_y = self.scrollbar_rect.top
            
            thumb_rect = pygame.Rect(
                self.scrollbar_rect.left,
                thumb_y,
                self.scrollbar_rect.width,
                thumb_height
            )
            pygame.draw.rect(self.screen, ACCENT_COLOR, thumb_rect, border_radius=5)