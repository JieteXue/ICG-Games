"""
Split Cards Game UI Components
"""

import pygame
from ui.buttons import Button
from utils.constants import *
from utils.helpers import wrap_text

class SplitCardsUI:
    """Handles all UI rendering for Split Cards game"""
    
    def __init__(self, screen, font_manager):
        self.screen = screen
        self.font_manager = font_manager
        self.table_color = (210, 180, 140)  # Beige table color
        self.table_rect = pygame.Rect(50, 150, SCREEN_WIDTH - 100, 400)
    
    def draw_background(self):
        """Draw the background with table"""
        # Draw dark background
        self.screen.fill((30, 25, 20))
        
        # Draw wooden table
        pygame.draw.rect(self.screen, self.table_color, self.table_rect, border_radius=20)
        
        # Draw table texture (wood grain)
        for y in range(self.table_rect.top, self.table_rect.bottom, 4):
            pygame.draw.line(self.screen, 
                            (200, 170, 130), 
                            (self.table_rect.left, y), 
                            (self.table_rect.right, y), 
                            1)
        
        # Draw table edge
        pygame.draw.rect(self.screen, (180, 150, 110), self.table_rect, 5, border_radius=20)
        
        # Draw table shadow
        shadow_rect = self.table_rect.move(8, 8)
        pygame.draw.rect(self.screen, (20, 15, 10), shadow_rect, border_radius=20)
    
    def draw_game_info(self, game_logic):
        """Draw game information panel"""
        # Draw header
        header_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 120)
        pygame.draw.rect(self.screen, (40, 35, 30), header_rect)
        pygame.draw.line(self.screen, (180, 150, 110), (0, 120), (SCREEN_WIDTH, 120), 3)
        
        # Game title
        title = self.font_manager.large.render("Split Cards", True, (240, 230, 220))
        title_shadow = self.font_manager.large.render("Split Cards", True, (20, 15, 10))
        self.screen.blit(title_shadow, (SCREEN_WIDTH//2 - title.get_width()//2 + 2, 15))
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 13))
        
        # Game rules
        rules = "Take 1-{} cards from a pile, or split a pile into two non-empty piles".format(game_logic.max_take)
        rules_text = self.font_manager.small.render(rules, True, (200, 190, 170))
        self.screen.blit(rules_text, (SCREEN_WIDTH//2 - rules_text.get_width()//2, 50))
        
        # Game mode and difficulty
        if game_logic.game_mode == "PVP":
            mode_text = "Mode: Player vs Player"
        else:
            difficulty_names = ["Easy", "Normal", "Hard", "Insane"]
            mode_text = f"Mode: Player vs AI - {difficulty_names[game_logic.difficulty-1]}"
        
        mode_info = self.font_manager.small.render(mode_text, True, (180, 150, 110))
        self.screen.blit(mode_info, (20, 85))
        
        # Current player
        player_colors = {
            "Player 1": (100, 200, 100),
            "Player 2": (255, 200, 50),
            "AI": (220, 100, 100)
        }
        player_color = player_colors.get(game_logic.current_player, (240, 230, 220))
        
        player_text = self.font_manager.medium.render(
            f"Current Player: {game_logic.current_player}", 
            True, player_color
        )
        
        player_bg = pygame.Rect(SCREEN_WIDTH - player_text.get_width() - 40, 75, 
                              player_text.get_width() + 20, player_text.get_height() + 10)
        pygame.draw.rect(self.screen, (50, 45, 40), player_bg, border_radius=8)
        pygame.draw.rect(self.screen, player_color, player_bg, 2, border_radius=8)
        self.screen.blit(player_text, (SCREEN_WIDTH - player_text.get_width() - 30, 80))
        
        # Game message
        message_color = (100, 200, 100) if game_logic.game_over and game_logic.winner == "Player 1" \
                        else (220, 100, 100) if game_logic.game_over and (game_logic.winner == "AI" or game_logic.winner == "Player 2") \
                        else (240, 230, 220)
        
        message_lines = wrap_text(game_logic.message, self.font_manager.medium, SCREEN_WIDTH - 100)
        for i, line in enumerate(message_lines):
            message_text = self.font_manager.medium.render(line, True, message_color)
            if i == 0:
                message_bg_width = message_text.get_width() + 30
                message_bg = pygame.Rect(SCREEN_WIDTH//2 - message_bg_width//2, 105, 
                                       message_bg_width, message_text.get_height() + 6)
                pygame.draw.rect(self.screen, (50, 45, 40), message_bg, border_radius=8)
                pygame.draw.rect(self.screen, (180, 150, 110), message_bg, 2, border_radius=8)
            self.screen.blit(message_text, (SCREEN_WIDTH//2 - message_text.get_width()//2, 108 + i * 25))
    
    def draw_card_piles(self, card_piles, selected_index, selected_action):
        """Draw all card piles on the table"""
        if not card_piles:
            return []
        
        pile_rects = []
        num_piles = len(card_piles)
        
        # Calculate pile positions
        pile_width = 100
        pile_height = 150
        spacing = 30
        
        # Adjust layout based on number of piles
        if num_piles <= 5:
            # Single row
            total_width = num_piles * pile_width + (num_piles - 1) * spacing
            start_x = self.table_rect.centerx - total_width // 2
            y = self.table_rect.centery - pile_height // 2
            
            for i, pile_count in enumerate(card_piles):
                x = start_x + i * (pile_width + spacing)
                pile_rect = self.draw_pile(x, y, pile_width, pile_height, pile_count, 
                                          i, selected_index, selected_action)
                pile_rects.append(pile_rect)
        else:
            # Two rows
            row1_count = (num_piles + 1) // 2
            row2_count = num_piles - row1_count
            
            # Row 1
            total_width = row1_count * pile_width + (row1_count - 1) * spacing
            start_x = self.table_rect.centerx - total_width // 2
            y1 = self.table_rect.centery - pile_height - 20
            
            for i in range(row1_count):
                x = start_x + i * (pile_width + spacing)
                pile_rect = self.draw_pile(x, y1, pile_width, pile_height, 
                                          card_piles[i], i, selected_index, selected_action)
                pile_rects.append(pile_rect)
            
            # Row 2
            total_width = row2_count * pile_width + (row2_count - 1) * spacing
            start_x = self.table_rect.centerx - total_width // 2
            y2 = self.table_rect.centery + 20
            
            for i in range(row2_count):
                x = start_x + i * (pile_width + spacing)
                pile_idx = row1_count + i
                pile_rect = self.draw_pile(x, y2, pile_width, pile_height, 
                                          card_piles[pile_idx], pile_idx, selected_index, selected_action)
                pile_rects.append(pile_rect)
        
        return pile_rects
    
    def draw_pile(self, x, y, width, height, count, index, selected_index, selected_action):
        """Draw a single card pile"""
        # Pile background (card stack)
        pile_rect = pygame.Rect(x, y, width, height)
        
        # Draw pile shadow
        shadow_rect = pile_rect.move(5, 5)
        pygame.draw.rect(self.screen, (150, 120, 90), shadow_rect, border_radius=10)
        
        # Draw cards in stack (visual effect)
        card_color = (255, 245, 230)  # Off-white card color
        border_color = (180, 150, 110)  # Wood-like border
        
        if index == selected_index:
            if selected_action == 'take':
                card_color = (255, 255, 200)  # Yellowish for take selection
                border_color = (255, 200, 50)
            elif selected_action == 'split':
                card_color = (200, 255, 200)  # Greenish for split selection
                border_color = (100, 200, 100)
        
        # Draw card stack (multiple cards slightly offset)
        for i in range(min(5, count)):
            offset = i * 3
            card_rect = pygame.Rect(x + offset, y + offset, width, height)
            pygame.draw.rect(self.screen, card_color, card_rect, border_radius=8)
            pygame.draw.rect(self.screen, border_color, card_rect, 2, border_radius=8)
        max_offset = min(4, count-1) * 3
        # Draw card count
        count_text = self.font_manager.large.render(str(count), True, (40, 35, 30))
        count_bg = pygame.Rect(x + width//2 - 25+max_offset, y + height//2 - 20+max_offset, 50, 40)
        pygame.draw.rect(self.screen, (255, 245, 230), count_bg, border_radius=8)
        pygame.draw.rect(self.screen, (180, 150, 110), count_bg, 2, border_radius=8)
        self.screen.blit(count_text, (x + width//2 - count_text.get_width()//2+max_offset, 
                                     y + height//2 - count_text.get_height()//2+max_offset))
        
        # Draw pile number background
        pygame.draw.rect(self.screen, (50, 45, 40), 
                         (x+10, y + height + 15, width-10, 30), border_radius=5)
        pygame.draw.rect(self.screen, (180, 150, 110), 
                         (x+10, y + height + 15, width-10, 30), 2, border_radius=5)

        # Draw pile number
        pile_num = self.font_manager.small.render(f"Pile {index + 1}", True, (255, 255, 255))
        self.screen.blit(pile_num, (x + width//2 - pile_num.get_width()//2+5, y + height + 18))

        
        return pile_rect
    
    def draw_control_panel(self, game_logic):
        """Draw control panel for actions"""
        control_y = self.table_rect.bottom + 20
        control_width = 600
        control_x = (SCREEN_WIDTH - control_width) // 2
        
        # Control panel background
        control_bg = pygame.Rect(control_x - 20, control_y - 20, control_width + 40, 120)
        pygame.draw.rect(self.screen, (50, 45, 40), control_bg, border_radius=15)
        pygame.draw.rect(self.screen, (180, 150, 110), control_bg, 3, border_radius=15)
        
        # Action type selection
        action_text = self.font_manager.medium.render("Select Action:", True, (240, 230, 220))
        self.screen.blit(action_text, (control_x, control_y))
        
        return control_x, control_y
    
    def create_buttons(self):
        """Create all UI buttons for the game"""
        buttons = {}
        
        # Navigation buttons
        nav_button_size = 50
        buttons["back"] = Button(20, 20, nav_button_size, nav_button_size, "", 
                                self.font_manager, icon='back', tooltip="Back to mode selection")
        buttons["home"] = Button(20 + nav_button_size + 10, 20, nav_button_size, nav_button_size, "", 
                                self.font_manager, icon='home', tooltip="Back to main menu")
        buttons["refresh"] = Button(SCREEN_WIDTH - 20 - nav_button_size, 20, nav_button_size, nav_button_size, "", 
                                   self.font_manager, icon='refresh', tooltip="Restart current game")
        
        # Action buttons
        control_y = self.table_rect.bottom + 20 if hasattr(self, 'table_rect') else 500
        control_width = 600
        control_x = (SCREEN_WIDTH - control_width) // 2
        
        buttons["take_btn"] = Button(control_x, control_y + 40, 180, 50, "Take Cards", 
                                    self.font_manager, tooltip="Take cards from selected pile")
        buttons["split_btn"] = Button(control_x + 200, control_y + 40, 180, 50, "Split Pile", 
                                     self.font_manager, tooltip="Split selected pile into two")
        buttons["confirm_btn"] = Button(control_x + 400, control_y + 40, 180, 50, "Confirm Move", 
                                       self.font_manager, tooltip="Execute selected move")
        
        # Number adjustment buttons
        buttons["minus"] = Button(control_x + 100, control_y + 100, 50, 40, "−", 
                                 self.font_manager, tooltip="Decrease count")
        buttons["plus"] = Button(control_x + 150, control_y + 100, 50, 40, "+", 
                                self.font_manager, tooltip="Increase count")
        
        # Restart button
        buttons["restart"] = Button(SCREEN_WIDTH//2 - 120, control_y + 150, 240, 60, 
                                   "New Game", self.font_manager, tooltip="Start a new game")
        
        return buttons