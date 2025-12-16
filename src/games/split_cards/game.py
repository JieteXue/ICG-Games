"""
Split Cards Game - Main game class
"""

import pygame
import sys
from core.base_game import BaseGame
from games.split_cards.logic import SplitCardsLogic
from games.split_cards.ui import SplitCardsUI
from ui.menus import GameModeSelector
from utils.constants import CARD_GAME_FPS, SCREEN_WIDTH, SCREEN_HEIGHT
from utils.key_repeat import KeyRepeatManager

class SplitCardsInputHandler:
    """Handles input for Split Cards game"""
    
    def __init__(self, game_logic):
        self.game_logic = game_logic
        self.key_repeat_manager = KeyRepeatManager()
    
    def handle_mouse_click(self, event, pile_rects, buttons):
        """Handle mouse click events"""
        mouse_pos = pygame.mouse.get_pos()
        
        # Check if game is over
        if self.game_logic.game_over:
            if buttons["restart"].is_clicked(event):
                self.game_logic.initialize_game(self.game_logic.game_mode, self.game_logic.difficulty)
                self.key_repeat_manager._reset_state()
                return True
        else:
            # Check if current player can interact
            can_interact = False
            if self.game_logic.game_mode == "PVP":
                can_interact = True
            elif self.game_logic.game_mode == "PVE" and self.game_logic.current_player == "Player 1":
                can_interact = True
            
            if can_interact:
                # Check pile selection
                for i, rect in enumerate(pile_rects):
                    if rect.collidepoint(mouse_pos):
                        self.game_logic.selected_pile_index = i
                        self.game_logic.selected_action = None  # Reset action on new selection
                        self.game_logic.selected_count = 1
                        self.game_logic.message = f"Selected pile {i + 1}. Choose action: Take or Split."
                        break
                
                # Check action buttons
                if self.game_logic.selected_pile_index is not None:
                    # 检查split按钮是否可用（牌堆必须大于1）
                    pile_size = self.game_logic.card_piles[self.game_logic.selected_pile_index]
                    
                    if buttons["take_btn"].is_clicked(event):
                        self.game_logic.selected_action = 'take'
                        max_take = min(self.game_logic.max_take, pile_size)
                        self.game_logic.selected_count = min(self.game_logic.selected_count, max_take)
                        self.game_logic.message = f"Taking from pile {self.game_logic.selected_pile_index + 1}. Select amount (1-{max_take})."
                    
                    elif buttons["split_btn"].is_clicked(event) and pile_size > 1:  # 添加牌堆大小检查
                        self.game_logic.selected_action = 'split'
                        pile_size = self.game_logic.card_piles[self.game_logic.selected_pile_index]
                        self.game_logic.selected_count = min(self.game_logic.selected_count, pile_size - 1)
                        self.game_logic.message = f"Splitting pile {self.game_logic.selected_pile_index + 1}. Split after {self.game_logic.selected_count} cards."
                    
                    # Check number adjustment buttons
                    if self.game_logic.selected_action:
                        pile_size = self.game_logic.card_piles[self.game_logic.selected_pile_index]
                        
                        if buttons["minus"].is_clicked(event):
                            if self.game_logic.selected_action == 'take':
                                if self.game_logic.selected_count > 1:
                                    self.game_logic.selected_count -= 1
                            else:  # split
                                if self.game_logic.selected_count > 1:
                                    self.game_logic.selected_count -= 1
                        
                        elif buttons["plus"].is_clicked(event):
                            if self.game_logic.selected_action == 'take':
                                max_take = min(self.game_logic.max_take, pile_size)
                                if self.game_logic.selected_count < max_take:
                                    self.game_logic.selected_count += 1
                            else:  # split
                                if self.game_logic.selected_count < pile_size - 1:
                                    self.game_logic.selected_count += 1
                    
                    # Check confirm button
                    if buttons["confirm_btn"].is_clicked(event) and self.game_logic.selected_action:
                        if self.game_logic.selected_action == 'take':
                            move_info = {
                                'type': 'take',
                                'pile_index': self.game_logic.selected_pile_index,
                                'count': self.game_logic.selected_count
                            }
                        else:  # split
                            pile_size = self.game_logic.card_piles[self.game_logic.selected_pile_index]
                            move_info = {
                                'type': 'split',
                                'pile_index': self.game_logic.selected_pile_index,
                                'left_count': self.game_logic.selected_count,
                                'right_count': pile_size - self.game_logic.selected_count
                            }
                        
                        if self.game_logic.make_move(move_info):
                            self.game_logic.selected_pile_index = None
                            self.game_logic.selected_action = None
                            self.key_repeat_manager._reset_state()
        
        # Check navigation buttons
        if "back" in buttons and buttons["back"].is_clicked(event):
            return "back"
        elif "home" in buttons and buttons["home"].is_clicked(event):
            return "home"
        elif "refresh" in buttons and buttons["refresh"].is_clicked(event):
            self.game_logic.initialize_game(self.game_logic.game_mode, self.game_logic.difficulty)
            self.key_repeat_manager._reset_state()
        
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
        
        if can_interact and self.game_logic.selected_pile_index is not None and self.game_logic.selected_action:
            callbacks = {
                pygame.K_LEFT: self._decrease_count,
                pygame.K_RIGHT: self._increase_count,
                pygame.K_UP: self._increase_count,
                pygame.K_DOWN: self._decrease_count
            }
            
            self.key_repeat_manager.handle_key_event(event, callbacks)
            
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                if self.game_logic.selected_action == 'take':
                    move_info = {
                        'type': 'take',
                        'pile_index': self.game_logic.selected_pile_index,
                        'count': self.game_logic.selected_count
                    }
                else:  # split
                    pile_size = self.game_logic.card_piles[self.game_logic.selected_pile_index]
                    move_info = {
                        'type': 'split',
                        'pile_index': self.game_logic.selected_pile_index,
                        'left_count': self.game_logic.selected_count,
                        'right_count': pile_size - self.game_logic.selected_count
                    }
                
                if self.game_logic.make_move(move_info):
                    self.game_logic.selected_pile_index = None
                    self.game_logic.selected_action = None
                    self.key_repeat_manager._reset_state()
    
    def update_key_repeat(self):
        """Update key repeat state"""
        if (not self.game_logic.game_over and
            ((self.game_logic.game_mode == "PVP") or 
             (self.game_logic.game_mode == "PVE" and self.game_logic.current_player == "Player 1"))):
            
            if self.game_logic.selected_pile_index is not None and self.game_logic.selected_action:
                callbacks = {
                    pygame.K_LEFT: self._decrease_count,
                    pygame.K_RIGHT: self._increase_count,
                    pygame.K_UP: self._increase_count,
                    pygame.K_DOWN: self._decrease_count
                }
                self.key_repeat_manager.update(callbacks)
    
    def _increase_count(self):
        """Increase selected count"""
        if self.game_logic.selected_pile_index is not None and self.game_logic.selected_action:
            pile_size = self.game_logic.card_piles[self.game_logic.selected_pile_index]
            
            if self.game_logic.selected_action == 'take':
                max_take = min(self.game_logic.max_take, pile_size)
                if self.game_logic.selected_count < max_take:
                    self.game_logic.selected_count += 1
            else:  # split
                if self.game_logic.selected_count < pile_size - 1:
                    self.game_logic.selected_count += 1
    
    def _decrease_count(self):
        """Decrease selected count"""
        if self.game_logic.selected_pile_index is not None and self.game_logic.selected_action:
            if self.game_logic.selected_count > 1:
                self.game_logic.selected_count -= 1

