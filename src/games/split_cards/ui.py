"""
Split Cards Game UI Components
"""

import pygame
from ui.buttons import Button
from utils.constants import *
from utils.helpers import wrap_text

class SplitCardsUI:
    """Handles all UI rendering for Split Cards game"""
    
    def __init__(self, screen, font_manager):
        self.screen = screen
        self.font_manager = font_manager
        self.table_color = (210, 180, 140)  # Beige table color
        self.table_rect = pygame.Rect(50, 150, SCREEN_WIDTH - 100, 400)
    
    def draw_background(self):
        """Draw the background with table"""
        # Draw dark background
        self.screen.fill((30, 25, 20))
        
        # Draw table shadow
        shadow_rect = self.table_rect.move(8, 8)
        pygame.draw.rect(self.screen, (20, 15, 10), shadow_rect, border_radius=20)

        # Draw wooden table
        pygame.draw.rect(self.screen, self.table_color, self.table_rect, border_radius=20)
        
        # Draw table texture (wood grain)
        for y in range(self.table_rect.top, self.table_rect.bottom, 4):
            pygame.draw.line(self.screen, 
                            (200, 170, 130), 
                            (self.table_rect.left, y), 
                            (self.table_rect.right, y), 
                            1)
        
        # Draw table edge
        pygame.draw.rect(self.screen, (180, 150, 110), self.table_rect, 5, border_radius=20)
    
    def draw_game_info(self, game_logic):
        """Draw game information panel"""
        # Draw header
        header_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 120)
        pygame.draw.rect(self.screen, (40, 35, 30), header_rect)
        pygame.draw.line(self.screen, (180, 150, 110), (0, 120), (SCREEN_WIDTH, 120), 3)
        
        # Game title
        title = self.font_manager.large.render("Split Cards", True, (240, 230, 220))
        title_shadow = self.font_manager.large.render("Split Cards", True, (20, 15, 10))
        self.screen.blit(title_shadow, (SCREEN_WIDTH//2 - title.get_width()//2 + 2, 15))
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 13))
        
        # Game rules
        rules = "Take 1-{} cards from a pile, or split a pile into two non-empty piles".format(game_logic.max_take)
        rules_text = self.font_manager.small.render(rules, True, (200, 190, 170))
        self.screen.blit(rules_text, (SCREEN_WIDTH//2 - rules_text.get_width()//2, 50))
        
        # Game mode and difficulty
        if game_logic.game_mode == "PVP":
            mode_text = "Mode: Player vs Player"
        else:
            difficulty_names = ["Easy", "Normal", "Hard", "Insane"]
            mode_text = f"Mode: Player vs AI - {difficulty_names[game_logic.difficulty-1]}"
        
        mode_info = self.font_manager.small.render(mode_text, True, (180, 150, 110))
        self.screen.blit(mode_info, (20, 85))
        
        # Current player
        player_colors = {
            "Player 1": (100, 200, 100),
            "Player 2": (255, 200, 50),
            "AI": (220, 100, 100)
        }
        player_color = player_colors.get(game_logic.current_player, (240, 230, 220))
        
        player_text = self.font_manager.medium.render(
            f"Current Player: {game_logic.current_player}", 
            True, player_color
        )
        
        player_bg = pygame.Rect(SCREEN_WIDTH - player_text.get_width() - 40, 75, 
                              player_text.get_width() + 20, player_text.get_height() + 10)
        pygame.draw.rect(self.screen, (50, 45, 40), player_bg, border_radius=8)
        pygame.draw.rect(self.screen, player_color, player_bg, 2, border_radius=8)
        self.screen.blit(player_text, (SCREEN_WIDTH - player_text.get_width() - 30, 80))
        
        # Game message
        message_color = (100, 200, 100) if game_logic.game_over and game_logic.winner == "Player 1" \
                        else (220, 100, 100) if game_logic.game_over and (game_logic.winner == "AI" or game_logic.winner == "Player 2") \
                        else (240, 230, 220)
        
        message_lines = wrap_text(game_logic.message, self.font_manager.medium, SCREEN_WIDTH - 100)
        for i, line in enumerate(message_lines):
            message_text = self.font_manager.medium.render(line, True, message_color)
            if i == 0:
                message_bg_width = message_text.get_width() + 30
                message_bg = pygame.Rect(SCREEN_WIDTH//2 - message_bg_width//2, 105, 
                                       message_bg_width, message_text.get_height() + 6)
                pygame.draw.rect(self.screen, (50, 45, 40), message_bg, border_radius=8)
                pygame.draw.rect(self.screen, (180, 150, 110), message_bg, 2, border_radius=8)
            self.screen.blit(message_text, (SCREEN_WIDTH//2 - message_text.get_width()//2, 108 + i * 25))
    
    def draw_card_piles(self, card_piles, selected_index, selected_action):
        """Draw all card piles on the table"""
        if not card_piles:
            return []
        
        pile_rects = []
        num_piles = len(card_piles)
        
        # Calculate pile positions
        pile_width = 100
        pile_height = 150
        spacing = 30
        
        # Adjust layout based on number of piles
        if num_piles <= 5:
            # Single row
            total_width = num_piles * pile_width + (num_piles - 1) * spacing
            start_x = self.table_rect.centerx - total_width // 2
            y = self.table_rect.centery - pile_height // 2
            
            for i, pile_count in enumerate(card_piles):
                x = start_x + i * (pile_width + spacing)
                pile_rect = self.draw_pile(x, y, pile_width, pile_height, pile_count, 
                                          i, selected_index, selected_action)
                pile_rects.append(pile_rect)
        else:
            # Two rows - 修复重叠问题
            row1_count = (num_piles + 1) // 2
            row2_count = num_piles - row1_count
            
            # Row 1
            total_width = row1_count * pile_width + (row1_count - 1) * spacing
            start_x = self.table_rect.centerx - total_width // 2
            y1 = self.table_rect.centery - pile_height - 40  # 增加间距
            
            for i in range(row1_count):
                x = start_x + i * (pile_width + spacing)
                pile_rect = self.draw_pile(x, y1, pile_width, pile_height, 
                                          card_piles[i], i, selected_index, selected_action)
                pile_rects.append(pile_rect)
            
            # Row 2
            total_width = row2_count * pile_width + (row2_count - 1) * spacing
            start_x = self.table_rect.centerx - total_width // 2
            y2 = self.table_rect.centery + 20  # 调整位置
            
            for i in range(row2_count):
                x = start_x + i * (pile_width + spacing)
                pile_idx = row1_count + i
                pile_rect = self.draw_pile(x, y2, pile_width, pile_height, 
                                          card_piles[pile_idx], pile_idx, selected_index, selected_action)
                pile_rects.append(pile_rect)
        
        return pile_rects
    
    def draw_pile(self, x, y, width, height, count, index, selected_index, selected_action):
        """Draw a single card pile"""
        # 增强选中效果：在选中的牌堆周围绘制高亮边框
        if index == selected_index:
            # 绘制一个更大的高亮矩形
            highlight_rect = pygame.Rect(x-8, y-8, width+16, height+16)
            if selected_action == 'take':
                pygame.draw.rect(self.screen, (255, 255, 100), highlight_rect, 4, border_radius=12)
            elif selected_action == 'split':
                pygame.draw.rect(self.screen, (100, 255, 100), highlight_rect, 4, border_radius=12)
            else:
                pygame.draw.rect(self.screen, (255, 200, 50), highlight_rect, 4, border_radius=12)
        
        # Pile background (card stack)
        pile_rect = pygame.Rect(x, y, width, height)
        
        # Draw pile shadow
        shadow_rect = pile_rect.move(2, 2)
        pygame.draw.rect(self.screen, (150, 120, 90), shadow_rect, border_radius=10)
        
        # Draw cards in stack (visual effect)
        card_color = (255, 245, 230)  # Off-white card color
        border_color = (180, 150, 110)  # Wood-like border
        
        if index == selected_index:
            if selected_action == 'take':
                card_color = (255, 255, 200)  # Yellowish for take selection
                border_color = (255, 200, 50)
            elif selected_action == 'split':
                card_color = (200, 255, 200)  # Greenish for split selection
                border_color = (100, 200, 100)
        
        # Draw card stack (multiple cards slightly offset)
        for i in range(min(5, count)):
            offset = i * 3
            card_rect = pygame.Rect(x + offset, y + offset, width, height)
            pygame.draw.rect(self.screen, card_color, card_rect, border_radius=8)
            pygame.draw.rect(self.screen, border_color, card_rect, 2, border_radius=8)
        
        max_offset = min(4, count-1) * 3
        # Draw card count
        count_text = self.font_manager.large.render(str(count), True, (40, 35, 30))
        count_bg = pygame.Rect(x + width//2 - 25+max_offset, y + height//2 - 20+max_offset, 50, 40)
        pygame.draw.rect(self.screen, (255, 245, 230), count_bg, border_radius=8)
        pygame.draw.rect(self.screen, (180, 150, 110), count_bg, 2, border_radius=8)
        self.screen.blit(count_text, (x + width//2 - count_text.get_width()//2+max_offset, 
                                     y + height//2 - count_text.get_height()//2+max_offset))
        
        # Draw pile number background
        pygame.draw.rect(self.screen, (50, 45, 40), 
                         (x+10, y + height + 15, width-10, 30), border_radius=5)
        pygame.draw.rect(self.screen, (180, 150, 110), 
                         (x+10, y + height + 15, width-10, 30), 2, border_radius=5)

        # Draw pile number
        pile_num = self.font_manager.small.render(f"Pile {index + 1}", True, (255, 255, 255))
        self.screen.blit(pile_num, (x + width//2 - pile_num.get_width()//2+5, y + height + 18))

        
        return pile_rect
    
    def draw_control_panel(self, game_logic, buttons):
        """Draw control panel for actions - 动态显示"""
        control_y = self.table_rect.bottom + 40
        control_width = 600
        control_x = (SCREEN_WIDTH - control_width) // 2
        
        # Control panel background (仅在需要时显示)
        should_draw_panel = (game_logic.selected_pile_index is not None or 
                            game_logic.selected_action is not None)
        
        if should_draw_panel:
            control_bg = pygame.Rect(control_x - 20, control_y - 20, control_width + 40, 120)
            pygame.draw.rect(self.screen, (50, 45, 40), control_bg, border_radius=15)
            pygame.draw.rect(self.screen, (180, 150, 110), control_bg, 3, border_radius=15)
            
            # Action type selection
            if game_logic.selected_action is None:
                action_text = self.font_manager.medium.render("Select Action:", True, (240, 230, 220))
                self.screen.blit(action_text, (control_x, control_y))
            
            # 数量显示（当选择了动作时显示）
            if game_logic.selected_action is not None:
                # 在加减按钮中间显示数量
                count_display = str(game_logic.selected_count)
                count_text = self.font_manager.large.render(count_display, True, (240, 230, 220))
                
                # 计算中间位置
                minus_rect = buttons["minus"].rect
                plus_rect = buttons["plus"].rect
                center_x = (minus_rect.x + plus_rect.x) // 2
                
                count_bg = pygame.Rect(center_x - 25, control_y + 95, 50, 40)
                pygame.draw.rect(self.screen, (50, 45, 40), count_bg, border_radius=8)
                pygame.draw.rect(self.screen, (180, 150, 110), count_bg, 2, border_radius=8)
                self.screen.blit(count_text, (center_x - count_text.get_width()//2, 
                                             control_y + 115 - count_text.get_height()//2))
        
        return control_x, control_y
    
    def create_buttons(self):
        """Create all UI buttons for the game"""
        buttons = {}
        
        # Navigation buttons
        nav_button_size = 50
        buttons["back"] = Button(20, 20, nav_button_size, nav_button_size, "", 
                                self.font_manager, icon='back', tooltip="Back to mode selection")
        buttons["home"] = Button(20 + nav_button_size + 10, 20, nav_button_size, nav_button_size, "", 
                                self.font_manager, icon='home', tooltip="Back to main menu")
        buttons["refresh"] = Button(SCREEN_WIDTH - 20 - nav_button_size, 20, nav_button_size, nav_button_size, "", 
                                   self.font_manager, icon='refresh', tooltip="Restart current game")
        
        # Action buttons - 初始设置为不可见
        control_y = self.table_rect.bottom + 40 if hasattr(self, 'table_rect') else 500
        control_width = 600
        control_x = (SCREEN_WIDTH - control_width) // 2
        
        buttons["take_btn"] = Button(control_x, control_y + 60, 180, 50, "Take Cards", 
                                    self.font_manager, tooltip="Take cards from selected pile",
                                    visible=False)
        buttons["split_btn"] = Button(control_x + 200, control_y + 60, 180, 50, "Split Pile", 
                                     self.font_manager, tooltip="Split selected pile into two",
                                     visible=False)
        buttons["confirm_btn"] = Button(control_x + 400, control_y + 60, 180, 50, "Confirm Move", 
                                       self.font_manager, tooltip="Execute selected move",
                                       visible=False)
        
        # Number adjustment buttons - 重新调整位置
        # 减号按钮在左边，加号按钮在右边，中间留出空间显示数字
        number_panel_x = control_x + 200
        buttons["minus"] = Button(number_panel_x, control_y + 60, 50, 40, "−", 
                                 self.font_manager, tooltip="Decrease count",
                                 visible=False)
        buttons["plus"] = Button(number_panel_x + 110, control_y + 60, 50, 40, "+", 
                                self.font_manager, tooltip="Increase count",
                                visible=False)
        
        # New Game / Restart button (游戏结束时显示)
        buttons["new_game"] = Button(SCREEN_WIDTH//2 - 120, control_y + 150, 240, 60, 
                                   "New Game", self.font_manager, 
                                   tooltip="Start a new game", visible=False)
        
        return buttons
    
    def update_button_visibility(self, buttons, game_logic):
        """根据游戏状态更新按钮的可见性"""
        # 导航按钮始终可见
        buttons["back"].visible = True
        buttons["home"].visible = True
        buttons["refresh"].visible = True
        
        if game_logic.game_over:
            # 游戏结束时只显示New Game按钮
            buttons["take_btn"].visible = False
            buttons["split_btn"].visible = False
            buttons["confirm_btn"].visible = False
            buttons["minus"].visible = False
            buttons["plus"].visible = False
            buttons["new_game"].visible = True
            return
        
        # 隐藏New Game按钮
        buttons["new_game"].visible = False
        
        # 检查当前玩家是否可以交互
        can_interact = False
        if game_logic.game_mode == "PVP":
            can_interact = True
        elif game_logic.game_mode == "PVE" and game_logic.current_player == "Player 1":
            can_interact = True
        
        if not can_interact:
            # AI回合或不能交互时，隐藏所有动作按钮
            buttons["take_btn"].visible = False
            buttons["split_btn"].visible = False
            buttons["confirm_btn"].visible = False
            buttons["minus"].visible = False
            buttons["plus"].visible = False
            return
        
        # 玩家可以交互时
        if game_logic.selected_pile_index is None:
            # 没有选择牌堆，隐藏所有动作按钮
            buttons["take_btn"].visible = False
            buttons["split_btn"].visible = False
            buttons["confirm_btn"].visible = False
            buttons["minus"].visible = False
            buttons["plus"].visible = False
        elif game_logic.selected_action is None:
            # 选择了牌堆但未选择动作，显示Take/Split按钮
            buttons["take_btn"].visible = True
            buttons["split_btn"].visible = True
            buttons["confirm_btn"].visible = False
            buttons["minus"].visible = False
            buttons["plus"].visible = False
        else:
            # 选择了动作，显示加减按钮和确认按钮
            buttons["take_btn"].visible = False
            buttons["split_btn"].visible = False
            buttons["confirm_btn"].visible = True
            buttons["minus"].visible = True
            buttons["plus"].visible = True