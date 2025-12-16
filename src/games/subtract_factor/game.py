"""
Subtract Factor Game Implementation
"""

import pygame
import sys
from core.game_manager import GameManager
from games.subtract_factor.logic import SubtractFactorLogic
from games.subtract_factor.ui import SubtractFactorUI, FactorButton, ScrollButton
from ui.components.sidebar import Sidebar
from utils.constants import CARD_GAME_FPS, SCREEN_WIDTH, SCREEN_HEIGHT, ACCENT_COLOR, TEXT_COLOR
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
        """Handle mouse click events with double-click support"""
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
                        if button.text == "<":
                            self.ui.scroll_left(len(self.game_logic.valid_factors))
                        else:
                            self.ui.scroll_right(len(self.game_logic.valid_factors))
                        return None
                
                # Check factor selection with double-click support
                for button in factor_buttons:
                    if button.is_clicked(event):
                        # 使用通用的双击管理器
                        callbacks = {
                            'single_click': lambda: self._handle_single_click(button.factor_value),
                            'double_click': lambda: self._handle_double_click(button.factor_value)
                        }
                        self.key_repeat_manager.handle_mouse_click(event, button.factor_value, callbacks)
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
    
    def _handle_single_click(self, factor_value):
        """处理单点击"""
        self.game_logic.select_factor(factor_value)
    
    def _handle_double_click(self, factor_value):
        """处理双击"""
        if self.game_logic.select_factor(factor_value):
            if (self.game_logic.selected_factor is not None and
                self.game_logic.selected_factor in self.game_logic.valid_factors):
                if self.game_logic.make_move(self.game_logic.selected_factor):
                    self.game_logic.selected_factor = 1
                    self.ui.scroll_offset = 0
                    self.key_repeat_manager._reset_state()
    
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


