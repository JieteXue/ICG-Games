"""
Subtract Factor Game - Main game class
"""

import pygame
import sys
from core.base_game import BaseGame
from games.subtract_factor.logic import SubtractFactorLogic
from games.subtract_factor.ui import SubtractFactorUI, FactorButton, ScrollButton
from ui.menus import GameModeSelector
from utils.constants import CARD_GAME_FPS
from utils.key_repeat import KeyRepeatManager  

class SubtractFactorInputHandler:
    """Handles input for Subtract Factor game"""
    
    def __init__(self, game_logic, ui):
        self.game_logic = game_logic
        self.ui = ui
        self.key_repeat_manager = KeyRepeatManager()
    
    def _create_key_callbacks(self):
        """创建按键回调字典"""
        return {
            pygame.K_LEFT: self._select_previous_factor,
            pygame.K_RIGHT: self._select_next_factor,
            pygame.K_UP: lambda: self.ui.scroll_left(len(self.game_logic.valid_factors)),
            pygame.K_DOWN: lambda: self.ui.scroll_right(len(self.game_logic.valid_factors))
        }
    
    def handle_mouse_click(self, event, factor_buttons, scroll_buttons, control_buttons):
        """Handle mouse click events"""
        mouse_pos = pygame.mouse.get_pos()
        
        if self.game_logic.game_over:
            # Check restart button
            if control_buttons["restart"].is_clicked(event):
                self.game_logic.initialize_game(self.game_logic.game_mode, self.game_logic.difficulty)
                self.ui.scroll_offset = 0
                self.key_repeat_manager._reset_state()
        else:
            # Check if current player can interact
            can_interact = False
            if self.game_logic.game_mode == "PVP":
                can_interact = True
            elif self.game_logic.game_mode == "PVE" and self.game_logic.current_player == "Player 1":
                can_interact = True
            
            if can_interact:
                # Check scroll buttons first
                for button in scroll_buttons:
                    if button.is_clicked(event):
                        if button.text == "◀":
                            self.ui.scroll_left(len(self.game_logic.valid_factors))
                        else:
                            self.ui.scroll_right(len(self.game_logic.valid_factors))
                        return None
                
                # Check factor selection
                for button in factor_buttons:
                    if button.is_clicked(event):
                        self.game_logic.select_factor(button.factor_value)
                        break
                
                # Check control buttons
                if self.game_logic.valid_factors:
                    if control_buttons["minus"].is_clicked(event) and self.game_logic.selected_factor > 1:
                        self._select_previous_factor()
                    
                    elif control_buttons["plus"].is_clicked(event):
                        self._select_next_factor()
                
                # Check confirm button
                if (control_buttons["confirm"].is_clicked(event) and 
                    self.game_logic.selected_factor in self.game_logic.valid_factors):
                    if self.game_logic.make_move(self.game_logic.selected_factor):
                        self.game_logic.selected_factor = 1
                        self.ui.scroll_offset = 0
                        self.key_repeat_manager._reset_state()
        
        # Check navigation buttons
        if "back" in control_buttons and control_buttons["back"].is_clicked(event):
            return "back"
        elif "home" in control_buttons and control_buttons["home"].is_clicked(event):
            return "home"
        
        return None
    
    def handle_keyboard(self, event):
        """Handle keyboard events"""
        if self.game_logic.game_over:
            return
        
        # Check if current player can interact
        can_interact = False
        if self.game_logic.game_mode == "PVP":
            can_interact = True
        elif self.game_logic.game_mode == "PVE" and self.game_logic.current_player == "Player 1":
            can_interact = True
        
        if can_interact and self.game_logic.valid_factors:
            callbacks = self._create_key_callbacks()
            
            # 处理方向键
            self.key_repeat_manager.handle_key_event(event, callbacks)
            
            # 处理回车键（不需要重复）
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                if self.game_logic.selected_factor in self.game_logic.valid_factors:
                    if self.game_logic.make_move(self.game_logic.selected_factor):
                        self.game_logic.selected_factor = 1
                        self.ui.scroll_offset = 0
                        self.key_repeat_manager._reset_state()
    
    def update_key_repeat(self):
        """更新按键重复状态"""
        if (not self.game_logic.game_over and 
            self.game_logic.valid_factors and
            ((self.game_logic.game_mode == "PVP") or 
             (self.game_logic.game_mode == "PVE" and self.game_logic.current_player == "Player 1"))):
            
            callbacks = self._create_key_callbacks()
            self.key_repeat_manager.update(callbacks)
    
    def _select_previous_factor(self):
        """选择前一个因数"""
        if self.game_logic.selected_factor in self.game_logic.valid_factors:
            current_index = self.game_logic.valid_factors.index(self.game_logic.selected_factor)
            if current_index > 0:
                self.game_logic.select_factor(self.game_logic.valid_factors[current_index - 1])
                if current_index - 1 < self.ui.scroll_offset:
                    self.ui.scroll_offset = max(0, current_index - 1)
        elif self.game_logic.valid_factors:
            self.game_logic.select_factor(self.game_logic.valid_factors[0])
    
    def _select_next_factor(self):
        """选择下一个因数"""
        if self.game_logic.selected_factor in self.game_logic.valid_factors:
            current_index = self.game_logic.valid_factors.index(self.game_logic.selected_factor)
            if current_index < len(self.game_logic.valid_factors) - 1:
                self.game_logic.select_factor(self.game_logic.valid_factors[current_index + 1])
                if current_index + 1 >= self.ui.scroll_offset + self.ui.visible_factor_count:
                    self.ui.scroll_offset = min(
                        len(self.game_logic.valid_factors) - self.ui.visible_factor_count,
                        current_index + 1 - self.ui.visible_factor_count + 1
                    )
        elif self.game_logic.valid_factors:
            self.game_logic.select_factor(self.game_logic.valid_factors[0])

