"""
Additional UI components
"""

import pygame
from utils.constants import *

class CardPosition:
    """Represents a card position with a stack of cards"""
    def __init__(self, index, card_count, font_manager):
        self.index = index
        self.card_count = card_count
        self.font_manager = font_manager
        self.rect = None
        self.selected = False
    
    def draw(self, surface, x, y):
        """Draw the card stack at specified position with enhanced visuals"""
        
        # Draw position base with shadow
        base_rect = pygame.Rect(x - CARD_WIDTH//2, y + 20, CARD_WIDTH, 20)
        shadow_rect = base_rect.move(3, 3)
        pygame.draw.rect(surface, SHADOW_COLOR, shadow_rect, border_radius=6)
        pygame.draw.rect(surface, POSITION_COLOR, base_rect, border_radius=6)
        
        # Draw card stack
        if self.card_count > 0:
            max_visible = min(self.card_count, 10)  # Show max 10 cards
            
            for i in range(max_visible):
                card_y = y - i * 4  # Increased spacing for better visual
                card_rect = pygame.Rect(x - CARD_WIDTH//2, card_y - CARD_HEIGHT, CARD_WIDTH, CARD_HEIGHT)
                
                # Draw card shadow
                shadow_rect = card_rect.move(2, 2)
                pygame.draw.rect(surface, SHADOW_COLOR, shadow_rect, border_radius=10)
                
                # Draw card
                color = HIGHLIGHT_COLOR if self.selected else CARD_COLOR
                pygame.draw.rect(surface, color, card_rect, border_radius=10)
                
                # Draw card border
                border_color = (255, 200, 50) if self.selected else CARD_BORDER_COLOR
                pygame.draw.rect(surface, border_color, card_rect, 3, border_radius=10)
                
                # Draw card corner decoration
                corner_size = 8
                pygame.draw.rect(surface, border_color, 
                                (card_rect.left + 5, card_rect.top + 5, corner_size, corner_size), 
                                border_radius=2)
                pygame.draw.rect(surface, border_color, 
                                (card_rect.right - 13, card_rect.top + 5, corner_size, corner_size), 
                                border_radius=2)
            
            # Display card count with background
            count_text = self.font_manager.medium.render(str(self.card_count), True, TEXT_COLOR)
            count_bg = pygame.Rect(x - 20, y - CARD_HEIGHT//2 - 15, 40, 30)
            pygame.draw.rect(surface, SHADOW_COLOR, count_bg.move(2, 2), border_radius=8)
            pygame.draw.rect(surface, (40, 60, 80), count_bg, border_radius=8)
            pygame.draw.rect(surface, ACCENT_COLOR, count_bg, 2, border_radius=8)
            surface.blit(count_text, (x - count_text.get_width()//2, y - CARD_HEIGHT//2 - count_text.get_height()//2))
        
        # Store rectangle for click detection
        self.rect = pygame.Rect(x - CARD_WIDTH//2 - 10, y - CARD_HEIGHT - 10, 
                               CARD_WIDTH + 20, CARD_HEIGHT + 80)
        
        # Draw position number with background
        pos_text = self.font_manager.small.render(f"Pos {self.index + 1}", True, TEXT_COLOR)
        pos_bg = pygame.Rect(x - pos_text.get_width()//2 - 6, y + 45,
                            pos_text.get_width() + 12, pos_text.get_height() + 6)
        pygame.draw.rect(surface, SHADOW_COLOR, pos_bg.move(2, 2), border_radius=6)
        pygame.draw.rect(surface, (40, 60, 80), pos_bg, border_radius=6)
        surface.blit(pos_text, (x - pos_text.get_width()//2, y + 48))