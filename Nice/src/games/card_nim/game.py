"""
Card Nim Game - Main game class
"""

import pygame
import sys

# 修复导入 - 使用绝对导入
from core.base_game import BaseGame
from games.card_nim.logic import CardNimLogic
from games.card_nim.ui import CardNimUI
from ui.menus import GameModeSelector
from utils.constants import CARD_GAME_FPS

# 其余的CardNimGame代码保持不变...

class CardNimInputHandler:
    """Handles input for Card Nim game"""
    
    def __init__(self, game_logic):
        self.game_logic = game_logic
    
    def handle_mouse_click(self, event, position_rects, buttons):
        """Handle mouse click events"""
        mouse_pos = pygame.mouse.get_pos()
        
        if self.game_logic.game_over:
            # Check restart button
            if buttons["restart"].is_clicked(event):
                self.game_logic.initialize_game(self.game_logic.game_mode, self.game_logic.difficulty)
        else:
            # Check if current player can interact
            can_interact = False
            if self.game_logic.game_mode == "PVP":
                # In PvP mode, both players can interact
                can_interact = True
            elif self.game_logic.game_mode == "PVE" and self.game_logic.current_player == "Player 1":
                # In PvE mode, only Player 1 can interact
                can_interact = True
            
            if can_interact:
                # Check position selection
                for i, rect in enumerate(position_rects):
                    if rect.collidepoint(mouse_pos):
                        self.game_logic.select_position(i)
                        break
                
                # Check number buttons (only if a position is selected)
                if self.game_logic.selected_position_index is not None:
                    if buttons["minus"].is_clicked(event) and self.game_logic.selected_count > 1:
                        self.game_logic.selected_count -= 1
                    elif (buttons["plus"].is_clicked(event) and 
                          self.game_logic.selected_count < self.game_logic.positions[self.game_logic.selected_position_index]):
                        self.game_logic.selected_count += 1
                
                # Check confirm button (only if a position is selected)
                if (buttons["confirm"].is_clicked(event) and 
                    self.game_logic.selected_position_index is not None):
                    if self.game_logic.make_move(self.game_logic.selected_position_index, self.game_logic.selected_count):
                        self.game_logic.selected_position_index = None
        
        # Check navigation buttons (always available)
        if buttons["back"].is_clicked(event):
            # Go back to previous screen (difficulty selection)
            return "back"
        elif buttons["home"].is_clicked(event):
            # Go back to main menu
            return "home"
        
        return None
    
    def handle_keyboard(self, event):
        """Handle keyboard events"""
        if self.game_logic.game_over:
            return
        
        # Check if current player can interact
        can_interact = False
        if self.game_logic.game_mode == "PVP":
            # In PvP mode, both players can interact
            can_interact = True
        elif self.game_logic.game_mode == "PVE" and self.game_logic.current_player == "Player 1":
            # In PvE mode, only Player 1 can interact
            can_interact = True
        
        if can_interact:
            if self.game_logic.selected_position_index is not None:
                # Number adjustment with up/down arrows
                if event.key == pygame.K_UP and self.game_logic.selected_count < self.game_logic.positions[self.game_logic.selected_position_index]:
                    self.game_logic.selected_count += 1
                elif event.key == pygame.K_DOWN and self.game_logic.selected_count > 1:
                    self.game_logic.selected_count -= 1
                elif event.key == pygame.K_RETURN:
                    if self.game_logic.make_move(self.game_logic.selected_position_index, self.game_logic.selected_count):
                        self.game_logic.selected_position_index = None
            
            # Position selection with left/right arrows
            if event.key == pygame.K_LEFT:
                self._select_previous_position()
            elif event.key == pygame.K_RIGHT:
                self._select_next_position()
    
    def _select_previous_position(self):
        """Select the previous available position"""
        if self.game_logic.selected_position_index is None and len(self.game_logic.positions) > 0:
            # Select the first available position from the right
            for i in range(len(self.game_logic.positions)-1, -1, -1):
                if self.game_logic.positions[i] > 0:
                    self.game_logic.select_position(i)
                    break
        elif self.game_logic.selected_position_index is not None:
            # Move left through positions
            new_position = self.game_logic.selected_position_index
            for i in range(1, len(self.game_logic.positions)):
                new_position = (self.game_logic.selected_position_index - i) % len(self.game_logic.positions)
                if self.game_logic.positions[new_position] > 0:
                    self.game_logic.select_position(new_position)
                    self.game_logic.selected_count = min(self.game_logic.selected_count, self.game_logic.positions[new_position])
                    break
    
    def _select_next_position(self):
        """Select the next available position"""
        if self.game_logic.selected_position_index is None and len(self.game_logic.positions) > 0:
            # Select the first available position from the left
            for i in range(len(self.game_logic.positions)):
                if self.game_logic.positions[i] > 0:
                    self.game_logic.select_position(i)
                    break
        elif self.game_logic.selected_position_index is not None:
            # Move right through positions
            new_position = self.game_logic.selected_position_index
            for i in range(1, len(self.game_logic.positions)):
                new_position = (self.game_logic.selected_position_index + i) % len(self.game_logic.positions)
                if self.game_logic.positions[new_position] > 0:
                    self.game_logic.select_position(new_position)
                    self.game_logic.selected_count = min(self.game_logic.selected_count, self.game_logic.positions[new_position])
                    break

