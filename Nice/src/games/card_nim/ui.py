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
        """Draw game information panel with enhanced styling"""
        # Draw header background
        header_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 180)
        pygame.draw.rect(self.screen, (35, 45, 60), header_rect)
        pygame.draw.line(self.screen, ACCENT_COLOR, (0, 180), (SCREEN_WIDTH, 180), 3)
        
        # Game title with shadow
        title = self.font_manager.large.render("Card Taking Game", True, TEXT_COLOR)
        title_shadow = self.font_manager.large.render("Card Taking Game", True, SHADOW_COLOR)
        self.screen.blit(title_shadow, (SCREEN_WIDTH//2 - title.get_width()//2 + 2, 15))
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 13))
        
        # Game mode and difficulty info
        difficulty_names = ["Easy", "Normal", "Hard", "Insane"]
        position_count = len(game_logic.positions)
        
        if game_logic.game_mode == "PVP":
            mode_text = "Mode: Player vs Player"
        else:
            mode_text = f"Mode: Player vs AI - {difficulty_names[game_logic.difficulty-1]}"
        
        mode_info = self.font_manager.small.render(
            f"{mode_text} | Positions: {position_count}", 
            True, ACCENT_COLOR)
        self.screen.blit(mode_info, (20, 120))
        
        # Current player info with highlight
        player_colors = {
            "Player 1": WIN_COLOR,
            "Player 2": (255, 200, 50),  # Yellow for Player 2
            "AI": LOSE_COLOR
        }
        player_color = player_colors.get(game_logic.current_player, TEXT_COLOR)
        
        player_text = self.font_manager.small.render(
            f"Current Player: {game_logic.current_player}", 
            True, player_color
        )
        
        # Draw player info with background
        player_bg = pygame.Rect(SCREEN_WIDTH - player_text.get_width() - 40, 135, 
                              player_text.get_width() + 20, player_text.get_height() + 10)
        pygame.draw.rect(self.screen, (40, 50, 65), player_bg, border_radius=8)
        pygame.draw.rect(self.screen, player_color, player_bg, 2, border_radius=8)
        self.screen.blit(player_text, (SCREEN_WIDTH - player_text.get_width() - 30, 140))
        
        # Current message with background - with text wrapping
        message_color = (WIN_COLOR if game_logic.game_over and game_logic.winner == "Player 1" 
                        else LOSE_COLOR if game_logic.game_over and game_logic.winner == "AI"
                        else (255, 200, 50) if game_logic.game_over and game_logic.winner == "Player 2"
                        else TEXT_COLOR)
        
        # Handle long messages with text wrapping
        message_lines = wrap_text(game_logic.message, self.font_manager.medium, SCREEN_WIDTH - 100)
        for i, line in enumerate(message_lines):
            message_text = self.font_manager.medium.render(line, True, message_color)
            message_bg_width = message_text.get_width() + 30
            message_bg = pygame.Rect(SCREEN_WIDTH//2 - message_bg_width//2, 85 + i * 25, 
                                   message_bg_width, message_text.get_height() + 6)
            
            # Only show background on first line
            if i == 0:
                pygame.draw.rect(self.screen, (40, 50, 65), message_bg, border_radius=8)
                pygame.draw.rect(self.screen, ACCENT_COLOR, message_bg, 2, border_radius=8)
            
            self.screen.blit(message_text, (SCREEN_WIDTH//2 - message_text.get_width()//2, 88 + i * 25))
        
        # Current selection info
        if game_logic.selected_position_index is not None:
            select_info = self.font_manager.small.render(
                f"Selected: Position {game_logic.selected_position_index + 1}, Count: {game_logic.selected_count}", 
                True, ACCENT_COLOR)
            self.screen.blit(select_info, (SCREEN_WIDTH//2 - select_info.get_width()//2, 130))
        
        # Game state indicator (winning/losing position)
        if not game_logic.game_over:
            game_state = "Winning Position" if game_logic.judge_win() else "Losing Position"
            state_color = WIN_COLOR if game_logic.judge_win() else LOSE_COLOR
            state_text = self.font_manager.small.render(game_state, True, state_color)
            
            state_bg = pygame.Rect(SCREEN_WIDTH//2 - state_text.get_width()//2 - 10, 155, 
                                 state_text.get_width() + 20, state_text.get_height() + 6)
            pygame.draw.rect(self.screen, (40, 50, 65), state_bg, border_radius=6)
            pygame.draw.rect(self.screen, state_color, state_bg, 2, border_radius=6)
            self.screen.blit(state_text, (SCREEN_WIDTH//2 - state_text.get_width()//2, 158))
    
    def draw_card_positions(self, positions, selected_position_index):
        """Draw all card positions and return their clickable rectangles"""
        if not positions:
            return []
        
        total_positions = len(positions)
        start_x = (SCREEN_WIDTH - (total_positions * (CARD_WIDTH + MARGIN))) // 2
        position_rects = []
        
        # Adjust vertical position for card stacks
        y = POSITION_HEIGHT + 20
        
        for i, count in enumerate(positions):
            x = start_x + i * (CARD_WIDTH + MARGIN) + CARD_WIDTH // 2
            
            # Create temporary card position for drawing
            card_pos = CardPosition(i, count, self.font_manager)
            card_pos.selected = (i == selected_position_index)
            card_pos.draw(self.screen, x, y)
            position_rects.append(card_pos.rect)
        
        return position_rects
    
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
            "minus": Button(control_x, control_y, number_button_width, number_button_height, "−", self.font_manager, tooltip="Decrease card count"),
            "plus": Button(control_x + control_width - number_button_width, control_y, number_button_width, number_button_height, "+", self.font_manager, tooltip="Increase card count"),
            "confirm": Button(control_x + 100, control_y + 60, 200, 50, "Confirm Move", self.font_manager, tooltip="Make move with selected cards"),
            "restart": Button(SCREEN_WIDTH//2 - 120, POSITION_HEIGHT + 250, 240, 60, "New Game", self.font_manager, tooltip="Start a new game"),
            "back": Button(20, 20, nav_button_size, nav_button_size, "", self.font_manager, icon='back', tooltip="Back to mode selection"),
            "home": Button(20 + nav_button_size + 10, 20, nav_button_size, nav_button_size, "", self.font_manager, icon='home', tooltip="Back to main menu"),
            "refresh": Button(SCREEN_WIDTH - 20 - nav_button_size, 20, nav_button_size, nav_button_size, "", self.font_manager, icon='refresh', tooltip="Restart current game")
        }
        
        return buttons