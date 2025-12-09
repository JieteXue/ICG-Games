"""
Card Nim Game using Universal Game Manager
"""

import pygame
from core.game_manager import GameManager
from games.card_nim.logic import CardNimLogic
from games.card_nim.ui import CardNimUI
from utils.constants import CARD_GAME_FPS

class CardNimGame(GameManager):
    """Card Nim Game implementation"""
    
    def __init__(self, screen, font_manager):
        super().__init__(screen, font_manager)
        
        # Create game-specific components
        self.logic = CardNimLogic()
        self.ui = CardNimUI(screen, font_manager)
        
        # Initialize game settings
        self.initialize_game_settings()
        
        # Create components if not returning to menu
        if not self.should_return_to_menu:
            self.create_components()
    
    def initialize_game_settings(self):
        """Universal game settings initialization - 使用延迟导入"""
        try:
            # 延迟导入，避免循环导入
            from ui.menus import GameModeSelector
            selector = GameModeSelector(self.screen, self.font_manager)
            game_mode = selector.get_game_mode()
            
            if game_mode == "back":
                self.should_return_to_menu = True
                return
            
            if game_mode == "PVE":
                difficulty = selector.get_difficulty()
                if difficulty == "back":
                    self.should_return_to_menu = True
                    return
                self.logic.initialize_game("PVE", difficulty)
            else:
                self.logic.initialize_game("PVP")
                
        except Exception as e:
            print(f"Error initializing game settings: {e}")
            self.logic.initialize_game("PVE", 2)
    
    def create_components(self):
        """Create game-specific components"""
        # Create buttons
        self.buttons = self.ui.create_buttons()
        self.position_rects = []
        
        # Create input handler
        from games.card_nim.input_handler import CardNimInputHandler
        self.input_handler = CardNimInputHandler(self.logic, self.ui)
    
    def handle_events(self):
        """Handle game events"""
        if self.should_return_to_menu:
            return False
        
        mouse_pos = pygame.mouse.get_pos()
        
        # Update button hover states
        for button in self.buttons.values():
            button.update_hover(mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            # Handle navigation events
            nav_result = self.handle_navigation_events(event)
            if nav_result == "back":
                self.initialize_game_settings()
                return True
            elif nav_result == "home":
                return False
            elif nav_result == "refresh":
                return True
            
            # Handle game-specific events
            if not self.logic.game_over:
                result = self.input_handler.handle_event(event, self.position_rects, self.buttons)
            else:
                # 修复：游戏结束后也要处理事件
                result = self.input_handler.handle_event(event, self.position_rects, self.buttons)
                
            # 检查是否重启了游戏
            if result == "restart":
                # 重新创建组件来重置状态
                self.create_components()
                return True
        
        return True
    
    def update(self):
        """Update game state"""
        if not self.logic.game_over:
            self.update_ai_turn()
            self.update_button_states()
        
        # Update position rectangles
        self.position_rects = self.ui.draw_card_positions(
            self.logic.positions, self.logic.selected_position_index
        )
    
    def draw(self):
        """Draw game interface"""
        # Draw background
        self.ui.draw_background()
        
        # Draw game information
        self.ui.draw_game_info(self.logic)
        
        # Draw card positions
        self.ui.draw_card_positions(self.logic.positions, self.logic.selected_position_index)
        
        # Draw navigation buttons
        self.draw_navigation_buttons()
        
        # Draw game-specific UI
        if not self.logic.game_over:
            self.ui.draw_control_panel(self.buttons, self.logic.selected_count, self.logic.selected_position_index)
            for button_name in ["minus", "plus", "confirm"]:
                if button_name in self.buttons:
                    self.buttons[button_name].draw(self.screen)
            self.ui.draw_hints()
        else:
            # 修复：游戏结束后确保显示 restart 按钮
            if "restart" in self.buttons:
                self.buttons["restart"].draw(self.screen)
        
        pygame.display.flip()
    
    def update_ai_turn(self):
        """Universal AI turn update"""
        if (self.logic.game_mode == "PVE" and 
            self.logic.current_player == "AI" and 
            not self.logic.game_over):
            
            self.ai_timer += 1
            if self.ai_timer > 30:
                self.logic.ai_make_move()
                self.ai_timer = 0
    
    def update_button_states(self):
        """Universal button states update"""
        if self.logic.game_mode == "PVE":
            buttons_enabled = (self.logic.current_player == "Player 1")
        else:
            buttons_enabled = True
        
        # Update control buttons
        if "confirm" in self.buttons:
            can_confirm = (self.logic.selected_position_index is not None)
            self.buttons["confirm"].enabled = buttons_enabled and can_confirm
        
        # 确保游戏结束后 restart 按钮可用
        if self.logic.game_over and "restart" in self.buttons:
            self.buttons["restart"].enabled = True
    
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