class SubtractFactorGame(BaseGame):
    """Subtract Factor Game implementation"""
    
    def __init__(self, screen, font_manager):
        super().__init__(screen, font_manager)
        self.logic = SubtractFactorLogic()
        self.ui = SubtractFactorUI(screen, font_manager)
        self.input_handler = SubtractFactorInputHandler(self.logic, self.ui)
        
        # 确保字体已初始化
        self.font_manager.initialize_fonts()
        
        # Initialize game mode and difficulty
        self.initialize_game_settings()
        
        # Create UI components
        self.control_buttons = self.ui.create_buttons()
        self.factor_buttons = []
        self.scroll_buttons = []
        self.ai_timer = 0
    
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
        
        for button in self.scroll_buttons:
            button.update_hover(mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                result = self.input_handler.handle_mouse_click(
                    event, self.factor_buttons, self.scroll_buttons, self.control_buttons
                )
                if result == "back":
                    # Reinitialize game settings
                    self.initialize_game_settings()
                    self.ui.scroll_offset = 0
                elif result == "home":
                    # Return to main menu
                    return False
            
            elif event.type in [pygame.KEYDOWN, pygame.KEYUP]:
                self.input_handler.handle_keyboard(event)
            
            elif event.type == pygame.MOUSEWHEEL:
                # Handle mouse wheel scrolling
                self.ui.handle_mouse_wheel(event, len(self.logic.valid_factors))
        
        return True
    
    def update(self):
        """Update game state"""
        # Update factor buttons based on current valid factors
        self.factor_buttons = self.ui.create_factor_buttons(
            self.logic.valid_factors, self.logic.selected_factor
        )
        
        # Update scroll buttons
        self.scroll_buttons = self.ui.create_scroll_buttons(len(self.logic.valid_factors))
        
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
                self.ui.scroll_offset = 0  # Reset scroll after AI move
    
    def draw(self):
        """Draw the complete game interface"""
        try:
            # Draw background
            self.ui.draw_background()
            
            # Draw game information
            self.ui.draw_game_info(self.logic)
            
            # Draw factor selection area with scrolling
            self.ui.draw_factor_selection(self.logic, self.factor_buttons, self.scroll_buttons)
            
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
            
            # 自动更新按键重复状态
            if self.key_repeat_enabled:
                self.update_key_repeat()
                
            self.draw()
            self.clock.tick(CARD_GAME_FPS)  # 使用自定义FPS