class SplitCardsGame(BaseGame):
    """Split Cards Game implementation"""
    
    def __init__(self, screen, font_manager):
        super().__init__(screen, font_manager)
        self.logic = SplitCardsLogic()
        self.ui = SplitCardsUI(screen, font_manager)
        self.input_handler = SplitCardsInputHandler(self.logic)
        
        # Ensure fonts are initialized
        self.font_manager.initialize_fonts()
        
        # Initialize game mode and difficulty
        self.initialize_game_settings()
        
        # Create UI components
        self.buttons = self.ui.create_buttons()
        self.pile_rects = []
        self.ai_timer = 0
    
    def get_game_info(self):
        """Return game information"""
        return {
            'name': 'Split Cards',
            'description': 'Card splitting strategy game',
            'current_player': self.logic.current_player,
            'game_over': self.logic.game_over,
            'winner': self.logic.winner,
            'card_piles': self.logic.card_piles.copy() if self.logic.card_piles else [],
            'max_take': self.logic.max_take
        }
    
    def initialize_game_settings(self):
        """Initialize game mode and difficulty"""
        try:
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
                    self.input_handler.key_repeat_manager._reset_state()
                    return True
                
                result = self.input_handler.handle_mouse_click(event, self.pile_rects, self.buttons)
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
            
            # Draw card piles
            self.pile_rects = self.ui.draw_card_piles(
                self.logic.card_piles, 
                self.logic.selected_pile_index,
                self.logic.selected_action
            )
            
            # Draw navigation buttons
            self.buttons["back"].draw(self.screen)
            self.buttons["home"].draw(self.screen)
            self.buttons["refresh"].draw(self.screen)
            
            if not self.logic.game_over:
                # Set button enabled states based on game mode and current player
                if self.logic.game_mode == "PVE":
                    buttons_enabled = (self.logic.current_player == "Player 1")
                else:
                    buttons_enabled = True
                
                # Update button enabled states
                for btn_name in ["take_btn", "split_btn", "confirm_btn", "minus", "plus"]:
                    if btn_name in self.buttons:
                        self.buttons[btn_name].enabled = buttons_enabled
                
                # 特殊处理：如果选中的牌堆只有1张，则split按钮不可用
                if (self.logic.selected_pile_index is not None and 
                    self.buttons["split_btn"].enabled and
                    self.logic.card_piles[self.logic.selected_pile_index] <= 1):
                    self.buttons["split_btn"].enabled = False
                
                # Draw control panel
                self.ui.draw_control_panel(self.logic)
                
                # Draw control buttons
                for btn_name in ["take_btn", "split_btn", "confirm_btn"]:
                    if btn_name in self.buttons:
                        self.buttons[btn_name].draw(self.screen)
                for btn_name in ["minus", "plus"]:
                    # If no action selected, hide plus/minus buttons
                    if self.logic.selected_action is None:
                        self.buttons[btn_name].visible = False
                    else:
                        self.buttons[btn_name].visible = True
                        if btn_name in self.buttons:
                            self.buttons[btn_name].draw(self.screen)
                # Draw count display
                if (self.logic.selected_pile_index is not None and 
                    self.logic.selected_action):
                    
                    control_y = self.ui.table_rect.bottom + 20
                    control_x = (SCREEN_WIDTH - 600) // 2
                    
                    count_display = str(self.logic.selected_count)
                    count_text = self.font_manager.large.render(count_display, True, (240, 230, 220))
                    count_bg = pygame.Rect(control_x + 265, control_y +10, 50, 40)
                    pygame.draw.rect(self.screen, (50, 45, 40), count_bg, border_radius=8)
                    pygame.draw.rect(self.screen, (180, 150, 110), count_bg, 2, border_radius=8)
                    self.screen.blit(count_text, (control_x + 290 - count_text.get_width()//2, 
                                                 control_y +30 - count_text.get_height()//2))
                
                # Draw hints
                hints = [
                    "Select a pile, then choose action: Take or Split",
                    "Use UP/DOWN arrows to adjust count, ENTER to confirm",
                    "The player who takes the last card wins!"
                ]
                
                hint_y = self.ui.table_rect.bottom + 180
                for i, hint in enumerate(hints):
                    hint_text = self.font_manager.small.render(hint, True, (200, 190, 170))
                    self.screen.blit(hint_text, (SCREEN_WIDTH//2 - hint_text.get_width()//2, hint_y + i * 20))
            else:
                # Draw game over screen
                self.buttons["restart"].draw(self.screen)
            
            pygame.display.flip()
            
        except Exception as e:
            print(f"Error in draw: {e}")
            import traceback
            traceback.print_exc()
    
    def run(self):
        """Run the main game loop"""
        self.running = True
        while self.running:
            if not self.handle_events():
                break
            
            self.update()
            self.input_handler.update_key_repeat()
            self.draw()
            self.clock.tick(CARD_GAME_FPS)