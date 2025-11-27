import pygame
import sys
import os

# Add Modules to path for importing other modules
current_dir = os.path.dirname(os.path.abspath(__file__))
modules_path = os.path.join(current_dir, 'Modules')
pygame_path = os.path.join(modules_path, 'pygame')

sys.path.insert(0, modules_path)
sys.path.insert(0, pygame_path)

# Game constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60


# Color definitions
BACKGROUND_COLOR = (25, 35, 45)
TEXT_COLOR = (220, 230, 240)
BUTTON_COLOR = (80, 120, 180)
BUTTON_HOVER_COLOR = (100, 150, 220)
ACCENT_COLOR = (100, 180, 255)
SHADOW_COLOR = (15, 25, 35)

class FontManager:
    """Font manager"""
    def __init__(self):
        self.large = pygame.font.SysFont('Arial', 48, bold=True)
        self.medium = pygame.font.SysFont('Arial', 32)
        self.small = pygame.font.SysFont('Arial', 24)

class Button:
    """Button class"""
    def __init__(self, x, y, width, height, text, font_manager):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font_manager = font_manager
        self.hovered = False
    
    def draw(self, surface):
        """Draw the button"""
        # Draw shadow
        shadow_rect = self.rect.move(4, 4)
        pygame.draw.rect(surface, SHADOW_COLOR, shadow_rect, border_radius=15)
        
        # Draw button
        color = BUTTON_HOVER_COLOR if self.hovered else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect, border_radius=15)
        pygame.draw.rect(surface, ACCENT_COLOR, self.rect, 3, border_radius=15)
        
        # Draw text
        text_surface = self.font_manager.medium.render(self.text, True, TEXT_COLOR)
        text_rect = text_surface.get_rect(center=self.rect.center)
        
        # Text shadow
        shadow_surface = self.font_manager.medium.render(self.text, True, (0, 0, 0, 100))
        shadow_rect = text_rect.move(2, 2)
        surface.blit(shadow_surface, shadow_rect)
        
        surface.blit(text_surface, text_rect)
    
    def update_hover(self, mouse_pos):
        """Update hover state"""
        self.hovered = self.rect.collidepoint(mouse_pos)
    
    def is_clicked(self, event):
        """Check if button was clicked"""
        return (event.type == pygame.MOUSEBUTTONDOWN and 
                event.button == 1 and 
                self.hovered)

class MainMenu:
    """Main menu class"""
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("ICG Games - Main Menu")
        self.clock = pygame.time.Clock()
        self.font_manager = FontManager()
        self.buttons = self.create_buttons()
        self.running = True
    
    def create_buttons(self):
        """Create menu buttons"""
        button_width = 300
        button_height = 80
        button_x = SCREEN_WIDTH // 2 - button_width // 2
        
        buttons = {
            "card_game": Button(button_x, 250, button_width, button_height, 
                               "Card Taking Game", self.font_manager),
            "other_game1": Button(button_x, 350, button_width, button_height, 
                                 "Game 2 (Coming Soon)", self.font_manager),
            "other_game2": Button(button_x, 450, button_width, button_height, 
                                 "Game 3 (Coming Soon)", self.font_manager),
            "quit": Button(button_x, 550, button_width, button_height, 
                          "Quit", self.font_manager)
        }
        return buttons
    
    def draw_background(self):
        """Draw background with gradient effect"""
        self.screen.fill(BACKGROUND_COLOR)
        
        # Draw subtle grid pattern
        for x in range(0, SCREEN_WIDTH, 40):
            pygame.draw.line(self.screen, (35, 45, 55), (x, 0), (x, SCREEN_HEIGHT), 1)
        for y in range(0, SCREEN_HEIGHT, 40):
            pygame.draw.line(self.screen, (35, 45, 55), (0, y), (SCREEN_WIDTH, y), 1)
    
    def draw_title(self):
        """Draw game title"""
        title = self.font_manager.large.render("ICG GAMES", True, TEXT_COLOR)
        subtitle = self.font_manager.medium.render("Interactive Card Games", True, ACCENT_COLOR)
        
        # Draw title shadow
        title_shadow = self.font_manager.large.render("ICG GAMES", True, SHADOW_COLOR)
        subtitle_shadow = self.font_manager.medium.render("Interactive Card Games", True, SHADOW_COLOR)
        
        self.screen.blit(title_shadow, (SCREEN_WIDTH//2 - title.get_width()//2 + 3, 103))
        self.screen.blit(subtitle_shadow, (SCREEN_WIDTH//2 - subtitle.get_width()//2 + 2, 163))
        
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
        self.screen.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, 160))
    
    def handle_events(self):
        """Handle menu events"""
        mouse_pos = pygame.mouse.get_pos()
        
        # Update button hover states
        for button in self.buttons.values():
            button.update_hover(mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.buttons["card_game"].is_clicked(event):
                    self.start_card_game()
                elif self.buttons["quit"].is_clicked(event):
                    return False
        
        return True
    
    def start_card_game(self):
        """Start the card taking game"""
        try:
            # Import and start the card game
            from Modules.pygame import game3
            pygame.quit()  # Close main menu
            
            # Start the card game
            card_game = game3.CardGame()
            card_game.run()
            
            # After card game ends, restart main menu
            self.__init__()  # Reinitialize main menu
            self.run()
            
        except Exception as e:
            print(f"Error starting card game: {e}")
            # Fallback: restart main menu
            self.__init__()
            self.run()
    
    def draw(self):
        """Draw the main menu"""
        self.draw_background()
        self.draw_title()
        
        # Draw buttons
        for button in self.buttons.values():
            button.draw(self.screen)
        
        # Draw footer
        footer_text = self.font_manager.small.render(
            "© 2024 ICG Games - Interactive Card Games Collection", 
            True, (150, 170, 190))
        self.screen.blit(footer_text, 
                        (SCREEN_WIDTH//2 - footer_text.get_width()//2, 
                         SCREEN_HEIGHT - 40))
        
        pygame.display.flip()
    
    def run(self):
        """Run the main menu loop"""
        self.running = True
        
        while self.running:
            self.running = self.handle_events()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

def main():
    """Main entry point"""
    menu = MainMenu()
    menu.run()

if __name__ == "__main__":
    main()