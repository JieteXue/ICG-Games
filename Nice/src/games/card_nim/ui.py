"""
Card Nim Game UI Components
"""

import pygame
from ui.buttons import Button
from ui.components import CardPosition
from utils.constants import *
from utils.helpers import wrap_text

class CardNimUI:
    """Handles all UI rendering for Card Nim game"""
    
    def __init__(self, screen, font_manager):
        self.screen = screen
        self.font_manager = font_manager
    
    def draw_background(self):
        """Draw the background with gradient effect"""
        self.screen.fill(BACKGROUND_COLOR)
        
        for x in range(0, SCREEN_WIDTH, 40):
            pygame.draw.line(self.screen, (35, 45, 55), (x, 0), (x, SCREEN_HEIGHT), 1)
        for y in range(0, SCREEN_HEIGHT, 40):
            pygame.draw.line(self.screen, (35, 45, 55), (0, y), (SCREEN_WIDTH, y), 1)
    
    def draw_game_info(self, game_logic):
        """Draw game information panel"""
        header_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 180)
        pygame.draw.rect(self.screen, (35, 45, 60), header_rect)
        
        title = self.font_manager.large.render("Card Taking Game", True, TEXT_COLOR)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 20))
        
        # Current message
        message_color = TEXT_COLOR
        if game_logic.game_over:
            message_color = WIN_COLOR if game_logic.winner == "Player 1" else LOSE_COLOR
        
        message_lines = wrap_text(game_logic.message, self.font_manager.medium, SCREEN_WIDTH - 100)
        for i, line in enumerate(message_lines):
            message_text = self.font_manager.medium.render(line, True, message_color)
            self.screen.blit(message_text, (SCREEN_WIDTH//2 - message_text.get_width()//2, 80 + i * 25))
    
    def draw_card_positions(self, positions, selected_position_index):
        """Draw all card positions"""
        if not positions:
            return []
        
        total_positions = len(positions)
        start_x = (SCREEN_WIDTH - (total_positions * (CARD_WIDTH + MARGIN))) // 2
        position_rects = []
        y = POSITION_HEIGHT + 20
        
        for i, count in enumerate(positions):
            x = start_x + i * (CARD_WIDTH + MARGIN) + CARD_WIDTH // 2
            
            card_pos = CardPosition(i, count, self.font_manager)
            card_pos.selected = (i == selected_position_index)
            card_pos.draw(self.screen, x, y)
            position_rects.append(card_pos.rect)
        
        return position_rects
    
    def create_buttons(self):
        """Create all UI buttons for the game"""
        control_y = POSITION_HEIGHT + 150
        control_width = 400
        control_x = (SCREEN_WIDTH - control_width) // 2
        number_button_width = 80
        number_button_height = 50
        
        # Navigation buttons (top left corner)
        nav_button_size = 50
        
        buttons = {
            "minus": Button(control_x, control_y, number_button_width, number_button_height, "−", self.font_manager),
            "plus": Button(control_x + control_width - number_button_width, control_y, number_button_width, number_button_height, "+", self.font_manager),
            "confirm": Button(control_x + 100, control_y + 60, 200, 50, "Confirm Move", self.font_manager),
            "restart": Button(SCREEN_WIDTH//2 - 120, POSITION_HEIGHT + 290, 240, 60, "New Game", self.font_manager),
            "back": Button(20, 20, nav_button_size, nav_button_size, "", self.font_manager, icon='back'),
            "home": Button(20 + nav_button_size + 10, 20, nav_button_size, nav_button_size, "", self.font_manager, icon='home')
        }
        
        return buttons
    
    def draw_control_panel(self, buttons, selected_count, selected_position_index):
        """Draw the control panel with enhanced styling"""
        control_y = POSITION_HEIGHT + 150
        control_width = 400
        control_x = (SCREEN_WIDTH - control_width) // 2
        
        # Draw control panel background
        control_bg = pygame.Rect(control_x - 20, control_y - 20, control_width + 40, 150) 
        pygame.draw.rect(self.screen, (35, 45, 60), control_bg, border_radius=15)
        pygame.draw.rect(self.screen, ACCENT_COLOR, control_bg, 3, border_radius=15)
        
        # Draw count display with background
        count_display = str(selected_count) if selected_position_index is not None else "-"
        count_text = self.font_manager.large.render(count_display, True, TEXT_COLOR)
        count_bg = pygame.Rect(control_x + control_width//2 - 35, control_y-5, 70, 60)
        pygame.draw.rect(self.screen, (40, 60, 80), count_bg, border_radius=12)
        pygame.draw.rect(self.screen, ACCENT_COLOR, count_bg, 3, border_radius=12)
        self.screen.blit(count_text, 
                        (control_x + control_width//2 - count_text.get_width()//2, 
                         control_y + 25 - count_text.get_height()//2))
    
    def draw_hints(self):
        """Draw operation hints separately below control panel"""
        hint_y = POSITION_HEIGHT + 290
        hints = [
            "Use UP/DOWN arrows to adjust number, ENTER to confirm",
            "Use LEFT/RIGHT arrows to switch between positions", 
            "Click on card stacks to select them"
        ]
        
        for i, hint in enumerate(hints):
            hint_text = self.font_manager.small.render(hint, True, (150, 170, 190))
            self.screen.blit(hint_text, (SCREEN_WIDTH//2 - hint_text.get_width()//2, hint_y + i * 20))