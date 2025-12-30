import pygame
import sys
from core.game_manager import GameManager
from games.take_coins.logic import TakeCoinsLogic
from games.take_coins.ui import TakeCoinsUI, ScrollButton
from utils.constants import *
from utils.key_repeat import KeyRepeatManager
from ui.components.sidebar import Sidebar
from utils.config_manager import config_manager  # 新增导入

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
        
        # 检查游戏控制按钮
        if self.game_logic.game_over:
            if "restart" in control_buttons and control_buttons["restart"].is_clicked(event):
                self.game_logic.initialize_game(self.game_logic.game_mode, self.game_logic.difficulty)
                self.ui.scroll_offset = 0
                self.key_repeat_manager._reset_state()
                return "restart"  # 返回重启标记
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
                if (control_buttons.get("confirm") and control_buttons["confirm"].is_clicked(event) and 
                    self.game_logic.selected_position is not None and
                    self.game_logic.selected_position in self.game_logic.valid_positions):
                    if self.game_logic.make_move():
                        self.key_repeat_manager._reset_state()
        
        # Check hint button
        if "hint" in control_buttons and control_buttons["hint"].is_clicked(event):
            if self.game_logic.winning_hints_enabled:
                hint_text = self.game_logic.get_winning_hint()
                if hasattr(self.ui, 'show_hint_window'):
                    self.ui.show_hint_window(hint_text)
            return "hint"
        
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
            # 游戏结束后允许按R键重启
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.game_logic.initialize_game(self.game_logic.game_mode, self.game_logic.difficulty)
                self.ui.scroll_offset = 0
                self.key_repeat_manager._reset_state()
                return "restart"
            return None
        
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
            
            # Handle hint key (H)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_h:
                if self.game_logic.winning_hints_enabled:
                    hint_text = self.game_logic.get_winning_hint()
                    if hasattr(self.ui, 'show_hint_window'):
                        self.ui.show_hint_window(hint_text)
                return "hint"
        
        return None
    
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
    """Take Coins Game implementation with scrolling support and sidebar"""
    
    def __init__(self, screen, font_manager):
        super().__init__(screen, font_manager)
        self.logic = TakeCoinsLogic()
        self.ui = TakeCoinsUI(screen, font_manager)
        self.input_handler = TakeCoinsInputHandler(self.logic, self.ui)
        self.sidebar = Sidebar(screen, font_manager)
        self.config_manager = config_manager
        
        self.font_manager.initialize_fonts()
        
        # 游戏说明 - 更新以包含Winning Hints信息
        self.game_instructions = """
TAKE COINS GAME - INSTRUCTIONS

Objective:
Take coins from adjacent positions. The player who cannot make a move loses!

How to Play:
1. Select a position to add a coin (except first and last positions)
2. The selected position gains 1 coin
3. Both neighboring positions lose 1 coin each
4. A move is only valid if both neighbors have at least 1 coin
5. Press CONFIRM or double-click to make your move

Game Rules:
- You can only select positions that have neighbors with coins
- If a position reaches 0 coins, it becomes "Empty"
- The game ends when no valid moves remain
- Last player to make a move wins!

Game Modes:
- Player vs Player: Play against another person
- Player vs AI: Play against computer AI with adjustable difficulty

Strategies:
- Try to leave your opponent with no valid moves
- Control the center positions for more options
- Watch the "Winning Position"/"Losing Position" indicator

Winning Hints Feature:
- Enable "Winning Hints" in Settings (gear icon)
- Click on the light bulb (💡) button to get AI suggestions
- AI will suggest optimal moves when in a winning position
- In losing positions, AI will suggest defensive strategies
- Press H key for quick hint

Controls:
- Mouse: Click to select positions and buttons
- Arrow Keys: Navigate between positions
- UP/DOWN: Scroll through positions
- ENTER: Confirm move
- R: Restart game
- I: Show these instructions
- H: Get quick hint (if Winning Hints enabled)
- ESC: Back to mode selection

Difficulty Levels:
- Easy: AI makes more random moves
- Normal: Balanced AI difficulty
- Hard: AI uses advanced strategies
- Insane: AI plays nearly perfectly

Navigation:
- Back (←): Return to mode selection
- Home (🏠): Return to main menu  
- Restart: Restart current game
- Info (i): Show these instructions
- Settings (⚙️): Open settings panel
- Hint (💡): Show winning hint (when enabled)

Good luck and have fun!
"""
        
        # 信息对话框状态
        self.showing_instructions = False
        
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
                current_prefs = config_manager.get_user_preferences()
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
                self.logic.initialize_game("PVE", difficulty, winning_hints=winning_hints)
            else:
                self.logic.initialize_game("PVP", None, winning_hints=winning_hints)
                
        except Exception as e:
            print(f"Error initializing game settings: {e}")
            try:
                winning_hints = config_manager.get_user_preferences().winning_hints
            except:
                winning_hints = False
            self.logic.initialize_game("PVE", 2, winning_hints=winning_hints)
    
    def handle_events(self):
        """Handle game events with scrolling support"""
        if self.should_return_to_menu:
            return False
        
        mouse_pos = pygame.mouse.get_pos()
        
        # 处理侧边栏事件
        sidebar_result = self.sidebar.handle_event(pygame.event.Event(pygame.MOUSEMOTION, {'pos': mouse_pos}), mouse_pos)
        
        # Update button hover states
        for button in self.control_buttons.values():
            button.update_hover(mouse_pos)
        
        for button in self.scroll_buttons:
            button.update_hover(mouse_pos)
        
        # Update hint tooltip
        self.ui.update_hint_tooltip(mouse_pos)
        
        # 检查提示窗口事件优先处理
        if hasattr(self.ui, 'hint_window_visible') and self.ui.hint_window_visible:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                
                # 先让提示窗口处理事件
                if self.ui.handle_hint_window_events(event, mouse_pos):
                    continue
                
                # 其他事件处理...
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            # 如果提示窗口打开，让提示窗口优先处理事件
            if hasattr(self.ui, 'hint_window_visible') and self.ui.hint_window_visible:
                if self.ui.handle_hint_window_events(event, mouse_pos):
                    continue
            
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
            
            # Handle navigation events
            nav_result = self.handle_navigation_events(event)
            if nav_result == "back":
                self.initialize_game_settings()
                self.ui.scroll_offset = 0
                return True
            elif nav_result == "home":
                return False
            elif nav_result == "refresh":
                # Restart game
                game_mode = getattr(self.logic, 'game_mode', "PVE")
                difficulty = getattr(self.logic, 'difficulty', 2)
                winning_hints = getattr(self.logic, 'winning_hints_enabled', False)
                self.logic.initialize_game(game_mode, difficulty, winning_hints=winning_hints)
                self.ui.scroll_offset = 0
                if hasattr(self.input_handler, 'key_repeat_manager'):
                    self.input_handler.key_repeat_manager._reset_state()
                # 关闭提示窗口
                if hasattr(self.ui, 'hint_window_visible'):
                    self.ui.close_hint_window()
                return True
            elif nav_result == "info":
                self.showing_instructions = True
                return True
            elif nav_result == "hint":
                # 处理hint按键
                if self.logic.winning_hints_enabled:
                    hint_text = self.logic.get_winning_hint()
                    if hasattr(self.ui, 'show_hint_window'):
                        self.ui.show_hint_window(hint_text)
                return True
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                result = self.input_handler.handle_mouse_click(
                    event, self.position_buttons, self.scroll_buttons, self.control_buttons
                )
                # 检查是否重启了游戏
                if result == "restart":
                    self.create_components()
                    return True
            
            elif event.type in [pygame.KEYDOWN, pygame.KEYUP]:
                result = self.input_handler.handle_keyboard(event)
                # 检查是否重启了游戏
                if result == "restart":
                    self.create_components()
                    return True
            
            elif event.type == pygame.MOUSEWHEEL:
                self.ui.handle_mouse_wheel(event, len(self.logic.coins))
        
        return True
    
    def handle_navigation_events(self, event):
        """Universal navigation events handling"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            # 不再检查游戏控制按钮，因为这些现在在侧边栏中
            pass
        
        # 按键事件
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_i:
                return "info"
            elif event.key == pygame.K_r:
                return "refresh"
            elif event.key == pygame.K_h:
                # H键显示提示窗口
                if self.logic.winning_hints_enabled:
                    hint_text = self.logic.get_winning_hint()
                    if hasattr(self.ui, 'show_hint_window'):
                        self.ui.show_hint_window(hint_text)
                return "hint"
            elif event.key == pygame.K_F2:
                self.show_perf_overlay = not self.show_perf_overlay
        
        return None
    
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
            self.logic.initialize_game(game_mode, difficulty, winning_hints=winning_hints)
            self.ui.scroll_offset = 0
            # 关闭提示窗口
            if hasattr(self.ui, 'hint_window_visible'):
                self.ui.close_hint_window()
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
                if hasattr(self.sidebar, 'settings_panel'):
                    settings = self.sidebar.settings_panel.get_settings()
                    winning_hints = settings.get('winning_hints', False)
                    
                    print(f"Winning hints setting changed to: {winning_hints}")
                    
                    # 更新配置管理器
                    try:
                        prefs = config_manager.get_user_preferences()
                        prefs.winning_hints = winning_hints
                        config_manager.update_user_preferences(prefs)
                        
                        # 更新游戏逻辑中的设置
                        self.logic.winning_hints_enabled = winning_hints
                        
                        # 显示反馈消息
                        if winning_hints:
                            self.logic.message = "Winning Hints enabled! Press H or click ? button for guidance."
                        else:
                            self.logic.message = "Winning Hints disabled."
                            
                    except Exception as e:
                        print(f"Error updating setting: {e}")
                        
                    # 强制更新按钮状态
                    self.update_button_states()
            return True
        elif action == "sponsor_clicked":
            print("Sponsor link clicked")
            return True
        return True
    
    def update(self):
        """Update game state with scrolling support"""
        self.sidebar.update()
        
        # Update position buttons based on current valid positions
        self.position_buttons = self.ui.create_position_buttons(
            self.logic.coins, self.logic.valid_positions, self.logic.selected_position
        )
        
        # Update scroll buttons
        self.scroll_buttons = self.ui.create_scroll_buttons(len(self.logic.coins))
        
        # Update key repeat
        self.input_handler.update_key_repeat()
        
        # Update button states
        self.update_button_states()
        
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
            # 如果显示说明，绘制说明页面
            if self.showing_instructions:
                self.draw_instructions()
                pygame.display.flip()
                return
            
            # Draw background
            self.ui.draw_background()
            
            # Draw game information
            self.ui.draw_game_info(self.logic)
            
            # Draw coin positions with scrolling
            self.ui.draw_coin_stacks(self.logic, self.position_buttons, self.scroll_buttons)
            
            # Draw game-specific UI
            if not self.logic.game_over:
                # Draw control panel
                self.ui.draw_control_panel(self.control_buttons, self.logic)
                
                # Draw confirm button and hint button
                for button_name in ["confirm", "hint"]:
                    if button_name in self.control_buttons:
                        self.control_buttons[button_name].draw(self.screen)
                
                # Draw hints
                self.ui.draw_hints()
            else:
                # Draw restart button
                if "restart" in self.control_buttons:
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
        title = self.font_manager.large.render("Take Coins Game - Instructions", True, TEXT_COLOR)
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
    
    def update_button_states(self):
        """Update button states based on game logic"""
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
        
        # Update confirm button
        if "confirm" in self.control_buttons:
            can_confirm = (self.logic.selected_position is not None and 
                          self.logic.selected_position in self.logic.valid_positions)
            self.control_buttons["confirm"].enabled = buttons_enabled and can_confirm
        
        # Update hint button
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
            
            self.control_buttons["hint"].enabled = hint_enabled
        
        # 确保游戏结束后 restart 按钮可用
        if self.logic.game_over and "restart" in self.control_buttons:
            self.control_buttons["restart"].enabled = True
    
    def get_game_info(self):
        """Return game information"""
        return {
            'name': 'Take Coins Game',
            'description': 'Strategic coin manipulation game on a line',
            'current_player': self.logic.current_player,
            'game_over': self.logic.game_over,
            'winner': self.logic.winner,
            'coins': self.logic.coins.copy(),
            'valid_positions': self.logic.valid_positions.copy(),
            'winning_hints_enabled': getattr(self.logic, 'winning_hints_enabled', False)
        }