import pygame
import sys
import subprocess
import os

def select_difficulty():
    """
    Open difficulty selection in a separate process to avoid Pygame conflicts
    """
    # Create a clean script that only outputs the selected difficulty
    selector_script = """
import pygame
import sys
import os

# Suppress pygame welcome message
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

def main():
    pygame.init()
    
    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Difficulty Selection")
    
    # Colors
    BACKGROUND = (25, 25, 40)
    TITLE_COLOR = (220, 220, 255)
    BUTTON_COLORS = {
        "Easy": (70, 180, 80),
        "Normal": (60, 140, 220),
        "Hard": (220, 160, 60),
        "Insane": (200, 70, 70)
    }
    BUTTON_HOVER = {
        "Easy": (90, 200, 100),
        "Normal": (80, 160, 240),
        "Hard": (240, 180, 80),
        "Insane": (220, 90, 90)
    }
    BUTTON_TEXT = (255, 255, 255)
    
    # Fonts
    title_font = pygame.font.SysFont("arial", 48, bold=True)
    button_font = pygame.font.SysFont("arial", 32, bold=True)
    
    class Button:
        def __init__(self, x, y, width, height, text, value):
            self.rect = pygame.Rect(x, y, width, height)
            self.text = text
            self.value = value
            self.hovered = False
            
        def draw(self, surface):
            color = BUTTON_HOVER[self.text] if self.hovered else BUTTON_COLORS[self.text]
            pygame.draw.rect(surface, color, self.rect, border_radius=15)
            
            text_surf = button_font.render(self.text, True, BUTTON_TEXT)
            text_rect = text_surf.get_rect(center=self.rect.center)
            surface.blit(text_surf, text_rect)
            
        def check_hover(self, pos):
            self.hovered = self.rect.collidepoint(pos)
            
        def is_clicked(self, pos, event):
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                return self.rect.collidepoint(pos)
            return False
    
    buttons = [
        Button(WIDTH//2 - 150, 200, 300, 60, "Easy", 1),
        Button(WIDTH//2 - 150, 280, 300, 60, "Normal", 2),
        Button(WIDTH//2 - 150, 360, 300, 60, "Hard", 3),
        Button(WIDTH//2 - 150, 440, 300, 60, "Insane", 4)
    ]
    
    clock = pygame.time.Clock()
    selected_value = None
    
    while selected_value is None:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(2)  # Exit with code 2 for Normal
                
            for button in buttons:
                if button.is_clicked(mouse_pos, event):
                    selected_value = button.value
                    break
        
        for button in buttons:
            button.check_hover(mouse_pos)
        
        screen.fill(BACKGROUND)
        
        title_surf = title_font.render("Select Difficulty", True, TITLE_COLOR)
        title_rect = title_surf.get_rect(center=(WIDTH//2, 100))
        screen.blit(title_surf, title_rect)
        
        for button in buttons:
            button.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    # Only output the selected value, nothing else
    print(selected_value)
    sys.exit(0)

if __name__ == "__main__":
    main()
"""
    
    # Run the selector in a subprocess
    try:
        result = subprocess.run(
            [sys.executable, "-c", selector_script],
            capture_output=True,
            text=True,
            timeout=60,
            env={**os.environ, 'PYGAME_HIDE_SUPPORT_PROMPT': '1'}  # Suppress pygame welcome
        )
        
        if result.returncode == 0:
            # Clean the output - only take the last line and remove any non-digit characters
            output_lines = result.stdout.strip().split('\n')
            for line in reversed(output_lines):
                clean_line = ''.join(filter(str.isdigit, line))
                if clean_line:
                    return int(clean_line)
            return 2  # Default if no valid output
        else:
            print(f"Difficulty selection failed with code {result.returncode}")
            return 2
    except subprocess.TimeoutExpired:
        print("Difficulty selection timed out")
        return 2
    except Exception as e:
        print(f"Error in difficulty selection: {e}")
        return 2

# Simple console selection as fallback
def select_difficulty_console():
    """Fallback console-based difficulty selection"""
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

# Main export
def get_difficulty():
    """Get difficulty level with fallback"""
    try:
        return select_difficulty()
    except Exception as e:
        print(f"GUI selection failed, using console fallback: {e}")
        return select_difficulty_console()

if __name__ == "__main__":
    difficulty = get_difficulty()
    print(f"Selected difficulty: {difficulty}")