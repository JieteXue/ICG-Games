import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
CARD_WIDTH = 80
CARD_HEIGHT = 120
MARGIN = 20
POSITION_HEIGHT = 350  # Increased significantly to prevent overlap
INFO_HEIGHT = 200      # Dedicated space for information
FPS = 60

# Colors
BACKGROUND_COLOR = (240, 245, 255)
CARD_COLOR = (255, 255, 255)
CARD_BORDER_COLOR = (100, 100, 200)
POSITION_COLOR = (200, 230, 255)
TEXT_COLOR = (50, 50, 100)
BUTTON_COLOR = (70, 130, 180)
BUTTON_HOVER_COLOR = (100, 160, 210)
HIGHLIGHT_COLOR = (255, 215, 0)
WIN_COLOR = (50, 180, 50)
LOSE_COLOR = (220, 80, 80)

class CardGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Card Taking Game")
        self.clock = pygame.time.Clock()
        
        # Dynamic font sizes based on screen dimensions
        self.font_large = pygame.font.SysFont('arial', max(24, SCREEN_HEIGHT // 25))
        self.font_medium = pygame.font.SysFont('arial', max(18, SCREEN_HEIGHT // 30))
        self.font_small = pygame.font.SysFont('arial', max(14, SCREEN_HEIGHT // 40))
        
        self.positions = []
        self.selected_position = None
        self.selected_count = 1
        self.game_over = False
        self.winner = None
        self.message = ""
        
        self.initialize_game()
    
    def initialize_game(self):
        """Initialize game"""
        n = self.get_position_count()
        self.positions = self.random_list(n)
        self.selected_position = None
        self.selected_count = 1
        self.game_over = False
        self.winner = None
        self.message = "Game Started! Please select a position to take cards."
    
    def get_position_count(self):
        """Get number of positions"""
        return random.randint(5, 8)
    
    def random_list(self, n):
        """Generate random card list"""
        return [random.randint(1, 8) for _ in range(n)]
    
    def judge_win(self, positions):
        """Determine if current position is winning"""
        F = 0
        for count in positions:
            F ^= count
        return F != 0
    
    def make_move(self, position_idx, count):
        """Execute move"""
        if 0 <= position_idx < len(self.positions) and 1 <= count <= self.positions[position_idx]:
            self.positions[position_idx] -= count
            self.message = f"From position {position_idx + 1} took {count} cards."
            
            # Check if game is over
            if not any(self.positions):
                self.game_over = True
                self.winner = "Player"
                self.message = "Game Over! You Win!"
            
            return True
        return False
    
    def draw_card(self, x, y, count, is_selected=False):
        """Draw card stack"""
        # Draw position base
        pygame.draw.rect(self.screen, POSITION_COLOR, 
                        (x - CARD_WIDTH//2, y + 20, CARD_WIDTH, 20), 
                        border_radius=5)
        
        # Draw card stack
        if count > 0:
            for i in range(min(count, 8)):  # Show max 8 cards
                card_y = y - i * 3
                color = HIGHLIGHT_COLOR if is_selected else CARD_COLOR
                pygame.draw.rect(self.screen, color, 
                                (x - CARD_WIDTH//2, card_y - CARD_HEIGHT, CARD_WIDTH, CARD_HEIGHT),
                                border_radius=8)
                pygame.draw.rect(self.screen, CARD_BORDER_COLOR, 
                                (x - CARD_WIDTH//2, card_y - CARD_HEIGHT, CARD_WIDTH, CARD_HEIGHT),
                                2, border_radius=8)
            
            # Display card count
            count_text = self.font_medium.render(str(count), True, TEXT_COLOR)
            self.screen.blit(count_text, (x - count_text.get_width()//2, y - CARD_HEIGHT//2 - count_text.get_height()//2))
    
    def draw_button(self, x, y, width, height, text, hover=False):
        """Draw button"""
        color = BUTTON_HOVER_COLOR if hover else BUTTON_COLOR
        pygame.draw.rect(self.screen, color, (x, y, width, height), border_radius=10)
        pygame.draw.rect(self.screen, (50, 50, 100), (x, y, width, height), 2, border_radius=10)
        
        text_surface = self.font_medium.render(text, True, (255, 255, 255))
        self.screen.blit(text_surface, (x + width//2 - text_surface.get_width()//2, 
                                      y + height//2 - text_surface.get_height()//2))
        return pygame.Rect(x, y, width, height)
    
    def draw_game_info(self):
        """Draw game information"""
        # Game title
        title = self.font_large.render("Take Cards", True, TEXT_COLOR)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 20))
        
        # Game instructions
        instruction = self.font_small.render("Click on a position, use +/- buttons to take cards", True, TEXT_COLOR)
        self.screen.blit(instruction, (SCREEN_WIDTH//2 - instruction.get_width()//2, 70))
        
        # Current message
        message_color = WIN_COLOR if self.game_over and self.winner == "Player" else LOSE_COLOR if self.game_over else TEXT_COLOR
        message_text = self.font_medium.render(self.message, True, message_color)
        self.screen.blit(message_text, (SCREEN_WIDTH//2 - message_text.get_width()//2, 110))
        
        # Current selection info
        if self.selected_position is not None:
            select_info = self.font_small.render(f"Selected position: {self.selected_position + 1}, Selected count: {self.selected_count}", True, TEXT_COLOR)
            self.screen.blit(select_info, (SCREEN_WIDTH//2 - select_info.get_width()//2, 150))
        
        # Game state
        if not self.game_over:
            game_state = "Current game state: " + ("Winning" if self.judge_win(self.positions) else "Losing")
            state_text = self.font_small.render(game_state, True, WIN_COLOR if self.judge_win(self.positions) else LOSE_COLOR)
            self.screen.blit(state_text, (SCREEN_WIDTH//2 - state_text.get_width()//2, 180))
    
    def handle_events(self):
        """Handle events"""
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.game_over:
                    # Check restart button
                    if self.restart_button.collidepoint(mouse_pos):
                        self.initialize_game()
                else:
                    # Check position selection
                    for i, rect in enumerate(self.position_rects):
                        if rect.collidepoint(mouse_pos):
                            if self.positions[i] > 0:
                                self.selected_position = i
                                self.selected_count = 1
                                self.message = f"Selected position {i + 1}, please select number of cards and press confirm."
                    
                    # Check number buttons
                    for i, rect in enumerate(self.number_buttons):
                        if rect.collidepoint(mouse_pos) and self.selected_position is not None:
                            if i == 0 and self.selected_count > 1:  # -
                                self.selected_count -= 1
                            elif i == 1 and self.selected_count < self.positions[self.selected_position]:  # +
                                self.selected_count += 1
                    
                    # Check confirm button
                    if self.confirm_button.collidepoint(mouse_pos) and self.selected_position is not None:
                        if self.make_move(self.selected_position, self.selected_count):
                            self.selected_position = None
            
            elif event.type == pygame.KEYDOWN:
                if not self.game_over:
                    if self.selected_position is not None:
                        # Number adjustment with up/down arrows
                        if event.key == pygame.K_UP and self.selected_count < self.positions[self.selected_position]:
                            self.selected_count += 1
                        elif event.key == pygame.K_DOWN and self.selected_count > 1:
                            self.selected_count -= 1
                        elif event.key == pygame.K_RETURN:
                            if self.make_move(self.selected_position, self.selected_count):
                                self.selected_position = None
                    
                    # Position selection with left/right arrows
                    if event.key == pygame.K_LEFT:
                        if self.selected_position is None and len(self.positions) > 0:
                            # Select the first available position from the right
                            for i in range(len(self.positions)-1, -1, -1):
                                if self.positions[i] > 0:
                                    self.selected_position = i
                                    self.selected_count = 1
                                    break
                        elif self.selected_position is not None:
                            # Move left through positions
                            new_position = self.selected_position
                            for i in range(1, len(self.positions)):
                                new_position = (self.selected_position - i) % len(self.positions)
                                if self.positions[new_position] > 0:
                                    self.selected_position = new_position
                                    self.selected_count = min(self.selected_count, self.positions[new_position])
                                    break
                    
                    elif event.key == pygame.K_RIGHT:
                        if self.selected_position is None and len(self.positions) > 0:
                            # Select the first available position from the left
                            for i in range(len(self.positions)):
                                if self.positions[i] > 0:
                                    self.selected_position = i
                                    self.selected_count = 1
                                    break
                        elif self.selected_position is not None:
                            # Move right through positions
                            new_position = self.selected_position
                            for i in range(1, len(self.positions)):
                                new_position = (self.selected_position + i) % len(self.positions)
                                if self.positions[new_position] > 0:
                                    self.selected_position = new_position
                                    self.selected_count = min(self.selected_count, self.positions[new_position])
                                    break
        
        return True
    
    def draw(self):
        """Draw game interface"""
        self.screen.fill(BACKGROUND_COLOR)
        
        # Draw game information (top section)
        self.draw_game_info()
        
        # Draw all positions and cards (middle section)
        total_positions = len(self.positions)
        start_x = (SCREEN_WIDTH - (total_positions * (CARD_WIDTH + MARGIN))) // 2
        self.position_rects = []
        
        for i, count in enumerate(self.positions):
            x = start_x + i * (CARD_WIDTH + MARGIN) + CARD_WIDTH // 2
            y = POSITION_HEIGHT
            
            # Store position rectangle for click detection
            pos_rect = pygame.Rect(x - CARD_WIDTH//2, y - CARD_HEIGHT, CARD_WIDTH, CARD_HEIGHT + 40)
            self.position_rects.append(pos_rect)
            
            # Draw card stack
            is_selected = (i == self.selected_position)
            self.draw_card(x, y, count, is_selected)
            
            # Draw position number
            pos_text = self.font_small.render(f"Position {i + 1}", True, TEXT_COLOR)
            self.screen.blit(pos_text, (x - pos_text.get_width()//2, y + 50))
        
        if not self.game_over:
            # Draw control panel (bottom section)
            control_y = POSITION_HEIGHT + 150
            control_width = 300
            control_x = (SCREEN_WIDTH - control_width) // 2
            
            # Number adjustment buttons
            number_button_width = 60
            number_button_height = 40
            
            minus_rect = pygame.Rect(control_x, control_y, number_button_width, number_button_height)
            plus_rect = pygame.Rect(control_x + control_width - number_button_width, control_y, number_button_width, number_button_height)
            
            self.number_buttons = [minus_rect, plus_rect]
            
            mouse_pos = pygame.mouse.get_pos()
            
            # Draw - button
            self.draw_button(minus_rect.x, minus_rect.y, minus_rect.width, minus_rect.height, "-", minus_rect.collidepoint(mouse_pos))
            
            # Draw count display
            count_text = self.font_large.render(str(self.selected_count) if self.selected_position is not None else "-", True, TEXT_COLOR)
            self.screen.blit(count_text, (control_x + control_width//2 - count_text.get_width()//2, control_y + number_button_height//2 - count_text.get_height()//2))
            
            # Draw + button
            self.draw_button(plus_rect.x, plus_rect.y, plus_rect.width, plus_rect.height, "+", plus_rect.collidepoint(mouse_pos))
            
            # Draw confirm button
            confirm_y = control_y + number_button_height + 20
            confirm_rect = pygame.Rect(control_x, confirm_y, control_width, number_button_height)
            self.confirm_button = confirm_rect
            
            can_confirm = self.selected_position is not None and self.selected_count > 0
            self.draw_button(confirm_rect.x, confirm_rect.y, confirm_rect.width, confirm_rect.height, 
                           "Confirm", confirm_rect.collidepoint(mouse_pos) and can_confirm)
            
            # Draw operation hints
            hint_y = confirm_y + number_button_height + 10
            hint1 = self.font_small.render("Use arrow keys to adjust number, Enter to confirm", True, (150, 150, 150))
            hint2 = self.font_small.render("Left/Right arrows to switch between positions", True, (150, 150, 150))
            self.screen.blit(hint1, (SCREEN_WIDTH//2 - hint1.get_width()//2, hint_y))
            self.screen.blit(hint2, (SCREEN_WIDTH//2 - hint2.get_width()//2, hint_y + 25))
        else:
            # Game over interface
            end_y = POSITION_HEIGHT + 150
            result_text = self.font_large.render(f"{self.winner} Wins!", True, WIN_COLOR if self.winner == "Player" else LOSE_COLOR)
            self.screen.blit(result_text, (SCREEN_WIDTH//2 - result_text.get_width()//2, end_y))
            
            # Restart button
            button_width, button_height = 200, 50
            restart_rect = pygame.Rect(SCREEN_WIDTH//2 - button_width//2, end_y + 80, button_width, button_height)
            self.restart_button = restart_rect
            
            mouse_pos = pygame.mouse.get_pos()
            self.draw_button(restart_rect.x, restart_rect.y, restart_rect.width, restart_rect.height, 
                           "Restart", restart_rect.collidepoint(mouse_pos))
        
        pygame.display.flip()
    
    def run(self):
        """Run game main loop"""
        running = True
        while running:
            running = self.handle_events()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = CardGame()
    game.run()