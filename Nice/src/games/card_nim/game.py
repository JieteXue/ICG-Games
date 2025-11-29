"""
Card Nim Game - Main game class
"""

import pygame
import sys
from core.base_game import BaseGame
from games.card_nim.logic import CardNimLogic
from games.card_nim.ui import CardNimUI
from ui.menus import GameModeSelector
from utils.constants import CARD_GAME_FPS
from utils.key_repeat import KeyRepeatManager  # 添加导入

class CardNimInputHandler:
    """Handles input for Card Nim game"""
    
    def __init__(self, game_logic):
        self.game_logic = game_logic
        self.key_repeat_manager = KeyRepeatManager()
    
    def _create_key_callbacks(self):
        """创建按键回调字典"""
        return {
            pygame.K_LEFT: self._select_previous_position,
            pygame.K_RIGHT: self._select_next_position,
            pygame.K_UP: self._increase_count,
            pygame.K_DOWN: self._decrease_count
        }
    
    def handle_mouse_click(self, event, position_rects, buttons):
        """Handle mouse click events"""
        mouse_pos = pygame.mouse.get_pos()
        
        if self.game_logic.game_over:
            # Check restart button
            if buttons["restart"].is_clicked(event):
                self.game_logic.initialize_game(self.game_logic.game_mode, self.game_logic.difficulty)
                self.key_repeat_manager._reset_state()
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
                        self._decrease_count()
                    elif (buttons["plus"].is_clicked(event) and 
                          self.game_logic.selected_count < self.game_logic.positions[self.game_logic.selected_position_index]):
                        self._increase_count()
                
                # Check confirm button (only if a position is selected)
                if (buttons["confirm"].is_clicked(event) and 
                    self.game_logic.selected_position_index is not None):
                    if self.game_logic.make_move(self.game_logic.selected_position_index, self.game_logic.selected_count):
                        self.game_logic.selected_position_index = None
                        self.key_repeat_manager._reset_state()
        
        # Check navigation buttons (always available)
        if "back" in buttons and buttons["back"].is_clicked(event):
            # Go back to previous screen (difficulty selection)
            return "back"
        elif "home" in buttons and buttons["home"].is_clicked(event):
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
            callbacks = self._create_key_callbacks()
            
            # 处理方向键（带重复）
            self.key_repeat_manager.handle_key_event(event, callbacks)
            
            # 处理回车键（不需要重复）
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                if (self.game_logic.selected_position_index is not None and
                    self.game_logic.make_move(self.game_logic.selected_position_index, 
                                            self.game_logic.selected_count)):
                    self.game_logic.selected_position_index = None
                    self.key_repeat_manager._reset_state()
    
    def update_key_repeat(self):
        """更新按键重复状态"""
        if (not self.game_logic.game_over and
            ((self.game_logic.game_mode == "PVP") or 
             (self.game_logic.game_mode == "PVE" and self.game_logic.current_player == "Player 1"))):
            
            callbacks = self._create_key_callbacks()
            self.key_repeat_manager.update(callbacks)
    
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
    
    def _increase_count(self):
        """增加数量"""
        if (self.game_logic.selected_position_index is not None and
            self.game_logic.selected_count < self.game_logic.positions[self.game_logic.selected_position_index]):
            self.game_logic.selected_count += 1
    
    def _decrease_count(self):
        """减少数量"""
        if (self.game_logic.selected_position_index is not None and
            self.game_logic.selected_count > 1):
            self.game_logic.selected_count -= 1

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

        self.key_repeat_manager = KeyRepeatManager()
    
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
                # Check refresh button first
                if "refresh" in self.buttons and self.buttons["refresh"].is_clicked(event):
                    self.logic.initialize_game(self.logic.game_mode, self.logic.difficulty)
                    if hasattr(self, 'key_repeat_manager'):
                        self.key_repeat_manager._reset_state()
                    return True

                result = self.input_handler.handle_mouse_click(event, self.position_rects, self.buttons)
                if result == "back":
                    # Reinitialize game settings
                    self.initialize_game_settings()
                elif result == "home":
                    # Return to main menu
                    return False

            elif event.type in [pygame.KEYDOWN, pygame.KEYUP]:
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
        """Draw the complete game interface"""
        try:
            # Draw background
            self.ui.draw_background()
            
            # Draw game information
            self.ui.draw_game_info(self.logic)
            
            # Draw card positions
            self.position_rects = self.ui.draw_card_positions(
                self.logic.positions, self.logic.selected_position_index)
            
            # Draw navigation buttons (包括刷新按钮)
            if "back" in self.buttons:
                self.buttons["back"].draw(self.screen)
            if "home" in self.buttons:
                self.buttons["home"].draw(self.screen)
            if "refresh" in self.buttons:  # 添加刷新按钮绘制
                self.buttons["refresh"].draw(self.screen)
            
            if not self.logic.game_over:
                # Set button enabled states based on game mode and current player
                if self.logic.game_mode == "PVE":
                    # In PvE mode, only enable buttons during Player 1's turn
                    buttons_enabled = (self.logic.current_player == "Player 1")
                else:
                    # In PvP mode, always enable buttons for both players
                    buttons_enabled = True
                
                for button in [self.buttons["minus"], self.buttons["plus"], self.buttons["confirm"]]:
                    button.enabled = buttons_enabled
                
                self.ui.draw_control_panel(
                    self.buttons, self.logic.selected_count, self.logic.selected_position_index)
                
                # Draw control panel buttons
                for button in [self.buttons["minus"], self.buttons["plus"], self.buttons["confirm"]]:
                    button.draw(self.screen)
                
                # Draw hints
                self.ui.draw_hints()
            else:
                # Draw game over screen
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
            
            # 自动更新按键重复状态
            if self.key_repeat_enabled:
                self.update_key_repeat()
                
            self.draw()
            self.clock.tick(CARD_GAME_FPS)