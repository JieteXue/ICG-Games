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
from utils.config_manager import config_manager  # 新增导入

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
        
        # 首先检查提示按钮点击
        if "hint" in control_buttons and control_buttons["hint"].is_clicked(event):
            return "hint"
        
        if self.game_logic.game_over:
            # Check restart button
            if control_buttons["restart"].is_clicked(event):
                self.game_logic.initialize_game(self.game_logic.game_mode, self.game_logic.difficulty, self.game_logic.winning_hints_enabled)
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
            
            # 新增：H键显示提示
            if event.type == pygame.KEYDOWN and event.key == pygame.K_h:
                if self.game_logic.winning_hints_enabled:
                    return "hint"
    
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
        self.config_manager = config_manager  # 新增配置管理器
        
        # 确保字体已初始化
        self.font_manager.initialize_fonts()
        
        # 更新游戏说明以包含提示功能信息
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

Winning Hints Feature:
- Enable "Winning Hints" in Settings (gear icon)
- Click on the light bulb (💡) button to get AI suggestions
- AI will suggest optimal moves when in a winning position
- In losing positions, AI will suggest defensive strategies

Controls:
Mouse Controls:
- Click on factors to select them
- Double-click on a factor to select and confirm immediately
- Scroll Wheel: Scroll through factors
- Click CONFIRM button: Execute move with selected factor
- Click HINT button (💡): Get winning hints (when enabled)

Keyboard Shortcuts:
- LEFT/RIGHT Arrow Keys: Select factors
- UP/DOWN Arrow Keys: Scroll through factors
- ENTER: Confirm move
- R: Restart game
- I: Show these instructions
- H: Get quick hint (if Winning Hints enabled)
- ESC: Toggle sidebar / Close hint window

Panel Controls:
- MINUS (-): Select previous factor
- PLUS (+): Select next factor
- CONFIRM: Make move with selected factor

Navigation:
- Toggle Sidebar (☰): Show/hide navigation
- Back (←): Return to mode selection
- Home (🏠): Return to main menu  
- Restart: Restart current game
- Info (i): Show these instructions
- Settings (⚙️): Open settings panel
- Hint (💡): Show winning hint (when enabled)

