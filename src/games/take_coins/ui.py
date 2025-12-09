import pygame
import math
from ui.components.buttons import GameButton
from utils.constants import *
from utils.helpers import wrap_text

class TakeCoinsUI:
    """Take Coins UI with dark display for invalid positions"""
    
    def __init__(self, screen, font_manager):
        self.screen = screen
        self.font_manager = font_manager
        self.scroll_offset = 0
        self.visible_positions = 8
    
    def draw_background(self):
        """Draw clean background"""
        self.screen.fill(BACKGROUND_COLOR)
        
        # Subtle grid pattern
        for x in range(0, SCREEN_WIDTH, 50):
            pygame.draw.line(self.screen, (40, 50, 65), (x, 0), (x, SCREEN_HEIGHT), 1)
        for y in range(0, SCREEN_HEIGHT, 50):
            pygame.draw.line(self.screen, (40, 50, 65), (0, y), (SCREEN_WIDTH, y), 1)
    
    def draw_game_info(self, game_logic):
        """Draw game information panel"""
        # Header background
        header_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 180)
        pygame.draw.rect(self.screen, (35, 45, 60), header_rect)
        pygame.draw.line(self.screen, ACCENT_COLOR, (0, 180), (SCREEN_WIDTH, 180), 3)
        
        # Game title
        title = self.font_manager.large.render("Take Coins Game", True, TEXT_COLOR)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 20))
        
        # Game mode info
        difficulty_names = ["Easy", "Normal", "Hard", "Insane"]
        
        if game_logic.game_mode == "PVP":
            mode_text = "Mode: Player vs Player"
        else:
            mode_text = f"Mode: Player vs AI - {difficulty_names[game_logic.difficulty-1]}"
        
        positions_text = f"Positions: {len(game_logic.coins)}"
        mode_info = self.font_manager.small.render(mode_text, True, ACCENT_COLOR)
        positions_info = self.font_manager.small.render(positions_text, True, ACCENT_COLOR)
        
        self.screen.blit(mode_info, (20, 80))
        self.screen.blit(positions_info, (20, 105))
        
        # Current player
        player_colors = {
            "Player 1": WIN_COLOR,
            "Player 2": (255, 200, 50),
            "AI": LOSE_COLOR
        }
        player_color = player_colors.get(game_logic.current_player, TEXT_COLOR)
        
        player_text = self.font_manager.medium.render(
            f"Current Player: {game_logic.current_player}", True, player_color
        )
        self.screen.blit(player_text, (SCREEN_WIDTH - player_text.get_width() - 20, 80))
        
        # Game message
        message_color = (
            WIN_COLOR if game_logic.game_over and game_logic.winner == "Player 1" else
            LOSE_COLOR if game_logic.game_over and game_logic.winner in ["AI", "Player 2"] else
            TEXT_COLOR
        )
        
        message_lines = wrap_text(game_logic.message, self.font_manager.medium, SCREEN_WIDTH - 100)
        for i, line in enumerate(message_lines):
            message_text = self.font_manager.medium.render(line, True, message_color)
            self.screen.blit(message_text, (SCREEN_WIDTH//2 - message_text.get_width()//2, 130 + i * 25))
        
        # Game state indicator
        if not game_logic.game_over:
            game_state = "Winning Position" if game_logic.judge_win() else "Losing Position"
            state_color = WIN_COLOR if game_logic.judge_win() else LOSE_COLOR
            state_text = self.font_manager.small.render(game_state, True, state_color)
            self.screen.blit(state_text, (SCREEN_WIDTH//2 - state_text.get_width()//2, 160))
    
    def draw_coin_stacks(self, game_logic, position_buttons, scroll_buttons):
        """Draw coin stacks with dark display for invalid positions"""
        # Game area background
        game_area = pygame.Rect(50, 200, SCREEN_WIDTH - 100, 250)
        pygame.draw.rect(self.screen, (35, 45, 60), game_area, border_radius=12)
        pygame.draw.rect(self.screen, ACCENT_COLOR, game_area, 3, border_radius=12)
        
        # Title with scroll info
        total_positions = len(game_logic.coins)
        if total_positions > self.visible_positions:
            scroll_info = f" ({self.scroll_offset + 1}-{min(self.scroll_offset + self.visible_positions, total_positions)} of {total_positions})"
        else:
            scroll_info = f" ({total_positions} positions)"
            
        title_text = self.font_manager.medium.render(f"Select a Position to Add Coin:{scroll_info}", True, TEXT_COLOR)
        self.screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, 215))
        
        # Draw scroll buttons if needed
        if total_positions > self.visible_positions:
            for button in scroll_buttons:
                button.draw(self.screen)
        
        # Draw visible position buttons
        for button in position_buttons:
            if (button.position_index >= self.scroll_offset and 
                button.position_index < self.scroll_offset + self.visible_positions):
                visible_index = button.position_index - self.scroll_offset
                self._draw_single_coin_stack(button, visible_index, game_logic)
        
        # Selected position info
        if game_logic.selected_position is not None:
            i = game_logic.selected_position
            if i in game_logic.valid_positions:
                info_text = f"Selected: Position {i} (Add 1 coin, neighbors lose 1 each)"
                result_text = self.font_manager.small.render(info_text, True, HIGHLIGHT_COLOR)
            else:
                info_text = f"Selected: Position {i} (Invalid - cannot move here)"
                result_text = self.font_manager.small.render(info_text, True, LOSE_COLOR)
            self.screen.blit(result_text, (SCREEN_WIDTH//2 - result_text.get_width()//2, 420))
    
    def _draw_single_coin_stack(self, button, visible_index, game_logic):
        """Draw a single coin stack at the correct scroll position"""
        position_width = 80
        spacing = 20
        total_visible_width = self.visible_positions * position_width + (self.visible_positions - 1) * spacing
        start_x = (SCREEN_WIDTH - total_visible_width) // 2
        base_y = 350
        
        x = start_x + visible_index * (position_width + spacing)
        
        # Position base - 根据是否有效改变颜色
        base_rect = pygame.Rect(x, base_y - 10, position_width, 20)
        
        if button.selected:
            if button.enabled:
                base_color = (80, 100, 120)  # 有效选中的底座
                border_color = HIGHLIGHT_COLOR
            else:
                base_color = (100, 80, 80)   # 无效选中的底座
                border_color = LOSE_COLOR
        elif button.enabled:
            base_color = (60, 80, 100)
            border_color = (100, 140, 200)
        else:
            base_color = (40, 50, 60)
            border_color = (60, 70, 80)
        
        pygame.draw.rect(self.screen, base_color, base_rect, border_radius=6)
        pygame.draw.rect(self.screen, border_color, base_rect, 2, border_radius=6)
        
        # Position number
        if button.selected:
            pos_text_color = HIGHLIGHT_COLOR if button.enabled else LOSE_COLOR
        else:
            pos_text_color = TEXT_COLOR if button.enabled else (100, 110, 120)
        
        pos_text = self.font_manager.small.render(f"Pos {button.position_index}", True, pos_text_color)
        self.screen.blit(pos_text, (x + position_width//2 - pos_text.get_width()//2, base_y - 10))
        
        # Draw coin stack or empty indicator
        self._draw_coin_graphics(x + position_width//2, base_y - 40, button.coin_count,
                               button.enabled, button.selected)
    
    def _draw_coin_graphics(self, x, base_y, coin_count, is_valid, is_selected):
        """Draw coin graphics with dark colors for invalid positions"""
        max_display_coins = 8
        coin_radius = 12
        coin_spacing = 6
        
        if coin_count == 0:
            # 空位置
            empty_circle = pygame.Rect(x - 20, base_y - 20, 40, 40)
            
            if is_selected:
                if is_valid:
                    pygame.draw.ellipse(self.screen, (255, 225, 50, 100), empty_circle)
                    pygame.draw.ellipse(self.screen, HIGHLIGHT_COLOR, empty_circle, 3)
                    empty_text = self.font_manager.small.render("Empty", True, HIGHLIGHT_COLOR)
                else:
                    pygame.draw.ellipse(self.screen, (255, 100, 100, 100), empty_circle)
                    pygame.draw.ellipse(self.screen, LOSE_COLOR, empty_circle, 3)
                    empty_text = self.font_manager.small.render("Empty", True, LOSE_COLOR)
            else:
                if is_valid:
                    pygame.draw.ellipse(self.screen, (80, 80, 100, 100), empty_circle, 2)
                    empty_text = self.font_manager.small.render("Empty", True, (180, 180, 200))
                else:
                    pygame.draw.ellipse(self.screen, (50, 50, 60, 100), empty_circle, 2)
                    empty_text = self.font_manager.small.render("Empty", True, (100, 100, 110))
            
            self.screen.blit(empty_text, (x - empty_text.get_width()//2, base_y - 8))
            return
        
        # 有硬币的位置
        if not is_valid:
            coin_color = (70, 70, 80)
            border_color = (50, 50, 60)
            highlight_color = (90, 90, 100, 100)
        elif is_selected:
            coin_color = (255, 225, 50)
            border_color = (218, 165, 32)
            highlight_color = (255, 255, 255, 150)
        else:
            coin_color = (255, 200, 50)
            border_color = (184, 134, 11)
            highlight_color = (255, 255, 255, 150)
        
        display_count = min(coin_count, max_display_coins)
        for i in range(display_count):
            coin_y = base_y - i * coin_spacing
            
            # 绘制硬币阴影
            shadow_rect = (x - coin_radius + 1, coin_y - coin_radius + 1, 
                         coin_radius * 2, coin_radius * 2)
            pygame.draw.ellipse(self.screen, (0, 0, 0, 100), shadow_rect)
            
            # 绘制硬币
            pygame.draw.circle(self.screen, coin_color, (x, coin_y), coin_radius)
            pygame.draw.circle(self.screen, border_color, (x, coin_y), coin_radius, 2)
            
            # 添加高光
            highlight_pos = (x - coin_radius//2, coin_y - coin_radius//2)
            pygame.draw.circle(self.screen, highlight_color, highlight_pos, coin_radius//3)
        
        # 如果硬币太多，显示数量
        if coin_count > max_display_coins:
            count_color = TEXT_COLOR if is_valid else (100, 100, 110)
            count_text = self.font_manager.small.render(f"+{coin_count - max_display_coins}", 
                                                      True, count_color)
            self.screen.blit(count_text, 
                           (x - count_text.get_width()//2, 
                            base_y - (display_count * coin_spacing) - 15))
        
        # 高亮选中的位置
        if is_selected:
            highlight_height = 60 if coin_count == 0 else 50
            highlight_y = base_y - (display_count * coin_spacing) - 25
            highlight_rect = pygame.Rect(x - 25, highlight_y, 50, highlight_height)
            
            if is_valid:
                pygame.draw.rect(self.screen, HIGHLIGHT_COLOR, highlight_rect, 3, border_radius=8)
            else:
                pygame.draw.rect(self.screen, LOSE_COLOR, highlight_rect, 3, border_radius=8)
    
    def draw_control_panel(self, buttons, game_logic):
        """Draw control panel"""
        control_y = 470
        
        # Control panel background
        control_bg = pygame.Rect(SCREEN_WIDTH//2 - 220, control_y, 440, 110)
        pygame.draw.rect(self.screen, (35, 45, 60), control_bg, border_radius=12)
        pygame.draw.rect(self.screen, ACCENT_COLOR, control_bg, 3, border_radius=12)
        
        # Selected position display
        if game_logic.selected_position is not None:
            pos_display = f"Position {game_logic.selected_position}"
            if game_logic.selected_position in game_logic.valid_positions:
                status = "✓ Valid Move"
                status_color = WIN_COLOR
            else:
                status = "✗ Invalid Move"
                status_color = LOSE_COLOR
        else:
            pos_display = "No position selected"
            status = "Select a position"
            status_color = TEXT_COLOR
        
        pos_text = self.font_manager.medium.render(pos_display, True, TEXT_COLOR)
        status_text = self.font_manager.small.render(status, True, status_color)
        
        self.screen.blit(pos_text, (SCREEN_WIDTH//2 - pos_text.get_width()//2, control_y + 20))
        self.screen.blit(status_text, (SCREEN_WIDTH//2 - status_text.get_width()//2, control_y + 50))
    
    def draw_hints(self):
        """Draw operation hints"""
        hint_y = 580
        hints = [
            "Click on bright positions to select where to add a coin",
            "Double-click on selected position to make move immediately", 
            "Selected position: +1 coin, neighbors: -1 coin each",
            "Use LEFT/RIGHT arrows to navigate, ENTER to confirm",
            "Use mouse wheel or scroll buttons to view all positions"
        ]

        for i, hint in enumerate(hints):
            hint_text = self.font_manager.small.render(hint, True, (150, 170, 190))
            self.screen.blit(hint_text, (SCREEN_WIDTH//2 - hint_text.get_width()//2, hint_y + i * 20))
    
    def create_buttons(self):
        """Create UI buttons"""
        control_y = 370
        control_width = 400
        control_x = (SCREEN_WIDTH - control_width) // 2
        number_button_width = 80
        number_button_height = 50
        nav_button_size = 50
        
        buttons = {
            "confirm": GameButton(SCREEN_WIDTH//2 - 100, 520, 200, 45, "Confirm Move", 
                            self.font_manager, tooltip="Make move at selected position"),
            "restart": GameButton(SCREEN_WIDTH//2 - 80, 620, 160, 45, "New Game", 
                            self.font_manager, tooltip="Start a new game"),
            "back": GameButton(20, 20, 45, 45, "", self.font_manager, icon='back', 
                          tooltip="Back to mode selection"),
            "home": GameButton(75, 20, 45, 45, "", self.font_manager, icon='home', 
                          tooltip="Back to main menu"),
            "refresh": GameButton(SCREEN_WIDTH - 20 - nav_button_size, 20, nav_button_size, nav_button_size, "", self.font_manager, icon='refresh', tooltip="Restart current game")
        }
        
        return buttons
    
    def create_position_buttons(self, coins, valid_positions, selected_position):
        """Create position selection buttons for all positions"""
        buttons = []
        
        for i, coin_count in enumerate(coins):
            # 创建一个简单的按钮对象用于绘制
            button = type('PositionButton', (), {})()
            button.position_index = i
            button.enabled = (i in valid_positions)
            button.selected = (i == selected_position)
            button.coin_count = coin_count
            buttons.append(button)
        
        return buttons
    
    def create_scroll_buttons(self, total_positions):
        """Create scroll buttons for position navigation"""
        buttons = []
        
        if total_positions > self.visible_positions:
            # Left scroll button
            left_button = ScrollButton(80, 260, 40, 40, "<", self.font_manager)
            left_button.enabled = (self.scroll_offset > 0)
            buttons.append(left_button)
            
            # Right scroll button
            right_button = ScrollButton(SCREEN_WIDTH - 120, 260, 40, 40, ">", self.font_manager)
            right_button.enabled = (self.scroll_offset + self.visible_positions < total_positions)
            buttons.append(right_button)
        
        return buttons
    
    def scroll_left(self, total_positions):
        """Scroll positions to the left"""
        if self.scroll_offset > 0:
            self.scroll_offset -= 1
    
    def scroll_right(self, total_positions):
        """Scroll positions to the right"""
        if self.scroll_offset + self.visible_positions < total_positions:
            self.scroll_offset += 1
    
    def handle_mouse_wheel(self, event, total_positions):
        """Handle mouse wheel scrolling"""
        if event.type == pygame.MOUSEWHEEL:
            if event.y > 0:
                self.scroll_left(total_positions)
            elif event.y < 0:
                self.scroll_right(total_positions)
            return True
        return False

class ScrollButton:
    """Button for scrolling through positions"""
    
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
            color = (80, 80, 100)
        
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        
        # Draw border
        border_color = ACCENT_COLOR if self.hovered and self.enabled else (100, 140, 200)
        if not self.enabled:
            border_color = (60, 60, 80)
        pygame.draw.rect(surface, border_color, self.rect, 2, border_radius=8)
        
        # Draw arrow
        arrow_color = (255, 255, 255) if self.enabled else (150, 150, 150)
        arrow_font = pygame.font.SysFont('Arial', 20, bold=True)
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