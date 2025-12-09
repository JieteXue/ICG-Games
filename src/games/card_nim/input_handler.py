"""
Card Nim Game Input Handler
"""

import pygame
from utils.key_repeat import KeyRepeatManager

class CardNimInputHandler:
    """Handles input for Card Nim game"""
    
    def __init__(self, game_logic, ui):
        self.game_logic = game_logic
        self.ui = ui
        self.key_repeat_manager = KeyRepeatManager()
    
    def _create_key_callbacks(self):
        """Create key callback dictionary"""
        return {
            pygame.K_LEFT: self._select_previous_position,
            pygame.K_RIGHT: self._select_next_position,
            pygame.K_UP: self._increase_count,
            pygame.K_DOWN: self._decrease_count
        }
    
    def handle_event(self, event, position_rects, buttons):
        """Handle input event"""
        mouse_pos = pygame.mouse.get_pos()
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            return self._handle_mouse_click(event, position_rects, buttons, mouse_pos)
        elif event.type in [pygame.KEYDOWN, pygame.KEYUP]:
            return self._handle_keyboard(event)
        
        return None
    
    def _handle_mouse_click(self, event, position_rects, buttons, mouse_pos):
        """Handle mouse click"""
        if self.game_logic.game_over:
            # 修复：检查 restart 按钮
            if "restart" in buttons and buttons["restart"].is_clicked(event):
                self.game_logic.initialize_game(self.game_logic.game_mode, self.game_logic.difficulty)
                self.key_repeat_manager._reset_state()
                return "restart"  # 返回特殊标记，让上层知道游戏已重启
        else:
            can_interact = (self.game_logic.game_mode == "PVP" or 
                           (self.game_logic.game_mode == "PVE" and self.game_logic.current_player == "Player 1"))
            
            if can_interact:
                # Check position selection
                for i, rect in enumerate(position_rects):
                    if rect.collidepoint(mouse_pos):
                        self.game_logic.select_position(i)
                        break
                
                # Check control buttons
                if self.game_logic.selected_position_index is not None:
                    if "minus" in buttons and buttons["minus"].is_clicked(event) and self.game_logic.selected_count > 1:
                        self._decrease_count()
                    elif ("plus" in buttons and buttons["plus"].is_clicked(event) and 
                          self.game_logic.selected_count < self.game_logic.positions[self.game_logic.selected_position_index]):
                        self._increase_count()
                
                # Check confirm button
                if ("confirm" in buttons and buttons["confirm"].is_clicked(event) and 
                    self.game_logic.selected_position_index is not None):
                    if self.game_logic.make_move(self.game_logic.selected_position_index, self.game_logic.selected_count):
                        self.game_logic.selected_position_index = None
                        self.key_repeat_manager._reset_state()
        
        # Check navigation buttons
        if "back" in buttons and buttons["back"].is_clicked(event):
            return "back"
        elif "home" in buttons and buttons["home"].is_clicked(event):
            return "home"
        
        return None
    
    def _handle_keyboard(self, event):
        """Handle keyboard input"""
        if self.game_logic.game_over:
            # 修复：游戏结束后也允许按 R 键重启
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.game_logic.initialize_game(self.game_logic.game_mode, self.game_logic.difficulty)
                self.key_repeat_manager._reset_state()
                return "restart"
            return
        
        can_interact = (self.game_logic.game_mode == "PVP" or 
                       (self.game_logic.game_mode == "PVE" and self.game_logic.current_player == "Player 1"))
        
        if can_interact:
            callbacks = self._create_key_callbacks()
            self.key_repeat_manager.handle_key_event(event, callbacks)
            
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                if (self.game_logic.selected_position_index is not None and
                    self.game_logic.make_move(self.game_logic.selected_position_index, 
                                            self.game_logic.selected_count)):
                    self.game_logic.selected_position_index = None
                    self.key_repeat_manager._reset_state()
    
    def update_key_repeat(self):
        """Update key repeat state"""
        if (not self.game_logic.game_over and
            ((self.game_logic.game_mode == "PVP") or 
             (self.game_logic.game_mode == "PVE" and self.game_logic.current_player == "Player 1"))):
            
            callbacks = self._create_key_callbacks()
            self.key_repeat_manager.update(callbacks)
    
    def _select_previous_position(self):
        """Select previous available position"""
        if self.game_logic.selected_position_index is None and len(self.game_logic.positions) > 0:
            for i in range(len(self.game_logic.positions)-1, -1, -1):
                if self.game_logic.positions[i] > 0:
                    self.game_logic.select_position(i)
                    break
        elif self.game_logic.selected_position_index is not None:
            new_position = self.game_logic.selected_position_index
            for i in range(1, len(self.game_logic.positions)):
                new_position = (self.game_logic.selected_position_index - i) % len(self.game_logic.positions)
                if self.game_logic.positions[new_position] > 0:
                    self.game_logic.select_position(new_position)
                    self.game_logic.selected_count = min(self.game_logic.selected_count, 
                                                        self.game_logic.positions[new_position])
                    break
    
    def _select_next_position(self):
        """Select next available position"""
        if self.game_logic.selected_position_index is None and len(self.game_logic.positions) > 0:
            for i in range(len(self.game_logic.positions)):
                if self.game_logic.positions[i] > 0:
                    self.game_logic.select_position(i)
                    break
        elif self.game_logic.selected_position_index is not None:
            new_position = self.game_logic.selected_position_index
            for i in range(1, len(self.game_logic.positions)):
                new_position = (self.game_logic.selected_position_index + i) % len(self.game_logic.positions)
                if self.game_logic.positions[new_position] > 0:
                    self.game_logic.select_position(new_position)
                    self.game_logic.selected_count = min(self.game_logic.selected_count, 
                                                        self.game_logic.positions[new_position])
                    break
    
    def _increase_count(self):
        """Increase selected count"""
        if (self.game_logic.selected_position_index is not None and
            self.game_logic.selected_count < self.game_logic.positions[self.game_logic.selected_position_index]):
            self.game_logic.selected_count += 1
    
    def _decrease_count(self):
        """Decrease selected count"""
        if (self.game_logic.selected_position_index is not None and
            self.game_logic.selected_count > 1):
            self.game_logic.selected_count -= 1