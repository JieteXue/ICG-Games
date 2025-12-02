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

class SquareButton(Button):
    """Specialized square button for game selection grid"""
    
    def __init__(self, x, y, width, height, text, font_manager, icon=None, tooltip="", enabled=True):
        # 确保按钮是方形的
        super().__init__(x, y, width, height, text, font_manager, icon, tooltip)
        self.enabled = enabled
    
    def draw(self, surface):
        """Override draw method for square button styling"""
        # 确保字体已初始化
        self.font_manager.ensure_initialized()
        
        # Draw shadow
        shadow_rect = self.rect.move(4, 4)
        pygame.draw.rect(surface, SHADOW_COLOR, shadow_rect, border_radius=15)
        
        # 不同的颜色样式
        if not self.enabled:
            # 禁用按钮 - 灰色样式
            color = (100, 100, 120)
            border_color = (80, 80, 100)
            text_color = (150, 150, 150)
        elif self.hovered:
            # 悬停状态 - 高亮蓝色
            color = (100, 150, 220)
            border_color = ACCENT_COLOR
            text_color = (255, 255, 255)
        else:
            # 正常状态 - 深蓝色
            color = (60, 100, 160)
            border_color = (80, 130, 200)
            text_color = (220, 230, 240)
        
        # Draw button with rounded corners
        pygame.draw.rect(surface, color, self.rect, border_radius=15)
        pygame.draw.rect(surface, border_color, self.rect, 3, border_radius=15)
        
        # Draw text with wrapping for long names
        words = self.text.split(' ')
        lines = []
        current_line = []
        
        # 简单的文本换行逻辑
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_width = self.font_manager.medium.size(test_line)[0]
            
            if test_width <= self.rect.width - 20:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # 绘制文本行
        total_text_height = len(lines) * 25
        start_y = self.rect.centery - total_text_height // 2
        
        for i, line in enumerate(lines):
            text_surface = self.font_manager.medium.render(line, True, text_color)
            text_rect = text_surface.get_rect(center=(self.rect.centerx, start_y + i * 25))
            
            # Text shadow for enabled buttons
            if self.enabled:
                shadow_surface = self.font_manager.medium.render(line, True, (0, 0, 0, 100))
                shadow_rect = text_rect.move(1, 1)
                surface.blit(shadow_surface, shadow_rect)
            
            surface.blit(text_surface, text_rect)
        
        # 绘制提示（如果悬停时间足够长）
        if self.hovered and self.tooltip and self.enabled:
            self.tooltip_timer += 1
            if self.tooltip_timer > 20:
                self._draw_tooltip(surface)
        else:
            self.tooltip_timer = 0
    
    def update_hover(self, mouse_pos):
        """Update hover state based on mouse position"""
        self.hovered = self.rect.collidepoint(mouse_pos)
    
    def is_clicked(self, event):
        """Check if button was clicked (only if enabled)"""
        return (event.type == pygame.MOUSEBUTTONDOWN and 
                event.button == 1 and 
                self.hovered and 
                self.enabled)

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
        """Create menu buttons - 6 square buttons in 2 rows, 3 columns"""
        # 方形按钮尺寸
        button_size = 170
        button_spacing = 50
        
        # 计算网格总宽度和高度
        grid_width = 3 * button_size + 2 * button_spacing
        grid_height = 2 * button_size + button_spacing
        
        # 计算网格起始位置（居中）
        grid_start_x = (SCREEN_WIDTH - grid_width) // 2
        grid_start_y = 170
        
        # 定义6个按钮的信息
        button_configs = [
            {"id": "take_coins", "name": "Take Coins", "description": "Coin taking strategy game"},
            {"id": "split_cards", "name": "Split Cards", "description": "Card splitting strategy game"},
            {"id": "card_nim", "name": "Card Nim", "description": "Strategic card taking game using Nim theory"},
            {"id": "dawson_kayles", "name": "Laser Defense", "description": "Strategic tower connection game"},
            {"id": "subtract_factor", "name": "Subtract Factor", "description": "Strategic number reduction using factor subtraction"},
            {"id": "coming_soon", "name": "Coming Soon", "description": "New game coming soon"}
        ]
        
        # 获取实际注册的游戏
        registered_games = {game['id']: game for game in game_registry.get_available_games()}
        
        buttons = {}
        
        # 创建6个方形按钮
        for i in range(6):
            row = i // 3
            col = i % 3
            
            x = grid_start_x + col * (button_size + button_spacing)
            y = grid_start_y + row * (button_size + button_spacing)
            
            config = button_configs[i]
            game_id = config["id"]
            
            if game_id == "coming_soon":
                btn = SquareButton(x, y, button_size, button_size,
                                  config["name"], self.font_manager,
                                  tooltip=config["description"],
                                  enabled=False)
            elif game_id in registered_games:
                game_info = registered_games[game_id]
                btn = SquareButton(x, y, button_size, button_size,
                                  game_info['name'], self.font_manager,
                                  tooltip=game_info['description'])
            else:
                btn = SquareButton(x, y, button_size, button_size,
                                  config["name"], self.font_manager,
                                  tooltip="Game under development",
                                  enabled=False)
            
            buttons[game_id] = btn
        
        # 添加退出按钮
        quit_y = grid_start_y + grid_height + 30
        quit_width = 200
        quit_x = SCREEN_WIDTH // 2 - quit_width // 2
        buttons["quit"] = Button(quit_x, quit_y, quit_width, 60, 
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
        
        self.screen.blit(title_shadow, (SCREEN_WIDTH//2 - title.get_width()//2 + 3, 53))
        self.screen.blit(subtitle_shadow, (SCREEN_WIDTH//2 - subtitle.get_width()//2 + 2, 113))
        
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        self.screen.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, 110))
    
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
                
                # 预定义的游戏ID顺序
                game_ids = ["take_coins", "split_cards", "card_nim", 
                           "dawson_kayles", "subtract_factor", "coming_soon"]
                
                # Check game buttons in order
                for game_id in game_ids:
                    if game_id in self.buttons and self.buttons[game_id].is_clicked(event):
                        # 检查按钮是否可用
                        if hasattr(self.buttons[game_id], 'enabled') and not self.buttons[game_id].enabled:
                            # 游戏未实现
                            print(f"Game '{game_id}' is not available yet")
                            # 可以在这里添加一个弹窗提示
                        else:
                            self.start_game(game_id)
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