class CardNimGame(BaseGame):
    """Card Taking Game implementation"""
    
    def __init__(self, screen, font_manager):
        super().__init__(screen, font_manager)
        self.logic = CardNimLogic()
        self.ui = CardNimUI(screen, font_manager)
        self.input_handler = CardNimInputHandler(self.logic)
        
        # 确保字体已初始化
        self.font_manager.initialize_fonts()
        
        # Initialize game mode and difficulty
        self.initialize_game_settings()
        
        # Create UI components
        self.buttons = self.ui.create_buttons()
        self.position_rects = []
        self.ai_timer = 0
        self.clock = pygame.time.Clock()
    
    def initialize_game_settings(self):
        """Initialize game mode and difficulty"""
        try:
            # Use the game mode selector
            selector = GameModeSelector(self.screen, self.font_manager)
            game_mode = selector.get_game_mode()
            
            if game_mode == "PVE":
                difficulty = selector.get_difficulty()
                self.logic.initialize_game("PVE", difficulty)
            else:
                self.logic.initialize_game("PVP")
                
        except Exception as e:
            print(f"Error initializing game settings: {e}")
            # Fallback initialization
            self.logic.initialize_game("PVE", 2)
    
    def handle_events(self):
        """Handle game events"""
        mouse_pos = pygame.mouse.get_pos()
        
        # Update button hover states
        for button in self.buttons.values():
            button.update_hover(mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                result = self.input_handler.handle_mouse_click(event, self.position_rects, self.buttons)
                if result == "back":
                    # Reinitialize game settings
                    self.initialize_game_settings()
                elif result == "home":
                    # Return to main menu
                    return False
            
            elif event.type == pygame.KEYDOWN:
                self.input_handler.handle_keyboard(event)
        
        return True
    
    def update(self):
        """Update game state"""
        # AI's turn (only in PvE mode)
        if (self.logic.game_mode == "PVE" and 
            self.logic.current_player == "AI" and 
            not self.logic.game_over):
            
            self.ai_timer += 1
            # Add delay for AI move to make it visible
            if self.ai_timer > 30:
                self.logic.ai_make_move()
                self.ai_timer = 0
    
    def draw(self):
        """Draw the game"""
        try:
            self.ui.draw_background()
            self.ui.draw_game_info(self.logic)
            
            # Draw card positions
            self.position_rects = self.ui.draw_card_positions(
                self.logic.positions, self.logic.selected_position_index)
            
            # Draw navigation buttons (检查是否存在)
            if "back" in self.buttons:
                self.buttons["back"].draw(self.screen)
            if "home" in self.buttons:
                self.buttons["home"].draw(self.screen)
            
            if not self.logic.game_over:
                # Set button enabled states
                buttons_enabled = (self.logic.game_mode == "PVP" or 
                                 self.logic.current_player == "Player 1")
                
                # 只绘制存在的按钮
                for button_name in ["minus", "plus", "confirm"]:
                    if button_name in self.buttons:
                        self.buttons[button_name].enabled = buttons_enabled
                
                self.ui.draw_control_panel(
                    self.buttons, self.logic.selected_count, self.logic.selected_position_index)
                
                # Draw control panel buttons
                for button_name in ["minus", "plus", "confirm"]:
                    if button_name in self.buttons:
                        self.buttons[button_name].draw(self.screen)
                
                self.ui.draw_hints()
            else:
                if "restart" in self.buttons:
                    self.buttons["restart"].draw(self.screen)
            
            pygame.display.flip()
            
        except Exception as e:
            print(f"Error in draw: {e}")
            import traceback
            traceback.print_exc()
    
    def get_game_info(self):
        """Return game information"""
        return {
            'name': 'Card Nim Game',
            'description': 'Strategic card taking game using Nim theory',
            'current_player': self.logic.current_player,
            'game_over': self.logic.game_over,
            'winner': self.logic.winner,
            'positions': self.logic.positions.copy() if self.logic.positions else []
        }
    
    def run(self):
        """Run the main game loop with custom FPS"""
        self.running = True
        while self.running:
            if not self.handle_events():
                break
            self.update()
            self.draw()
            self.clock.tick(CARD_GAME_FPS)