"""
Subtract Factor Game - Main game class
"""

import pygame
import sys
from core.base_game import BaseGame
from games.subtract_factor.logic import SubtractFactorLogic
from games.subtract_factor.ui import SubtractFactorUI, FactorButton
from ui.menus import GameModeSelector
from utils.constants import CARD_GAME_FPS

class SubtractFactorInputHandler:
    """Handles input for Subtract Factor game"""
    
    def __init__(self, game_logic):
        self.game_logic = game_logic
    
    def handle_mouse_click(self, event, factor_buttons, control_buttons):
        """Handle mouse click events"""
        mouse_pos = pygame.mouse.get_pos()
        
        if self.game_logic.game_over:
            # Check restart button
            if control_buttons["restart"].is_clicked(event):
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
                # Check factor selection
                for button in factor_buttons:
                    if button.is_clicked(event):
                        self.game_logic.select_factor(int(button.text))
                        break
                
                # Check control buttons (only if factors are available)
                if self.game_logic.valid_factors:
                    if control_buttons["minus"].is_clicked(event) and self.game_logic.selected_factor > 1:
                        # Find previous valid factor
                        current_index = self.game_logic.valid_factors.index(self.game_logic.selected_factor)
                        if current_index > 0:
                            self.game_logic.select_factor(self.game_logic.valid_factors[current_index - 1])
                    
                    elif control_buttons["plus"].is_clicked(event):
                        # Find next valid factor
                        current_index = self.game_logic.valid_factors.index(self.game_logic.selected_factor)
                        if current_index < len(self.game_logic.valid_factors) - 1:
                            self.game_logic.select_factor(self.game_logic.valid_factors[current_index + 1])
                
                # Check confirm button (only if a factor is selected)
                if (control_buttons["confirm"].is_clicked(event) and 
                    self.game_logic.selected_factor in self.game_logic.valid_factors):
                    if self.game_logic.make_move(self.game_logic.selected_factor):
                        self.game_logic.selected_factor = 1
        
        # Check navigation buttons (always available)
        if "back" in control_buttons and control_buttons["back"].is_clicked(event):
            # Go back to previous screen (difficulty selection)
            return "back"
        elif "home" in control_buttons and control_buttons["home"].is_clicked(event):
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
        
        if can_interact and self.game_logic.valid_factors:
            if event.key == pygame.K_LEFT:
                # Select previous factor
                if self.game_logic.selected_factor in self.game_logic.valid_factors:
                    current_index = self.game_logic.valid_factors.index(self.game_logic.selected_factor)
                    if current_index > 0:
                        self.game_logic.select_factor(self.game_logic.valid_factors[current_index - 1])
                elif self.game_logic.valid_factors:
                    self.game_logic.select_factor(self.game_logic.valid_factors[0])
            
            elif event.key == pygame.K_RIGHT:
                # Select next factor
                if self.game_logic.selected_factor in self.game_logic.valid_factors:
                    current_index = self.game_logic.valid_factors.index(self.game_logic.selected_factor)
                    if current_index < len(self.game_logic.valid_factors) - 1:
                        self.game_logic.select_factor(self.game_logic.valid_factors[current_index + 1])
                elif self.game_logic.valid_factors:
                    self.game_logic.select_factor(self.game_logic.valid_factors[0])
            
            elif event.key == pygame.K_RETURN:
                if self.game_logic.selected_factor in self.game_logic.valid_factors:
                    if self.game_logic.make_move(self.game_logic.selected_factor):
                        self.game_logic.selected_factor = 1

class SubtractFactorGame(BaseGame):
    """Subtract Factor Game implementation"""
    
    def __init__(self, screen, font_manager):
        super().__init__(screen, font_manager)
        self.logic = SubtractFactorLogic()
        self.ui = SubtractFactorUI(screen, font_manager)
        self.input_handler = SubtractFactorInputHandler(self.logic)
        
        # Ensure fonts are initialized
        self.font_manager.initialize_fonts()
        
        # Initialize game mode and difficulty
        self.initialize_game_settings()
        
        # Create UI components
        self.control_buttons = self.ui.create_buttons()
        self.factor_buttons = []
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
        for button in self.control_buttons.values():
            button.update_hover(mouse_pos)
        
        for button in self.factor_buttons:
            button.update_hover(mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                result = self.input_handler.handle_mouse_click(event, self.factor_buttons, self.control_buttons)
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
        # Update factor buttons based on current valid factors
        self.factor_buttons = self.ui.create_factor_buttons(
            self.logic.valid_factors, self.logic.selected_factor
        )
        
        # Set button enabled states
        if self.logic.game_mode == "PVE":
            buttons_enabled = (self.logic.current_player == "Player 1")
        else:
            buttons_enabled = True
        
        for button in [self.control_buttons["minus"], self.control_buttons["plus"], self.control_buttons["confirm"]]:
            button.enabled = buttons_enabled and bool(self.logic.valid_factors)
        
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
        """Draw the complete game interface"""
        try:
            # Draw background
            self.ui.draw_background()
            
            # Draw game information
            self.ui.draw_game_info(self.logic)
            
            # Draw factor selection area
            self.ui.draw_factor_selection(self.logic, self.factor_buttons)
            
            # Draw navigation buttons
            if "back" in self.control_buttons:
                self.control_buttons["back"].draw(self.screen)
            if "home" in self.control_buttons:
                self.control_buttons["home"].draw(self.screen)
            
            if not self.logic.game_over:
                # Draw control panel
                self.ui.draw_control_panel(self.control_buttons, self.logic)
                
                # Draw control panel buttons
                for button in [self.control_buttons["minus"], self.control_buttons["plus"], self.control_buttons["confirm"]]:
                    button.draw(self.screen)
                
                # Draw hints
                self.ui.draw_hints()
            else:
                # Draw game over screen
                self.control_buttons["restart"].draw(self.screen)
            
            pygame.display.flip()
            
        except Exception as e:
            print(f"Error in draw: {e}")
            import traceback
            traceback.print_exc()
    
    def get_game_info(self):
        """Return game information"""
        return {
            'name': 'Subtract Factor Game',
            'description': 'Strategic number reduction game using factor subtraction',
            'current_player': self.logic.current_player,
            'game_over': self.logic.game_over,
            'winner': self.logic.winner,
            'current_value': self.logic.current_value,
            'valid_factors': self.logic.valid_factors.copy() if self.logic.valid_factors else []
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