import pygame
import math
from ui.components.buttons import GameButton
from utils.constants import *
from utils.helpers import wrap_text
from ui.components.scrollables import ScrollablePanel

class TakeCoinsUI:
    """Take Coins UI with dark display for invalid positions and hint support"""
    
    def __init__(self, screen, font_manager):
        self.screen = screen
        self.font_manager = font_manager
        self.scroll_offset = 0
        self.visible_positions = 8
        
        # Hint system variables
        self.is_hint_tooltip_visible = False
        self.hint_tooltip_text = ""
        self.hint_tooltip_pos = (0, 0)
        
        self.hint_window_visible = False
        self.hint_scrollable_panel = None
        self.hint_close_button = None
        self.hint_window_rect = None
    
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
        
        # Winning hints indicator
        if hasattr(game_logic, 'winning_hints_enabled') and game_logic.winning_hints_enabled:
            hint_indicator = self.font_manager.small.render("Winning Hints: ON", True, (100, 200, 255))
            self.screen.blit(hint_indicator, (SCREEN_WIDTH - hint_indicator.get_width() - 20, 105))
    
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
        
        # Draw hint tooltip if visible
        if self.is_hint_tooltip_visible and self.hint_tooltip_text:
            self._draw_hint_tooltip()
    
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
        
        # Draw hint window if visible
        if self.hint_window_visible:
            self._draw_hint_window()
    
    def draw_hints(self):
        """Draw operation hints"""
        hint_y = 580
        hints = [
            "Click on bright positions to select where to add a coin",
            "Double-click on selected position to make move immediately", 
            "Selected position: +1 coin, neighbors: -1 coin each",
            "Use LEFT/RIGHT arrows to navigate, ENTER to confirm",
            "Use mouse wheel or scroll buttons to view all positions",
            "Press H for quick hint (if Winning Hints enabled)"
        ]

        for i, hint in enumerate(hints):
            hint_text = self.font_manager.small.render(hint, True, (150, 170, 190))
            self.screen.blit(hint_text, (SCREEN_WIDTH//2 - hint_text.get_width()//2, hint_y + i * 20))
    
    def create_buttons(self):
        """Create UI buttons with hint button"""
        control_y = 370
        control_width = 400
        control_x = (SCREEN_WIDTH - control_width) // 2
        number_button_width = 80
        number_button_height = 50
        nav_button_size = 50
        
        # Hint button position
        hint_button_x = control_x + control_width - 50
        hint_button_y = control_y + 145
        
        buttons = {
            "confirm": GameButton(SCREEN_WIDTH//2 - 100, 520, 200, 45, "Confirm Move", 
                            self.font_manager, tooltip="Make move at selected position"),
            "restart": GameButton(SCREEN_WIDTH//2 - 80, 620, 160, 45, "New Game", 
                            self.font_manager, tooltip="Start a new game"),
            "hint": GameButton(hint_button_x, hint_button_y, 50, 50, "", 
                            self.font_manager, icon='hint', tooltip="Click for AI hints and strategy guidance"),
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
    
    # ========== HINT SYSTEM METHODS ==========
    
    def _draw_hint_tooltip(self):
        """Draw hint tooltip box"""
        if not self.hint_tooltip_text:
            return
        
        # Split text into multiple lines
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
        
        # Calculate tooltip dimensions
        line_height = 20
        padding = 10
        tooltip_width = max_width + 2 * padding
        tooltip_height = len(lines) * line_height + 2 * padding
        
        # Position tooltip (ensure within screen)
        tooltip_x = self.hint_tooltip_pos[0]
        tooltip_y = self.hint_tooltip_pos[1] - tooltip_height - 10
        
        # If goes beyond top, show below
        if tooltip_y < 50:
            tooltip_y = self.hint_tooltip_pos[1] + 10
        
        # If goes beyond right edge, shift left
        if tooltip_x + tooltip_width > SCREEN_WIDTH - 20:
            tooltip_x = SCREEN_WIDTH - tooltip_width - 20
        
        # Draw tooltip background
        tooltip_rect = pygame.Rect(tooltip_x, tooltip_y, tooltip_width, tooltip_height)
        pygame.draw.rect(self.screen, (20, 30, 50, 230), tooltip_rect, border_radius=8)
        pygame.draw.rect(self.screen, (100, 180, 255), tooltip_rect, 2, border_radius=8)
        
        # Draw title
        title = self.font_manager.medium.render("Winning Hint", True, (100, 200, 255))
        title_x = tooltip_x + (tooltip_width - title.get_width()) // 2
        self.screen.blit(title, (title_x, tooltip_y + padding))
        
        # Draw separator line
        pygame.draw.line(self.screen, (80, 160, 220), 
                        (tooltip_x + padding, tooltip_y + padding + title.get_height() + 5),
                        (tooltip_x + tooltip_width - padding, tooltip_y + padding + title.get_height() + 5), 1)
        
        # Draw text lines
        for i, line in enumerate(lines):
            line_text = self.font_manager.small.render(line, True, (220, 240, 255))
            self.screen.blit(line_text, (tooltip_x + padding, 
                                       tooltip_y + padding + title.get_height() + 10 + i * line_height))
    
    def show_hint_tooltip(self, text, pos):
        """Show hint tooltip"""
        self.is_hint_tooltip_visible = True
        self.hint_tooltip_text = text
        self.hint_tooltip_pos = pos
    
    def hide_hint_tooltip(self):
        """Hide hint tooltip"""
        self.is_hint_tooltip_visible = False
        self.hint_tooltip_text = ""
    
    def _draw_hint_window(self):
        """Draw hint window"""
        if not self.hint_window_visible:
            return
        
        # Define window size and position
        window_width = 280
        window_height = 350
        window_x = SCREEN_WIDTH - window_width - 20
        window_y = 100
        self.hint_window_rect = pygame.Rect(window_x, window_y, window_width, window_height)
        
        # Draw window background (dark with transparency)
        overlay = pygame.Surface((window_width, window_height), pygame.SRCALPHA)
        overlay.fill((25, 35, 50, 245))
        self.screen.blit(overlay, (window_x, window_y))
        
        # Draw window border
        pygame.draw.rect(self.screen, (100, 180, 255), self.hint_window_rect, 2, border_radius=10)
        
        # Draw window title
        title_text = self.font_manager.medium.render("Winning Hint", True, (100, 200, 255))
        title_rect = title_text.get_rect(center=(window_x + window_width//2, window_y + 25))
        self.screen.blit(title_text, title_rect)
        
        # Draw separator line
        pygame.draw.line(self.screen, (80, 160, 220),
                        (window_x + 10, window_y + 50),
                        (window_x + window_width - 10, window_y + 50), 2)
        
        # Draw scrollable panel (if content exists)
        if self.hint_scrollable_panel:
            self.hint_scrollable_panel.draw(self.screen)
        
        # Draw close button (if not created yet)
        if self.hint_close_button is None:
            close_button_rect = pygame.Rect(
                window_x + window_width - 35,
                window_y + 15,
                25, 25
            )
            
            # Use inline button class
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
        
        # Draw close button
        self.hint_close_button.draw(self.screen)
    
    def show_hint_window(self, hint_text):
        """Show hint window"""
        # Create or reset scroll panel
        window_x = SCREEN_WIDTH - 280 - 20
        window_y = 100
        window_width = 280
        window_height = 350
        
        # Create scrollable panel
        self.hint_scrollable_panel = ScrollablePanel(
            window_x + 5,
            window_y + 55,
            window_width - 10,
            window_height - 65,
            self.font_manager,
            bg_color=(30, 40, 60, 240)
        )
        
        # Split text and add to panel
        paragraphs = hint_text.split('\n')
        
        for para in paragraphs:
            if para.strip():
                words = para.split()
                current_line = ""
                
                for word in words:
                    test_line = f"{current_line} {word}".strip()
                    
                    if self.font_manager.small.size(test_line)[0] < (window_width - 20):
                        current_line = test_line
                    else:
                        if current_line:
                            self.hint_scrollable_panel.add_line(current_line, (220, 240, 255), 'small')
                        current_line = word
                
                if current_line:
                    self.hint_scrollable_panel.add_line(current_line, (220, 240, 255), 'small')
                
                self.hint_scrollable_panel.add_spacing(8)
            else:
                self.hint_scrollable_panel.add_spacing(15)
        
        # Show window
        self.hint_window_visible = True
        self.hide_hint_tooltip()
    
    def close_hint_window(self):
        """Close hint window"""
        self.hint_window_visible = False
        self.hint_scrollable_panel = None
        self.hint_close_button = None
    
    def handle_hint_window_events(self, event, mouse_pos):
        """Handle hint window events"""
        if not self.hint_window_visible:
            return False
        
        # Update close button hover state
        if self.hint_close_button:
            self.hint_close_button.update_hover(mouse_pos)
        
        # Handle mouse clicks
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check if close button clicked
            if self.hint_close_button and self.hint_close_button.hovered:
                self.close_hint_window()
                return True
            
            # Check if clicked outside window (close window)
            if self.hint_window_rect and not self.hint_window_rect.collidepoint(mouse_pos):
                self.close_hint_window()
                return True
        
        # Handle scroll panel events
        if self.hint_scrollable_panel:
            if self.hint_scrollable_panel.handle_event(event):
                return True
        
        # Handle keyboard events
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.close_hint_window()
                return True
        
        return False
    
    def update_hint_tooltip(self, mouse_pos):
        """Update hint tooltip state"""
        # Check if need to hide hint
        if self.is_hint_tooltip_visible:
            self.hint_tooltip_pos = mouse_pos
        
        # Update hint window close button hover state
        if self.hint_window_visible and self.hint_close_button:
            self.hint_close_button.update_hover(mouse_pos)

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