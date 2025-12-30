"""
Split Cards Game UI Components
"""

import pygame
import math
from utils.constants import *
from utils.helpers import wrap_text
from ui.components.input_box import InputBox  # 新增导入
from ui.components.scrollables import ScrollablePanel  # 新增导入

# 内联Button类定义（避免导入错误）
class Button:
    def __init__(self, x, y, width, height, text, font_manager, icon=None, tooltip=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font_manager = font_manager
        self.hovered = False
        self.enabled = True
        self.visible = True
        self.icon = icon
        self.tooltip = tooltip
        self.corner_radius = 12
    
    def update_hover(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos) and self.enabled and self.visible
    
    def is_clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN and 
                event.button == 1 and 
                self.hovered and 
                self.enabled and
                self.visible)
    
    def draw(self, surface):
        if not self.visible:
            return
            
        # Draw shadow
        shadow_rect = self.rect.move(2, 2)
        pygame.draw.rect(surface, SHADOW_COLOR, shadow_rect, border_radius=self.corner_radius)
        
        # Draw button
        color = BUTTON_HOVER_COLOR_BEIGE if self.hovered and self.enabled else BUTTON_COLOR_BEIGE
        if not self.enabled:
            color = (100, 100, 120)
        
        pygame.draw.rect(surface, color, self.rect, border_radius=self.corner_radius)
        
        # Draw border
        border_color = ACCENT_COLOR if self.hovered and self.enabled else (180, 150, 110)
        if not self.enabled:
            border_color = (80, 80, 100)
        pygame.draw.rect(surface, border_color, self.rect, 3, border_radius=self.corner_radius)
        
        # Draw icon or text
        if self.icon:
            self._draw_icon(surface)
        else:
            self._draw_text(surface)  # 确保这里调用的是 _draw_text
    
    def _draw_icon(self, surface):
        icon_color = (255, 255, 255) if self.enabled else (150, 150, 150)
        
        if self.icon == 'back':
            # Draw back arrow
            pygame.draw.polygon(surface, icon_color, [
                (self.rect.centerx - 8, self.rect.centery),
                (self.rect.centerx + 2, self.rect.centery - 8),
                (self.rect.centerx + 2, self.rect.centery - 4),
                (self.rect.centerx + 8, self.rect.centery - 4),
                (self.rect.centerx + 8, self.rect.centery + 4),
                (self.rect.centerx + 2, self.rect.centery + 4),
                (self.rect.centerx + 2, self.rect.centery + 8)
            ])
        elif self.icon == 'home':
            # Draw home icon
            pygame.draw.polygon(surface, icon_color, [
                (self.rect.centerx, self.rect.centery - 8),
                (self.rect.centerx - 10, self.rect.centery + 2),
                (self.rect.centerx - 6, self.rect.centery + 2),
                (self.rect.centerx - 6, self.rect.centery + 8),
                (self.rect.centerx + 6, self.rect.centery + 8),
                (self.rect.centerx + 6, self.rect.centery + 2),
                (self.rect.centerx + 10, self.rect.centery + 2)
            ])
        elif self.icon == 'refresh':
            # Draw refresh icon as text
            refresh_font = pygame.font.SysFont('Arial', 12, bold=True)
            refresh_text = refresh_font.render("Refresh", True, icon_color)
            refresh_rect = refresh_text.get_rect(center=self.rect.center)
            surface.blit(refresh_text, refresh_rect)
        elif self.icon == 'info':
            # Draw info icon (i)
            info_font = pygame.font.SysFont('Arial', 18, bold=True)
            info_text = info_font.render("i", True, icon_color)
            info_rect = info_text.get_rect(center=self.rect.center)
            surface.blit(info_text, info_rect)
        elif self.icon == 'settings':
            # Draw settings icon (gear)
            center_x, center_y = self.rect.center
            radius = 10
            # Draw gear outer circle
            pygame.draw.circle(surface, icon_color, (center_x, center_y), radius, 2)
            # Draw gear teeth
            for i in range(8):
                angle = i * 45
                rad = math.radians(angle)
                x1 = center_x + (radius - 2) * math.cos(rad)
                y1 = center_y + (radius - 2) * math.sin(rad)
                x2 = center_x + (radius + 4) * math.cos(rad)
                y2 = center_y + (radius + 4) * math.sin(rad)
                pygame.draw.line(surface, icon_color, (x1, y1), (x2, y2), 2)
        elif self.icon == 'hint':
            # Draw hint icon (light bulb)
            center = (self.rect.centerx, self.rect.centery)
            
            # Draw light bulb body
            pygame.draw.circle(surface, (255, 255, 200), center, 12)
            pygame.draw.circle(surface, (255, 255, 100), center, 12, 2)
            
            # Draw light rays
            for angle in range(0, 360, 45):
                rad = angle * 3.14159 / 180
                start_x = center[0] + 12 * pygame.math.Vector2(1, 0).rotate(angle).x
                start_y = center[1] + 12 * pygame.math.Vector2(1, 0).rotate(angle).y
                end_x = center[0] + 20 * pygame.math.Vector2(1, 0).rotate(angle).x
                end_y = center[1] + 20 * pygame.math.Vector2(1, 0).rotate(angle).y
                pygame.draw.line(surface, (255, 255, 150), (start_x, start_y), (end_x, end_y), 2)
            
            # Draw question mark inside
            font = pygame.font.SysFont('Arial', 14, bold=True)
            q_text = font.render("?", True, (50, 50, 50))
            text_rect = q_text.get_rect(center=center)
            surface.blit(q_text, text_rect)
    
    # 添加 _draw_text 方法（之前缺失的方法）
    def _draw_text(self, surface):
        """绘制按钮文本"""
        text_color = (255, 255, 255) if self.enabled else (150, 150, 150)
        text_surface = self.font_manager.medium.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        
        # 文本阴影
        if self.enabled:
            shadow_surface = self.font_manager.medium.render(self.text, True, (0, 0, 0, 100))
            shadow_rect = text_rect.move(2, 2)
            surface.blit(shadow_surface, shadow_rect)
        
        surface.blit(text_surface, text_rect)
    
    # 添加 _draw_tooltip 方法（如果需要工具提示的话）
    def _draw_tooltip(self, surface):
        """绘制按钮工具提示（可选）"""
        if self.hovered and self.tooltip:
            tooltip_surface = self.font_manager.small.render(self.tooltip, True, (220, 240, 255))
            tooltip_rect = tooltip_surface.get_rect(midleft=(self.rect.right + 10, self.rect.centery))
            
            # 绘制工具提示背景
            bg_rect = tooltip_rect.inflate(10, 6)
            pygame.draw.rect(surface, (40, 50, 70), bg_rect, border_radius=4)
            pygame.draw.rect(surface, (100, 150, 200), bg_rect, 1, border_radius=4)
            
            surface.blit(tooltip_surface, tooltip_rect)


