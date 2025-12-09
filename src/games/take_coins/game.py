import pygame
import sys
from core.game_manager import GameManager
from games.take_coins.logic import TakeCoinsLogic
from games.take_coins.ui import TakeCoinsUI, ScrollButton
from utils.constants import *
from utils.key_repeat import KeyRepeatManager

class TakeCoinsInputHandler:
    """Handles input for Take Coins game with scrolling support"""
    
    def __init__(self, game_logic, ui):
        self.game_logic = game_logic
        self.ui = ui
        self.key_repeat_manager = KeyRepeatManager()
    
    def _create_key_callbacks(self):
        """创建按键回调字典"""
        return {
            pygame.K_LEFT: self._select_previous_position,
            pygame.K_RIGHT: self._select_next_position,
            pygame.K_UP: lambda: self.ui.scroll_left(len(self.game_logic.coins)),
            pygame.K_DOWN: lambda: self.ui.scroll_right(len(self.game_logic.coins))
        }
    
    def handle_mouse_click(self, event, position_buttons, scroll_buttons, control_buttons):
        """Handle mouse click events with double-click support"""
        mouse_pos = pygame.mouse.get_pos()
        
        # Check scroll buttons first
        for button in scroll_buttons:
            if button.is_clicked(event):
                if button.text == "<":
                    self.ui.scroll_left(len(self.game_logic.coins))
                else:
                    self.ui.scroll_right(len(self.game_logic.coins))
                return None
        
        if self.game_logic.game_over:
            if control_buttons["restart"].is_clicked(event):
                self.game_logic.initialize_game(self.game_logic.game_mode, self.game_logic.difficulty)
                self.ui.scroll_offset = 0
                self.key_repeat_manager._reset_state()
        else:
            can_interact = False
            if self.game_logic.game_mode == "PVP":
                can_interact = True
            elif self.game_logic.game_mode == "PVE" and self.game_logic.current_player == "Player 1":
                can_interact = True
            
            if can_interact:
                # 处理位置点击
                self._handle_position_click(event, mouse_pos, position_buttons)
                
                # Check confirm button
                if (control_buttons["confirm"].is_clicked(event) and 
                    self.game_logic.selected_position is not None and
                    self.game_logic.selected_position in self.game_logic.valid_positions):
                    if self.game_logic.make_move():
                        self.key_repeat_manager._reset_state()
        
        # Check navigation buttons
        if "back" in control_buttons and control_buttons["back"].is_clicked(event):
            return "back"
        elif "home" in control_buttons and control_buttons["home"].is_clicked(event):
            return "home"
        
        return None
    
    def _handle_position_click(self, event, mouse_pos, position_buttons):
        """处理位置点击"""
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return
        
        # 检查可见位置
        for button in position_buttons:
            if (button.enabled and
                button.position_index >= self.ui.scroll_offset and
                button.position_index < self.ui.scroll_offset + self.ui.visible_positions):
                
                visible_index = button.position_index - self.ui.scroll_offset
                position_width = 80
                spacing = 20
                total_visible_width = self.ui.visible_positions * position_width + (self.ui.visible_positions - 1) * spacing
                start_x = (SCREEN_WIDTH - total_visible_width) // 2
                base_y = 350
                
                x = start_x + visible_index * (position_width + spacing)
                button_rect = pygame.Rect(x, base_y - 100, position_width, 120)
                
                if button_rect.collidepoint(mouse_pos):
                    # 使用双击管理器
                    callbacks = {
                        'single_click': lambda: self._handle_single_click(button.position_index),
                        'double_click': lambda: self._handle_double_click(button.position_index)
                    }
                    self.key_repeat_manager.handle_mouse_click(event, button.position_index, callbacks)
                    break
    
    def _handle_single_click(self, position_index):
        """处理单点击"""
        self.game_logic.select_position(position_index)
    
    def _handle_double_click(self, position_index):
        """处理双击"""
        if self.game_logic.select_position(position_index):
            if (self.game_logic.selected_position is not None and
                self.game_logic.selected_position in self.game_logic.valid_positions):
                if self.game_logic.make_move():
                    self.key_repeat_manager._reset_state()
    
    def handle_keyboard(self, event):
        """Handle keyboard events"""
        if self.game_logic.game_over:
            return
        
        can_interact = False
        if self.game_logic.game_mode == "PVP":
            can_interact = True
        elif self.game_logic.game_mode == "PVE" and self.game_logic.current_player == "Player 1":
            can_interact = True
        
        if can_interact and self.game_logic.valid_positions:
            callbacks = self._create_key_callbacks()
            
            self.key_repeat_manager.handle_key_event(event, callbacks)
            
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                if (self.game_logic.selected_position is not None and
                    self.game_logic.selected_position in self.game_logic.valid_positions):
                    if self.game_logic.make_move():
                        self.key_repeat_manager._reset_state()
    
    def update_key_repeat(self):
        """更新按键重复状态"""
        if (not self.game_logic.game_over and 
            self.game_logic.valid_positions and
            ((self.game_logic.game_mode == "PVP") or 
             (self.game_logic.game_mode == "PVE" and self.game_logic.current_player == "Player 1"))):
            
            callbacks = self._create_key_callbacks()
            self.key_repeat_manager.update(callbacks)
    
    def _select_previous_position(self):
        """选择前一个位置，支持边界循环"""
        if not self.game_logic.valid_positions:
            return

        if self.game_logic.selected_position in self.game_logic.valid_positions:
            current_index = self.game_logic.valid_positions.index(self.game_logic.selected_position)
            if current_index > 0:
                new_index = self.game_logic.valid_positions[current_index - 1]
            else:
                new_index = self.game_logic.valid_positions[-1]
        else:
            new_index = self.game_logic.valid_positions[-1]

        self.game_logic.select_position(new_index)

        if new_index < self.ui.scroll_offset:
            self.ui.scroll_offset = max(0, new_index)

    def _select_next_position(self):
        """选择下一个位置，支持边界循环"""
        if not self.game_logic.valid_positions:
            return

        if self.game_logic.selected_position in self.game_logic.valid_positions:
            current_index = self.game_logic.valid_positions.index(self.game_logic.selected_position)
            if current_index < len(self.game_logic.valid_positions) - 1:
                new_index = self.game_logic.valid_positions[current_index + 1]
            else:
                new_index = self.game_logic.valid_positions[0]
        else:
            new_index = self.game_logic.valid_positions[0]

        self.game_logic.select_position(new_index)

        if new_index >= self.ui.scroll_offset + self.ui.visible_positions:
            self.ui.scroll_offset = min(
                len(self.game_logic.coins) - self.ui.visible_positions,
                new_index - self.ui.visible_positions + 1
            )

