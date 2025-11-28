"""
Menu components
"""

import pygame
import sys

# 修复导入 - 使用绝对导入
from ui.buttons import Button, InfoButton
from utils.constants import *
from utils.helpers import FontManager
from core.game_registry import game_registry

class MainMenu:
    """Main menu class"""
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("ICG Games - Main Menu")
        self.clock = pygame.time.Clock()
        self.font_manager = FontManager(SCREEN_HEIGHT)
        self.font_manager.initialize_fonts()  # 显式初始化字体
        self.buttons = self.create_buttons()
        self.info_button = InfoButton(SCREEN_WIDTH - 60, 20, 40, self.font_manager)
        self.showing_info = False
        self.running = True
    
    def create_buttons(self):
        """Create menu buttons"""
        button_width = 300
        button_height = 80
        button_x = SCREEN_WIDTH // 2 - button_width // 2

        # Get available games
        available_games = game_registry.get_available_games()

        buttons = {}
        y_position = 250

        # Create buttons for each game
        for game_info in available_games:
            buttons[game_info['id']] = Button(
                button_x, y_position, button_width, button_height,
                game_info['name'], self.font_manager,
                tooltip=game_info['description']  # 使用游戏描述作为提示
            )
            y_position += 100

        # Add quit button
        buttons["quit"] = Button(button_x, y_position, button_width, button_height, 
                                "Quit", self.font_manager, tooltip="Exit the game")

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
        
        # Update info button hover state
        self.info_button.update_hover(mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check info button first
                if self.info_button.is_clicked(event):
                    self.showing_info = not self.showing_info
                    self.info_button.showing_tooltip = self.showing_info
                    continue
                
                # If showing info, clicking anywhere else should close it
                if self.showing_info:
                    self.showing_info = False
                    self.info_button.showing_tooltip = False
                    continue
                
                # Check game buttons
                available_games = game_registry.get_available_games()
                for game_info in available_games:
                    if self.buttons[game_info['id']].is_clicked(event):
                        self.start_game(game_info['id'])
                        return True
                
                # Check quit button
                if self.buttons["quit"].is_clicked(event):
                    return False
        
        return True
    
    def start_game(self, game_id):
        """Start the selected game"""
        try:
            game_info = game_registry.get_game(game_id)
            if game_info:
                game_class = game_info['class']
                print(f"🎯 Starting {game_info['name']}...")
                
                # Start the selected game
                game_screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                font_manager = FontManager(SCREEN_HEIGHT)
                font_manager.initialize_fonts()  # 确保字体初始化
                
                game_instance = game_class(game_screen, font_manager)
                game_instance.run()
                
                # After game ends, restart main menu
                print("🔄 Returning to main menu...")
                self.__init__()  # Reinitialize main menu
                self.run()
            
        except Exception as e:
            print(f"❌ Error starting game {game_id}: {e}")
            import traceback
            traceback.print_exc()
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
        
        # Draw info button (右上角)
        self.info_button.draw(self.screen)
        
        # Draw tooltip if showing info
        if self.showing_info:
            available_games = game_registry.get_available_games()
            self.info_button.draw_tooltip(self.screen, available_games)
        
        # Draw footer
        footer_text = self.font_manager.small.render(
            "© 2025 ICG Games - Interactive Card Games Collection", 
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

class GameModeSelector:
    """Game mode selection screen"""
    def __init__(self, screen, font_manager):
        self.screen = screen
        self.font_manager = font_manager
        self.selected_mode = None
        self.selected_difficulty = None
        
        # Game mode definitions
        self.modes = [
            {"name": "Player vs AI", "value": "PVE", "color": (60, 140, 220), "hover_color": (80, 160, 240)},
            {"name": "Player vs Player", "value": "PVP", "color": (70, 180, 80), "hover_color": (90, 200, 100)}
        ]
        
        # Difficulty definitions
        self.difficulties = [
            {"name": "Easy", "value": 1, "color": (70, 180, 80), "hover_color": (90, 200, 100)},
            {"name": "Normal", "value": 2, "color": (60, 140, 220), "hover_color": (80, 160, 240)},
            {"name": "Hard", "value": 3, "color": (220, 160, 60), "hover_color": (240, 180, 80)},
            {"name": "Insane", "value": 4, "color": (200, 70, 70), "hover_color": (220, 90, 90)}
        ]
        
        self.mode_buttons = []
        self.difficulty_buttons = []
        self._create_mode_buttons()
    
    def _create_mode_buttons(self):
        """Create game mode selection buttons"""
        button_width = 350
        button_height = 80
        start_y = 200

        for i, mode in enumerate(self.modes):
            x = self.screen.get_width() // 2 - button_width // 2
            y = start_y + i * (button_height + 30)
            button = ModeButton(x, y, button_width, button_height, 
                              mode["name"], mode["value"], 
                              mode["color"], mode["hover_color"], self.font_manager)
            # 为模式按钮添加提示
            if mode["value"] == "PVE":
                button.tooltip = "Play against computer AI"
            else:
                button.tooltip = "Play against another player"
            self.mode_buttons.append(button)

    def _create_difficulty_buttons(self):
        """Create difficulty selection buttons"""
        button_width = 300
        button_height = 60
        start_y = 200

        for i, diff in enumerate(self.difficulties):
            x = self.screen.get_width() // 2 - button_width // 2
            y = start_y + i * (button_height + 20)
            button = DifficultyButton(x, y, button_width, button_height, 
                                    diff["name"], diff["value"], 
                                    diff["color"], diff["hover_color"], self.font_manager)
            # 为难度按钮添加提示
            if diff["value"] == 1:
                button.tooltip = "Easy: AI makes more random moves"
            elif diff["value"] == 2:
                button.tooltip = "Normal: Balanced AI difficulty"
            elif diff["value"] == 3:
                button.tooltip = "Hard: AI uses advanced strategies"
            else:
                button.tooltip = "Insane: AI plays nearly perfectly"
            self.difficulty_buttons.append(button)
    
    def draw_mode_selection(self):
        """Draw the game mode selection screen"""
        self.screen.fill((25, 25, 40))
        
        # Draw title
        title = self.font_manager.large.render("Select Game Mode", True, (220, 220, 255))
        title_rect = title.get_rect(center=(self.screen.get_width()//2, 100))
        self.screen.blit(title, title_rect)
        
        # Draw description
        desc = self.font_manager.medium.render("Choose your preferred game mode", True, (180, 180, 200))
        desc_rect = desc.get_rect(center=(self.screen.get_width()//2, 150))
        self.screen.blit(desc, desc_rect)
        
        # Draw buttons
        for button in self.mode_buttons:
            button.draw(self.screen)
        
        pygame.display.flip()
    
    def draw_difficulty_selection(self):
        """Draw the difficulty selection screen"""
        self.screen.fill((25, 25, 40))
        
        # Draw title
        title = self.font_manager.large.render("Select Difficulty", True, (220, 220, 255))
        title_rect = title.get_rect(center=(self.screen.get_width()//2, 100))
        self.screen.blit(title, title_rect)
        
        # Draw buttons
        for button in self.difficulty_buttons:
            button.draw(self.screen)
        
        pygame.display.flip()
    
    def handle_mode_events(self):
        """Handle game mode selection events"""
        mouse_pos = pygame.mouse.get_pos()
        
        # Update button hover states
        for button in self.mode_buttons:
            button.update_hover(mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for button in self.mode_buttons:
                    if button.hovered:
                        self.selected_mode = button.value
                        if self.selected_mode == "PVE":
                            self._create_difficulty_buttons()
                        return True
        
        return True 

    def handle_difficulty_events(self):
        """Handle difficulty selection events"""
        mouse_pos = pygame.mouse.get_pos()
        
        # Update button hover states
        for button in self.difficulty_buttons:
            button.update_hover(mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for button in self.difficulty_buttons:
                    if button.hovered:
                        self.selected_difficulty = button.value
                        return True
        
        return True
    
    def get_game_mode(self):
        """Run the game mode selector and return selected mode"""
        clock = pygame.time.Clock()
        
        while self.selected_mode is None:
            if not self.handle_mode_events():
                return "PVE"  # Default to PvE if window closed
            
            self.draw_mode_selection()
            clock.tick(60)
        
        return self.selected_mode
    
    def get_difficulty(self):
        """Run the difficulty selector and return selected difficulty"""
        if self.selected_mode != "PVE":
            return None
            
        clock = pygame.time.Clock()
        
        while self.selected_difficulty is None:
            if not self.handle_difficulty_events():
                return 2  # Default to Normal if window closed
            
            self.draw_difficulty_selection()
            clock.tick(60)
        
        return self.selected_difficulty

class ModeButton:
    """Game mode selection button"""
    def __init__(self, x, y, width, height, text, value, color, hover_color, font_manager):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.value = value
        self.color = color
        self.hover_color = hover_color
        self.hovered = False
        self.font_manager = font_manager
        self.tooltip = ""
        self.tooltip_timer = 0
    
    def update_hover(self, mouse_pos):
        """Update hover state based on mouse position"""
        self.hovered = self.rect.collidepoint(mouse_pos)
    
    def draw(self, surface):
        """Draw the button"""
        color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=15)
        
        text_surf = self.font_manager.large.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
        # 绘制提示
        if self.hovered and self.tooltip:
            self.tooltip_timer += 1
            if self.tooltip_timer > 30:
                self._draw_tooltip(surface)
        else:
            self.tooltip_timer = 0
    
    def _draw_tooltip(self, surface):
        """绘制提示"""
        tooltip_font = pygame.font.SysFont('Arial', 14)
        tooltip_text = tooltip_font.render(self.tooltip, True, (255, 255, 255))
        tooltip_rect = tooltip_text.get_rect()
        
        tooltip_x = self.rect.centerx - tooltip_rect.width // 2
        tooltip_y = self.rect.top - tooltip_rect.height - 8
        
        tooltip_bg = pygame.Rect(
            tooltip_x - 6, tooltip_y - 4,
            tooltip_rect.width + 12, tooltip_rect.height + 8
        )
        pygame.draw.rect(surface, (40, 40, 60), tooltip_bg, border_radius=6)
        pygame.draw.rect(surface, ACCENT_COLOR, tooltip_bg, 1, border_radius=6)
        surface.blit(tooltip_text, (tooltip_x, tooltip_y))

class DifficultyButton:
    """Difficulty selection button"""
    def __init__(self, x, y, width, height, text, value, color, hover_color, font_manager):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.value = value
        self.color = color
        self.hover_color = hover_color
        self.hovered = False
        self.font_manager = font_manager
        self.tooltip = ""
        self.tooltip_timer = 0
    
    def update_hover(self, mouse_pos):
        """Update hover state based on mouse position"""
        self.hovered = self.rect.collidepoint(mouse_pos)
    
    def draw(self, surface):
        """Draw the button"""
        color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=15)
        
        text_surf = self.font_manager.large.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
        # 绘制提示
        if self.hovered and self.tooltip:
            self.tooltip_timer += 1
            if self.tooltip_timer > 30:
                self._draw_tooltip(surface)
        else:
            self.tooltip_timer = 0
    
    def _draw_tooltip(self, surface):
        """绘制提示"""
        tooltip_font = pygame.font.SysFont('Arial', 14)
        tooltip_text = tooltip_font.render(self.tooltip, True, (255, 255, 255))
        tooltip_rect = tooltip_text.get_rect()
        
        tooltip_x = self.rect.centerx - tooltip_rect.width // 2
        tooltip_y = self.rect.top - tooltip_rect.height - 8
        
        tooltip_bg = pygame.Rect(
            tooltip_x - 6, tooltip_y - 4,
            tooltip_rect.width + 12, tooltip_rect.height + 8
        )
        pygame.draw.rect(surface, (40, 40, 60), tooltip_bg, border_radius=6)
        pygame.draw.rect(surface, ACCENT_COLOR, tooltip_bg, 1, border_radius=6)
        surface.blit(tooltip_text, (tooltip_x, tooltip_y))