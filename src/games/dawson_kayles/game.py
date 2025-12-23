# [file name]: src/games/dawson_kayles/game.py
"""
Dawson-Kayles Game using Universal Game Manager
"""

import pygame
from core.game_manager import GameManager
from games.dawson_kayles.logic import DawsonKaylesLogic
from games.dawson_kayles.ui import DawsonKaylesUI, TowerButton
from utils.constants import CARD_GAME_FPS, SCREEN_WIDTH, SCREEN_HEIGHT
from ui.components.sidebar import Sidebar  # 新增导入

class DawsonKaylesInputHandler:
    """Handles input for Dawson-Kayles game"""
    
    def __init__(self, game_logic, ui):
        self.game_logic = game_logic
        self.ui = ui
        self.selected_position = None
        self.connect_button_rect = None  # 新增：连接按钮区域
    
    def handle_mouse_click(self, event, tower_buttons, scroll_buttons, control_buttons):
        """处理鼠标点击事件"""
        mouse_pos = pygame.mouse.get_pos()
        
        # 首先检查滚动按钮
        for button in scroll_buttons:
            if button.is_clicked(event):
                if button.text == "<":
                    self.ui.scroll_left(len(self.game_logic.towers))
                else:
                    self.ui.scroll_right(len(self.game_logic.towers))
                return None
        
        # 获取输入框实例
        input_box = self.ui.get_input_box()
        
        # 处理输入框事件（优先处理）
        if input_box and input_box.handle_event(event):
            # 输入框处理了事件
            if not input_box.is_active():
                # 输入框已确认，验证输入值
                self._validate_input_box_value(input_box)
            return "input_box"
        
        # 如果不是导航按钮，再处理游戏逻辑
        if self.game_logic.game_over:
            # 游戏结束，只处理重新开始按钮
            if "restart" in control_buttons and control_buttons["restart"].is_clicked(event):
                self.game_logic.initialize_game(self.game_logic.game_mode, self.game_logic.difficulty)
                self.ui.scroll_offset = 0
                self.selected_position = None
                return "restart"  # 返回重启标记
        else:
            # 游戏进行中，检查是否可以交互
            can_interact = False
            if self.game_logic.game_mode == "PVP":
                can_interact = True
            elif self.game_logic.game_mode == "PVE" and self.game_logic.current_player == "Player 1":
                can_interact = True
            
            if can_interact:
                # 检查连接按钮点击
                if (self.connect_button_rect and 
                    self.connect_button_rect.collidepoint(mouse_pos) and 
                    event.type == pygame.MOUSEBUTTONDOWN and event.button == 1):
                    self._handle_connect_button_click(input_box)
                    return None
                
                # 检查炮塔选择
                for button in tower_buttons:
                    if button.is_clicked(event) and self.game_logic.towers[button.tower_id] == 1:
                        self.handle_tower_click(button.tower_id)
                        return None
        
        return None
    
    def _handle_connect_button_click(self, input_box):
        """处理连接按钮点击"""
        if not input_box:
            return
            
        # 获取输入值
        tower_n = input_box.get_int_value()
        
        # 验证输入
        if tower_n < 1 or tower_n >= len(self.game_logic.towers):
            self.game_logic.message = f"Please check if your input is out of range. Valid range: 1 to {len(self.game_logic.towers)-1}"
            input_box.set_value(1)
            return
        
        # 转换为0索引
        move_index = tower_n - 1
        
        # 检查炮塔是否已被连接
        if self.game_logic.towers[move_index] == 0 or self.game_logic.towers[move_index + 1] == 0:
            self.game_logic.message = "Please check if the tower has been connected."
            input_box.set_value(1)
            return
        
        # 检查是否是有效移动
        available_moves = self.game_logic.get_available_moves()
        if move_index not in available_moves:
            self.game_logic.message = f"Cannot connect tower {tower_n} and {tower_n+1}. They must be adjacent and available."
            input_box.set_value(1)
            return
        
        # 执行移动
        self.game_logic.make_move(move_index)
        input_box.set_value(1)
        self.selected_position = None
    
    def _validate_input_box_value(self, input_box):
        """验证输入框的值"""
        if not input_box:
            return
            
        tower_n = input_box.get_int_value()
        
        # 基本验证
        if tower_n < 1:
            input_box.set_value(1)
        elif tower_n >= len(self.game_logic.towers):
            max_val = len(self.game_logic.towers) - 1
            input_box.set_value(max_val if max_val > 0 else 1)
    
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
            # 先检查输入框是否激活
            input_box = self.ui.get_input_box()
            if input_box and input_box.is_active():
                # 如果输入框激活，只处理ESC和回车（已经在输入框中处理）
                pass
            elif event.key == pygame.K_LEFT:
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
            elif event.key == pygame.K_r and self.game_logic.game_over:
                # 按R键重启游戏
                self.game_logic.initialize_game(self.game_logic.game_mode, self.game_logic.difficulty)
                self.ui.scroll_offset = 0
                self.selected_position = None
                return "restart"
            elif event.key == pygame.K_c:
                # 按C键触发连接按钮（快捷方式）
                input_box = self.ui.get_input_box()
                if input_box and not self.game_logic.game_over:
                    self._handle_connect_button_click(input_box)

