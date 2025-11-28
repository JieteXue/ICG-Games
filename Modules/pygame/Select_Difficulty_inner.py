import pygame
import sys

# Global variables to store screen and font manager references
_screen = None
_font_manager = None

def set_global_references(screen, font_manager):
    """Set global references for difficulty selection"""
    global _screen, _font_manager
    _screen = screen
    _font_manager = font_manager

def select_difficulty():
    """
    Difficulty selection within the main game window
    """
    selector = DifficultySelector()
    return selector.get_difficulty()

class DifficultySelector:
    """Integrated difficulty selector"""
    def __init__(self):
        self.selected_difficulty = None
        
        # Difficulty button definitions
        self.difficulties = [
            {"name": "Easy", "value": 1, "color": (70, 180, 80), "hover_color": (90, 200, 100)},
            {"name": "Normal", "value": 2, "color": (60, 140, 220), "hover_color": (80, 160, 240)},
            {"name": "Hard", "value": 3, "color": (220, 160, 60), "hover_color": (240, 180, 80)},
            {"name": "Insane", "value": 4, "color": (200, 70, 70), "hover_color": (220, 90, 90)}
        ]
        
        self.buttons = []
        self._create_buttons()
    
    def _create_buttons(self):
        """Create difficulty selection buttons"""
        button_width = 300
        button_height = 60
        start_y = 200
        
        for i, diff in enumerate(self.difficulties):
            x = _screen.get_width() // 2 - button_width // 2
            y = start_y + i * (button_height + 20)
            button = DifficultyButton(x, y, button_width, button_height, 
                                    diff["name"], diff["value"], 
                                    diff["color"], diff["hover_color"])
            self.buttons.append(button)
    
    def draw(self):
        """Draw the difficulty selection screen"""
        # Clear canvas and draw new background
        _screen.fill((25, 25, 40))
        
        # Draw title
        title_font = pygame.font.SysFont("arial", 48, bold=True)
        title = title_font.render("Select Difficulty", True, (220, 220, 255))
        title_rect = title.get_rect(center=(_screen.get_width()//2, 100))
        _screen.blit(title, title_rect)
        
        # Draw buttons
        for button in self.buttons:
            button.draw(_screen)
        
        pygame.display.flip()
    
    def handle_events(self):
        """Handle difficulty selection events"""
        mouse_pos = pygame.mouse.get_pos()
        
        # Update button hover states
        for button in self.buttons:
            button.update_hover(mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for button in self.buttons:
                    if button.hovered:
                        self.selected_difficulty = button.value
                        return True
        
        return True
    
    def get_difficulty(self):
        """Run the difficulty selector and return selected difficulty"""
        clock = pygame.time.Clock()
        
        while self.selected_difficulty is None:
            if not self.handle_events():
                return 2  # Default to Normal if window closed
            
            self.draw()
            clock.tick(60)
        
        return self.selected_difficulty

class DifficultyButton:
    """Difficulty selection button"""
    def __init__(self, x, y, width, height, text, value, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.value = value
        self.color = color
        self.hover_color = hover_color
        self.hovered = False
    
    def draw(self, surface):
        """Draw the button"""
        color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=15)
        
        # Use global font manager
        text_surf = _font_manager.large.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
    
    def update_hover(self, mouse_pos):
        """Update hover state"""
        self.hovered = self.rect.collidepoint(mouse_pos)

# Console fallback selection
def select_difficulty_console():
    """Console fallback difficulty selection"""
    print("\n" + "="*50)
    print("Select Difficulty Level:")
    print("1. Easy")
    print("2. Normal")
    print("3. Hard") 
    print("4. Insane")
    print("="*50)
    
    while True:
        try:
            choice = int(input("Enter your choice (1-4): "))
            if 1 <= choice <= 4:
                return choice
            else:
                print("Please enter a number between 1 and 4")
        except ValueError:
            print("Please enter a valid number")

# Main export function with fallback
def get_difficulty():
    """Get difficulty level with fallback mechanism"""
    try:
        if _screen and _font_manager:
            return select_difficulty()
        else:
            return select_difficulty_console()
    except Exception as e:
        print(f"GUI selection failed, using console fallback: {e}")
        return select_difficulty_console()

if __name__ == "__main__":
    # Test the difficulty selector
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    
    # Create temporary font manager for testing
    class TestFontManager:
        def __init__(self):
            self.large = pygame.font.SysFont('Arial', 32, bold=True)
    
    font_manager = TestFontManager()
    set_global_references(screen, font_manager)
    
    difficulty = get_difficulty()
    print(f"Selected difficulty: {difficulty}")
    pygame.quit()