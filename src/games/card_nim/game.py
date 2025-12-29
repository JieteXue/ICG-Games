"""
Card Nim Game using Universal Game Manager
"""

import pygame
from core.game_manager import GameManager
from games.card_nim.logic import CardNimLogic
from games.card_nim.ui import CardNimUI
from utils.constants import CARD_GAME_FPS, SCREEN_WIDTH, SCREEN_HEIGHT, ACCENT_COLOR, TEXT_COLOR
from ui.components.sidebar import Sidebar

class CardNimGame(GameManager):
    """Card Nim Game implementation"""
    
    def __init__(self, screen, font_manager):
        super().__init__(screen, font_manager)

        self.sidebar = Sidebar(screen, font_manager)

        # Create game-specific components
        self.logic = CardNimLogic()
        self.ui = CardNimUI(screen, font_manager)
        
        # 游戏说明
        self.game_instructions = """
CARD NIM GAME - INSTRUCTIONS

Objective:
Take cards from stacks. The player who takes the last card wins!

How to Play:
1. Click on a card stack to select it
2. Click on the number box to input count directly, or use UP/DOWN arrows/buttons
3. Press CONFIRM or ENTER to make your move
4. Try to leave your opponent in a losing position

Game Modes:
- Player vs Player: Play against another person
- Player vs AI: Play against computer AI with adjustable difficulty

Strategies:
- The game uses Nim theory: XOR sum determines winning/losing positions
- Try to make moves that leave the XOR sum at 0 for your opponent
- Watch the "Winning Position"/"Losing Position" indicator

Controls:
- Mouse: Click to select stacks and buttons
- Arrow Keys: Navigate between stacks and adjust card count
- Click on number box: Direct number input
- ENTER: Confirm move
- ESC: Cancel input or go back
- R: Restart game
- I: Show these instructions
- ESC (when input active): Cancel input

Difficulty Levels:
- Easy: AI makes more random moves
- Normal: Balanced AI difficulty
- Hard: AI uses advanced strategies
- Insane: AI plays nearly perfectly

Navigation:
- Back (←): Return to mode selection
- Home (🏠): Return to main menu  
- Refresh (↻): Restart current game
- Info (i): Show these instructions
- Settings (⚙️): Open settings panel

Good luck and have fun!
"""
        
        # 信息对话框状态
        self.showing_instructions = False
        
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
                # 输入框处理了事件，更新选择的数量
                if not input_box.is_active():
                    # 输入框已确认，更新逻辑中的选择数量
                    new_value = input_box.get_int_value()
                    
                    # 验证数值范围
                    if self.logic.selected_position_index is not None:
                        max_count = self.logic.positions[self.logic.selected_position_index]
                        if new_value < 1:
                            new_value = 1
                        elif new_value > max_count:
                            new_value = max_count
                        
                        self.logic.selected_count = new_value
                return True
            
            # 如果输入框激活，不处理其他事件（除了ESC和回车已经在输入框处理了）
            if input_box and input_box.is_active():
                # 输入框激活时，只允许处理ESC和回车（已在上面处理）
                continue
            
            # Handle navigation events
            nav_result = self.handle_navigation_events(event)
            if nav_result == "back":
                self.initialize_game_settings()
                return True
            elif nav_result == "home":
                return False
            elif nav_result == "refresh":
                return True
            elif nav_result == "info":
                self.showing_instructions = True
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
    
    def handle_navigation_events(self, event):
        """Universal navigation events handling"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if "info" in self.buttons and self.buttons["info"].is_clicked(event):
                return "info"
            if "refresh" in self.buttons and self.buttons["refresh"].is_clicked(event):
                # Restart game logic
                game_mode = getattr(self.logic, 'game_mode', "PVE")
                difficulty = getattr(self.logic, 'difficulty', 2)
                self.logic.initialize_game(game_mode, difficulty)
                if hasattr(self.ui, 'scroll_offset'):
                    self.ui.scroll_offset = 0
                return "refresh"
            
            if "back" in self.buttons and self.buttons["back"].is_clicked(event):
                return "back"
            elif "home" in self.buttons and self.buttons["home"].is_clicked(event):
                return "home"
        
        # 按 I 键显示信息
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_i:
            return "info"
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
            return True
        elif action == "home":
            return False  # 返回主菜单
        elif action == "refresh":
            # 重启游戏
            game_mode = getattr(self.logic, 'game_mode', "PVE")
            difficulty = getattr(self.logic, 'difficulty', 2)
            self.logic.initialize_game(game_mode, difficulty)
            return True
        elif action == "info":
            self.showing_instructions = True
            return True
        elif action == "settings":
            # 处理设置变化
            setting_name = action.replace("setting_changed_", "")
            print(f"Setting changed: {setting_name}")
            # 笑死我了只有按钮还没实装
            # 这里可以添加具体的设置处理逻辑
            return True
        elif action == "sponsor_clicked":
            print("Sponsor link clicked")
            return True
        return True

    def update(self):
        """Update game state"""
        self.sidebar.update()

        # 更新输入框状态（光标闪烁等）
        input_box = self.ui.get_input_box()
        if input_box:
            input_box.update()
        
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
        
        # 如果显示说明，绘制说明页面
        if self.showing_instructions:
            self.draw_instructions()
            pygame.display.flip()
            return
        
        # Draw game information
        self.ui.draw_game_info(self.logic)
        
        # Draw card positions
        self.position_rects = self.ui.draw_card_positions(self.logic.positions, self.logic.selected_position_index)
        
        # Draw game-specific UI
        if not self.logic.game_over:
            self.ui.draw_control_panel(self.buttons, self.logic.selected_count, self.logic.selected_position_index)
            
            # 只绘制加减按钮和确认按钮（数字显示已在control_panel中绘制）
            for button_name in ["minus", "plus", "confirm"]:
                if button_name in self.buttons:
                    self.buttons[button_name].draw(self.screen)
            self.ui.draw_hints()
        else:
            if "restart" in self.buttons:
                self.buttons["restart"].draw(self.screen)
        
        # 最后绘制侧边栏，使其在最上层
        self.sidebar.draw()
        
        pygame.display.flip()
    
    def draw_instructions(self):
        """Draw game instructions overlay"""
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
        pygame.draw.rect(self.screen, (35, 45, 60), (panel_x, panel_y, panel_width, panel_height), border_radius=15)
        pygame.draw.rect(self.screen, ACCENT_COLOR, (panel_x, panel_y, panel_width, panel_height), 3, border_radius=15)
        
        # Title
        title = self.font_manager.large.render("Card Nim Game - Instructions", True, TEXT_COLOR)
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