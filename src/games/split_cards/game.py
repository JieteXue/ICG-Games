"""
Split Cards Game - Main game class with Sidebar
"""

import pygame
from core.game_manager import GameManager
from games.split_cards.logic import SplitCardsLogic
from games.split_cards.ui import SplitCardsUI
from ui.components.sidebar import Sidebar
from utils.constants import CARD_GAME_FPS, SCREEN_WIDTH, SCREEN_HEIGHT, ACCENT_COLOR, TEXT_COLOR
from utils.key_repeat import KeyRepeatManager
class SplitCardsInputHandler:
    """Handles input for Split Cards game"""
    
    def __init__(self, game_logic):
        self.game_logic = game_logic
        self.key_repeat_manager = KeyRepeatManager()
    
    def _create_key_callbacks(self):
        """创建按键回调字典"""
        return {
            pygame.K_LEFT: self._select_previous_pile,
            pygame.K_RIGHT: self._select_next_pile,
            pygame.K_UP: self._increase_count,
            pygame.K_DOWN: self._decrease_count
        }
    
    def handle_mouse_click(self, event, pile_rects, buttons, input_box):
        """Handle mouse click events"""
        mouse_pos = pygame.mouse.get_pos()
        
        # 检查输入框点击
        if input_box and input_box.handle_event(event):
            # 输入框处理了事件
            if not input_box.is_active():
                # 输入框已确认，更新游戏逻辑中的选择数量
                new_value = input_box.get_int_value()
                self._validate_and_set_count(new_value)
            return "input_box"
        
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
            elif self.game_logic.game_mode == "PVE" and self.game_logic.current_player == "Player 1":  # 使用self.game_logic
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
                if self.game_logic.selected_pile_index is not None:  # 使用self.game_logic
                    # 检查split按钮是否可用（牌堆必须大于1）
                    pile_size = self.game_logic.card_piles[self.game_logic.selected_pile_index]  # 使用self.game_logic
                    
                    if buttons["take_btn"].is_clicked(event):
                        self.game_logic.selected_action = 'take'  # 使用self.game_logic
                        max_take = min(self.game_logic.max_take, pile_size)  # 使用self.game_logic
                        self.game_logic.selected_count = min(self.game_logic.selected_count, max_take)  # 使用self.game_logic
                        self.game_logic.message = f"Taking from pile {self.game_logic.selected_pile_index + 1}. Select amount (1-{max_take})."  # 使用self.game_logic
                    
                    elif buttons["split_btn"].is_clicked(event) and pile_size > 1:  # 添加牌堆大小检查
                        self.game_logic.selected_action = 'split'  # 使用self.game_logic
                        pile_size = self.game_logic.card_piles[self.game_logic.selected_pile_index]  # 使用self.game_logic
                        self.game_logic.selected_count = min(self.game_logic.selected_count, pile_size - 1)  # 使用self.game_logic
                        self.game_logic.message = f"Splitting pile {self.game_logic.selected_pile_index + 1}. Split after {self.game_logic.selected_count} cards."  # 使用self.game_logic
                    
                    # Check number adjustment buttons
                    if self.game_logic.selected_action:  # 使用self.game_logic
                        pile_size = self.game_logic.card_piles[self.game_logic.selected_pile_index]  # 使用self.game_logic
                        
                        if buttons["minus"].is_clicked(event):
                            self._decrease_count()
                        
                        elif buttons["plus"].is_clicked(event):
                            self._increase_count()
                    
                    # Check confirm button
                    if buttons["confirm_btn"].is_clicked(event) and self.game_logic.selected_action:  # 使用self.game_logic
                        if self.game_logic.selected_action == 'take':  # 使用self.game_logic
                            move_info = {
                                'type': 'take',
                                'pile_index': self.game_logic.selected_pile_index,  # 使用self.game_logic
                                'count': self.game_logic.selected_count  # 使用self.game_logic
                            }
                        else:  # split
                            pile_size = self.game_logic.card_piles[self.game_logic.selected_pile_index]  # 使用self.game_logic
                            move_info = {
                                'type': 'split',
                                'pile_index': self.game_logic.selected_pile_index,  # 使用self.game_logic
                                'left_count': self.game_logic.selected_count,  # 使用self.game_logic
                                'right_count': pile_size - self.game_logic.selected_count  # 使用self.game_logic
                            }
                        
                        if self.game_logic.make_move(move_info):  # 使用self.game_logic
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
    
    def _validate_and_set_count(self, new_value):
        """验证并设置选择的数量"""
        if self.game_logic.selected_pile_index is not None and self.game_logic.selected_action:
            pile_size = self.game_logic.card_piles[self.game_logic.selected_pile_index]
            
            if self.game_logic.selected_action == 'take':
                max_take = min(self.game_logic.max_take, pile_size)
                if new_value < 1:
                    new_value = 1
                elif new_value > max_take:
                    new_value = max_take
            else:  # split
                if new_value < 1:
                    new_value = 1
                elif new_value > pile_size - 1:
                    new_value = pile_size - 1
            
            self.game_logic.selected_count = new_value
    
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
        
        if can_interact:
            callbacks = self._create_key_callbacks()
            
            # 处理方向键（带重复）
            self.key_repeat_manager.handle_key_event(event, callbacks)
            
            # 处理回车键（不需要重复）
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                if (self.game_logic.selected_pile_index is not None and 
                    self.game_logic.selected_action):
                    
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
            
            callbacks = self._create_key_callbacks()
            self.key_repeat_manager.update(callbacks)
    
    def _select_previous_pile(self):
        """Select the previous available pile"""
        if not self.game_logic.card_piles:
            return
        
        if self.game_logic.selected_pile_index is None:
            # 如果没有选中的牌堆，选择最后一个可用的牌堆
            for i in range(len(self.game_logic.card_piles)-1, -1, -1):
                if self.game_logic.card_piles[i] > 0:
                    self.game_logic.selected_pile_index = i
                    self.game_logic.selected_action = None
                    self.game_logic.selected_count = 1
                    self.game_logic.message = f"Selected pile {i + 1}. Choose action: Take or Split."
                    break
        else:
            # 从当前选中的牌堆向左循环选择
            new_index = self.game_logic.selected_pile_index
            for i in range(1, len(self.game_logic.card_piles)):
                new_index = (self.game_logic.selected_pile_index - i) % len(self.game_logic.card_piles)
                if self.game_logic.card_piles[new_index] > 0:
                    self.game_logic.selected_pile_index = new_index
                    self.game_logic.selected_action = None
                    self.game_logic.selected_count = 1
                    self.game_logic.message = f"Selected pile {new_index + 1}. Choose action: Take or Split."
                    break
    
    def _select_next_pile(self):
        """Select the next available pile"""
        if not self.game_logic.card_piles:
            return
        
        if self.game_logic.selected_pile_index is None:
            # 如果没有选中的牌堆，选择第一个可用的牌堆
            for i in range(len(self.game_logic.card_piles)):
                if self.game_logic.card_piles[i] > 0:
                    self.game_logic.selected_pile_index = i
                    self.game_logic.selected_action = None
                    self.game_logic.selected_count = 1
                    self.game_logic.message = f"Selected pile {i + 1}. Choose action: Take or Split."
                    break
        else:
            # 从当前选中的牌堆向右循环选择
            new_index = self.game_logic.selected_pile_index
            for i in range(1, len(self.game_logic.card_piles)):
                new_index = (self.game_logic.selected_pile_index + i) % len(self.game_logic.card_piles)
                if self.game_logic.card_piles[new_index] > 0:
                    self.game_logic.selected_pile_index = new_index
                    self.game_logic.selected_action = None
                    self.game_logic.selected_count = 1
                    self.game_logic.message = f"Selected pile {new_index + 1}. Choose action: Take or Split."
                    break
    
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

