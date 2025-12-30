"""
Subtract Factor Game UI Components
"""

import pygame
from utils.constants import *
from utils.helpers import wrap_text
from ui.components.scrollables import ScrollablePanel  # 新增导入

class SubtractFactorUI:
    """Handles all UI rendering for Subtract Factor game"""
    
    def __init__(self, screen, font_manager):
        self.screen = screen
        self.font_manager = font_manager
        self.scroll_offset = 0  # 滚动偏移量
        self.visible_factor_count = 8  # 可见的因数数量
        
        # 新增：提示功能属性
        self.is_hint_tooltip_visible = False  # 工具提示可见性
        self.hint_tooltip_text = ""
        self.hint_tooltip_pos = (0, 0)
        
        # 新增：提示窗口属性
        self.hint_window_visible = False
        self.hint_scrollable_panel = None
        self.hint_close_button = None
        self.hint_window_rect = None
    
    def draw_background(self):
        """Draw the background with gradient effect"""
        self.screen.fill(BACKGROUND_COLOR)
        
        for x in range(0, SCREEN_WIDTH, 40):
            pygame.draw.line(self.screen, (35, 45, 55), (x, 0), (x, SCREEN_HEIGHT), 1)
        for y in range(0, SCREEN_HEIGHT, 40):
            pygame.draw.line(self.screen, (35, 45, 55), (0, y), (SCREEN_WIDTH, y), 1)
    
    def draw_game_info(self, game_logic):
        """Draw game information panel"""
        # Draw header background
        header_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 180)
        pygame.draw.rect(self.screen, (35, 45, 60), header_rect)
        pygame.draw.line(self.screen, ACCENT_COLOR, (0, 180), (SCREEN_WIDTH, 180), 3)
        
        # Game title with shadow
        title = self.font_manager.large.render("Subtract Factor Game", True, TEXT_COLOR)
        title_shadow = self.font_manager.large.render("Subtract Factor Game", True, SHADOW_COLOR)
        self.screen.blit(title_shadow, (SCREEN_WIDTH//2 - title.get_width()//2 + 2, 15))
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 13))
        
        # Game mode and parameters info
        difficulty_names = ["Easy", "Normal", "Hard", "Insane"]
        
        if game_logic.game_mode == "PVP":
            mode_text = "Mode: Player vs Player"
        else:
            mode_text = f"Mode: Player vs AI - {difficulty_names[game_logic.difficulty-1]}"
        
        params_text = f"Initial n: {game_logic.initial_n} | Threshold k: {game_logic.threshold_k}"
        mode_info = self.font_manager.small.render(mode_text, True, ACCENT_COLOR)
        params_info = self.font_manager.small.render(params_text, True, ACCENT_COLOR)
        
        self.screen.blit(mode_info, (20, 145))
        
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
        player_bg = pygame.Rect(SCREEN_WIDTH - player_text.get_width() - 40, 143, 
                              player_text.get_width() + 20, player_text.get_height() + 10)
        pygame.draw.rect(self.screen, (40, 50, 65), player_bg, border_radius=8)
        pygame.draw.rect(self.screen, player_color, player_bg, 2, border_radius=8)
        self.screen.blit(player_text, (SCREEN_WIDTH - player_text.get_width() - 30, 148))
        
        # Current value display
        value_text = self.font_manager.large.render(f"Current Value: {game_logic.current_value} | Threshold: {game_logic.threshold_k}", True, HIGHLIGHT_COLOR)
        self.screen.blit(value_text, (SCREEN_WIDTH//2 - value_text.get_width()//2, 60))
        
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
            message_bg = pygame.Rect(SCREEN_WIDTH//2 - message_bg_width//2, 110 + i * 25, 
                                   message_bg_width, message_text.get_height() + 6)
            
            # Only show background on first line
            if i == 0:
                pygame.draw.rect(self.screen, (40, 50, 65), message_bg, border_radius=8)
                pygame.draw.rect(self.screen, ACCENT_COLOR, message_bg, 2, border_radius=8)
            
            self.screen.blit(message_text, (SCREEN_WIDTH//2 - message_text.get_width()//2, 113 + i * 25))
        
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
    
    def draw_factor_selection(self, game_logic, factor_buttons, scroll_buttons):
        """Draw factor selection area with scrolling"""
        if not game_logic.valid_factors:
            return
        
        # Draw selection area background
        selection_y = 200
        selection_height = 150
        selection_bg = pygame.Rect(50, selection_y, SCREEN_WIDTH - 100, selection_height)
        pygame.draw.rect(self.screen, (35, 45, 60), selection_bg, border_radius=15)
        pygame.draw.rect(self.screen, ACCENT_COLOR, selection_bg, 3, border_radius=15)
        
        # Draw title with scroll info
        total_factors = len(game_logic.valid_factors)
        if total_factors > self.visible_factor_count:
            scroll_info = f" ({self.scroll_offset + 1}-{min(self.scroll_offset + self.visible_factor_count, total_factors)} of {total_factors})"
        else:
            scroll_info = f" ({total_factors} factors)"
            
        title_text = self.font_manager.medium.render(f"Select a Factor to Subtract:{scroll_info}", True, TEXT_COLOR)
        self.screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, selection_y + 20))
        
        # Draw scroll buttons if needed
        if total_factors > self.visible_factor_count:
            for button in scroll_buttons:
                button.draw(self.screen)
        
        # Draw visible factor buttons
        visible_factors = game_logic.valid_factors[self.scroll_offset:self.scroll_offset + self.visible_factor_count]
        for button in factor_buttons:
            if button.factor_value in visible_factors:
                button.draw(self.screen)
        
        # Draw selected factor info
        if game_logic.selected_factor > 0:
            result = game_logic.current_value - game_logic.selected_factor
            result_color = LOSE_COLOR if result < game_logic.threshold_k else TEXT_COLOR
            result_status = "LOSE!" if result < game_logic.threshold_k else f"{result}"
            result_text = self.font_manager.small.render(
                f"Selected: {game_logic.selected_factor}    New value: {result_status}", 
                True, result_color
            )
            self.screen.blit(result_text, (SCREEN_WIDTH//2 - result_text.get_width()//2, selection_y + 120))
    
    def draw_control_panel(self, buttons, game_logic):
        """Draw the control panel with hint button"""
        control_y = 370
        control_width = 400
        control_x = (SCREEN_WIDTH - control_width) // 2
        
        # Draw control panel background
        control_bg = pygame.Rect(control_x - 20, control_y + 20, control_width + 40, 170)
        pygame.draw.rect(self.screen, (35, 45, 60), control_bg, border_radius=15)
        pygame.draw.rect(self.screen, ACCENT_COLOR, control_bg, 3, border_radius=15)
        
        # Draw selected factor display
        factor_display = str(game_logic.selected_factor) if game_logic.selected_factor > 0 else "-"
        factor_text = self.font_manager.large.render(factor_display, True, TEXT_COLOR)
        factor_bg = pygame.Rect(control_x + control_width//2 - 35, control_y+40, 70, 60)
        pygame.draw.rect(self.screen, (40, 60, 80), factor_bg, border_radius=12)
        pygame.draw.rect(self.screen, ACCENT_COLOR, factor_bg, 3, border_radius=12)
        self.screen.blit(factor_text, 
                        (control_x + control_width//2 - factor_text.get_width()//2, 
                         control_y + 70 - factor_text.get_height()//2))
        
        # 新增：绘制提示按钮（如果buttons参数提供）
        if buttons and "hint" in buttons:
            hint_button = buttons["hint"]
            # 设置提示按钮位置（在控制面板右侧）
            hint_button.rect = pygame.Rect(
                control_bg.right + 20,
                control_bg.centery - 25,
                50, 50
            )
            hint_button.draw(self.screen)
            
            # 绘制提示按钮的悬停工具提示
            if hint_button.hovered and game_logic.winning_hints_enabled and not self.hint_window_visible:
                self.show_hint_tooltip("Click for winning hints", pygame.mouse.get_pos())
            elif not hint_button.hovered and self.is_hint_tooltip_visible:
                # 如果鼠标不在按钮上，但工具提示仍显示，则隐藏它
                self.hide_hint_tooltip()
        
        # 新增：绘制提示工具提示（如果可见）
        if self.is_hint_tooltip_visible and self.hint_tooltip_text:
            self._draw_hint_tooltip()
        
        # 新增：绘制提示窗口（如果可见）
        if self.hint_window_visible:
            self._draw_hint_window()
    
    def _draw_hint_tooltip(self):
        """绘制提示工具提示框"""
        if not self.hint_tooltip_text:
            return
        
        # 分割文本为多行
        max_width = 200
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
        line_height = 18
        padding = 8
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
        pygame.draw.rect(self.screen, (20, 40, 70, 230), tooltip_rect, border_radius=8)
        pygame.draw.rect(self.screen, (0, 200, 255), tooltip_rect, 2, border_radius=8)
        
        # 绘制文本行
        for i, line in enumerate(lines):
            line_text = self.font_manager.small.render(line, True, (220, 240, 255))
            self.screen.blit(line_text, (tooltip_x + padding, 
                                       tooltip_y + padding + i * line_height))
    
    def _draw_hint_window(self):
        """绘制提示窗口"""
        if not self.hint_window_visible:
            return
        
        # 定义窗口大小和位置
        window_width = 500
        window_height = 400
        window_x = (SCREEN_WIDTH - window_width) // 2
        window_y = (SCREEN_HEIGHT - window_height) // 2
        self.hint_window_rect = pygame.Rect(window_x, window_y, window_width, window_height)
        
        # 绘制窗口背景（带透明度的深色背景）
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        
        # 绘制窗口主体
        pygame.draw.rect(self.screen, (15, 25, 40), self.hint_window_rect, border_radius=12)
        pygame.draw.rect(self.screen, (0, 200, 255), self.hint_window_rect, 3, border_radius=12)
        
        # 绘制窗口标题
        title_text = self.font_manager.large.render("WINNING HINT", True, (0, 255, 220))
        title_rect = title_text.get_rect(center=(window_x + window_width//2, window_y + 30))
        self.screen.blit(title_text, title_rect)
        
        # 绘制分隔线
        pygame.draw.line(self.screen, (0, 180, 220),
                        (window_x + 20, window_y + 60),
                        (window_x + window_width - 20, window_y + 60), 2)
        
        # 绘制可滚动面板（如果内容存在）
        if self.hint_scrollable_panel:
            self.hint_scrollable_panel.draw(self.screen)
        
        # 绘制关闭按钮（如果尚未创建）
        if self.hint_close_button is None:
            close_button_rect = pygame.Rect(
                window_x + window_width - 40,
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
        
        # 绘制关闭提示
        close_hint = self.font_manager.small.render("Press ESC or click X to close", True, (180, 200, 220))
        close_hint_rect = close_hint.get_rect(center=(window_x + window_width//2, window_y + window_height - 20))
        self.screen.blit(close_hint, close_hint_rect)
    
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
        window_width = 500
        window_height = 400
        window_x = (SCREEN_WIDTH - window_width) // 2
        window_y = (SCREEN_HEIGHT - window_height) // 2
        
        # 创建可滚动面板
        self.hint_scrollable_panel = ScrollablePanel(
            window_x + 15,
            window_y + 70,
            window_width - 30,
            window_height - 100,
            self.font_manager,
            bg_color=(25, 35, 55, 240)
        )
        
        # 分割文本并添加到面板
        paragraphs = hint_text.split('\n')
        
        for para in paragraphs:
            if para.strip():
                words = para.split()
                current_line = ""
                
                for word in words:
                    test_line = f"{current_line} {word}".strip()
                    
                    if self.font_manager.small.size(test_line)[0] < (window_width - 40):
                        current_line = test_line
                    else:
                        if current_line:
                            self.hint_scrollable_panel.add_line(current_line, (220, 240, 255), 'small')
                        current_line = word
                
                if current_line:
                    self.hint_scrollable_panel.add_line(current_line, (220, 240, 255), 'small')
                
                self.hint_scrollable_panel.add_spacing(6)
            else:
                self.hint_scrollable_panel.add_spacing(10)
        
        # 显示窗口
        self.hint_window_visible = True
        self.hide_hint_tooltip()
    
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
            if event.key == pygame.K_ESCAPE:
                self.close_hint_window()
                return True
        
        return False
    
    def update_hint_tooltip(self, mouse_pos):
        """更新提示工具提示状态"""
        # 检查是否需要隐藏提示
        if self.is_hint_tooltip_visible:
            # 如果鼠标移动了，可能需要更新提示位置
            self.hint_tooltip_pos = mouse_pos
            
            # 添加：如果提示窗口已经打开，则隐藏工具提示
            if self.hint_window_visible:
                self.hide_hint_tooltip()
    
    def draw_hints(self):
        """Draw operation hints - 更新以包含提示功能信息"""
        hint_y = 600
        hints = [
            "Use LEFT/RIGHT to select factors, UP/DOWN to scroll",
            "Click on factors or use CONFIRM to make move", 
            "If new value < threshold, you lose immediately!",
            "Use mouse wheel to scroll through factors"
        ]
        
        # 如果提示功能开启，添加提示信息
        # 注意：这个函数在游戏逻辑中调用，我们需要从其他地方获取winning_hints_enabled状态
        
        for i, hint in enumerate(hints):
            hint_text = self.font_manager.small.render(hint, True, (150, 170, 190))
            self.screen.blit(hint_text, (SCREEN_WIDTH//2 - hint_text.get_width()//2, hint_y + i * 20))
    
    def create_buttons(self):
        """Create all UI buttons for the game - 添加提示按钮"""
        # 内联的 Button 类
        class Button:
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
                elif self.icon == 'hint':  # 新增：提示图标
                    # 绘制灯泡图标
                    center = (self.rect.centerx, self.rect.centery)
                    
                    # 灯泡主体
                    pygame.draw.circle(surface, (255, 255, 180), center, 15)
                    pygame.draw.circle(surface, (255, 255, 100), center, 15, 2)
                    
                    # 灯泡底部
                    bottom_rect = pygame.Rect(
                        center[0] - 8,
                        center[1] + 10,
                        16, 6
                    )
                    pygame.draw.rect(surface, (200, 180, 100), bottom_rect, border_radius=3)
                    
                    # 问号
                    font = pygame.font.SysFont('Arial', 16, bold=True)
                    q_text = font.render("?", True, (60, 60, 80))
                    text_rect = q_text.get_rect(center=center)
                    surface.blit(q_text, text_rect)
                    
                    # 灯泡光晕效果（如果启用）
                    if self.enabled:
                        for i in range(3):
                            radius = 18 + i * 4
                            alpha = 50 - i * 15
                            s = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
                            pygame.draw.circle(s, (255, 255, 150, alpha), (radius, radius), radius)
                            surface.blit(s, (center[0] - radius, center[1] - radius))
            
            def _draw_text(self, surface):
                text_color = (255, 255, 255) if self.enabled else (150, 150, 150)
                text_surface = self.font_manager.medium.render(self.text, True, text_color)
                text_rect = text_surface.get_rect(center=self.rect.center)
                
                # Text shadow
                if self.enabled:
                    shadow_surface = self.font_manager.medium.render(self.text, True, (0, 0, 0, 100))
                    shadow_rect = text_rect.move(2, 2)
                    surface.blit(shadow_surface, shadow_rect)
                
                surface.blit(text_surface, text_rect)
        
        control_y = 370
        control_width = 400
        control_x = (SCREEN_WIDTH - control_width) // 2
        number_button_width = 80
        number_button_height = 50
        
        # Navigation buttons (top left corner)
        nav_button_size = 50
        
        buttons = {
            "minus": Button(control_x, control_y + 55, number_button_width, number_button_height, "−", self.font_manager, tooltip="Decrease selected factor"),
            "plus": Button(control_x + control_width - number_button_width, control_y + 55, number_button_width, number_button_height, "+", self.font_manager, tooltip="Increase selected factor"),
            "confirm": Button(control_x + 100, control_y + 120, 200, 50, "Confirm Move", self.font_manager, tooltip="Make move with selected factor"),
            "restart": Button(SCREEN_WIDTH//2 - 120, 550, 240, 60, "New Game", self.font_manager, tooltip="Start a new game"),
            # 导航按钮在侧边栏中处理，这里只保留控制按钮
            "hint": Button(0, 0, 50, 50, "", self.font_manager, icon='hint', tooltip="Click for winning hints")  # 新增：提示按钮
        }
        
        return buttons
    
    def create_factor_buttons(self, valid_factors, selected_factor):
        """Create buttons for each valid factor with scrolling support"""
        buttons = []
        button_width = 60
        button_height = 40
        spacing = 10
        
        # 计算可见的因数数量
        visible_count = min(len(valid_factors), self.visible_factor_count)
        
        # 计算起始位置 - 总是居中显示可见的按钮
        total_visible_width = visible_count * (button_width + spacing) - spacing
        start_x = (SCREEN_WIDTH - total_visible_width) // 2
        y_position = 260
        
        # 获取当前可见的因数范围
        visible_factors = valid_factors[self.scroll_offset:self.scroll_offset + self.visible_factor_count]
        
        # 为可见的因数创建按钮
        for i, factor in enumerate(visible_factors):
            x = start_x + i * (button_width + spacing)
            button = FactorButton(x, y_position, button_width, button_height, str(factor), self.font_manager)
            button.factor_value = factor
            button.selected = (factor == selected_factor)
            buttons.append(button)
        
        return buttons
    
    def create_scroll_buttons(self, total_factors):
        """Create scroll buttons for factor navigation"""
        buttons = []
        
        if total_factors > self.visible_factor_count:
            # Left scroll button
            left_button = ScrollButton(80, 260, 40, 40, "<", self.font_manager)
            left_button.enabled = (self.scroll_offset > 0)
            buttons.append(left_button)
            
            # Right scroll button
            right_button = ScrollButton(SCREEN_WIDTH - 120, 260, 40, 40, ">", self.font_manager)
            right_button.enabled = (self.scroll_offset + self.visible_factor_count < total_factors)
            buttons.append(right_button)
        
        return buttons
    
    def scroll_left(self, total_factors):
        """Scroll factors to the left"""
        if self.scroll_offset > 0:
            self.scroll_offset -= 1
    
    def scroll_right(self, total_factors):
        """Scroll factors to the right"""
        if self.scroll_offset + self.visible_factor_count < total_factors:
            self.scroll_offset += 1
    
    def handle_mouse_wheel(self, event, total_factors):
        """Handle mouse wheel scrolling"""
        if event.type == pygame.MOUSEWHEEL:
            if event.y > 0:  # Scroll up/left
                self.scroll_left(total_factors)
            elif event.y < 0:  # Scroll down/right
                self.scroll_right(total_factors)
            return True
        return False

class FactorButton:
    """Specialized button for factor selection"""
    
    def __init__(self, x, y, width, height, text, font_manager):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font_manager = font_manager
        self.hovered = False
        self.selected = False
        self.enabled = True
        self.factor_value = 0
    
    def draw(self, surface):
        """Draw the factor button"""
        # Draw shadow
        shadow_rect = self.rect.move(2, 2)
        pygame.draw.rect(surface, SHADOW_COLOR, shadow_rect, border_radius=8)
        
        # Draw button with different colors based on state
        if self.selected:
            color = HIGHLIGHT_COLOR
        elif self.hovered:
            color = BUTTON_HOVER_COLOR
        else:
            color = BUTTON_COLOR
        
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        
        # Draw border
        border_color = ACCENT_COLOR if self.hovered or self.selected else (100, 140, 200)
        pygame.draw.rect(surface, border_color, self.rect, 2, border_radius=8)
        
        # Draw text
        text_color = (255, 255, 255)
        text_surface = self.font_manager.medium.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        
        # Text shadow
        shadow_surface = self.font_manager.medium.render(self.text, True, (0, 0, 0, 100))
        shadow_rect = text_rect.move(1, 1)
        surface.blit(shadow_surface, shadow_rect)
        
        surface.blit(text_surface, text_rect)
    
    def update_hover(self, mouse_pos):
        """Update hover state"""
        self.hovered = self.rect.collidepoint(mouse_pos) and self.enabled
    
    def is_clicked(self, event):
        """Check if button was clicked"""
        return (event.type == pygame.MOUSEBUTTONDOWN and 
                event.button == 1 and 
                self.hovered and 
                self.enabled)

class ScrollButton:
    """Button for scrolling through factors"""
    
    def __init__(self, x, y, width, height, text, font_manager):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font_manager = font_manager
        self.hovered = False
        self.enabled = True
    
    def draw(self, surface):
        """Draw the scroll button"""
        # Draw shadow
        shadow_rect = self.rect.move(2, 2)
        pygame.draw.rect(surface, SHADOW_COLOR, shadow_rect, border_radius=8)
        
        # Draw button
        color = BUTTON_HOVER_COLOR if self.hovered and self.enabled else BUTTON_COLOR
        if not self.enabled:
            color = (80, 80, 100)  # Disabled color
        
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        
        # Draw border
        border_color = ACCENT_COLOR if self.hovered and self.enabled else (100, 140, 200)
        if not self.enabled:
            border_color = (60, 60, 80)
        pygame.draw.rect(surface, border_color, self.rect, 2, border_radius=8)
        
        # Draw arrow
        arrow_color = (255, 255, 255) if self.enabled else (150, 150, 150)
        arrow_font = pygame.font.SysFont('Arial', 24, bold=True)
        arrow_text = arrow_font.render(self.text, True, arrow_color)
        arrow_rect = arrow_text.get_rect(center=self.rect.center)
        surface.blit(arrow_text, arrow_rect)
    
    def update_hover(self, mouse_pos):
        """Update hover state"""
        self.hovered = self.rect.collidepoint(mouse_pos) and self.enabled
    
    def is_clicked(self, event):
        """Check if button was clicked"""
        return (event.type == pygame.MOUSEBUTTONDOWN and 
                event.button == 1 and 
                self.hovered and 
                self.enabled)