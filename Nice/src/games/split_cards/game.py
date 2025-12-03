"""
Split Cards Game - Main game class
神秘魔术风格的卡牌分割游戏
"""

import pygame
import sys
from core.base_game import BaseGame
from games.split_cards.logic import SplitCardsLogic
from games.split_cards.ui import SplitCardsUI
from ui.menus import GameModeSelector
from ui.buttons import Button  # 添加这行导入
from utils.constants import CARD_GAME_FPS, SCREEN_WIDTH, SCREEN_HEIGHT

class SplitCardsInputHandler:
    """Split Cards游戏输入处理器"""
    
    def __init__(self, game_logic, ui):
        self.game_logic = game_logic
        self.ui = ui
    
    def handle_mouse_click(self, event, card_piles, control_buttons, game_over_buttons=None):
        """处理鼠标点击事件"""
        mouse_pos = pygame.mouse.get_pos()
        
        if self.game_logic.game_over:
            # 游戏结束，只处理重新开始和导航按钮
            if game_over_buttons and "restart" in game_over_buttons:
                if game_over_buttons["restart"].is_clicked(event):
                    self.game_logic.initialize_game(self.game_logic.game_mode, self.game_logic.difficulty)
                    self.ui.reset_selection()
                    return None
        else:
            # 游戏进行中，检查是否可以交互
            can_interact = False
            if self.game_logic.game_mode == "PVP":
                can_interact = True
            elif self.game_logic.game_mode == "PVE" and self.game_logic.current_player == 1:
                can_interact = True
            
            if can_interact:
                # 检查卡牌堆点击
                for card_pile in card_piles:
                    if card_pile.is_clicked(event):
                        self.handle_card_pile_click(card_pile.pile_index)
                        break
                
                # 检查动作按钮点击
                if self.game_logic.selected_pile is not None:
                    self.handle_action_buttons_click(event, mouse_pos)
        
        # 检查控制按钮
        button_result = self.handle_control_buttons_click(event, control_buttons)
        if button_result:
            return button_result
        
        # 检查游戏结束按钮
        if game_over_buttons:
            for button_name, button in game_over_buttons.items():
                if button.is_clicked(event):
                    if button_name == "restart":
                        self.game_logic.initialize_game(self.game_logic.game_mode, self.game_logic.difficulty)
                        self.ui.reset_selection()
                    return None
        
        return None
    
    def handle_card_pile_click(self, pile_index):
        """处理卡牌堆点击"""
        if pile_index < len(self.game_logic.cards):
            # 如果已经选中了同一个牌堆，取消选择
            if self.game_logic.selected_pile == pile_index:
                self.game_logic.set_selection(None, None)
            else:
                # 选择新的牌堆
                self.game_logic.set_selection(pile_index, None)
            
            # 更新UI选择状态
            self.ui.update_selection(self.game_logic)
    
    def handle_action_buttons_click(self, event, mouse_pos):
        """处理动作按钮点击"""
        if self.game_logic.selected_pile is None:
            return
        
        selected_pile_size = self.game_logic.cards[self.game_logic.selected_pile]
        
        # 动作面板位置
        action_panel_y = 400
        
        # 如果没有选择动作类型，检查两个大按钮
        if not self.game_logic.selected_action:
            # 拿牌按钮区域
            take_btn_rect = pygame.Rect(SCREEN_WIDTH//2 - 210, action_panel_y + 50, 180, 60)
            
            # 分割按钮区域
            split_btn_rect = pygame.Rect(SCREEN_WIDTH//2 + 30, action_panel_y + 50, 180, 60)
            
            if take_btn_rect.collidepoint(mouse_pos):
                # 选择拿牌动作
                self.game_logic.set_selection(self.game_logic.selected_pile, 'take', take_count=1)
                self.ui.update_selection(self.game_logic)
                return
            
            if split_btn_rect.collidepoint(mouse_pos) and selected_pile_size >= 2:
                # 选择分割动作
                self.game_logic.set_selection(self.game_logic.selected_pile, 'split', split_point=1)
                self.ui.update_selection(self.game_logic)
                return
        
        # 如果已经选择了拿牌动作
        elif self.game_logic.selected_action == 'take':
            max_take = min(selected_pile_size, self.game_logic.k)
            for i in range(max_take):
                take_count = i + 1
                btn_x = 120 + i * 60
                btn_y = action_panel_y + 80  # take_y + 30, where take_y = action_panel_y + 50
                btn_width = 50
                btn_height = 40
                
                btn_rect = pygame.Rect(btn_x, btn_y, btn_width, btn_height)
                if btn_rect.collidepoint(mouse_pos):
                    self.game_logic.set_selection(self.game_logic.selected_pile, 'take', take_count=take_count)
                    self.ui.update_selection(self.game_logic)
                    return
        
        # 如果已经选择了分割动作
        elif self.game_logic.selected_action == 'split':
            split_y = action_panel_y + 50
            
            # 减少按钮区域
            minus_btn_rect = pygame.Rect(SCREEN_WIDTH//2 - 140, split_y + 70, 80, 50)
            # 增加按钮区域
            plus_btn_rect = pygame.Rect(SCREEN_WIDTH//2 + 60, split_y + 70, 80, 50)
            
            if minus_btn_rect.collidepoint(mouse_pos):
                # 减少分割点
                if self.game_logic.adjust_split_point(-1):
                    self.ui.update_selection(self.game_logic)
                return
            
            if plus_btn_rect.collidepoint(mouse_pos):
                # 增加分割点
                if self.game_logic.adjust_split_point(1):
                    self.ui.update_selection(self.game_logic)
                return
    
    def handle_control_buttons_click(self, event, control_buttons):
        """处理控制按钮点击"""
        for button_name, button in control_buttons.items():
            if button.is_clicked(event):
                if button_name == 'back':
                    return 'back'
                elif button_name == 'home':
                    return 'home'
                elif button_name == 'confirm':
                    self.handle_confirm_action()
                    return None
                elif button_name == 'cancel':
                    self.game_logic.set_selection(None, None)
                    self.ui.update_selection(self.game_logic)
                    return None
        
        return None
    
    def handle_confirm_action(self):
        """确认动作"""
        if self.game_logic.selected_pile is None or self.game_logic.selected_action is None:
            return
        
        move_info = None
        
        if self.game_logic.selected_action == 'take':
            take_count = self.game_logic.get_selection_param('take_count')
            if take_count is None:
                return
                
            move_info = {
                'type': 'take',
                'pile_index': self.game_logic.selected_pile,
                'take_count': take_count,
                'description': f"Take {take_count} card{'s' if take_count > 1 else ''} from pile {self.game_logic.selected_pile + 1}"
            }
        elif self.game_logic.selected_action == 'split':
            split_point = self.game_logic.get_selection_param('split_point')
            if split_point is None:
                split_point = 1  # 默认值
                
            move_info = {
                'type': 'split',
                'pile_index': self.game_logic.selected_pile,
                'split_point': split_point,
                'description': f"Split pile {self.game_logic.selected_pile + 1} into {split_point} and {self.game_logic.cards[self.game_logic.selected_pile] - split_point} cards"
            }
        
        if move_info and self.game_logic.make_move(move_info):
            # 添加魔法效果
            try:
                if self.game_logic.selected_action == 'take':
                    take_count = self.game_logic.get_selection_param('take_count')
                    if take_count:
                        start_x = 120 + (take_count - 1) * 60 + 25
                        start_y = 480 + 20
                        end_x = SCREEN_WIDTH // 2
                        end_y = 100
                        self.ui.add_magic_effect((start_x, start_y), (end_x, end_y), "beam")
                elif self.game_logic.selected_action == 'split':
                    split_point = self.game_logic.get_selection_param('split_point')
                    if split_point:
                        start_x = SCREEN_WIDTH // 2
                        start_y = 500
                        end_x = SCREEN_WIDTH // 2
                        end_y = 150
                        self.ui.add_magic_effect((start_x, start_y), (end_x, end_y), "sparkle")
            except Exception as e:
                print(f"魔法效果创建失败: {e}")
            
            # 重置选择
            self.game_logic.set_selection(None, None)
            self.ui.update_selection(self.game_logic)
    
    def handle_keyboard(self, event):
        """处理键盘事件"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # 取消选择
                self.game_logic.set_selection(None, None)
                self.ui.update_selection(self.game_logic)
            elif event.key == pygame.K_RETURN and self.game_logic.selected_action:
                # 确认动作
                self.handle_confirm_action()
            elif event.key == pygame.K_LEFT and self.game_logic.selected_action == 'split':
                # 减少分割点
                if self.game_logic.adjust_split_point(-1):
                    self.ui.update_selection(self.game_logic)
            elif event.key == pygame.K_RIGHT and self.game_logic.selected_action == 'split':
                # 增加分割点
                if self.game_logic.adjust_split_point(1):
                    self.ui.update_selection(self.game_logic)

class SplitCardsGame(BaseGame):
    """Split Cards游戏实现"""
    
    def __init__(self, screen, font_manager):
        super().__init__(screen, font_manager)
        self.logic = SplitCardsLogic()
        self.ui = SplitCardsUI(screen, font_manager)
        self.input_handler = SplitCardsInputHandler(self.logic, self.ui)
        
        # 确保字体已初始化
        self.font_manager.initialize_fonts()
        
        # 初始化游戏设置
        self.initialize_game_settings()
        
        # 创建UI组件
        self.control_buttons = {}
        self.game_over_buttons = {}
        self.card_piles = []
        self.ai_timer = 0
    
    def initialize_game_settings(self):
        """初始化游戏模式和难度"""
        try:
            # 使用游戏模式选择器
            selector = GameModeSelector(self.screen, self.font_manager)
            game_mode = selector.get_game_mode()
            
            if game_mode == "PVE":
                difficulty = selector.get_difficulty()
                self.logic.initialize_game("PVE", difficulty)
            else:
                self.logic.initialize_game("PVP")
                
        except Exception as e:
            print(f"Error initializing game settings: {e}")
            # 后备初始化
            self.logic.initialize_game("PVE", 2)
    
    def handle_events(self):
        """处理游戏事件"""
        mouse_pos = pygame.mouse.get_pos()
        
        # 更新按钮悬停状态
        for button in self.control_buttons.values():
            button.update_hover(mouse_pos)
        
        for button in self.game_over_buttons.values():
            button.update_hover(mouse_pos)
        
        # 更新卡牌堆悬停状态
        for card_pile in self.card_piles:
            card_pile.update_hover(mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                result = self.input_handler.handle_mouse_click(
                    event, self.card_piles, self.control_buttons, self.game_over_buttons
                )
                if result == "back":
                    # 重新初始化游戏设置
                    self.initialize_game_settings()
                    self.ui.reset_selection()
                    self.game_over_buttons = {}
                elif result == "home":
                    # 返回主菜单
                    return False
            
            elif event.type in [pygame.KEYDOWN, pygame.KEYUP]:
                self.input_handler.handle_keyboard(event)
        
        return True
    
    def update(self):
        """更新游戏状态"""
        # 每次更新都重新创建卡牌堆，确保状态同步
        self.card_piles = self.ui.create_card_piles(self.logic)
        
        # 更新控制按钮
        self.control_buttons = self.ui.draw_control_buttons()
        
        # 如果游戏结束，创建游戏结束按钮
        if self.logic.game_over and not self.game_over_buttons:
            self.game_over_buttons = self.ui.create_game_over_buttons(self.font_manager)
        
        # AI的回合（仅在PvE模式）
        if (self.logic.game_mode == "PVE" and 
            self.logic.current_player == 2 and 
            not self.logic.game_over):
            
            self.ai_timer += 1
            # 添加延迟使AI移动可见
            if self.ai_timer > 45:
                if self.logic.ai_make_move():
                    # 添加AI移动的魔法效果
                    try:
                        self.ui.add_magic_effect(
                            (SCREEN_WIDTH // 2, 100),
                            (SCREEN_WIDTH // 2, 250),
                            "sparkle"
                        )
                    except Exception as e:
                        print(f"AI魔法效果创建失败: {e}")
                self.ai_timer = 0
                self.logic.set_selection(None, None)
                self.ui.update_selection(self.logic)
    
    def draw(self):
        """绘制完整的游戏界面"""
        try:
            # 绘制背景
            self.ui.draw_background()
            
            # 绘制游戏信息
            self.ui.draw_game_info(self.logic)
            
            # 绘制卡牌堆 - 每次都重新获取，确保状态正确
            self.card_piles = self.ui.create_card_piles(self.logic)
            self.ui.draw_card_piles(self.card_piles)
            
            # 绘制魔法效果
            self.ui.draw_magic_effects()
            
            # 绘制动作按钮（如果选中了牌堆）
            if self.logic.selected_pile is not None and not self.logic.game_over:
                self.ui.draw_action_buttons(self.logic)
            
            # 绘制控制按钮
            for button in self.control_buttons.values():
                button.draw(self.screen)
            
            # 绘制操作提示（游戏进行中）
            if not self.logic.game_over:
                self.ui.draw_hints()
            else:
                # 游戏结束，绘制重新开始按钮
                for button in self.game_over_buttons.values():
                    button.draw(self.screen)
            
            pygame.display.flip()
            
        except Exception as e:
            print(f"Error in draw: {e}")
            import traceback
            traceback.print_exc()
    
    def get_game_info(self):
        """返回游戏信息"""
        return {
            'name': 'Magic Cards Split',
            'description': 'Strategic card splitting game with magical theme',
            'current_player': f"Player {self.logic.current_player}" if self.logic.current_player == 1 else "AI",
            'game_over': self.logic.game_over,
            'winner': f"Player {self.logic.winner}" if self.logic.winner else None,
            'total_cards': sum(self.logic.cards),
            'piles_count': len(self.logic.cards),
            'available_moves': len(self.logic.get_available_moves()),
            'winning_position': self.logic.judge_win()
        }
    
    def run(self):
        """运行主游戏循环"""
        self.running = True
        while self.running:
            if not self.handle_events():
                break
            self.update()
            self.draw()
            self.clock.tick(CARD_GAME_FPS)