class SubtractFactorGame(GameManager):
    """Subtract Factor Game implementation with Sidebar"""
    
    def __init__(self, screen, font_manager):
        super().__init__(screen, font_manager)
        self.logic = SubtractFactorLogic()
        self.ui = SubtractFactorUI(screen, font_manager)
        self.input_handler = SubtractFactorInputHandler(self.logic, self.ui)
        
        # 添加侧边栏
        self.sidebar = Sidebar(screen, font_manager)
        
        # 确保字体已初始化
        self.font_manager.initialize_fonts()
        
        # 添加游戏说明
        self.game_instructions = """
SUBTRACT FACTOR GAME - INSTRUCTIONS

Objective:
Subtract a proper factor from the current number. The player who cannot make a valid move loses!

How to Play:
1. Current value starts at n, threshold is k
2. Select a proper factor of the current number (a factor < n)
3. Subtract it to get new value
4. If new value < k, you lose immediately!
5. Continue until one player cannot make a valid move

Game Modes:
- Player vs Player: Play against another person
- Player vs AI: Play against computer AI with adjustable difficulty

Strategies:
- Try to leave your opponent in a losing position
- Watch the "Winning Position"/"Losing Position" indicator
- Remember: proper factors only (not the number itself)
- Avoid moves that leave value close to threshold

Controls:
- Mouse: Click on factors or use arrow keys
- Arrow Keys: Select factors (LEFT/RIGHT), scroll (UP/DOWN)
- ENTER: Confirm move
- R: Restart game
- I: Show these instructions
- Mouse Wheel: Scroll through factors
- ESC: Back to mode selection

Difficulty Levels:
- Easy: Smaller numbers, easier factors
- Normal: Balanced difficulty
- Hard: Larger numbers, more complex factors
- Insane: Challenging configurations

Navigation:
- Back (←): Return to mode selection
- Home (🏠): Return to main menu  
- Refresh (↻): Restart current game
- Info (i): Show these instructions

Tips:
- Prime numbers have limited factors (only 1)
- Large composite numbers have many factors
- The threshold k creates interesting endgame situations

Good luck and have fun!
"""
        
        # 信息对话框状态
        self.showing_instructions = False
        
        # Initialize game mode and difficulty
        self.initialize_game_settings()
        
        # Create UI components
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
        """创建游戏组件"""
        self.control_buttons = self.ui.create_buttons()
        self.factor_buttons = []
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

        for button in self.factor_buttons:
            button.update_hover(mouse_pos)

        for button in self.scroll_buttons:
            button.update_hover(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            # 处理侧边栏事件
            sidebar_result = self.sidebar.handle_event(event, mouse_pos)
            if sidebar_result:
                return self._handle_sidebar_action(sidebar_result)
            
            # 处理信息对话框
            if self.showing_instructions:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.showing_instructions = False
                    return True
                elif event.type == pygame.KEYDOWN and event.key in [pygame.K_ESCAPE, pygame.K_i]:
                    self.showing_instructions = False
                    return True
                else:
                    return True  # 忽略其他事件当显示说明时

            # 处理导航事件
            nav_result = self.handle_navigation_events(event)
            if nav_result == "back":
                # Reinitialize game settings
                self.initialize_game_settings()
                self.ui.scroll_offset = 0
                return True
            elif nav_result == "home":
                # Return to main menu
                return False
            elif nav_result == "refresh":
                return True
            elif nav_result == "info":
                self.showing_instructions = True
                return True

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # 检查刷新按钮 - 优先处理
                if "refresh" in self.control_buttons and self.control_buttons["refresh"].is_clicked(event):
                    self.logic.initialize_game(self.logic.game_mode, self.logic.difficulty)
                    self.ui.scroll_offset = 0
                    if hasattr(self.input_handler, 'key_repeat_manager'):
                        self.input_handler.key_repeat_manager._reset_state()
                    return True

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
    
    def _handle_sidebar_action(self, action):
        """处理侧边栏按钮点击"""
        if action == "toggle":
            return True
        elif action == "back":
            self.initialize_game_settings()
            self.ui.scroll_offset = 0
            return True
        elif action == "home":
            return False  # 返回主菜单
        elif action == "refresh":
            # 重启游戏
            self.logic.initialize_game(self.logic.game_mode, self.logic.difficulty)
            self.ui.scroll_offset = 0
            if hasattr(self.input_handler, 'key_repeat_manager'):
                self.input_handler.key_repeat_manager._reset_state()
            return True
        elif action == "info":
            self.showing_instructions = True
            return True
        elif action == "settings":
            print("Settings button clicked")
            return True
        return True
    
    def handle_navigation_events(self, event):
        """Universal navigation events handling"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            # 检查按钮点击
            if "refresh" in self.control_buttons and self.control_buttons["refresh"].is_clicked(event):
                # Restart game logic
                self.logic.initialize_game(self.logic.game_mode, self.logic.difficulty)
                self.ui.scroll_offset = 0
                if hasattr(self.input_handler, 'key_repeat_manager'):
                    self.input_handler.key_repeat_manager._reset_state()
                return "refresh"
            
            # 检查其他导航按钮
            for btn_name in ["back", "home"]:
                if btn_name in self.control_buttons and self.control_buttons[btn_name].is_clicked(event):
                    return btn_name
        
        # 键盘快捷键
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_i:
                return "info"
            elif event.key == pygame.K_F2:
                self.show_perf_overlay = not self.show_perf_overlay
            elif event.key == pygame.K_r:
                # R键重启游戏
                self.logic.initialize_game(self.logic.game_mode, self.logic.difficulty)
                self.ui.scroll_offset = 0
                return "refresh"
        
        return None
    
    def update(self):
        """Update game state"""
        # 更新侧边栏
        self.sidebar.update()

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
        # 如果显示说明，绘制说明页面
        if self.showing_instructions:
            self.draw_instructions()
            pygame.display.flip()
            return
        
        try:
            # Draw background
            self.ui.draw_background()
            
            # Draw game information
            self.ui.draw_game_info(self.logic)
            
            # Draw factor selection area with scrolling
            self.ui.draw_factor_selection(self.logic, self.factor_buttons, self.scroll_buttons)
            
            # Draw navigation buttons (包括刷新按钮)
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
                for button in [self.control_buttons["minus"], self.control_buttons["plus"], self.control_buttons["confirm"]]:
                    button.draw(self.screen)
                
                # Draw hints
                self.ui.draw_hints()
            else:
                # Draw game over screen
                self.control_buttons["restart"].draw(self.screen)
            
            # 最后绘制侧边栏，使其在最上层
            self.sidebar.draw()
            
            pygame.display.flip()
            
        except Exception as e:
            print(f"Error in draw: {e}")
            import traceback
            traceback.print_exc()
    
    def draw_instructions(self):
        """Draw game instructions overlay"""
        # Draw semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        # Draw instructions panel
        panel_width = 800
        panel_height = 600
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_y = (SCREEN_HEIGHT - panel_height) // 2
        
        # Panel background
        pygame.draw.rect(self.screen, (35, 45, 60), (panel_x, panel_y, panel_width, panel_height), border_radius=15)
        pygame.draw.rect(self.screen, ACCENT_COLOR, (panel_x, panel_y, panel_width, panel_height), 3, border_radius=15)
        
        # Title
        title = self.font_manager.large.render("Subtract Factor Game - Instructions", True, TEXT_COLOR)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, panel_y + 40))
        self.screen.blit(title, title_rect)
        
        # Close hint
        close_hint = self.font_manager.small.render("Click anywhere or press ESC/I to close", True, (180, 200, 220))
        close_rect = close_hint.get_rect(center=(SCREEN_WIDTH//2, panel_y + panel_height - 30))
        self.screen.blit(close_hint, close_rect)
        
        # Draw instructions text with word wrapping
        y_pos = panel_y + 80
        instructions = self.game_instructions.strip().split('\n')
        
        for line in instructions:
            if line.strip() == "":
                y_pos += 15  # Extra space for paragraph breaks
                continue
                
            # Determine font size based on line content
            if line.strip().endswith(":"):  # Section headers
                font = self.font_manager.medium
                color = ACCENT_COLOR
                y_pos += 10  # Extra space before section
            elif line.strip().startswith("-"):  # Bullet points
                line = "  • " + line[1:].strip()
                font = self.font_manager.small
                color = (220, 230, 240)
            else:  # Regular text
                font = self.font_manager.small
                color = (200, 210, 220)
            
            # Word wrapping
            words = line.split()
            lines = []
            current_line = []
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                test_width = font.size(test_line)[0]
                
                if test_width <= panel_width - 80:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                    current_line = [word]
            
            if current_line:
                lines.append(' '.join(current_line))
            
            # Draw each line
            for text_line in lines:
                if y_pos < panel_y + panel_height - 60:
                    text_surface = font.render(text_line, True, color)
                    text_rect = text_surface.get_rect(left=panel_x + 40, top=y_pos)
                    self.screen.blit(text_surface, text_rect)
                    y_pos += font.get_linesize() + 2
    
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