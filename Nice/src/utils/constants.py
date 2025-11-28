"""
Game constants and configuration
"""

# Screen dimensions
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

# Card game specific constants
CARD_WIDTH = 80
CARD_HEIGHT = 120
MARGIN = 20
POSITION_HEIGHT = 350
CARD_GAME_FPS = 24

CARD_COLOR = (255, 255, 255)
CARD_BORDER_COLOR = (70, 90, 120)
POSITION_COLOR = (60, 80, 100)
HIGHLIGHT_COLOR = (255, 215, 0)
WIN_COLOR = (100, 200, 100)
LOSE_COLOR = (220, 100, 100)

# Game configuration
DIFFICULTY_POSITION_RANGES = {
    1: (3, 5),   # Easy: 3-5 positions
    2: (4, 6),   # Normal: 4-6 positions  
    3: (5, 7),   # Hard: 5-7 positions
    4: (6, 8)    # Insane: 6-8 positions
}

DIFFICULTY_RANDOM_RATES = {
    1: 0.5, 
    2: 0.3, 
    3: 0.1, 
    4: 0.05
}

DIFFICULTY_NAMES = ["Easy", "Normal", "Hard", "Insane"]