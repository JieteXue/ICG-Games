"""
Subtract Factor Game UI Components
"""

import pygame
from utils.constants import *
from utils.helpers import wrap_text

class SubtractFactorUI:
    """Handles all UI rendering for Subtract Factor game"""
    
    def __init__(self, screen, font_manager):
        self.screen = screen
        self.font_manager = font_manager
        self.scroll_offset = 0  # 滚动偏移量
        self.visible_factor_count = 8  # 可见的因数数量
    
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
        """Draw the control panel"""
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
    
    def draw_hints(self):
        """Draw operation hints"""
        hint_y = 600
        hints = [
            "Use LEFT/RIGHT to select factors, UP/DOWN to scroll",
            "Click on factors or use CONFIRM to make move", 
            "If new value < threshold, you lose immediately!",
            "Use mouse wheel to scroll through factors"
        ]
        
        for i, hint in enumerate(hints):
            hint_text = self.font_manager.small.render(hint, True, (150, 170, 190))
            self.screen.blit(hint_text, (SCREEN_WIDTH//2 - hint_text.get_width()//2, hint_y + i * 20))
    
    def create_buttons(self):
        """Create all UI buttons for the game"""
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
         #   "back": Button(20, 20, nav_button_size, nav_button_size, "", self.font_manager, icon='back', tooltip="Back to mode selection"),
         #   "home": Button(20 + nav_button_size + 10, 20, nav_button_size, nav_button_size, "", self.font_manager, icon='home', tooltip="Back to main menu"),
         #   "refresh": Button(SCREEN_WIDTH - 20 - nav_button_size, 20, nav_button_size, nav_button_size, "", self.font_manager, icon='refresh', tooltip="Restart current game")
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