class TakeCoinsGame(GameManager):
    """Take Coins Game implementation with scrolling support"""
    
    def __init__(self, screen, font_manager):
        super().__init__(screen, font_manager)
        self.logic = TakeCoinsLogic()
        self.ui = TakeCoinsUI(screen, font_manager)
        self.input_handler = TakeCoinsInputHandler(self.logic, self.ui)
        
        self.font_manager.initialize_fonts()
        
        # Initialize game mode and difficulty
        self.initialize_game_settings()
        
        # Create UI components
        if not self.should_return_to_menu:
            self.create_components()
    
    def create_components(self):
        """创建游戏组件"""
        self.control_buttons = self.ui.create_buttons()
        self.position_buttons = []
        self.scroll_buttons = []
        self.ai_timer = 0
    
    def handle_events(self):
        """Handle game events with scrolling support"""
        if self.should_return_to_menu:
            return False
        
        mouse_pos = pygame.mouse.get_pos()
        
        # Update button hover states
        for button in self.control_buttons.values():
            button.update_hover(mouse_pos)
        
        for button in self.scroll_buttons:
            button.update_hover(mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if "refresh" in self.control_buttons and self.control_buttons["refresh"].is_clicked(event):
                    self.logic.initialize_game(self.logic.game_mode, self.logic.difficulty)
                    self.ui.scroll_offset = 0
                    if hasattr(self.input_handler, 'key_repeat_manager'):
                        self.input_handler.key_repeat_manager._reset_state()
                    return True
                
                result = self.input_handler.handle_mouse_click(
                    event, self.position_buttons, self.scroll_buttons, self.control_buttons
                )
                if result == "back":
                    self.initialize_game_settings()
                    self.ui.scroll_offset = 0
                elif result == "home":
                    return False
            
            elif event.type in [pygame.KEYDOWN, pygame.KEYUP]:
                self.input_handler.handle_keyboard(event)
            
            elif event.type == pygame.MOUSEWHEEL:
                self.ui.handle_mouse_wheel(event, len(self.logic.coins))
        
        return True
    
    def update(self):
        """Update game state with scrolling support"""
        # Update position buttons based on current valid positions
        self.position_buttons = self.ui.create_position_buttons(
            self.logic.coins, self.logic.valid_positions, self.logic.selected_position
        )
        
        # Update scroll buttons
        self.scroll_buttons = self.ui.create_scroll_buttons(len(self.logic.coins))
        
        # Set button enabled states
        if self.logic.game_mode == "PVE":
            buttons_enabled = (self.logic.current_player == "Player 1")
        else:
            buttons_enabled = True
        
        self.control_buttons["confirm"].enabled = (
            buttons_enabled and 
            self.logic.selected_position is not None and
            self.logic.selected_position in self.logic.valid_positions
        )
        
        # AI's turn (only in PvE mode)
        if (self.logic.game_mode == "PVE" and 
            self.logic.current_player == "AI" and 
            not self.logic.game_over):
            
            self.ai_timer += 1
            if self.ai_timer > 30:
                self.logic.ai_make_move()
                self.ai_timer = 0
                self.ui.scroll_offset = 0
    
    def draw(self):
        """Draw the complete game interface with scrolling"""
        try:
            # Draw background
            self.ui.draw_background()
            
            # Draw game information
            self.ui.draw_game_info(self.logic)
            
            # Draw coin positions with scrolling
            self.ui.draw_coin_stacks(self.logic, self.position_buttons, self.scroll_buttons)
            
            # Draw navigation buttons
            if "back" in self.control_buttons:
                self.control_buttons["back"].draw(self.screen)
            if "home" in self.control_buttons:
                self.control_buttons["home"].draw(self.screen)
            if "refresh" in self.control_buttons:
                self.control_buttons["refresh"].draw(self.screen)
            
            if not self.logic.game_over:
                # Draw control panel
                self.ui.draw_control_panel(self.control_buttons, self.logic)
                
                # Draw control panel buttons
                self.control_buttons["confirm"].draw(self.screen)
                
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
            'name': 'Take Coins Game',
            'description': 'Strategic coin manipulation game on a line',
            'current_player': self.logic.current_player,
            'game_over': self.logic.game_over,
            'winner': self.logic.winner,
            'coins': self.logic.coins.copy(),
            'valid_positions': self.logic.valid_positions.copy()
        }