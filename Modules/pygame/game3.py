import pygame
import sys
import random
import Select_Mode as Select_Difficulty_inner

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
CARD_WIDTH = 80
CARD_HEIGHT = 120
MARGIN = 20
POSITION_HEIGHT = 350
FPS = 24

# Colors - Enhanced color scheme
BACKGROUND_COLOR = (25, 35, 45)  # Dark blue-gray
CARD_COLOR = (255, 255, 255)
CARD_BORDER_COLOR = (70, 90, 120)
POSITION_COLOR = (60, 80, 100)
TEXT_COLOR = (220, 230, 240)
BUTTON_COLOR = (80, 120, 180)
BUTTON_HOVER_COLOR = (100, 150, 220)
HIGHLIGHT_COLOR = (255, 215, 0)
WIN_COLOR = (100, 200, 100)
LOSE_COLOR = (220, 100, 100)
ACCENT_COLOR = (100, 180, 255)
SHADOW_COLOR = (15, 25, 35)

class FontManager:
    """Manages all fonts in the game"""
    def __init__(self, screen_height):
        self.large = pygame.font.SysFont('Arial', max(28, screen_height // 25), bold=True)
        self.medium = pygame.font.SysFont('Arial', max(18, screen_height // 32))
        self.small = pygame.font.SysFont('Arial', max(14, screen_height // 40))

class Button:
    """Represents a clickable button"""
    def __init__(self, x, y, width, height, text, font_manager):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font_manager = font_manager
        self.hovered = False
        self.enabled = True
    
    def draw(self, surface):
        """Draw the button on the surface with enhanced styling"""
        # Draw shadow
        shadow_rect = self.rect.move(4, 4)
        pygame.draw.rect(surface, SHADOW_COLOR, shadow_rect, border_radius=12)
        
        # Draw button
        color = BUTTON_HOVER_COLOR if self.hovered and self.enabled else BUTTON_COLOR
        if not self.enabled:
            color = (100, 100, 120)  # Disabled color
        
        pygame.draw.rect(surface, color, self.rect, border_radius=12)
        
        # Draw border
        border_color = ACCENT_COLOR if self.hovered and self.enabled else (100, 140, 200)
        if not self.enabled:
            border_color = (80, 80, 100)
        pygame.draw.rect(surface, border_color, self.rect, 3, border_radius=12)
        
        # Draw text with shadow
        text_color = (255, 255, 255) if self.enabled else (150, 150, 150)
        text_surface = self.font_manager.medium.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        
        # Text shadow
        if self.enabled:
            shadow_surface = self.font_manager.medium.render(self.text, True, (0, 0, 0, 100))
            shadow_rect = text_rect.move(2, 2)
            surface.blit(shadow_surface, shadow_rect)
        
        surface.blit(text_surface, text_rect)
    
    def update_hover(self, mouse_pos):
        """Update hover state based on mouse position"""
        self.hovered = self.rect.collidepoint(mouse_pos) and self.enabled
    
    def is_clicked(self, event):
        """Check if button was clicked"""
        return (event.type == pygame.MOUSEBUTTONDOWN and 
                event.button == 1 and 
                self.hovered and 
                self.enabled)

class CardPosition:
    """Represents a card position with a stack of cards"""
    def __init__(self, index, card_count, font_manager):
        self.index = index
        self.card_count = card_count
        self.font_manager = font_manager
        self.rect = None
        self.selected = False
    
    def draw(self, surface, x, y):
        """Draw the card stack at specified position with enhanced visuals"""
        
        # Draw position base with shadow
        base_rect = pygame.Rect(x - CARD_WIDTH//2, y + 20, CARD_WIDTH, 20)
        shadow_rect = base_rect.move(3, 3)
        pygame.draw.rect(surface, SHADOW_COLOR, shadow_rect, border_radius=6)
        pygame.draw.rect(surface, POSITION_COLOR, base_rect, border_radius=6)
        
        # Draw card stack
        if self.card_count > 0:
            max_visible = min(self.card_count, 10)  # Show max 10 cards
            
            for i in range(max_visible):
                card_y = y - i * 4  # Increased spacing for better visual
                card_rect = pygame.Rect(x - CARD_WIDTH//2, card_y - CARD_HEIGHT, CARD_WIDTH, CARD_HEIGHT)
                
                # Draw card shadow
                shadow_rect = card_rect.move(2, 2)
                pygame.draw.rect(surface, SHADOW_COLOR, shadow_rect, border_radius=10)
                
                # Draw card
                color = HIGHLIGHT_COLOR if self.selected else CARD_COLOR
                pygame.draw.rect(surface, color, card_rect, border_radius=10)
                
                # Draw card border
                border_color = (255, 200, 50) if self.selected else CARD_BORDER_COLOR
                pygame.draw.rect(surface, border_color, card_rect, 3, border_radius=10)
                
                # Draw card corner decoration
                corner_size = 8
                pygame.draw.rect(surface, border_color, 
                                (card_rect.left + 5, card_rect.top + 5, corner_size, corner_size), 
                                border_radius=2)
                pygame.draw.rect(surface, border_color, 
                                (card_rect.right - 13, card_rect.top + 5, corner_size, corner_size), 
                                border_radius=2)
            
            # Display card count with background
            count_text = self.font_manager.medium.render(str(self.card_count), True, TEXT_COLOR)
            count_bg = pygame.Rect(x - 20, y - CARD_HEIGHT//2 - 15, 40, 30)
            pygame.draw.rect(surface, SHADOW_COLOR, count_bg.move(2, 2), border_radius=8)
            pygame.draw.rect(surface, (40, 60, 80), count_bg, border_radius=8)
            pygame.draw.rect(surface, ACCENT_COLOR, count_bg, 2, border_radius=8)
            surface.blit(count_text, (x - count_text.get_width()//2, y - CARD_HEIGHT//2 - count_text.get_height()//2))
        else:
            pass
        
        # Store rectangle for click detection
        self.rect = pygame.Rect(x - CARD_WIDTH//2 - 10, y - CARD_HEIGHT - 10, 
                               CARD_WIDTH + 20, CARD_HEIGHT + 80)
        
        # Draw position number with background
        pos_text = self.font_manager.small.render(f"Pos {self.index + 1}", True, TEXT_COLOR)
        pos_bg = pygame.Rect(x - pos_text.get_width()//2 - 6, y + 45,
                            pos_text.get_width() + 12, pos_text.get_height() + 6)
        pygame.draw.rect(surface, SHADOW_COLOR, pos_bg.move(2, 2), border_radius=6)
        pygame.draw.rect(surface, (40, 60, 80), pos_bg, border_radius=6)
        surface.blit(pos_text, (x - pos_text.get_width()//2, y + 48))
        
        

class AutoPlayer:
    """Handles AI logic"""
    def __init__(self, positions):
        self.positions = positions

    def this_turn_random(self, difficulty):
        """According to difficulty, whether to randomly move or not"""
        difficulty_random_rates = {1: 0.1, 2: 0.3, 3: 0.1, 4: 0.05}
        return random.random() < difficulty_random_rates.get(difficulty, 0.3)
    
    def calculate_nim_sum(self, positions):
        """Calculate the XOR (nim-sum) of all positions"""
        nim_sum = 0
        for count in positions:
            nim_sum ^= count
        return nim_sum
    
    def find_winning_move(self):
        """Find a move that makes the nim-sum zero (winning move)"""
        current_nim_sum = self.calculate_nim_sum(self.positions)
        
        # If nim-sum is already 0, any move will make it non-zero (losing position)
        if current_nim_sum == 0:
            return None
        
        # Find a move that makes nim-sum zero
        for i in range(len(self.positions)):
            if self.positions[i] > 0:
                # We need to find count such that: positions[i] XOR count = current_nim_sum XOR positions[i]
                # This means: count = positions[i] - (current_nim_sum XOR positions[i])
                target = current_nim_sum ^ self.positions[i]
                if target < self.positions[i]:
                    count = self.positions[i] - target
                    if 1 <= count <= self.positions[i]:
                        return i, count
        return None
    
    def move_instruction(self, difficulty):
        """Generate move instruction for AI"""
        # Try to find a winning move first
        winning_move = self.find_winning_move()
        
        # For higher difficulties, use winning moves more often
        if winning_move and not self.this_turn_random(difficulty):
            return winning_move
        else:
            # Make a random move
            available_moves = []
            for i in range(len(self.positions)):
                if self.positions[i] > 0:
                    available_moves.append(i)
            
            if available_moves:
                position_idx = random.choice(available_moves)
                # Prefer taking more cards to end game faster
                if difficulty >= 3:  # Hard and Insane take more cards
                    count = random.randint(max(1, self.positions[position_idx] // 2), self.positions[position_idx])
                else:
                    count = random.randint(1, self.positions[position_idx])
                return position_idx, count
            
            # Fallback
            return 0, 1

class GameLogic:
    """Handles game rules and logic"""
    def __init__(self):
        self.positions = []
        self.selected_position_index = None
        self.selected_count = 1
        self.game_over = False
        self.winner = None
        self.message = ""
        self.difficulty = None
        self.game_mode = None
        self.current_player = "Player 1"
        self.auto_player = None
    
    def calculate_nim_sum(self):
        """Calculate the XOR (nim-sum) of all positions"""
        nim_sum = 0
        for count in self.positions:
            nim_sum ^= count
        return nim_sum
    
    def judge_win(self):
        """Determine if current position is winning using XOR (nim-sum)"""
        return self.calculate_nim_sum() != 0
    
    def initialize_game(self):
        """Initialize a new game with difficulty-based position count"""
        try:
            # First select game mode
            print("Selecting game mode...")
            self.game_mode = Select_Difficulty_inner.get_game_mode()
            print(f"Game mode selected: {self.game_mode}")
            
            # If PvE mode, select difficulty
            if self.game_mode == "PVE":
                print("Selecting difficulty...")
                self.difficulty = Select_Difficulty_inner.select_difficulty()
                print(f"Difficulty selected: {self.difficulty}")
            else:
                self.difficulty = None
                print("PvP mode - no difficulty selection needed")
            
            # Set position count based on game mode and difficulty
            if self.game_mode == "PVP":
                # PvP mode: fixed medium difficulty
                min_pos, max_pos = (4, 6)
            else:
                # PvE mode: use difficulty-based ranges
                difficulty_position_ranges = {
                    1: (3, 5),   # Easy: 3-5 positions
                    2: (4, 6),   # Normal: 4-6 positions  
                    3: (5, 7),   # Hard: 5-7 positions
                    4: (6, 8)    # Insane: 6-8 positions
                }
                min_pos, max_pos = difficulty_position_ranges.get(self.difficulty, (4, 6))
            
            n = random.randint(min_pos, max_pos)
            print(f"Generating {n} positions")
            
            # Generate positions with card counts
            self.positions = [random.randint(1, 10) for _ in range(n)]
            self.selected_position_index = None
            self.selected_count = 1
            self.game_over = False
            self.winner = None
            self.current_player = "Player 1"
            
            if self.game_mode == "PVE":
                self.auto_player = AutoPlayer(self.positions)
                print("AI player initialized")
            else:
                self.auto_player = None
                print("PvP mode - no AI player")
            
            # Show initial game state with mode info
            nim_sum = self.calculate_nim_sum()
            if self.game_mode == "PVP":
                mode_info = " (Player vs Player)"
            else:
                difficulty_names = ["Easy", "Normal", "Hard", "Insane"]
                mode_info = f" (Player vs AI - {difficulty_names[self.difficulty-1]})"
            
            position_info = f" | {n} positions"
            
            if nim_sum == 0:
                self.message = f"Game Started! {self.current_player} is in a losing position.{mode_info}{position_info}"
            else:
                self.message = f"Game Started! {self.current_player} is in a winning position.{mode_info}{position_info}"
            
            print("Game initialization completed successfully")
            
        except Exception as e:
            print(f"Error in initialize_game: {e}")
            # Fallback initialization
            self.positions = [3, 4, 5]
            self.game_mode = "PVE"
            self.difficulty = 2
            self.current_player = "Player 1"
            self.auto_player = AutoPlayer(self.positions)
            self.message = "Game Started! Fallback mode activated."
    
    def make_move(self, position_idx, count):
        """Execute a move and return success status"""
        if (0 <= position_idx < len(self.positions) and 
            1 <= count <= self.positions[position_idx]):
            
            self.positions[position_idx] -= count
            self.message = f"{self.current_player} took {count} cards from position {position_idx + 1}."
            
            # Update AI's positions reference if in PvE mode
            if self.game_mode == "PVE":
                self.auto_player.positions = self.positions
            
            # Check if game is over
            if not any(self.positions):
                self.game_over = True
                self.winner = self.current_player
                self.message = f"Game Over! {self.current_player} Wins!"
                return True
            
            # Show position analysis after move (only in PvE mode)
            if self.game_mode == "PVE":
                nim_sum = self.calculate_nim_sum()
                if self.current_player == "Player 1":
                    if nim_sum == 0:
                        self.message += " You left a losing position for AI."
                    else:
                        self.message += " You left a winning position for AI."
                else:
                    if nim_sum == 0:
                        self.message += " AI left you in a losing position."
                    else:
                        self.message += " AI left you in a winning position."
            
            # Switch player
            self.switch_player()
            return True
        return False
    
    def switch_player(self):
        """Switch between players"""
        if self.game_mode == "PVE":
            if self.current_player == "Player 1":
                self.current_player = "AI"
                # Add analysis for AI's turn
                nim_sum = self.calculate_nim_sum()
                if nim_sum == 0:
                    self.message += " AI is in a losing position."
                else:
                    self.message += " AI is in a winning position."
            else:
                self.current_player = "Player 1"
                # Add analysis for player's turn
                nim_sum = self.calculate_nim_sum()
                if nim_sum == 0:
                    self.message += " You're in a losing position."
                else:
                    self.message += " You're in a winning position."
        else:
            # PvP mode
            if self.current_player == "Player 1":
                self.current_player = "Player 2"
                self.message += f" {self.current_player}'s turn."
            else:
                self.current_player = "Player 1"
                self.message += f" {self.current_player}'s turn."
    
    def ai_make_move(self):
        """Let AI make a move (only in PvE mode)"""
        if self.game_mode == "PVE" and self.current_player == "AI" and not self.game_over:
            position_idx, count = self.auto_player.move_instruction(self.difficulty)
            if self.make_move(position_idx, count):
                return True
        return False
    
    def select_position(self, position_idx):
        """Select a position for taking cards"""
        if 0 <= position_idx < len(self.positions) and self.positions[position_idx] > 0:
            self.selected_position_index = position_idx
            self.selected_count = 1
            
            if self.game_mode == "PVE":
                self.message = f"Selected position {position_idx + 1}, please select number of cards and press confirm."
            else:
                self.message = f"{self.current_player} selected position {position_idx + 1}, adjust cards and confirm."
            return True
        return False

class UIRenderer:
    """Handles all UI rendering"""
    def __init__(self, screen, font_manager):
        self.screen = screen
        self.font_manager = font_manager
    
    def draw_background(self):
        """Draw the background with gradient effect"""
        # Draw main background
        self.screen.fill(BACKGROUND_COLOR)
        
        # Draw subtle grid pattern
        for x in range(0, SCREEN_WIDTH, 40):
            pygame.draw.line(self.screen, (35, 45, 55), (x, 0), (x, SCREEN_HEIGHT), 1)
        for y in range(0, SCREEN_HEIGHT, 40):
            pygame.draw.line(self.screen, (35, 45, 55), (0, y), (SCREEN_WIDTH, y), 1)
    
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
        self.screen.blit(mode_info, (20, 60))
        
        # Current player info
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
        self.screen.blit(player_text, (SCREEN_WIDTH - player_text.get_width() - 20, 60))
        
        # Current message with background - with text wrapping
        message_color = (WIN_COLOR if game_logic.game_over and game_logic.winner == "Player 1" 
                        else LOSE_COLOR if game_logic.game_over and game_logic.winner == "AI"
                        else (255, 200, 50) if game_logic.game_over and game_logic.winner == "Player 2"
                        else TEXT_COLOR)
        
        # Handle long messages with text wrapping
        message_lines = self._wrap_text(game_logic.message, self.font_manager.medium, SCREEN_WIDTH - 100)
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
            self.screen.blit(select_info, (SCREEN_WIDTH//2 - select_info.get_width()//2, 140))
        
        # Game state indicator (only show in PvE mode)
        if not game_logic.game_over and game_logic.game_mode == "PVE":
            game_state = "Winning Position" if game_logic.judge_win() else "Losing Position"
            state_color = WIN_COLOR if game_logic.judge_win() else LOSE_COLOR
            state_text = self.font_manager.small.render(game_state, True, state_color)
            
            state_bg = pygame.Rect(SCREEN_WIDTH//2 - state_text.get_width()//2 - 10, 160, 
                                 state_text.get_width() + 20, state_text.get_height() + 6)
            pygame.draw.rect(self.screen, (40, 50, 65), state_bg, border_radius=6)
            pygame.draw.rect(self.screen, state_color, state_bg, 2, border_radius=6)
            self.screen.blit(state_text, (SCREEN_WIDTH//2 - state_text.get_width()//2, 163))
    
    def _wrap_text(self, text, font, max_width):
        """Wrap text to fit within max_width"""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_width = font.size(test_line)[0]
            
            if test_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
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
            
            
            # Create temporary card position for drawing
            card_pos = CardPosition(i, count, self.font_manager)
            card_pos.selected = (i == selected_position_index)
            card_pos.draw(self.screen, x, y)
            position_rects.append(card_pos.rect)
        
        
        return position_rects
    
    def draw_control_panel(self, buttons, selected_count, selected_position_index):
        """Draw the control panel with enhanced styling"""
        control_y = POSITION_HEIGHT + 150
        control_width = 400
        control_x = (SCREEN_WIDTH - control_width) // 2
        
        # Draw control panel background
        control_bg = pygame.Rect(control_x - 20, control_y - 20, control_width + 40, 150) 
        pygame.draw.rect(self.screen, (35, 45, 60), control_bg, border_radius=15)
        pygame.draw.rect(self.screen, ACCENT_COLOR, control_bg, 3, border_radius=15)
        
        # Draw count display with background
        count_display = str(selected_count) if selected_position_index is not None else "-"
        count_text = self.font_manager.large.render(count_display, True, TEXT_COLOR)
        count_bg = pygame.Rect(control_x + control_width//2 - 35, control_y-5, 70, 60)
        pygame.draw.rect(self.screen, (40, 60, 80), count_bg, border_radius=12)
        pygame.draw.rect(self.screen, ACCENT_COLOR, count_bg, 3, border_radius=12)
        self.screen.blit(count_text, 
                        (control_x + control_width//2 - count_text.get_width()//2, 
                         control_y + 25 - count_text.get_height()//2))
    
    def draw_hints(self):
        """Draw operation hints separately below control panel"""
        hint_y = POSITION_HEIGHT + 290
        hints = [
            "Use UP/DOWN arrows to adjust number, ENTER to confirm",
            "Use LEFT/RIGHT arrows to switch between positions", 
            "Click on card stacks to select them"
        ]
        
        for i, hint in enumerate(hints):
            hint_text = self.font_manager.small.render(hint, True, (150, 170, 190))
            self.screen.blit(hint_text, (SCREEN_WIDTH//2 - hint_text.get_width()//2, hint_y + i * 20))

class InputHandler:
    """Handles user input"""
    def __init__(self, game_logic):
        self.game_logic = game_logic
    
    def handle_mouse_click(self, event, position_rects, buttons):
        """Handle mouse click events"""
        mouse_pos = pygame.mouse.get_pos()
        
        if self.game_logic.game_over:
            # Check restart button
            if buttons["restart"].is_clicked(event):
                self.game_logic.initialize_game()
        else:
            # Check if current player can interact
            can_interact = False
            if self.game_logic.game_mode == "PVP":
                # In PvP mode, both players can interact
                can_interact = True
            elif self.game_logic.game_mode == "PVE" and self.game_logic.current_player == "Player 1":
                # In PvE mode, only Player 1 can interact
                can_interact = True
            
            if can_interact:
                # Check position selection
                for i, rect in enumerate(position_rects):
                    if rect.collidepoint(mouse_pos):
                        self.game_logic.select_position(i)
                        break
                
                # Check number buttons (only if a position is selected)
                if self.game_logic.selected_position_index is not None:
                    if buttons["minus"].is_clicked(event) and self.game_logic.selected_count > 1:
                        self.game_logic.selected_count -= 1
                    elif (buttons["plus"].is_clicked(event) and 
                          self.game_logic.selected_count < self.game_logic.positions[self.game_logic.selected_position_index]):
                        self.game_logic.selected_count += 1
                
                # Check confirm button (only if a position is selected)
                if (buttons["confirm"].is_clicked(event) and 
                    self.game_logic.selected_position_index is not None):
                    if self.game_logic.make_move(self.game_logic.selected_position_index, self.game_logic.selected_count):
                        self.game_logic.selected_position_index = None
    
    def handle_keyboard(self, event):
        """Handle keyboard events"""
        if self.game_logic.game_over:
            return
        
        # Check if current player can interact
        can_interact = False
        if self.game_logic.game_mode == "PVP":
            # In PvP mode, both players can interact
            can_interact = True
        elif self.game_logic.game_mode == "PVE" and self.game_logic.current_player == "Player 1":
            # In PvE mode, only Player 1 can interact
            can_interact = True
        
        if can_interact:
            if self.game_logic.selected_position_index is not None:
                # Number adjustment with up/down arrows
                if event.key == pygame.K_UP and self.game_logic.selected_count < self.game_logic.positions[self.game_logic.selected_position_index]:
                    self.game_logic.selected_count += 1
                elif event.key == pygame.K_DOWN and self.game_logic.selected_count > 1:
                    self.game_logic.selected_count -= 1
                elif event.key == pygame.K_RETURN:
                    if self.game_logic.make_move(self.game_logic.selected_position_index, self.game_logic.selected_count):
                        self.game_logic.selected_position_index = None
            
            # Position selection with left/right arrows
            if event.key == pygame.K_LEFT:
                self._select_previous_position()
            elif event.key == pygame.K_RIGHT:
                self._select_next_position()
    
    def _select_previous_position(self):
        """Select the previous available position"""
        if self.game_logic.selected_position_index is None and len(self.game_logic.positions) > 0:
            # Select the first available position from the right
            for i in range(len(self.game_logic.positions)-1, -1, -1):
                if self.game_logic.positions[i] > 0:
                    self.game_logic.select_position(i)
                    break
        elif self.game_logic.selected_position_index is not None:
            # Move left through positions
            new_position = self.game_logic.selected_position_index
            for i in range(1, len(self.game_logic.positions)):
                new_position = (self.game_logic.selected_position_index - i) % len(self.game_logic.positions)
                if self.game_logic.positions[new_position] > 0:
                    self.game_logic.select_position(new_position)
                    self.game_logic.selected_count = min(self.game_logic.selected_count, self.game_logic.positions[new_position])
                    break
    
    def _select_next_position(self):
        """Select the next available position"""
        if self.game_logic.selected_position_index is None and len(self.game_logic.positions) > 0:
            # Select the first available position from the left
            for i in range(len(self.game_logic.positions)):
                if self.game_logic.positions[i] > 0:
                    self.game_logic.select_position(i)
                    break
        elif self.game_logic.selected_position_index is not None:
            # Move right through positions
            new_position = self.game_logic.selected_position_index
            for i in range(1, len(self.game_logic.positions)):
                new_position = (self.game_logic.selected_position_index + i) % len(self.game_logic.positions)
                if self.game_logic.positions[new_position] > 0:
                    self.game_logic.select_position(new_position)
                    self.game_logic.selected_count = min(self.game_logic.selected_count, self.game_logic.positions[new_position])
                    break

class CardGame:
    """Main game class that coordinates all components"""
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Card Taking Game")
        self.clock = pygame.time.Clock()
        
        # Initialize components
        self.font_manager = FontManager(SCREEN_HEIGHT)
        Select_Difficulty_inner.set_global_references(self.screen, self.font_manager)
        
        self.game_logic = GameLogic()
        self.ui_renderer = UIRenderer(self.screen, self.font_manager)
        self.input_handler = InputHandler(self.game_logic)
        
        # Initialize buttons
        self.buttons = self._create_buttons()
        self.position_rects = []
        
        # 确保游戏初始化完成
        print("Starting game initialization...")
        self.game_logic.initialize_game()
        print("Game initialization completed")
        
        self.ai_timer = 0
    
    def _create_buttons(self):
        """Create all UI buttons"""
        control_y = POSITION_HEIGHT + 150
        control_width = 400
        control_x = (SCREEN_WIDTH - control_width) // 2
        number_button_width = 80
        number_button_height = 50
        
        buttons = {
            "minus": Button(control_x, control_y, number_button_width, number_button_height, "−", self.font_manager),
            "plus": Button(control_x + control_width - number_button_width, control_y, number_button_width, number_button_height, "+", self.font_manager),
            "confirm": Button(control_x + 100, control_y + 60, 200, 50, "Confirm Move", self.font_manager),
            "restart": Button(SCREEN_WIDTH//2 - 120, POSITION_HEIGHT + 290, 240, 60, "New Game", self.font_manager)
        }
        
        return buttons
    
    def handle_events(self):
        """Handle all game events"""
        mouse_pos = pygame.mouse.get_pos()
        
        # Update button hover states
        for button in self.buttons.values():
            button.update_hover(mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.input_handler.handle_mouse_click(event, self.position_rects, self.buttons)
            
            elif event.type == pygame.KEYDOWN:
                self.input_handler.handle_keyboard(event)
        
        return True
    
    def update(self):
        """Update game state"""
        # AI's turn (only in PvE mode)
        if (self.game_logic.game_mode == "PVE" and 
            self.game_logic.current_player == "AI" and 
            not self.game_logic.game_over):
            
            self.ai_timer += 1
            # Add delay for AI move to make it visible
            if self.ai_timer > 30:  # About 1.25 seconds at 24 FPS
                self.game_logic.ai_make_move()
                self.ai_timer = 0
    
    def draw(self):
        """Draw the complete game interface"""
        try:
            # Draw background
            self.ui_renderer.draw_background()
            
            # Draw game information
            self.ui_renderer.draw_game_info(self.game_logic)
            
            # Draw card positions
            self.position_rects = self.ui_renderer.draw_card_positions(
                self.game_logic.positions, self.game_logic.selected_position_index)
            
            if not self.game_logic.game_over:
                # Set button enabled states based on game mode and current player
                if self.game_logic.game_mode == "PVE":
                    # In PvE mode, only enable buttons during Player 1's turn
                    buttons_enabled = (self.game_logic.current_player == "Player 1")
                else:
                    # In PvP mode, always enable buttons for both players
                    buttons_enabled = True
                
                for button in [self.buttons["minus"], self.buttons["plus"], self.buttons["confirm"]]:
                    button.enabled = buttons_enabled
                
                self.ui_renderer.draw_control_panel(
                    self.buttons, self.game_logic.selected_count, self.game_logic.selected_position_index)
                
                # Draw control panel buttons
                for button in [self.buttons["minus"], self.buttons["plus"], self.buttons["confirm"]]:
                    button.draw(self.screen)
                
                # Draw hints
                self.ui_renderer.draw_hints()
            else:
                # Draw game over screen
                self.buttons["restart"].draw(self.screen)
            
            pygame.display.flip()
            
        except Exception as e:
            print(f"Error in draw: {e}")
    
    def run(self):
        """Run the main game loop"""
        running = True
        frame_count = 0
        
        while running:
            frame_count += 1
            
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = CardGame()
    game.run()