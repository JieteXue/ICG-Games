"""
Card Nim Game UI Components
"""

import pygame
from utils.constants import *
from utils.helpers import wrap_text
from ui.components.input_box import InputBox
from ui.components.scrollables import ScrollablePanel
from ui.components.scrollables import ScrollablePanel

class CardNimUI:
    """Handles all UI rendering for Card Nim game"""
    
    def __init__(self, screen, font_manager):
        self.screen = screen
        self.font_manager = font_manager
        self.input_box = None
        self.count_rect = None
        self.is_hint_tooltip_visible = False
        self.hint_tooltip_text = ""
        self.hint_tooltip_pos = (0, 0)
        
        self.hint_window_visible = False
        self.hint_scrollable_panel = None
        self.hint_close_button = None
        self.hint_window_rect = None
        self.input_box = None
        self.count_rect = None
        self.is_hint_tooltip_visible = False
        self.hint_tooltip_text = ""
        self.hint_tooltip_pos = (0, 0)

        self.hint_window_visible = False
        self.hint_scrollable_panel = None
        self.hint_close_button = None
        self.hint_window_rect = None
    
    def draw_background(self):
        """Draw the background with gradient effect"""
        self.screen.fill(BACKGROUND_COLOR)

        sidebar_width = SIDEBAR_WIDTH

        for x in range(sidebar_width, SCREEN_WIDTH, 40):
            pygame.draw.line(self.screen, (35, 45, 55), (x, 0), (x, SCREEN_HEIGHT), 1)
        for y in range(0, SCREEN_HEIGHT, 40):
            pygame.draw.line(self.screen, (35, 45, 55), (sidebar_width, y), (SCREEN_WIDTH, y), 1)
    
    def draw_game_info(self, game_logic):
        """Draw game information panel with enhanced styling"""
        # Draw header background
        header_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 180)
        pygame.draw.rect(self.screen, (35, 45, 60), header_rect)
        pygame.draw.line(self.screen, ACCENT_COLOR, (0, 180), (SCREEN_WIDTH, 180), 3)
        
        # Game title with shadow
        title = self.font_manager.large.render("Card Taking Game", True, TEXT_COLOR)
        title_shadow = self.font_manager.large.render("Card Taking Game", True, SHADOW_COLOR)
        self.screen.blit(title_shadow, (SCREEN_WIDTH//2 - title.get_width()//2 + 2, 15))
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 13))
        
        # Game mode and difficulty info
        difficulty_names = ["Easy", "Normal", "Hard", "Insane"]
        position_count = len(game_logic.positions)
        
        if game_logic.game_mode == "PVP":
            mode_text = "Mode: Player vs Player"
        else:
            mode_text = f"Mode: Player vs AI - {difficulty_names[game_logic.difficulty-1]}"
        
        mode_info = self.font_manager.small.render(
            f"{mode_text} | Positions: {position_count}", 
            True, ACCENT_COLOR)
        self.screen.blit(mode_info, (20, 120))
        
        # Current player info with highlight
        player_colors = {
            "Player 1": WIN_COLOR,
            "Player 2": (255, 200, 50),  # Yellow for Player 2
            "AI": LOSE_COLOR
        }
        player_color = player_colors.get(game_logic.current_player, TEXT_COLOR)
        
        player_text = self.font_manager.small.render(
            f"Current Player: {game_logic.current_player}", 
            True, player_color
        )
        
        # Draw player info with background
        player_bg = pygame.Rect(SCREEN_WIDTH - player_text.get_width() - 40, 135, 
                              player_text.get_width() + 20, player_text.get_height() + 10)
        pygame.draw.rect(self.screen, (40, 50, 65), player_bg, border_radius=8)
        pygame.draw.rect(self.screen, player_color, player_bg, 2, border_radius=8)
        self.screen.blit(player_text, (SCREEN_WIDTH - player_text.get_width() - 30, 140))
        
        # Current message with background - with text wrapping
        message_color = (WIN_COLOR if game_logic.game_over and game_logic.winner == "Player 1" 
                        else LOSE_COLOR if game_logic.game_over and game_logic.winner == "AI"
                        else (255, 200, 50) if game_logic.game_over and game_logic.winner == "Player 2"
                        else TEXT_COLOR)
        
        # Handle long messages with text wrapping
        message_lines = wrap_text(game_logic.message, self.font_manager.medium, SCREEN_WIDTH - 100)
        for i, line in enumerate(message_lines):
            message_text = self.font_manager.medium.render(line, True, message_color)
            message_bg_width = message_text.get_width() + 30
            message_bg = pygame.Rect(SCREEN_WIDTH//2 - message_bg_width//2, 85 + i * 25, 
                                   message_bg_width, message_text.get_height() + 6)
            
            # Only show background on first line
            if i == 0:
                pygame.draw.rect(self.screen, (40, 50, 65), message_bg, border_radius=8)
                pygame.draw.rect(self.screen, ACCENT_COLOR, message_bg, 2, border_radius=8)
            
            self.screen.blit(message_text, (SCREEN_WIDTH//2 - message_text.get_width()//2, 88 + i * 25))
        
        # Current selection info
        if game_logic.selected_position_index is not None:
            select_info = self.font_manager.small.render(
                f"Selected: Position {game_logic.selected_position_index + 1}, Count: {game_logic.selected_count}", 
                True, ACCENT_COLOR)
            self.screen.blit(select_info, (SCREEN_WIDTH//2 - select_info.get_width()//2, 130))
        
        # Game state indicator (winning/losing position)
        if not game_logic.game_over:
            game_state = "Winning Position" if game_logic.judge_win() else "Losing Position"
            state_color = WIN_COLOR if game_logic.judge_win() else LOSE_COLOR
            state_text = self.font_manager.small.render(game_state, True, state_color)
            
            state_bg = pygame.Rect(SCREEN_WIDTH//2 - state_text.get_width()//2 - 10, 155, 
                                 state_text.get_width() + 20, state_text.get_height() + 6)
            pygame.draw.rect(self.screen, (40, 50, 65), state_bg, border_radius=6)
            pygame.draw.rect(self.screen, state_color, state_bg, 2, border_radius=6)
            self.screen.blit(state_text, (SCREEN_WIDTH//2 - state_text.get_width()//2, 158))
    
    def draw_card_positions(self, positions, selected_position_index):
        """Draw all card positions and return their clickable rectangles"""
        if not positions:
            return []
        
        total_positions = len(positions)
        start_x = (SCREEN_WIDTH - (total_positions * (CARD_WIDTH + MARGIN))) // 2
        position_rects = []
        
        # Adjust vertical position for card stacks
        y = POSITION_HEIGHT + 20
        
        for i, count in enumerate(positions):
            x = start_x + i * (CARD_WIDTH + MARGIN) + CARD_WIDTH // 2
            
            # 内联绘制卡片位置
            self._draw_single_card_position(x, y, i, count, i == selected_position_index)
            
            # 存储点击区域
            card_rect = pygame.Rect(x - CARD_WIDTH//2 - 10, y - CARD_HEIGHT - 10, 
                                  CARD_WIDTH + 20, CARD_HEIGHT + 80)
            position_rects.append(card_rect)
        
        return position_rects
    
    def _draw_single_card_position(self, x, y, index, count, selected):
        """绘制单个卡片位置"""
        # Draw position base with shadow
        base_rect = pygame.Rect(x - CARD_WIDTH//2, y + 20, CARD_WIDTH, 20)
        shadow_rect = base_rect.move(3, 3)
        pygame.draw.rect(self.screen, SHADOW_COLOR, shadow_rect, border_radius=6)
        pygame.draw.rect(self.screen, POSITION_COLOR, base_rect, border_radius=6)
        
        # Draw card stack
        if count > 0:
            max_visible = min(count, 10)
            
            for i in range(max_visible):
                card_y = y - i * 4
                card_rect = pygame.Rect(x - CARD_WIDTH//2, card_y - CARD_HEIGHT, CARD_WIDTH, CARD_HEIGHT)
                
                # Draw card shadow
                shadow_rect = card_rect.move(2, 2)
                pygame.draw.rect(self.screen, SHADOW_COLOR, shadow_rect, border_radius=10)
                
                # Draw card
                color = HIGHLIGHT_COLOR if selected else CARD_COLOR
                pygame.draw.rect(self.screen, color, card_rect, border_radius=10)
                
                # Draw card border
                border_color = (255, 200, 50) if selected else CARD_BORDER_COLOR
                pygame.draw.rect(self.screen, border_color, card_rect, 3, border_radius=10)
            
            # Display card count with background
            count_text = self.font_manager.medium.render(str(count), True, TEXT_COLOR)
            count_bg = pygame.Rect(x - 20, y - CARD_HEIGHT//2 - 15, 40, 30)
            pygame.draw.rect(self.screen, SHADOW_COLOR, count_bg.move(2, 2), border_radius=8)
            pygame.draw.rect(self.screen, (40, 60, 80), count_bg, border_radius=8)
            pygame.draw.rect(self.screen, ACCENT_COLOR, count_bg, 2, border_radius=8)
            self.screen.blit(count_text, (x - count_text.get_width()//2, y - CARD_HEIGHT//2 - count_text.get_height()//2))
        
        # Draw position number with background
        pos_text = self.font_manager.small.render(f"Pos {index + 1}", True, TEXT_COLOR)
        pos_bg = pygame.Rect(x - pos_text.get_width()//2 - 6, y + 45,
                            pos_text.get_width() + 12, pos_text.get_height() + 6)
        pygame.draw.rect(self.screen, SHADOW_COLOR, pos_bg.move(2, 2), border_radius=6)
        pygame.draw.rect(self.screen, (40, 60, 80), pos_bg, border_radius=6)
        self.screen.blit(pos_text, (x - pos_text.get_width()//2, y + 48))
    
    def draw_control_panel(self, buttons, selected_count, selected_position_index, game_logic):
        """Draw the control panel with enhanced styling"""
        control_y = POSITION_HEIGHT + 150
        control_width = 400
        control_x = (SCREEN_WIDTH - control_width) // 2
        
        # Draw control panel background
        control_bg = pygame.Rect(control_x - 20, control_y - 20, control_width + 40, 150) 
        pygame.draw.rect(self.screen, (35, 45, 60), control_bg, border_radius=15)
        pygame.draw.rect(self.screen, ACCENT_COLOR, control_bg, 3, border_radius=15)
        
        # 新增：创建输入框（如果不存在）
        if self.input_box is None:
            # 数字显示区域的位置和尺寸
            self.count_rect = pygame.Rect(control_x + control_width//2 - 35, control_y - 5, 70, 60)
            self.input_box = InputBox(
                self.count_rect.x, self.count_rect.y,
                self.count_rect.width, self.count_rect.height,
                self.font_manager,
                initial_value=str(selected_count),
                max_length=3,
                is_numeric=True
            )
        
        # 更新输入框的值
        if not self.input_box.is_active():
            self.input_box.set_value(selected_count)
        
        # 绘制输入框
        self.input_box.draw(self.screen)
        
        # 如果输入框激活，显示提示
        if self.input_box.active:
            hint_text = self.font_manager.small.render("Input number, ENTER to confirm, ESC to cancel", True, (180, 200, 220))
            self.screen.blit(hint_text, (control_x + control_width//2 - hint_text.get_width()//2, control_y + 70))
        
        # 新增：绘制Winning Hints按钮的悬停提示
        if self.is_hint_tooltip_visible and self.hint_tooltip_text:
            self._draw_hint_tooltip()
        
        # 新增：绘制提示窗口（如果可见）
        if self.hint_window_visible:
            self._draw_hint_window()
    def _draw_hint_window(self):
        """绘制提示窗口"""
        if not self.hint_window_visible:
            return
        
        # 定义窗口大小和位置（横向更短，纵向更高）
        window_width = 280  # 横向宽度减小
        window_height = 350  # 纵向高度增加
        window_x = SCREEN_WIDTH - window_width - 20
        window_y = 100
        self.hint_window_rect = pygame.Rect(window_x, window_y, window_width, window_height)
        
        # 绘制窗口背景（带透明度的深色背景）
        overlay = pygame.Surface((window_width, window_height), pygame.SRCALPHA)
        overlay.fill((25, 35, 50, 245))  # 增加透明度
        self.screen.blit(overlay, (window_x, window_y))
        
        # 绘制窗口边框
        pygame.draw.rect(self.screen, (100, 180, 255), self.hint_window_rect, 2, border_radius=10)
        
        # 绘制窗口标题
        title_text = self.font_manager.medium.render("Winning Hint", True, (100, 200, 255))
        title_rect = title_text.get_rect(center=(window_x + window_width//2, window_y + 25))
        self.screen.blit(title_text, title_rect)
        
        # 绘制分隔线
        pygame.draw.line(self.screen, (80, 160, 220),
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
                    color = (255, 100, 100) if self.hovered else (200, 80, 80)
                    pygame.draw.rect(screen, color, self.rect, border_radius=4)
                    pygame.draw.rect(screen, (255, 200, 200), self.rect, 1, border_radius=4)
                    
                    font = pygame.font.SysFont('Arial', 20, bold=True)
                    text_surface = font.render(self.text, True, (255, 255, 255))
                    text_rect = text_surface.get_rect(center=self.rect.center)
                    screen.blit(text_surface, text_rect)
            
            self.hint_close_button = SimpleButton(close_button_rect)
        
        # 绘制关闭按钮
        self.hint_close_button.draw(self.screen)
    
    def draw_hints(self):
        """Draw operation hints separately below control panel"""
        hint_y = POSITION_HEIGHT + 290
        hints = [
            "Click on the number box to input a number, ENTER to confirm, ESC to cancel",
            "Use UP/DOWN arrows to adjust number, ENTER to confirm",
            "Use LEFT/RIGHT arrows to switch between positions", 
            "Click on card stacks to select them"
        ]
        
        for i, hint in enumerate(hints):
            hint_text = self.font_manager.small.render(hint, True, (150, 170, 190))
            self.screen.blit(hint_text, (SCREEN_WIDTH//2 - hint_text.get_width()//2, hint_y + i * 20))
    
    def create_buttons(self):
        """Create all UI buttons for the game"""
        # 使用内联的按钮类，避免导入循环
        class GameButton:
            def __init__(self, x, y, width, height, text, font_manager, icon=None, tooltip=""):
                self.rect = pygame.Rect(x, y, width, height)
                self.text = text
                self.font_manager = font_manager
                self.hovered = False
                self.enabled = True
                self.icon = icon
                self.tooltip = tooltip
                self.corner_radius = 12
            
            def update_hover(self, mouse_pos):
                self.hovered = self.rect.collidepoint(mouse_pos) and self.enabled
            
            def is_clicked(self, event):
                return (event.type == pygame.MOUSEBUTTONDOWN and 
                        event.button == 1 and 
                        self.hovered and 
                        self.enabled)
            
            def draw(self, surface):
                # Draw shadow
                shadow_rect = self.rect.move(4, 4)
                pygame.draw.rect(surface, SHADOW_COLOR, shadow_rect, border_radius=self.corner_radius)
                
                # Draw button
                color = BUTTON_HOVER_COLOR if self.hovered and self.enabled else BUTTON_COLOR
                if not self.enabled:
                    color = (100, 100, 120)
                
                pygame.draw.rect(surface, color, self.rect, border_radius=self.corner_radius)
                
                # Draw border
                border_color = ACCENT_COLOR if self.hovered and self.enabled else (100, 140, 200)
                if not self.enabled:
                    border_color = (80, 80, 100)
                pygame.draw.rect(surface, border_color, self.rect, 3, border_radius=self.corner_radius)
                
                # Draw icon or text
                if self.icon:
                    self._draw_icon(surface)
                else:
                    self._draw_text(surface)
                
                # Draw tooltip on hover
                if self.hovered and self.tooltip:
                    self._draw_tooltip(surface)
                
                # Draw tooltip on hover
                if self.hovered and self.tooltip:
                    self._draw_tooltip(surface)
            
            def _draw_icon(self, surface):
                icon_color = (255, 255, 255) if self.enabled else (150, 150, 150)
                
                if self.icon == 'back':
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
                    refresh_font = pygame.font.SysFont('Arial', 12, bold=True)
                    refresh_text = refresh_font.render("Refresh", True, icon_color)
                    refresh_rect = refresh_text.get_rect(center=self.rect.center)
                    surface.blit(refresh_text, refresh_rect)
                
                elif self.icon == 'info':
                    # Draw info icon (i in a circle)
                    center = (self.rect.centerx, self.rect.centery)
                    radius = 10
                    # Draw circle
                    pygame.draw.circle(surface, icon_color, center, radius, 2)
                    # Draw i
                    font = pygame.font.SysFont('Arial', 16, bold=True)
                    info_text = font.render("i", True, icon_color)
                    text_rect = info_text.get_rect(center=center)
                    surface.blit(info_text, text_rect)
                
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
            
            def _draw_text(self, surface):
                text_color = (255, 255, 255) if self.enabled else (150, 150, 150)
                text_surface = self.font_manager.medium.render(self.text, True, text_color)
                text_rect = text_surface.get_rect(center=self.rect.center)
                
                if self.enabled:
                    shadow_surface = self.font_manager.medium.render(self.text, True, (0, 0, 0, 100))
                    shadow_rect = text_rect.move(2, 2)
                    surface.blit(shadow_surface, shadow_rect)
                
                surface.blit(text_surface, text_rect)
            
            def _draw_tooltip(self, surface):
                tooltip_surface = self.font_manager.small.render(self.tooltip, True, (220, 240, 255))
                tooltip_rect = tooltip_surface.get_rect(midleft=(self.rect.right + 10, self.rect.centery))
                
                # Draw tooltip background
                bg_rect = tooltip_rect.inflate(10, 6)
                pygame.draw.rect(surface, (40, 50, 70), bg_rect, border_radius=4)
                pygame.draw.rect(surface, (100, 150, 200), bg_rect, 1, border_radius=4)
                
                surface.blit(tooltip_surface, tooltip_rect)
            
            def _draw_tooltip(self, surface):
                tooltip_surface = self.font_manager.small.render(self.tooltip, True, (220, 240, 255))
                tooltip_rect = tooltip_surface.get_rect(midleft=(self.rect.right + 10, self.rect.centery))
                
                # Draw tooltip background
                bg_rect = tooltip_rect.inflate(10, 6)
                pygame.draw.rect(surface, (40, 50, 70), bg_rect, border_radius=4)
                pygame.draw.rect(surface, (100, 150, 200), bg_rect, 1, border_radius=4)
                
                surface.blit(tooltip_surface, tooltip_rect)
        
        control_y = POSITION_HEIGHT + 150
        control_width = 400
        control_x = (SCREEN_WIDTH - control_width) // 2
        number_button_width = 80
        number_button_height = 50
        
        # Navigation buttons (top left corner)
        nav_button_size = 50
        
        # 新增：Hint按钮 - 放在控制面板旁边
        hint_button_x = control_x + control_width - 50
        hint_button_y = control_y + 60
        
        buttons = {
            "minus": GameButton(control_x, control_y, number_button_width, number_button_height, "−", self.font_manager, tooltip="Decrease card count"),
            "plus": GameButton(control_x + control_width - number_button_width, control_y, number_button_width, number_button_height, "+", self.font_manager, tooltip="Increase card count"),
            "confirm": GameButton(control_x + 100, control_y + 60, 200, 50, "Confirm Move", self.font_manager, tooltip="Make move with selected cards"),
            "hint": GameButton(hint_button_x, hint_button_y, 50, 50, "", self.font_manager, icon='hint', tooltip="Click for AI hints"),
            "hint": GameButton(hint_button_x, hint_button_y, 50, 50, "", self.font_manager, icon='hint', tooltip="Click for AI hints"),
            "restart": GameButton(SCREEN_WIDTH//2 - 120, POSITION_HEIGHT + 250, 240, 60, "New Game", self.font_manager, tooltip="Start a new game"),
            "back": GameButton(20, 20, nav_button_size, nav_button_size, "", self.font_manager, icon='back', tooltip="Back to mode selection"),
            "home": GameButton(20 + nav_button_size + 10, 20, nav_button_size, nav_button_size, "", self.font_manager, icon='home', tooltip="Back to main menu"),
            "refresh": GameButton(SCREEN_WIDTH - 20 - nav_button_size, 20, nav_button_size, nav_button_size, "", self.font_manager, icon='refresh', tooltip="Restart current game"),
            "info": GameButton(SCREEN_WIDTH - 20 - nav_button_size * 2 - 10, 20, nav_button_size, nav_button_size, "", self.font_manager, icon='info', tooltip="Game instructions (I)")
        }
        
        return buttons
    
    def _draw_hint_tooltip(self):
        """绘制提示工具提示框"""
        if not self.hint_tooltip_text:
            return
        
        # 分割文本为多行
        max_width = 400
        lines = []
        words = self.hint_tooltip_text.split(' ')
        current_line = ""
        
        for word in words:
            test_line = f"{current_line} {word}".strip()
            test_width = self.font_manager.small.size(test_line)[0]
            
            if test_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        # 计算工具提示框的尺寸
        line_height = 20
        padding = 10
        tooltip_width = max_width + 2 * padding
        tooltip_height = len(lines) * line_height + 2 * padding
        
        # 定位工具提示框（确保在屏幕内）
        tooltip_x = self.hint_tooltip_pos[0]
        tooltip_y = self.hint_tooltip_pos[1] - tooltip_height - 10
        
        # 如果超出屏幕顶部，显示在下方
        if tooltip_y < 50:
            tooltip_y = self.hint_tooltip_pos[1] + 10
        
        # 如果超出屏幕右侧，向左偏移
        if tooltip_x + tooltip_width > SCREEN_WIDTH - 20:
            tooltip_x = SCREEN_WIDTH - tooltip_width - 20
        
        # 绘制工具提示框背景
        tooltip_rect = pygame.Rect(tooltip_x, tooltip_y, tooltip_width, tooltip_height)
        pygame.draw.rect(self.screen, (20, 30, 50, 230), tooltip_rect, border_radius=8)
        pygame.draw.rect(self.screen, (100, 180, 255), tooltip_rect, 2, border_radius=8)
        
        # 绘制标题
        title = self.font_manager.medium.render("Winning Hint", True, (100, 200, 255))
        title_x = tooltip_x + (tooltip_width - title.get_width()) // 2
        self.screen.blit(title, (title_x, tooltip_y + padding))
        
        # 绘制分隔线
        pygame.draw.line(self.screen, (80, 160, 220), 
                        (tooltip_x + padding, tooltip_y + padding + title.get_height() + 5),
                        (tooltip_x + tooltip_width - padding, tooltip_y + padding + title.get_height() + 5), 1)
        
        # 绘制文本行
        for i, line in enumerate(lines):
            line_text = self.font_manager.small.render(line, True, (220, 240, 255))
            self.screen.blit(line_text, (tooltip_x + padding, 
                                       tooltip_y + padding + title.get_height() + 10 + i * line_height))
    
    def show_hint_tooltip(self, text, pos):
        """显示提示工具提示"""
        self.is_hint_tooltip_visible = True
        self.hint_tooltip_text = text
        self.hint_tooltip_pos = pos
    
    def hide_hint_tooltip(self):
        """隐藏提示工具提示"""
        self.is_hint_tooltip_visible = False
        self.hint_tooltip_text = ""
    def show_hint_window(self, hint_text):
        """显示提示窗口"""
        # 创建或重置滚动面板
        window_x = SCREEN_WIDTH - 280 - 20  # 与_draw_hint_window保持一致
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
            bg_color=(30, 40, 60, 240)
        )
        
        # 分割文本并添加到面板
        # 首先按换行符分割
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
                            self.hint_scrollable_panel.add_line(current_line, (220, 240, 255), 'small')
                        current_line = word
                
                # 添加最后一行
                if current_line:
                    self.hint_scrollable_panel.add_line(current_line, (220, 240, 255), 'small')
                
                # 段落后添加空行
                self.hint_scrollable_panel.add_spacing(8)
            else:
                # 空段落作为更大间距
                self.hint_scrollable_panel.add_spacing(15)
        
        # 显示窗口
        self.hint_window_visible = True
        self.hide_hint_tooltip()  # 隐藏原来的工具提示
    
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
        # 检查是否需要隐藏提示
        if self.is_hint_tooltip_visible:
            # 如果鼠标移动了，可能需要更新提示位置
            self.hint_tooltip_pos = mouse_pos
        
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