class SplitCardsUI:
    """Handles all UI rendering for Split Cards game"""
    
    def __init__(self, screen, font_manager):
        self.screen = screen
        self.font_manager = font_manager
        self.table_color = (210, 180, 140)  # Beige table color
        self.table_rect = pygame.Rect(50, 150, SCREEN_WIDTH - 100, 400)
        self.input_box = None  # 新增：输入框实例
        
        # 新增：hint功能相关属性
        self.is_hint_tooltip_visible = False
        self.hint_tooltip_text = ""
        self.hint_tooltip_pos = (0, 0)
        self.hint_window_visible = False
        self.hint_scrollable_panel = None
        self.hint_close_button = None
        self.hint_window_rect = None
    
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
        
        # 添加状态指示器（必胜/必败）
        if not game_logic.game_over:
            # 计算当前是否为必胜位置
            is_winning = game_logic.is_winning_position()
            position_text = "Winning Position" if is_winning else "Losing Position"
            position_color = (100, 200, 100) if is_winning else (220, 100, 100)
            
            position_display = self.font_manager.small.render(position_text, True, position_color)
            position_bg = pygame.Rect(SCREEN_WIDTH//2 - position_display.get_width()//2 - 10, 92, 
                               position_display.get_width() + 20, position_display.get_height() + 6)
            pygame.draw.rect(self.screen, (50, 45, 40), position_bg, border_radius=8)
            pygame.draw.rect(self.screen, position_color, position_bg, 2, border_radius=8)
            self.screen.blit(position_display, (SCREEN_WIDTH//2 - position_display.get_width()//2, 95))
        
        # Game message
        message_color = (100, 200, 100) if game_logic.game_over and game_logic.winner == "Player 1" \
                        else (220, 100, 100) if game_logic.game_over and (game_logic.winner == "AI" or game_logic.winner == "Player 2") \
                        else (240, 230, 220)
        
        message_lines = wrap_text(game_logic.message, self.font_manager.medium, SCREEN_WIDTH - 100)
        for i, line in enumerate(message_lines):
            message_text = self.font_manager.medium.render(line, True, message_color)
            if i == 0:
                message_bg_width = message_text.get_width() + 30
                message_bg = pygame.Rect(SCREEN_WIDTH//2 - message_bg_width//2, 119, 
                                    message_bg_width, message_text.get_height() + 6)
                pygame.draw.rect(self.screen, (50, 45, 40), message_bg, border_radius=8)
                pygame.draw.rect(self.screen, (180, 150, 110), message_bg, 2, border_radius=8)
            self.screen.blit(message_text, (SCREEN_WIDTH//2 - message_text.get_width()//2, 121 + i * 25))
        
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
            y1 = self.table_rect.centery - pile_height - 40  # 增加间距避免重叠
            
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
            else:
                # 选中但未选择动作时，给牌堆加一个明显的边框
                pygame.draw.rect(self.screen, (255, 200, 50), 
                                (x-6, y-6, width+12, height+12), 4, border_radius=12)
        
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
        
        # 绘制选中箭头（如果这个牌堆被选中）
        if index == selected_index:
            arrow_y = y + height + 50  # 在牌堆编号下方
            arrow_x = x + width // 2
            
            # 根据选择的操作确定箭头颜色
            if selected_action == 'take':
                arrow_color = (255, 200, 50)  # 黄色
            elif selected_action == 'split':
                arrow_color = (100, 200, 100)  # 绿色
            else:
                arrow_color = (255, 255, 0)    # 亮黄色（选中但未选择动作）
            
            # 绘制三角形箭头
            points = [
                (arrow_x, arrow_y - 15),           # 顶点
                (arrow_x - 10, arrow_y ), # 左下角
                (arrow_x + 10, arrow_y )  # 右下角
            ]
            pygame.draw.polygon(self.screen, arrow_color, points)
        
        return pile_rect
    
    def draw_control_panel(self, game_logic, buttons):
        """Draw control panel for actions"""
        control_y = self.table_rect.bottom + 40
        control_width = 600
        control_x = (SCREEN_WIDTH - control_width) // 2
        
        # 新增：绘制提示窗口（如果可见）
        if self.hint_window_visible:
            self._draw_hint_window()
        
        # Control panel background (只在需要时显示)
        if (game_logic.selected_pile_index is not None or 
            (game_logic.game_mode == "PVE" and game_logic.current_player == "Player 1") or
            game_logic.game_mode == "PVP"):
            
            control_bg = pygame.Rect(control_x - 20, control_y - 20, control_width + 40, 120)
            pygame.draw.rect(self.screen, (50, 45, 40), control_bg, border_radius=15)
            pygame.draw.rect(self.screen, (180, 150, 110), control_bg, 3, border_radius=15)
            
            # Action type selection (只在选中牌堆但未选择动作时显示)
            if (game_logic.selected_pile_index is not None and 
                game_logic.selected_action is None):
                
                action_text = self.font_manager.medium.render("Select Action:", True, (240, 230, 220))
                self.screen.blit(action_text, (control_x, control_y))
        
        # 新增：创建或更新输入框
        if game_logic.selected_pile_index is not None and game_logic.selected_action:
            # 数字显示区域的位置和尺寸
            count_bg = pygame.Rect(control_x + 265, control_y -10, 50, 40)
            
            if self.input_box is None:
                # 创建输入框
                self.input_box = InputBox(
                    count_bg.x, count_bg.y,
                    count_bg.width, count_bg.height,
                    self.font_manager,
                    initial_value=str(game_logic.selected_count),
                    max_length=3,
                    is_numeric=True
                )
            else:
                # 更新输入框位置和值
                self.input_box.rect = count_bg
                if not self.input_box.is_active():
                    self.input_box.set_value(game_logic.selected_count)
            
            # 绘制输入框
            self.input_box.draw(self.screen)
            
            # 如果输入框激活，显示提示
            if self.input_box.active:
                hint_text = self.font_manager.small.render("输入数字，回车确认，ESC取消", True, (200, 190, 170))
                self.screen.blit(hint_text, (control_x + 150, control_y + 50))
        
        return control_x, control_y
    
    def create_buttons(self):
        """Create all UI buttons for the game"""
        buttons = {}
        
        # Navigation buttons
        nav_button_size = 50
        
        # 注意：为了与侧边栏一致，我们暂时注释掉这些按钮，因为侧边栏已经包含了
        # buttons["back"] = Button(20, 20, nav_button_size, nav_button_size, "", 
        #                         self.font_manager, icon='back', tooltip="Back to mode selection")
        # buttons["home"] = Button(20 + nav_button_size + 10, 20, nav_button_size, nav_button_size, "", 
        #                         self.font_manager, icon='home', tooltip="Back to main menu")
        # buttons["refresh"] = Button(SCREEN_WIDTH - 20 - nav_button_size, 20, nav_button_size, nav_button_size, "", 
        #                            self.font_manager, icon='refresh', tooltip="Restart current game")
        
        buttons["info"] = Button(SCREEN_WIDTH - 20 - nav_button_size * 2 - 10, 20, nav_button_size, nav_button_size, "", 
                               self.font_manager, icon='info', tooltip="Show instructions")
        buttons["settings"] = Button(SCREEN_WIDTH - 20 - nav_button_size * 3 - 20, 20, nav_button_size, nav_button_size, "", 
                                   self.font_manager, icon='settings', tooltip="Game settings")
        
        # 新增：Hint按钮 - 放在控制面板旁边
        control_y = self.table_rect.bottom + 40 if hasattr(self, 'table_rect') else 500
        control_width = 600
        control_x = (SCREEN_WIDTH - control_width) // 2
        hint_button_x = control_x + control_width - 200
        hint_button_y = control_y - 15
        
        buttons["hint"] = Button(hint_button_x, hint_button_y, 50, 50, "", 
                                self.font_manager, icon='hint', tooltip="Click for winning hints")
        
        # Action buttons
        buttons["take_btn"] = Button(control_x, control_y +40, 180, 50, "Take Cards", 
                                    self.font_manager, tooltip="Take cards from selected pile")
        buttons["split_btn"] = Button(control_x + 200, control_y+40, 180, 50, "Split Pile", 
                                     self.font_manager, tooltip="Split selected pile into two")
        buttons["confirm_btn"] = Button(control_x + 400, control_y + 40, 180, 50, "Confirm Move", 
                                       self.font_manager, tooltip="Execute selected move")
        
        # Number adjustment buttons
        buttons["minus"] = Button(control_x + 200, control_y -10, 50, 40, "−", 
                                 self.font_manager, tooltip="Decrease count")
        buttons["plus"] = Button(control_x + 330, control_y-10, 50, 40, "+", 
                                self.font_manager, tooltip="Increase count")
        
        # Restart button
        buttons["restart"] = Button(SCREEN_WIDTH//2 - 120, control_y + 150, 240, 60, 
                                   "New Game", self.font_manager, tooltip="Start a new game")
        
        return buttons
    
    def _draw_hint_window(self):
        """绘制提示窗口"""
        if not self.hint_window_visible:
            return
        
        # 定义窗口大小和位置
        window_width = 280
        window_height = 350
        window_x = SCREEN_WIDTH - window_width - 20
        window_y = 100
        self.hint_window_rect = pygame.Rect(window_x, window_y, window_width, window_height)
        
        # 绘制窗口背景（带透明度的深色背景）
        overlay = pygame.Surface((window_width, window_height), pygame.SRCALPHA)
        overlay.fill((35, 30, 25, 245))  # 使用与游戏主题一致的颜色
        self.screen.blit(overlay, (window_x, window_y))
        
        # 绘制窗口边框
        pygame.draw.rect(self.screen, (180, 150, 110), self.hint_window_rect, 2, border_radius=10)
        
        # 绘制窗口标题
        title_text = self.font_manager.medium.render("Winning Hint", True, (200, 180, 110))
        title_rect = title_text.get_rect(center=(window_x + window_width//2, window_y + 25))
        self.screen.blit(title_text, title_rect)
        
        # 绘制分隔线
        pygame.draw.line(self.screen, (160, 130, 90),
                        (window_x + 10, window_y + 50),
                        (window_x + window_width - 10, window_y + 50), 2)
        
        # 绘制可滚动面板（如果内容存在）
        if self.hint_scrollable_panel:
            self.hint_scrollable_panel.draw(self.screen)
        
        # 绘制关闭按钮（如果尚未创建）
        if self.hint_close_button is None:
            close_button_rect = pygame.Rect(
                window_x + window_width - 35,
                window_y + 15,
                25, 25
            )
            
            # 使用内联按钮类
            class SimpleButton:
                def __init__(self, rect, text="×"):
                    self.rect = rect
                    self.text = text
                    self.hovered = False
                
                def update_hover(self, mouse_pos):
                    self.hovered = self.rect.collidepoint(mouse_pos)
                
                def draw(self, screen):
                    color = (220, 100, 100) if self.hovered else (180, 80, 80)  # 使用红色系
                    pygame.draw.rect(screen, color, self.rect, border_radius=4)
                    pygame.draw.rect(screen, (255, 200, 200), self.rect, 1, border_radius=4)
                    
                    font = pygame.font.SysFont('Arial', 20, bold=True)
                    text_surface = font.render(self.text, True, (255, 255, 255))
                    text_rect = text_surface.get_rect(center=self.rect.center)
                    screen.blit(text_surface, text_rect)
            
            self.hint_close_button = SimpleButton(close_button_rect)
        
        # 绘制关闭按钮
        self.hint_close_button.draw(self.screen)
    
    def show_hint_window(self, hint_text):
        """显示提示窗口"""
        # 创建或重置滚动面板
        window_x = SCREEN_WIDTH - 280 - 20
        window_y = 100
        window_width = 280
        window_height = 350
        
        # 创建可滚动面板
        self.hint_scrollable_panel = ScrollablePanel(
            window_x + 5,  # 内边距
            window_y + 55,  # 标题栏下面
            window_width - 10,  # 减去内边距
            window_height - 65,  # 减去标题栏和按钮高度
            self.font_manager,
            bg_color=(50, 45, 40, 240)  # 使用游戏主题颜色
        )
        
        # 分割文本并添加到面板
        paragraphs = hint_text.split('\n')
        
        for para in paragraphs:
            if para.strip():  # 非空段落
                # 再按空格分词，然后按面板宽度自动换行
                words = para.split()
                current_line = ""
                
                for word in words:
                    test_line = f"{current_line} {word}".strip()
                    
                    # 检查测试行的宽度是否超过面板宽度（减去边距）
                    if self.font_manager.small.size(test_line)[0] < (window_width - 20):
                        current_line = test_line
                    else:
                        # 如果超过宽度，添加当前行，开始新行
                        if current_line:
                            self.hint_scrollable_panel.add_line(current_line, (220, 210, 200), 'small')
                        current_line = word
                
                # 添加最后一行
                if current_line:
                    self.hint_scrollable_panel.add_line(current_line, (220, 210, 200), 'small')
                
                # 段落后添加空行
                self.hint_scrollable_panel.add_spacing(8)
            else:
                # 空段落作为更大间距
                self.hint_scrollable_panel.add_spacing(15)
        
        # 显示窗口
        self.hint_window_visible = True
    
    def close_hint_window(self):
        """关闭提示窗口"""
        self.hint_window_visible = False
        self.hint_scrollable_panel = None
    
    def handle_hint_window_events(self, event, mouse_pos):
        """处理提示窗口事件"""
        if not self.hint_window_visible:
            return False
        
        # 更新关闭按钮的悬停状态
        if self.hint_close_button:
            self.hint_close_button.update_hover(mouse_pos)
        
        # 处理鼠标点击
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # 检查是否点击了关闭按钮
            if self.hint_close_button and self.hint_close_button.hovered:
                self.close_hint_window()
                return True
            
            # 检查是否点击了窗口外部（关闭窗口）
            if self.hint_window_rect and not self.hint_window_rect.collidepoint(mouse_pos):
                self.close_hint_window()
                return True
        
        # 处理滚动面板事件
        if self.hint_scrollable_panel:
            if self.hint_scrollable_panel.handle_event(event):
                return True
        
        # 处理键盘事件
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:  # ESC键关闭窗口
                self.close_hint_window()
                return True
        
        return False
    
    def update_hint_tooltip(self, mouse_pos):
        """更新提示工具提示状态"""
        # 更新提示窗口的关闭按钮悬停状态
        if self.hint_window_visible and self.hint_close_button:
            self.hint_close_button.update_hover(mouse_pos)
    
    def get_input_box(self):
        """获取输入框实例"""
        return self.input_box
    
    def update_input_box(self):
        """更新输入框状态"""
        if self.input_box:
            self.input_box.update()