Difficulty Levels:
- Easy: Smaller numbers, easier factors
- Normal: Balanced difficulty
- Hard: Larger numbers, more complex factors
- Insane: Challenging configurations

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
            
            # 从配置管理器中获取最新的winning_hints设置
            try:
                current_prefs = self.config_manager.get_user_preferences()
                winning_hints = current_prefs.winning_hints
                print(f"Initializing game with winning_hints from config: {winning_hints}")
            except Exception as e:
                print(f"Error getting winning hints from config: {e}")
                winning_hints = False
            
            if game_mode == "PVE":
                difficulty = selector.get_difficulty()
                if difficulty == "back":
                    self.should_return_to_menu = True
                    return
                self.logic.initialize_game("PVE", difficulty, winning_hints)
            else:
                self.logic.initialize_game("PVP", None, winning_hints)
                
        except Exception as e:
            print(f"Error initializing game settings: {e}")
            # 使用默认设置，但尝试从配置获取
            try:
                winning_hints = self.config_manager.get_user_preferences().winning_hints
            except:
                winning_hints = False
            self.logic.initialize_game("PVE", 2, winning_hints)
    
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

        # 更新UI的提示工具提示
        if hasattr(self.ui, 'update_hint_tooltip'):
            self.ui.update_hint_tooltip(mouse_pos)

        # Update button hover states
        for button in self.control_buttons.values():
            button.update_hover(mouse_pos)

        for button in self.factor_buttons:
            button.update_hover(mouse_pos)

        for button in self.scroll_buttons:
            button.update_hover(mouse_pos)

        # 处理提示窗口事件（如果可见）优先处理
        if hasattr(self.ui, 'hint_window_visible') and self.ui.hint_window_visible:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                
                # 先让提示窗口处理事件
                if self.ui.handle_hint_window_events(event, mouse_pos):
                    continue  # 事件已处理，继续下一个
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            # 如果提示窗口打开，让提示窗口优先处理事件
            if hasattr(self.ui, 'hint_window_visible') and self.ui.hint_window_visible:
                if self.ui.handle_hint_window_events(event, mouse_pos):
                    continue  # 事件已处理，继续下一个
            
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
                # 关闭提示窗口
                if hasattr(self.ui, 'hint_window_visible'):
                    self.ui.close_hint_window()
                return True
            elif nav_result == "home":
                # Return to main menu
                # 关闭提示窗口
                if hasattr(self.ui, 'hint_window_visible'):
                    self.ui.close_hint_window()
                return False
            elif nav_result == "refresh":
                return True
            elif nav_result == "info":
                self.showing_instructions = True
                return True
            elif nav_result == "hint":
                # 提示按钮点击 - 已经在handle_navigation_events中处理
                return True

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # 检查刷新按钮 - 优先处理
                if "refresh" in self.control_buttons and self.control_buttons["refresh"].is_clicked(event):
                    self.logic.initialize_game(self.logic.game_mode, self.logic.difficulty, self.logic.winning_hints_enabled)
                    self.ui.scroll_offset = 0
                    if hasattr(self.input_handler, 'key_repeat_manager'):
                        self.input_handler.key_repeat_manager._reset_state()
                    # 关闭提示窗口
                    if hasattr(self.ui, 'hint_window_visible'):
                        self.ui.close_hint_window()
                    return True

                result = self.input_handler.handle_mouse_click(
                    event, self.factor_buttons, self.scroll_buttons, self.control_buttons
                )
                if result == "hint":
                    # 处理提示按钮点击
                    if self.logic.winning_hints_enabled:
                        hint_text = self.logic.get_winning_hint()
                        if hasattr(self.ui, 'show_hint_window'):
                            self.ui.show_hint_window(hint_text)
                    return True
                elif result == "back":
                    # Reinitialize game settings
                    self.initialize_game_settings()
                    self.ui.scroll_offset = 0
                elif result == "home":
                    # Return to main menu
                    return False

            elif event.type in [pygame.KEYDOWN, pygame.KEYUP]:
                result = self.input_handler.handle_keyboard(event)
                if result == "hint":
                    # H键触发的提示
                    if self.logic.winning_hints_enabled:
                        hint_text = self.logic.get_winning_hint()
                        if hasattr(self.ui, 'show_hint_window'):
                            self.ui.show_hint_window(hint_text)
                    return True

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
            return True
        elif action == "home":
            return False  # 返回主菜单
        elif action == "refresh":
            # 重启游戏
            game_mode = getattr(self.logic, 'game_mode', "PVE")
            difficulty = getattr(self.logic, 'difficulty', 2)
            winning_hints = getattr(self.logic, 'winning_hints_enabled', False)
            self.logic.initialize_game(game_mode, difficulty, winning_hints)
            return True
        elif action == "info":
            self.showing_instructions = True
            return True
        elif action.startswith("setting_changed_"):
            # 处理设置变化
            setting_name = action.replace("setting_changed_", "")
            print(f"Setting changed: {setting_name}")
            
            # 更新配置管理器中的设置
            if setting_name == "winning_hints":
                # 从侧边栏获取当前值
                if hasattr(self.sidebar, 'settings_panel'):
                    settings = self.sidebar.settings_panel.get_settings()
                    winning_hints = settings.get('winning_hints', False)
                    
                    print(f"Winning hints setting changed to: {winning_hints}")
                    
                    # 更新配置管理器
                    try:
                        prefs = self.config_manager.get_user_preferences()
                        prefs.winning_hints = winning_hints
                        self.config_manager.update_user_preferences(prefs)
                        
                        # 更新游戏逻辑中的设置
                        self.logic.winning_hints_enabled = winning_hints
                        
                        # 显示反馈消息
                        if winning_hints:
                            self.logic.message = "Winning Hints enabled! Click on the hint button for guidance."
                        else:
                            self.logic.message = "Winning hints disabled."
                            
                    except Exception as e:
                        print(f"Error updating setting: {e}")
                    
                    # 更新按钮状态
                    self.update_button_states()
            return True
        elif action == "sponsor_clicked":
            print("Sponsor link clicked")
            return True
        return True
    
    def handle_navigation_events(self, event):
        """Universal navigation events handling"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            # 检查提示按钮点击
            if "hint" in self.control_buttons and self.control_buttons["hint"].is_clicked(event):
                # Hint按钮点击 - 显示提示窗口
                if self.logic.winning_hints_enabled:
                    hint_text = self.logic.get_winning_hint()
                    # 调用提示窗口
                    if hasattr(self.ui, 'show_hint_window'):
                        self.ui.show_hint_window(hint_text)
                return "hint"
            
            # 检查刷新按钮
            if "refresh" in self.control_buttons and self.control_buttons["refresh"].is_clicked(event):
                # 重启游戏逻辑
                self.logic.initialize_game(self.logic.game_mode, self.logic.difficulty, self.logic.winning_hints_enabled)
                self.ui.scroll_offset = 0
                if hasattr(self.input_handler, 'key_repeat_manager'):
                    self.input_handler.key_repeat_manager._reset_state()
                # 如果提示窗口打开，关闭它
                if hasattr(self.ui, 'hint_window_visible'):
                    self.ui.close_hint_window()
                return "refresh"
            
            # 检查其他导航按钮（这些按钮现在在侧边栏中处理）
        
        # 键盘快捷键
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_i:
                return "info"
            elif event.key == pygame.K_h:  # H键显示提示
                # H键显示提示窗口
                if self.logic.winning_hints_enabled:
                    hint_text = self.logic.get_winning_hint()
                    if hasattr(self.ui, 'show_hint_window'):
                        self.ui.show_hint_window(hint_text)
                return "hint"
            elif event.key == pygame.K_r:  # R键重启游戏
                self.logic.initialize_game(self.logic.game_mode, self.logic.difficulty, self.logic.winning_hints_enabled)
                self.ui.scroll_offset = 0
                return "refresh"
            # Toggle performance overlay with F2
            elif event.key == pygame.K_F2:
                self.show_perf_overlay = not self.show_perf_overlay
        
        return None
    
    def update(self):
        """Update game state"""
        # 更新侧边栏
        self.sidebar.update()
        
        # 更新按键重复状态
        self.input_handler.update_key_repeat()

        # Update factor buttons based on current valid factors
        self.factor_buttons = self.ui.create_factor_buttons(
            self.logic.valid_factors, self.logic.selected_factor
        )
        
        # Update scroll buttons
        self.scroll_buttons = self.ui.create_scroll_buttons(len(self.logic.valid_factors))
        
        # Set button enabled states
        self.update_button_states()
        
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
    
    def update_button_states(self):
        """更新按钮状态 - 新增提示按钮状态控制"""
        # 每次更新按钮状态时都从配置文件同步最新的Winning Hints设置
        if self.logic and hasattr(self.logic, 'winning_hints_enabled'):
            try:
                # 从配置管理器获取最新的设置
                current_prefs = self.config_manager.get_user_preferences()
                # 同步到游戏逻辑中
                self.logic.winning_hints_enabled = current_prefs.winning_hints
            except Exception as e:
                print(f"Error syncing winning hints from config: {e}")
        
        # 确定按钮是否可用
        if self.logic.game_mode == "PVE":
            buttons_enabled = (self.logic.current_player == "Player 1")
        else:
            buttons_enabled = True  # PvP模式下双方都可以操作
        
        # 更新控制按钮状态
        for button_name in ["minus", "plus", "confirm"]:
            if button_name in self.control_buttons:
                self.control_buttons[button_name].enabled = buttons_enabled and bool(self.logic.valid_factors)
        
        # 更新提示按钮状态
        if "hint" in self.control_buttons:
            hint_enabled = False
            
            if self.logic.game_mode == "PVE":
                # PvE模式：只在玩家回合且Winning Hints启用时可用
                if self.logic.current_player == "Player 1" and self.logic.winning_hints_enabled:
                    hint_enabled = True
            else:
                # PvP模式：只要Winning Hints启用就可用
                if self.logic.winning_hints_enabled:
                    hint_enabled = True
            
            self.control_buttons["hint"].enabled = hint_enabled and not self.logic.game_over
        
        # 确保游戏结束后 restart 按钮可用
        if self.logic.game_over and "restart" in self.control_buttons:
            self.control_buttons["restart"].enabled = True
    
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
            
            if not self.logic.game_over:
                # Draw control panel (包含提示按钮)
                self.ui.draw_control_panel(self.control_buttons, self.logic)
                
                # Draw control panel buttons - 先绘制这些按钮
                for button_name in ["minus", "plus", "confirm"]:
                    if button_name in self.control_buttons:
                        self.control_buttons[button_name].draw(self.screen)
                
                # Draw hints
                hint_y = 600
                hints = [
                    "Use LEFT/RIGHT to select factors, UP/DOWN to scroll",
                    "Click on factors or use CONFIRM to make move", 
                    "If new value < threshold, you lose immediately!",
                    "Use mouse wheel to scroll through factors"
                ]
                
                if self.logic.winning_hints_enabled:
                    hints.append("Press H or click on the hint button (💡) for winning hints")
                
                for i, hint in enumerate(hints):
                    hint_text = self.font_manager.small.render(hint, True, (150, 170, 190))
                    self.screen.blit(hint_text, (SCREEN_WIDTH//2 - hint_text.get_width()//2, hint_y + i * 20))
            else:
                # Draw game over screen
                if "restart" in self.control_buttons:
                    self.control_buttons["restart"].draw(self.screen)
            
            # 新增：绘制提示窗口（如果可见） - 在侧边栏之前绘制，确保在最上层
            if hasattr(self.ui, 'hint_window_visible') and self.ui.hint_window_visible:
                if hasattr(self.ui, '_draw_hint_window'):
                    self.ui._draw_hint_window()
            
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
        panel_height = 600  # 增加高度以容纳提示功能信息
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
            'valid_factors': self.logic.valid_factors.copy() if self.logic.valid_factors else [],
            'winning_hints_enabled': getattr(self.logic, 'winning_hints_enabled', False)
        }