class SplitCardsGame(GameManager):
    """Split Cards Game implementation with Sidebar"""
    
    def __init__(self, screen, font_manager):
        super().__init__(screen, font_manager)
        self.logic = SplitCardsLogic()
        self.ui = SplitCardsUI(screen, font_manager)
        self.input_handler = SplitCardsInputHandler(self.logic) 
        
        # 添加侧边栏
        self.sidebar = Sidebar(screen, font_manager)
        
        # 确保字体已初始化
        self.font_manager.initialize_fonts()
        
        # 添加游戏说明
        self.game_instructions = """
SPLIT CARDS GAME - INSTRUCTIONS

Objective:
Take the last card! Players alternate taking cards or splitting piles.

How to Play:
1. Start with one pile of cards
2. On your turn, either
   - TAKE: Take 1 to M cards from one pile
   - SPLIT: Split a pile into two non-empty piles
3. The player who takes the last card wins!

Game Modes:
- Player vs Player: Play against another person
- Player vs AI: Play against computer AI with adjustable difficulty

Actions:
- Take: Remove cards from a pile (1 to max_take cards)
- Split: Divide a pile into two smaller piles (both must be non-empty)

Strategies:
- Try to leave your opponent in a losing position
- Watch the "Winning Position"/"Losing Position" indicator
- Split piles strategically to create more options
- Remember: the player who takes the last card wins

Controls:
- Mouse: Click on piles and action buttons
- Click on number box: Direct number input
- Arrow Keys: Adjust count (LEFT/RIGHT/UP/DOWN)
- ENTER: Confirm move
- ESC: Cancel input or go back
- R: Restart game
- I: Show these instructions
- ESC (when input active): Cancel input

Difficulty Levels:
- Easy: Smaller piles, easier to analyze
- Normal: Balanced difficulty
- Hard: Larger piles, more complex decisions
- Insane: Challenging configurations

Navigation:
- Back (←): Return to mode selection
- Home (🏠): Return to main menu  
- Refresh (↻): Restart current game
- Info (i): Show these instructions
- Settings (⚙): Open settings menu

Tips:
- Look for patterns in pile sizes
- Splitting can create winning opportunities
- The max_take limit affects strategy
- Prime numbered piles have different properties

Good luck and have fun!
"""
        
        # 信息对话框状态
        self.showing_instructions = False
        
        # 菜单返回标志
        self.should_return_to_menu = False
        
        # Initialize game mode and difficulty
        self.initialize_game_settings()
        
        # Create UI components
        if not self.should_return_to_menu:
            self.create_components()
    
    def create_components(self):
        """创建游戏组件（实现抽象方法）"""
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
            # Fallback initialization
            self.logic.initialize_game("PVE", 2)
    
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
                    # 输入框已确认，更新游戏逻辑中的选择数量
                    new_value = input_box.get_int_value()
                    if self.logic.selected_pile_index is not None and self.logic.selected_action:
                        pile_size = self.logic.card_piles[self.logic.selected_pile_index]
                        
                        if self.logic.selected_action == 'take':
                            max_take = min(self.logic.max_take, pile_size)
                            if new_value < 1:
                                new_value = 1
                            elif new_value > max_take:
                                new_value = max_take
                        else:  # split
                            if new_value < 1:
                                new_value = 1
                            elif new_value > pile_size - 1:
                                new_value = pile_size - 1
                        
                        self.logic.selected_count = new_value
                return True
            
            # 如果输入框激活，不处理其他事件（除了ESC和回车已经在输入框处理了）
            if input_box and input_box.is_active():
                # 输入框激活时，只允许处理ESC和回车（已在上面处理）
                continue

            # 处理导航事件
            nav_result = self.handle_navigation_events(event)
            if nav_result == "back":
                # Reinitialize game settings
                self.initialize_game_settings()
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
                if "refresh" in self.buttons and self.buttons["refresh"].is_clicked(event):
                    self.logic.initialize_game(self.logic.game_mode, self.logic.difficulty)
                    if hasattr(self.input_handler, 'key_repeat_manager'):
                        self.input_handler.key_repeat_manager._reset_state()
                    return True

                result = self.input_handler.handle_mouse_click(event, self.pile_rects, self.buttons, input_box)
                if result == "back":
                    # Reinitialize game settings
                    self.initialize_game_settings()
                elif result == "home":
                    # Return to main menu
                    return False

            elif event.type in [pygame.KEYDOWN, pygame.KEYUP]:
                self.input_handler.handle_keyboard(event)

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
            self.logic.initialize_game(self.logic.game_mode, self.logic.difficulty)
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
            if "refresh" in self.buttons and self.buttons["refresh"].is_clicked(event):
                # Restart game logic
                self.logic.initialize_game(self.logic.game_mode, self.logic.difficulty)
                if hasattr(self.input_handler, 'key_repeat_manager'):
                    self.input_handler.key_repeat_manager._reset_state()
                return "refresh"
            
            # 检查其他导航按钮
            for btn_name in ["back", "home"]:
                if btn_name in self.buttons and self.buttons[btn_name].is_clicked(event):
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
                if hasattr(self.input_handler, 'key_repeat_manager'):
                    self.input_handler.key_repeat_manager._reset_state()
                return "refresh"
        
        return None
    
    def update(self):
        """Update game state"""
        # 更新侧边栏
        self.sidebar.update()
        
        # 更新输入框状态
        self.ui.update_input_box()
        
        # AI's turn (only in PvE mode)
        if (self.logic.game_mode == "PVE" and 
            self.logic.current_player == "AI" and 
            not self.logic.game_over):
            
            self.ai_timer += 1
            # Add delay for AI move to make it visible
            if self.ai_timer > 30:
                self.logic.ai_make_move()
                self.ai_timer = 0
        else:
            # 更新按键重复状态（仅当不是AI回合时）
            self.input_handler.update_key_repeat()
    
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
            
            # Draw card piles
            self.pile_rects = self.ui.draw_card_piles(
                self.logic.card_piles, 
                self.logic.selected_pile_index,
                self.logic.selected_action
            )
            
            # Draw navigation buttons (包括刷新按钮)
            if "back" in self.buttons:
                self.buttons["back"].draw(self.screen)
            if "home" in self.buttons:
                self.buttons["home"].draw(self.screen)
            if "refresh" in self.buttons:
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
                control_x, control_y = self.ui.draw_control_panel(self.logic)
                
                # Draw control buttons
                for btn_name in ["take_btn", "split_btn", "confirm_btn"]:
                    if btn_name in self.buttons:
                        self.buttons[btn_name].draw(self.screen)
                
                # Draw plus/minus buttons if action selected
                if self.logic.selected_action is not None:
                    self.buttons["minus"].visible = True
                    self.buttons["plus"].visible = True
                    self.buttons["minus"].draw(self.screen)
                    self.buttons["plus"].draw(self.screen)
                    
                    # 注意：数字显示已在draw_control_panel中通过输入框绘制
                else:
                    self.buttons["minus"].visible = False
                    self.buttons["plus"].visible = False
            # Draw hints
                hints = [
                    "点击数字框直接输入数字，回车确认，ESC取消",
                    "Use LEFT/RIGHT arrows to select piles",
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
        pygame.draw.rect(self.screen, (50, 45, 40), (panel_x, panel_y, panel_width, panel_height), border_radius=15)
        pygame.draw.rect(self.screen, (180, 150, 110), (panel_x, panel_y, panel_width, panel_height), 3, border_radius=15)
        
        # Title
        title = self.font_manager.large.render("Split Cards Game - Instructions", True, (240, 230, 220))
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, panel_y + 40))
        self.screen.blit(title, title_rect)
        
        # Close hint
        close_hint = self.font_manager.small.render("Click anywhere or press ESC/I to close", True, (200, 190, 170))
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
                color = (180, 150, 110)
                y_pos += 10  # Extra space before section
            elif line.strip().startswith("-"):  # Bullet points
                line = "  • " + line[1:].strip()
                font = self.font_manager.small
                color = (220, 210, 200)
            else:  # Regular text
                font = self.font_manager.small
                color = (200, 190, 180)
            
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
    def run(self):
        """Run the main game loop"""
        self.running = True
        while self.running:
            if not self.handle_events():
                break
            
            self.update()
            self.draw()
            self.clock.tick(CARD_GAME_FPS)