class DawsonKaylesGame(GameManager):
    """Dawson-Kayles Game implementation with sidebar"""
    
    def __init__(self, screen, font_manager):
        super().__init__(screen, font_manager)
        self.logic = DawsonKaylesLogic()
        self.ui = DawsonKaylesUI(screen, font_manager)
        self.input_handler = DawsonKaylesInputHandler(self.logic, self.ui)
        self.sidebar = Sidebar(screen, font_manager)  # 新增侧边栏
        
        # 游戏说明
        self.game_instructions = """
LASER DEFENSE SYSTEM - INSTRUCTIONS

Objective:
Connect adjacent towers with lasers. The player who makes the last move wins!

How to Play:
1. Click on an available tower (highlighted in blue)
2. Click on an adjacent available tower to create a laser connection
3. Both connected towers are removed from play
4. Players alternate turns until no moves remain
5. The player who makes the last move wins the game

Game Rules:
- You can only connect towers that are directly adjacent
- Once a tower is connected, it cannot be used again
- Laser connections display in player colors:
  - Player 1: Blue-Green
  - Player 2/AI: Orange-Gold
- The game ends when no adjacent towers remain

NEW: Direct Input:
- Use the control panel at the bottom to directly enter tower numbers
- Enter a number n to connect towers n and n+1
- Press CONNECT button or C key to execute
- Invalid inputs will show error messages

Game Modes:
- Player vs Player: Play against another person
- Player vs AI: Play against computer AI with adjustable difficulty

Strategies:
- Try to leave your opponent with no valid moves
- Control multiple sections of the tower line
- Watch the "Winning Position"/"Losing Position" indicator
- Look for moves that create isolated towers

Controls:
- Mouse: Click to select towers and create lasers
- LEFT/RIGHT Arrow Keys: Scroll through towers
- ENTER: Complete move when a tower is selected
- C: Connect using input box value
- R: Restart game
- I: Show these instructions
- ESC: Back to mode selection

Difficulty Levels:
- Easy: AI makes mostly random moves
- Normal: Balanced AI difficulty
- Hard: AI uses basic winning strategies
- Insane: AI plays nearly perfect game

Navigation:
- Back (←): Return to mode selection
- Home (🏠): Return to main menu  
- Restart: Restart current game
- Info (i): Show these instructions

Good luck commander!
"""
        
        # 信息对话框状态
        self.showing_instructions = False
        
        # 确保字体已初始化
        self.font_manager.initialize_fonts()
        
        # 初始化游戏设置
        self.initialize_game_settings()
        
        # 创建UI组件
        if not self.should_return_to_menu:
            self.create_components()
    
    def create_components(self):
        """创建游戏组件"""
        # 现在只创建游戏控制按钮，导航按钮在侧边栏中
        self.control_buttons = self.ui.create_control_buttons()
        self.game_over_buttons = {}
        self.tower_buttons = []
        self.scroll_buttons = []
        self.ai_timer = 0
        self.connect_button_rect = None  # 新增：连接按钮区域
    
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
    
    def handle_events(self):
        """Handle game events"""
        if self.should_return_to_menu:
            return False
        
        mouse_pos = pygame.mouse.get_pos()
        
        # 处理侧边栏事件
        sidebar_result = self.sidebar.handle_event(pygame.event.Event(pygame.MOUSEMOTION, {'pos': mouse_pos}), mouse_pos)
        
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
            
            # 获取输入框实例
            input_box = self.ui.get_input_box()
            
            # 处理输入框事件（优先处理）
            if input_box and input_box.handle_event(event):
                # 输入框处理了事件
                if not input_box.is_active():
                    # 输入框已确认，验证输入值
                    tower_n = input_box.get_int_value()
                    if tower_n < 1:
                        input_box.set_value(1)
                    elif tower_n >= len(self.logic.towers):
                        max_val = len(self.logic.towers) - 1
                        input_box.set_value(max_val if max_val > 0 else 1)
                return True
            
            # 如果输入框激活，不处理其他事件（除了ESC和回车已经在输入框处理了）
            if input_box and input_box.is_active():
                # 输入框激活时，只允许处理ESC和回车（已在上面处理）
                continue
            
            # Handle navigation events
            nav_result = self.handle_navigation_events(event)
            if nav_result == "back":
                self.initialize_game_settings()
                self.ui.scroll_offset = 0
                self.input_handler.selected_position = None
                return True
            elif nav_result == "home":
                return False
            elif nav_result == "refresh":
                # Restart game
                game_mode = getattr(self.logic, 'game_mode', "PVE")
                difficulty = getattr(self.logic, 'difficulty', 2)
                self.logic.initialize_game(game_mode, difficulty)
                self.ui.scroll_offset = 0
                self.input_handler.selected_position = None
                return True
            elif nav_result == "info":
                self.showing_instructions = True
                return True
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                result = self.input_handler.handle_mouse_click(
                    event, self.tower_buttons, self.scroll_buttons, self.control_buttons
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
                # Handle mouse wheel scrolling
                self.ui.handle_mouse_wheel(event, len(self.logic.towers))
        
        return True
    
    def handle_navigation_events(self, event):
        """Universal navigation events handling"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            # 不再检查导航按钮，因为这些现在在侧边栏中
            pass
        
        # 按 I 键显示信息
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_i:
            return "info"
        # 按 R 键重启游戏
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            return "refresh"
        # 按 C 键触发连接按钮
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_c:
            # 触发连接按钮
            input_box = self.ui.get_input_box()
            if input_box and not self.logic.game_over:
                self.input_handler._handle_connect_button_click(input_box)
            return None
        # Toggle performance overlay with F2
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_F2:
            self.show_perf_overlay = not self.show_perf_overlay
        
        return None
    
    def _handle_sidebar_action(self, action):
        """处理侧边栏按钮点击"""
        if action == "toggle":
            return True
        elif action == "back":
            self.initialize_game_settings()
            self.ui.scroll_offset = 0
            self.input_handler.selected_position = None
            return True
        elif action == "home":
            return False  # 返回主菜单
        elif action == "refresh":
            # 重启游戏
            game_mode = getattr(self.logic, 'game_mode', "PVE")
            difficulty = getattr(self.logic, 'difficulty', 2)
            self.logic.initialize_game(game_mode, difficulty)
            self.ui.scroll_offset = 0
            self.input_handler.selected_position = None
            return True
        elif action == "info":
            self.showing_instructions = True
            return True
        elif action == "settings":
            print("Settings button clicked")
            return True
        return True
    
    def update(self):
        """Update game state"""
        self.sidebar.update()
        
        # 更新输入框状态
        self.ui.update_input_box()
        
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
            # 如果显示说明，绘制说明页面
            if self.showing_instructions:
                self.draw_instructions()
                pygame.display.flip()
                return
            
            # Draw background
            self.ui.draw_background()
            
            # Draw game information
            self.ui.draw_game_info(self.logic)
            
            # Draw towers and lasers
            self.ui.draw_towers_and_lasers(self.logic, self.tower_buttons)
            
            # Draw scroll bar
            self.ui.draw_scrollbar(len(self.logic.towers))
            
            # 绘制控制面板（包含输入框和连接按钮）
            if not self.logic.game_over:
                # 绘制控制面板并获取连接按钮区域
                self.connect_button_rect = self.ui.draw_control_panel(self.logic)
                self.input_handler.connect_button_rect = self.connect_button_rect
                
                # Draw hints
                self.ui.draw_hints()
                
                # 如果游戏进行中，显示输入提示
                hints = [
                    "Click on adjacent towers to connect them with lasers",
                    "Or use the control panel below: enter n to connect towers n and n+1",
                    "Press C key for quick connect, ESC to cancel input"
                ]
                hint_y = 630
                for i, hint in enumerate(hints):
                    hint_text = self.font_manager.small.render(hint, True, (180, 220, 255))
                    self.screen.blit(hint_text, (SCREEN_WIDTH//2 - hint_text.get_width()//2, hint_y + i * 18))
            else:
                # Draw game over restart button
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
        from utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT, ACCENT_COLOR, TEXT_COLOR
        
        # Draw semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        # Draw instructions panel
        panel_width = 800
        panel_height = 550
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_y = (SCREEN_HEIGHT - panel_height) // 2
        
        # Panel background
        pygame.draw.rect(self.screen, (15, 25, 40), (panel_x, panel_y, panel_width, panel_height), border_radius=15)
        pygame.draw.rect(self.screen, (0, 200, 255), (panel_x, panel_y, panel_width, panel_height), 3, border_radius=15)
        
        # Title
        title = self.font_manager.large.render("Laser Defense System - Instructions", True, (0, 255, 220))
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, panel_y + 40))
        self.screen.blit(title, title_rect)
        
        # Subtitle
        subtitle = self.font_manager.medium.render("DAWSON-KAYLES PROTOCOL", True, (100, 200, 255))
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH//2, panel_y + 70))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Close hint
        close_hint = self.font_manager.small.render("Click anywhere or press ESC/I to close", True, (180, 200, 220))
        close_rect = close_hint.get_rect(center=(SCREEN_WIDTH//2, panel_y + panel_height - 30))
        self.screen.blit(close_hint, close_rect)
        
        # Draw instructions text with word wrapping
        y_pos = panel_y + 100
        instructions = self.game_instructions.strip().split('\n')
        
        for line in instructions:
            if line.strip() == "":
                y_pos += 15  # Extra space for paragraph breaks
                continue
                
            # Determine font size based on line content
            if line.strip().endswith(":"):  # Section headers
                font = self.font_manager.medium
                color = (0, 200, 255)  # 科技蓝
                y_pos += 10  # Extra space before section
            elif line.strip().startswith("-"):  # Bullet points
                line = "  • " + line[1:].strip()
                font = self.font_manager.small
                color = (220, 240, 255)
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
            'name': 'Laser Defense - Dawson-Kayles',
            'description': 'Strategic tower connection game using Dawson-Kayles rules',
            'current_player': self.logic.current_player,
            'game_over': self.logic.game_over,
            'winner': self.logic.winner,
            'towers_remaining': sum(self.logic.towers),
            'available_moves': len(self.logic.get_available_moves()),
            'winning_position': self.logic.judge_win()
        }