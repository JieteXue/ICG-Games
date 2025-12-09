# [file name]: src/games/dawson_kayles/game.py
"""
Dawson-Kayles Game using Universal Game Manager
"""

import pygame
from core.game_manager import GameManager
from games.dawson_kayles.logic import DawsonKaylesLogic
from games.dawson_kayles.ui import DawsonKaylesUI, TowerButton
from utils.constants import CARD_GAME_FPS

class DawsonKaylesInputHandler:
    """Handles input for Dawson-Kayles game"""
    
    def __init__(self, game_logic, ui):
        self.game_logic = game_logic
        self.ui = ui
        self.selected_position = None
    
    def handle_mouse_click(self, event, tower_buttons, scroll_buttons, control_buttons):
        """处理鼠标点击事件"""
        mouse_pos = pygame.mouse.get_pos()
        
        # 首先检查导航按钮（无论游戏是否结束）
        if "back" in control_buttons and control_buttons["back"].is_clicked(event):
            return "back"
        elif "home" in control_buttons and control_buttons["home"].is_clicked(event):
            return "home"
        elif "refresh" in control_buttons and control_buttons["refresh"].is_clicked(event):
            self.game_logic.initialize_game(self.game_logic.game_mode, self.game_logic.difficulty)
            self.ui.scroll_offset = 0
            self.selected_position = None
            return "refresh"
        
        # 如果不是导航按钮，再处理游戏逻辑
        if self.game_logic.game_over:
            # 游戏结束，只处理重新开始按钮
            if "restart" in control_buttons and control_buttons["restart"].is_clicked(event):
                self.game_logic.initialize_game(self.game_logic.game_mode, self.game_logic.difficulty)
                self.ui.scroll_offset = 0
                self.selected_position = None
                return None
        else:
            # 游戏进行中，检查是否可以交互
            can_interact = False
            if self.game_logic.game_mode == "PVP":
                can_interact = True
            elif self.game_logic.game_mode == "PVE" and self.game_logic.current_player == "Player 1":
                can_interact = True
            
            if can_interact:
                # 检查滚动按钮
                for button in scroll_buttons:
                    if button.is_clicked(event):
                        if button.text == "<":
                            self.ui.scroll_left(len(self.game_logic.towers))
                        else:
                            self.ui.scroll_right(len(self.game_logic.towers))
                        return None
                
                # 检查炮塔选择
                for button in tower_buttons:
                    if button.is_clicked(event) and self.game_logic.towers[button.tower_id] == 1:
                        self.handle_tower_click(button.tower_id)
                        return None
        
        return None
    
    def handle_tower_click(self, tower_id):
        """Handle tower click"""
        available_moves = self.game_logic.get_available_moves()
        
        if self.selected_position is None:
            # First selection - check if this tower is part of any available move
            for move in available_moves:
                if move == tower_id or move + 1 == tower_id:
                    self.selected_position = tower_id
                    self.game_logic.message = f"Selected tower {tower_id}, select adjacent tower to connect laser."
                    return
        else:
            # Second selection - check if we can connect
            if abs(self.selected_position - tower_id) == 1:
                move_index = min(self.selected_position, tower_id)
                if move_index in available_moves:
                    self.game_logic.make_move(move_index)
                    self.selected_position = None
            else:
                # Invalid second selection, reset
                self.game_logic.message = f"Invalid selection. Towers must be adjacent. Please select tower adjacent to tower {self.selected_position}."
                self.selected_position = None
    
    def handle_keyboard(self, event):
        """Handle keyboard events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.ui.scroll_left(len(self.game_logic.towers))
            elif event.key == pygame.K_RIGHT:
                self.ui.scroll_right(len(self.game_logic.towers))
            elif event.key == pygame.K_RETURN and self.selected_position is not None:
                # If a tower is selected, try to make a move with adjacent tower
                available_moves = self.game_logic.get_available_moves()
                for move in available_moves:
                    if move == self.selected_position or move + 1 == self.selected_position:
                        self.game_logic.make_move(move)
                        self.selected_position = None
                        break

class DawsonKaylesGame(GameManager):
    """Dawson-Kayles Game implementation"""
    
    def __init__(self, screen, font_manager):
        super().__init__(screen, font_manager)
        self.logic = DawsonKaylesLogic()
        self.ui = DawsonKaylesUI(screen, font_manager)
        self.input_handler = DawsonKaylesInputHandler(self.logic, self.ui)
        
        # 确保字体已初始化
        self.font_manager.initialize_fonts()
        
        # 初始化游戏设置
        self.initialize_game_settings()
        
        # 创建UI组件
        if not self.should_return_to_menu:
            self.create_components()
    
    def create_components(self):
        """创建游戏组件"""
        self.control_buttons = self.ui.create_control_buttons()
        self.game_over_buttons = {}
        self.tower_buttons = []
        self.scroll_buttons = []
        self.ai_timer = 0
    
    def handle_events(self):
        """Handle game events"""
        if self.should_return_to_menu:
            return False
        
        mouse_pos = pygame.mouse.get_pos()
        
        # Update button hover states
        for button in self.control_buttons.values():
            button.update_hover(mouse_pos)
        
        for button in self.game_over_buttons.values():
            button.update_hover(mouse_pos)
        
        for button in self.tower_buttons:
            button.update_hover(mouse_pos)
        
        for button in self.scroll_buttons:
            button.update_hover(mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # 使用统一的鼠标点击处理方法（与其他游戏保持一致）
                result = self.input_handler.handle_mouse_click(
                    event, self.tower_buttons, self.scroll_buttons, self.control_buttons
                )
                
                if result == "back":
                    # 返回模式选择 - 重新初始化游戏设置
                    self.initialize_game_settings()
                    self.ui.scroll_offset = 0
                    self.input_handler.selected_position = None
                elif result == "home":
                    # 返回主菜单
                    return False
                elif result == "refresh":
                    # refresh已经处理过了，不需要额外操作
                    return True
            
            elif event.type in [pygame.KEYDOWN, pygame.KEYUP]:
                self.input_handler.handle_keyboard(event)
            
            elif event.type == pygame.MOUSEWHEEL:
                # Handle mouse wheel scrolling
                self.ui.handle_mouse_wheel(event, len(self.logic.towers))
        
        return True
    
    def update(self):
        """Update game state"""
        # Update tower buttons
        self.tower_buttons = self.ui.create_tower_buttons(len(self.logic.towers))
        
        # Update scroll buttons
        self.scroll_buttons = self.ui.create_scroll_buttons(len(self.logic.towers))
        
        # If game over, create game over buttons
        if self.logic.game_over and not self.game_over_buttons:
            self.game_over_buttons = self.ui.create_game_over_buttons()
        
        # AI's turn (only in PvE mode)
        if (self.logic.game_mode == "PVE" and 
            self.logic.current_player == "AI" and 
            not self.logic.game_over):
            
            self.ai_timer += 1
            if self.ai_timer > 30:
                self.logic.ai_make_move()
                self.ai_timer = 0
                self.input_handler.selected_position = None
                self.ui.scroll_offset = 0
        
        # Update highlighted towers
        self.ui.update_highlighted_towers(self.logic.get_available_moves(), 
                                         self.input_handler.selected_position)
    
    def draw(self):
        """Draw the complete game interface"""
        try:
            # Draw background
            self.ui.draw_background()
            
            # Draw game information
            self.ui.draw_game_info(self.logic)
            
            # Draw towers and lasers
            self.ui.draw_towers_and_lasers(self.logic, self.tower_buttons)
            
            # Draw scroll bar
            self.ui.draw_scrollbar(len(self.logic.towers))
            
            # Draw navigation buttons
            if "back" in self.control_buttons:
                self.control_buttons["back"].draw(self.screen)
            if "home" in self.control_buttons:
                self.control_buttons["home"].draw(self.screen)
            if "refresh" in self.control_buttons:
                self.control_buttons["refresh"].draw(self.screen)
            
            # Draw game state
            if not self.logic.game_over:
                # Draw control panel and hints
                self.ui.draw_hints()
            else:
                # Draw game over buttons
                for button in self.game_over_buttons.values():
                    button.draw(self.screen)
            
            pygame.display.flip()
            
        except Exception as e:
            print(f"Error in draw: {e}")
            import traceback
            traceback.print_exc()
    
    def get_game_info(self):
        """Return game information"""
        return {
            'name': 'Laser Defense - Dawson-Kayles',
            'description': 'Strategic tower connection game using Dawson-Kayles rules',
            'current_player': self.logic.current_player,
            'game_over': self.logic.game_over,
            'winner': self.logic.winner,
            'towers_remaining': sum(self.logic.towers),
            'available_moves': len(self.logic.get_available_moves()),
            'winning_position': self.logic.judge_win()
        }