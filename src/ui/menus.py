"""
Menu Components - Updated with error handling, resource cache, and performance optimization
"""

import pygame
import sys
import os

from ui.components.buttons import GameButton, IconButton
from ui.components.panels import InfoPanel
from ui.layout import UILayout
from utils.constants import *
from utils.helpers import FontManager
from utils.error_handler import handle_game_errors, log_resource_error, error_reporter
from utils.resource_cache import resource_cache
from utils.performance_monitor import performance_monitor, PerformanceProfiler
from utils.optimization_tools import optimize_game_performance, memory_optimizer
from ui.components.help_dialog import HelpDialog
from ui.components.settings_panel import SettingsPanel
from ui.components.music_panel import MusicPanel
from ui.components.redeem_dialog import RedeemDialog  # 新增

def get_icon_path(icon_filename):
    """Get icon file path using resource cache"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(current_dir, 'icon', icon_filename)
    
    if os.path.exists(icon_path):
        return icon_path
    
    # Try project root
    project_root = os.path.dirname(os.path.dirname(current_dir))
    alt_path = os.path.join(project_root, 'assets','image','icon', icon_filename)
    
    if os.path.exists(alt_path):
        return alt_path
    
    # Try other possible locations
    possible_paths = [
        os.path.join(project_root, 'icon', icon_filename),
        os.path.join(project_root, 'ui', 'icon', icon_filename),
        os.path.join(project_root, 'images', 'icon', icon_filename),
        icon_filename  # Maybe it's already a full path
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    log_resource_error(f"Icon file not found: {icon_filename}")
    return None

class MainMenu:
    """Main menu class with enhanced error handling and performance optimization"""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("ICG Games - Main Menu")
        self.clock = pygame.time.Clock()
        self.font_manager = FontManager(SCREEN_HEIGHT)
        self.font_manager.initialize_fonts()
        self.layout = UILayout(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Initialize game registry as None (lazy loading)
        self.game_registry = None
        
        # Add help dialog
        self.help_dialog = HelpDialog(SCREEN_WIDTH, SCREEN_HEIGHT, self.font_manager)

        # Performance monitoring
        self.show_perf_overlay = False
        self.last_optimization_time = 0
        self.optimization_interval = 30000  # 30 seconds
        
        # Performance statistics
        self.perf_stats = {
            'fps': 0,
            'frame_time': 0,
            'memory_usage': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
        
        self.buttons = self.create_buttons()
        self.info_button = None
        self.performance_button = None  # New performance button
        self.showing_info = False
        self.running = True
        self.error_message = None
        self.error_timer = 0
        
        # 新增：初始化音乐管理器
        try:
            from utils.music_manager import music_manager
            self.music_manager = music_manager
            print("✅ Music manager loaded in MainMenu")
        except ImportError as e:
            print(f"❌ Could not import music_manager: {e}")
            self.music_manager = None
        
        # 新增：初始化设置面板
        self.settings_panel = SettingsPanel(self.screen, self.font_manager, self.music_manager)
        
        # 新增：初始化音乐面板
        self.music_panel = MusicPanel(self.screen, self.font_manager, self.music_manager)
        
        # 新增：初始化兑换码对话框
        self.redeem_dialog = RedeemDialog(self.screen, self.font_manager, self.music_manager)
        
        # 初始化音乐（如果启用）
        if self.music_manager and self.music_manager.is_music_enabled():
            if self.music_manager.get_current_music_index() >= 0:
                self.music_manager.play_music(self.music_manager.get_current_music_index())
                print(f"🎵 Music started from MainMenu")
    
    def _get_game_registry(self):
        """Lazy load game registry to avoid circular imports"""
        if self.game_registry is None:
            try:
                # Delayed import to avoid circular imports
                from core.game_registry import game_registry
                self.game_registry = game_registry
            except ImportError as e:
                log_resource_error(f"Could not load game registry: {e}")
                self.show_error("Game registry not available. Some games may not work.")
                # Create a minimal registry
                self.game_registry = type('FallbackRegistry', (), {
                    'get_game': lambda game_id: None,
                    'get_available_games': lambda: []
                })()
        return self.game_registry
    
    @handle_game_errors
    def create_buttons(self):
        """Create menu buttons with enhanced error handling"""
        button_size = 170
        button_spacing = 50
        grid_width = 3 * button_size + 2 * button_spacing
        grid_height = 2 * button_size + button_spacing
        grid_start_x = (SCREEN_WIDTH - grid_width) // 2
        grid_start_y = 200  # 调整位置，为顶部按钮留出空间

        # Define button configurations
        button_configs = [
            {"id": "take_coins", "name": "Take Coins", "icon": "G1ICON.jpg"},
            {"id": "split_cards", "name": "Split Cards", "icon": "G2ICON.jpg"},
            {"id": "card_nim", "name": "Card Nim", "icon": "G3ICON.jpg"},
            {"id": "dawson_kayles", "name": "Laser Defense", "icon": "G4ICON.jpg"},
            {"id": "subtract_factor", "name": "Subtract Factor", "icon": "G5ICON.jpg"},
            {"id": "coming_soon", "name": "Coming Soon", "icon": "G6ICON.jpg"}
        ]

        buttons = {}

        # Create all buttons
        for i in range(6):
            row = i // 3
            col = i % 3
            x = grid_start_x + col * (button_size + button_spacing)
            y = grid_start_y + row * (button_size + button_spacing)

            config = button_configs[i]
            game_id = config["id"]
            icon_filename = config["icon"]

            # Get icon path
            icon_path = get_icon_path(icon_filename) if icon_filename else None

            # Create button
            btn = IconButton(x, y, button_size, config["name"], self.font_manager,
                           icon_path=icon_path, tooltip="Click to start game")

            # Disable coming_soon button
            if game_id == "coming_soon":
                btn.enabled = False
                btn.tooltip = "New game coming soon"

            buttons[game_id] = btn

        # 创建设置按钮 - 在左上角
        settings_button_size = 40
        self.settings_button = GameButton(
            20, 20,  # 左上角
            settings_button_size, settings_button_size,
            "", self.font_manager, 
            icon='settings',  # 使用齿轮图标
            tooltip="Game Settings"
        )

        # 创建兑换码按钮 - 在设置按钮旁边
        self.redeem_button = GameButton(
            70, 20,  # 设置按钮右边
            settings_button_size, settings_button_size,
            "", self.font_manager,
            icon='gift',  # 使用礼盒图标
            tooltip="Redeem CDKEY"
        )

        # 创建帮助按钮 - 在右上角
        self.help_button = GameButton(
            SCREEN_WIDTH - 60, 20,  # 右上角
            settings_button_size, settings_button_size,
            "", self.font_manager,
            icon='help',  # 使用帮助图标
            tooltip="Game Help & Guide (H)"
        )

        # Create quit button
        quit_y = grid_start_y + grid_height + 30
        quit_width = 200
        quit_x = self.layout.center_x(quit_width)
        buttons["quit"] = GameButton(quit_x, quit_y, quit_width, 60, 
                                   "Quit", self.font_manager, tooltip="Exit the game (ESC)")

        # Update button states based on available games
        self._update_button_states(buttons)

        return buttons
    
    def _update_button_states(self, buttons):
        """Update button enabled states based on available games"""
        try:
            registry = self._get_game_registry()
            registered_games = {game['id']: game for game in registry.get_available_games()}
            
            for game_id, button in buttons.items():
                if game_id in ["quit", "coming_soon"]:
                    continue
                    
                if game_id in registered_games:
                    game_info = registered_games[game_id]
                    button.tooltip = f"{game_info['description']}\nMin Players: {game_info['min_players']}, Max: {game_info['max_players']}"
                    button.enabled = True
                else:
                    # Game not registered, disable button
                    button.enabled = False
                    button.tooltip = "Game not available (check console for errors)"
        except Exception as e:
            print(f"Warning: Could not update button states: {e}")
    
    def show_error(self, message: str, duration: int = 300):
        """Show an error message on screen"""
        self.error_message = message
        self.error_timer = duration
    
    def update_performance_stats(self):
        """Update performance statistics"""
        try:
            # Get FPS and frame time from performance monitor
            stats = performance_monitor.get_performance_stats()
            self.perf_stats['fps'] = stats.get('fps', 0)
            self.perf_stats['frame_time'] = stats.get('frame_time_ms', 0)
            
            # Get cache statistics
            cache_stats = resource_cache.get_stats()
            self.perf_stats['cache_hits'] = cache_stats.get('cache_hits', 0)
            self.perf_stats['cache_misses'] = cache_stats.get('cache_misses', 0)
            self.perf_stats['cache_hit_rate'] = cache_stats.get('hit_rate', 0)
            
            # Get memory usage if available
            if hasattr(memory_optimizer, 'get_memory_usage_mb'):
                self.perf_stats['memory_usage'] = memory_optimizer.get_memory_usage_mb()
            
            # Periodic optimization
            current_time = pygame.time.get_ticks()
            if current_time - self.last_optimization_time > self.optimization_interval:
                self.last_optimization_time = current_time
                optimize_game_performance()
                
        except Exception as e:
            print(f"Warning: Error updating performance stats: {e}")
    
    @handle_game_errors
    def draw_background(self):
        """Draw background with gradient effect"""
        # Start frame profiling
        with PerformanceProfiler("menu_draw_background", performance_monitor):
            self.screen.fill(BACKGROUND_COLOR)
            
            # Subtle grid pattern (only if performance allows)
            if self.perf_stats['fps'] > 45:  # Only draw grid if we have good FPS
                for x in range(0, SCREEN_WIDTH, 40):
                    pygame.draw.line(self.screen, (35, 45, 55), (x, 0), (x, SCREEN_HEIGHT), 1)
                for y in range(0, SCREEN_HEIGHT, 40):
                    pygame.draw.line(self.screen, (35, 45, 55), (0, y), (SCREEN_WIDTH, y), 1)
    
    @handle_game_errors
    def draw_title(self):
        """Draw game title"""
        with PerformanceProfiler("menu_draw_title", performance_monitor):
            title = self.font_manager.large.render("ICG GAMES", True, TEXT_COLOR)
            subtitle = self.font_manager.medium.render("Interactive Card Games", True, ACCENT_COLOR)
            
            # Only draw shadows if performance is good
            if self.perf_stats['fps'] > 40:
                title_shadow = self.font_manager.large.render("ICG GAMES", True, SHADOW_COLOR)
                subtitle_shadow = self.font_manager.medium.render("Interactive Card Games", True, SHADOW_COLOR)
                
                self.screen.blit(title_shadow, (SCREEN_WIDTH//2 - title.get_width()//2 + 3, 83))
                self.screen.blit(subtitle_shadow, (SCREEN_WIDTH//2 - subtitle.get_width()//2 + 2, 143))
            
            self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 80))
            self.screen.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, 140))
    
    @handle_game_errors
    def handle_events(self):
        """Handle menu events with error handling"""
        with PerformanceProfiler("menu_handle_events", performance_monitor):
            mouse_pos = pygame.mouse.get_pos()
    
        # 更新按钮悬停状态
        for button in self.buttons.values():
            button.update_hover(mouse_pos)
    
        if self.settings_button:
            self.settings_button.update_hover(mouse_pos)
    
        if self.redeem_button:
            self.redeem_button.update_hover(mouse_pos)
    
        if self.help_button:
            self.help_button.update_hover(mouse_pos)
    
        # 处理所有事件
        for event in pygame.event.get():
            # 处理兑换码对话框事件（如果可见）
            if self.redeem_dialog.visible:
                redeem_result = self.redeem_dialog.handle_event(event, mouse_pos)
                if redeem_result:
                    continue
            
            # 处理帮助对话框事件
            if self.help_dialog.visible:
                # 特别是方向键和选择键，要确保帮助对话框能接收到
                if event.type == pygame.KEYDOWN:
                    # 这些键由帮助对话框处理
                    if event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, 
                                    pygame.K_RIGHT, pygame.K_RETURN, pygame.K_SPACE, 
                                    pygame.K_TAB, pygame.K_ESCAPE, pygame.K_h]:
                        if self.help_dialog.handle_event(event):
                            continue  # 如果帮助对话框处理了，继续下一个事件
                        
                # 其他事件正常传递
                if self.help_dialog.handle_event(event):
                    return True
            
            # 如果设置面板可见，优先处理设置面板事件
            if self.settings_panel.visible:
                settings_result = self.settings_panel.handle_event(event, mouse_pos)
                if settings_result == "back_from_settings":
                    self.settings_panel.hide()
                    print("🔙 Settings panel closed")
                elif settings_result and settings_result.startswith("setting_changed"):
                    print(f"⚙️ {settings_result}")
                # 设置面板处理了事件，跳过其他事件处理
                if settings_result is not None:
                    continue
            
            # 如果音乐面板可见，优先处理音乐面板事件
            if self.music_panel.visible:
                music_result = self.music_panel.handle_event(event, mouse_pos)
                if music_result == "music_panel_closed":
                    self.music_panel.hide()
                    print("🔙 Music panel closed")
                elif music_result and music_result.startswith("music_selected"):
                    print(f"🎵 {music_result}")
                # 音乐面板处理了事件，跳过其他事件处理
                if music_result is not None:
                    continue
                # 原有的帮助对话框处理
                if self.help_dialog.visible:
                    # 特别是方向键和选择键，要确保帮助对话框能接收到
                    if event.type == pygame.KEYDOWN:
                        # 这些键由帮助对话框处理
                        if event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, 
                                        pygame.K_RIGHT, pygame.K_RETURN, pygame.K_SPACE, 
                                        pygame.K_TAB, pygame.K_ESCAPE, pygame.K_h]:
                            if self.help_dialog.handle_event(event):
                                continue  # 如果帮助对话框处理了，继续下一个事件
                            
                    # 其他事件正常传递
                    if self.help_dialog.handle_event(event):
                        return True
            
            # 现有的事件处理代码
            if event.type == pygame.QUIT:
                return False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # 如果帮助对话框可见，优先由它处理
                    if self.help_dialog.visible:
                        # ESC已经在上面的help_dialog.handle_event中处理了
                        continue
                    else:
                        return False
                elif event.key == pygame.K_F2:
                        self.show_perf_overlay = not self.show_perf_overlay
                        print(f"📊 Performance overlay: {'ON' if self.show_perf_overlay else 'OFF'}")
                elif event.key == pygame.K_h:
                    self.help_dialog.toggle()
                elif event.key == pygame.K_s:  # S键打开设置面板
                    self.settings_panel.show()
                elif event.key == pygame.K_m:  # M键打开音乐面板
                    self.music_panel.toggle_visibility()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # 检查设置按钮
                if self.settings_button and self.settings_button.is_clicked(event):
                    self.settings_panel.show()
                    return True
                
                # 检查兑换码按钮
                if self.redeem_button and self.redeem_button.is_clicked(event):
                    self.redeem_dialog.show()
                    return True
                
                # 检查帮助按钮
                if self.help_button and self.help_button.is_clicked(event):
                    self.help_dialog.toggle()
                    return True

                # 如果帮助对话框可见，点击对话框外区域不应关闭菜单
                if self.help_dialog.visible:
                    # 检查是否点击在对话框内
                    if not self.help_dialog._is_inside_dialog(mouse_pos):
                        # 点击在对话框外，但不要关闭菜单，让对话框处理点击
                        continue
                    # Check performance button first
                    if self.performance_button and self.performance_button.is_clicked(event):
                        self.showing_performance = True
                        return self.show_performance_screen()                    
                # Check game buttons
                game_ids = ["take_coins", "split_cards", "card_nim", 
                           "dawson_kayles", "subtract_factor", "coming_soon"]

                for game_id in game_ids:
                    if game_id in self.buttons and self.buttons[game_id].is_clicked(event):
                        if not self.buttons[game_id].enabled:
                            self.show_error(f"Game '{game_id}' is not available. Check console for details.")
                        else:
                            self.start_game(game_id)
                        return True

                # Check quit button
                if self.buttons["quit"].is_clicked(event):
                    return False

        # Update error timer
        if self.error_timer > 0:
            self.error_timer -= 1
            if self.error_timer <= 0:
                self.error_message = None

        return True
    
    @handle_game_errors
    def start_game(self, game_id: str):
        """Start the selected game with error handling"""
        try:
            # Pre-optimization before starting game
            optimize_game_performance()
            
            registry = self._get_game_registry()
            game_info = registry.get_game(game_id)
            if game_info:
                game_class = game_info['class']
                print(f"🎯 Starting {game_info['name']}...")
                
                # Save current display mode
                current_display = pygame.display.get_surface()
                
                # Create new game instance
                game_screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                font_manager = FontManager(SCREEN_HEIGHT)
                font_manager.initialize_fonts()
                
                game_instance = game_class(game_screen, font_manager)
                
                # Enable performance monitoring for the game
                if hasattr(game_instance, 'set_performance_monitor'):
                    game_instance.set_performance_monitor(performance_monitor)
                
                # Check if user wants to return to menu
                if hasattr(game_instance, 'should_return_to_menu') and game_instance.should_return_to_menu:
                    print("↩️ Returning to main menu...")
                    return
                
                # Run the game
                print("⚡ Running game with performance monitoring...")
                game_instance.run()
                
                print("🔄 Returning to main menu...")
                # Post-game optimization
                optimize_game_performance()
                
                # Reinitialize the menu
                self.__init__()
                self.run()
            else:
                self.show_error(f"Game '{game_id}' could not be loaded.")
                
        except Exception as e:
            error_msg = f"❌ Error starting game {game_id}: {e}"
            print(error_msg)
            error_reporter.log_error("GAME_START", error_msg, game_id)
            self.show_error(f"Failed to start game. See console for details.")
            # Don't reinitialize, just return to menu
    @handle_game_errors
    def draw_background(self):
        """Draw background with gradient effect"""
        self.screen.fill(BACKGROUND_COLOR)
        
        # Subtle grid pattern
        for x in range(0, SCREEN_WIDTH, 40):
            pygame.draw.line(self.screen, (35, 45, 55), (x, 0), (x, SCREEN_HEIGHT), 1)
        for y in range(0, SCREEN_HEIGHT, 40):
            pygame.draw.line(self.screen, (35, 45, 55), (0, y), (SCREEN_WIDTH, y), 1)
    
    def draw_title(self):
        """Draw game title"""
        title = self.font_manager.large.render("ICG GAMES", True, TEXT_COLOR)
        subtitle = self.font_manager.medium.render("Interactive Card Games", True, ACCENT_COLOR)
        
        title_shadow = self.font_manager.large.render("ICG GAMES", True, SHADOW_COLOR)
        subtitle_shadow = self.font_manager.medium.render("Interactive Card Games", True, SHADOW_COLOR)
        
        self.screen.blit(title_shadow, (SCREEN_WIDTH//2 - title.get_width()//2 + 3, 103))
        self.screen.blit(subtitle_shadow, (SCREEN_WIDTH//2 - subtitle.get_width()//2 + 2, 153))
        
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
        self.screen.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, 150))
    
    def draw(self):
        """Draw the main menu with all components"""
        self.draw_background()
        self.draw_title()

        # Draw game buttons
        for button in self.buttons.values():
            button.draw(self.screen)

        # Draw top buttons
        if self.settings_button:
            self.settings_button.draw(self.screen)

        if self.redeem_button:
            self.redeem_button.draw(self.screen)

        if self.help_button:
            self.help_button.draw(self.screen)

        # Draw help dialog (if visible)
        self.help_dialog.draw(self.screen)
        
        # Draw settings panel (if visible)
        if self.settings_panel.visible:
            self.settings_panel.draw()
            
        # Draw music panel (if visible)
        if self.music_panel.visible:
            self.music_panel.draw()
            
        # Draw redeem dialog (if visible)
        if self.redeem_dialog.visible:
            self.redeem_dialog.draw()

        # Draw error message
        self.draw_error_message()

        # Draw footer
        footer_text = self.font_manager.small.render(
            f"© 2025 ICG Games - Interactive Card Games Collection | S: Settings | H: Help | M: Music | ESC: Quit", 
            True, (150, 170, 190))
        self.screen.blit(footer_text, 
                        (SCREEN_WIDTH//2 - footer_text.get_width()//2, 
                         SCREEN_HEIGHT - 40))

        pygame.display.flip()
    @handle_game_errors
    def draw_error_message(self):
        """Draw error message if any"""
        if self.error_message and self.error_timer > 0:
            # Calculate alpha based on timer
            alpha = min(255, self.error_timer * 255 // 60)  # Fade out
            
            # Create error message surface
            error_lines = self.error_message.split('\n')
            max_line_width = max(self.font_manager.small.size(line)[0] for line in error_lines)
            total_height = len(error_lines) * 25 + 20
            
            error_bg = pygame.Rect(
                SCREEN_WIDTH//2 - max_line_width//2 - 20,
                SCREEN_HEIGHT - total_height - 20,
                max_line_width + 40,
                total_height
            )
            
            # Draw semi-transparent background
            error_surface = pygame.Surface((error_bg.width, error_bg.height), pygame.SRCALPHA)
            pygame.draw.rect(error_surface, (200, 50, 50, alpha * 3 // 4), 
                           (0, 0, error_bg.width, error_bg.height), border_radius=10)
            pygame.draw.rect(error_surface, (255, 100, 100, alpha), 
                           (0, 0, error_bg.width, error_bg.height), 2, border_radius=10)
            
            self.screen.blit(error_surface, error_bg)
            
            # Draw error text
            for i, line in enumerate(error_lines):
                error_text = self.font_manager.small.render(line, True, (255, 255, 255, alpha))
                text_rect = error_text.get_rect(center=(
                    error_bg.centerx,
                    error_bg.top + 15 + i * 25
                ))
                self.screen.blit(error_text, text_rect)
    
    def run(self):
        """Run the main menu loop with error handling and performance monitoring"""
        self.running = True
        
        # Initialize performance monitor
        performance_monitor.enabled = True
        
        print("🚀 Main Menu started")
        print("📋 Available shortcuts:")
        print("   F2: Toggle performance overlay")
        print("   H: Toggle help dialog")
        print("   S: Open settings panel")
        print("   M: Open music panel")
        print("   ESC: Exit")
        
        while self.running:
            try:
                # Start frame timing
                performance_monitor.start_frame()
                
                # Update performance statistics
                self.update_performance_stats()
                
                # Handle events
                self.running = self.handle_events()
                
                # Draw
                self.draw()
                
                # End frame timing
                performance_monitor.end_frame()
                
                # Cap frame rate
                self.clock.tick(FPS)
                
                # Periodic optimization
                current_time = pygame.time.get_ticks()
                if current_time - self.last_optimization_time > self.optimization_interval:
                    self.last_optimization_time = current_time
                    optimize_game_performance()
                
            except Exception as e:
                error_msg = f"Critical error in main menu: {e}"
                print(error_msg)
                error_reporter.log_error("MAIN_MENU", error_msg)
                # Try to recover
                try:
                    self.show_error("Critical error occurred. Trying to recover...")
                    pygame.display.flip()
                    pygame.time.wait(1000)
                    # Clear cache and restart menu
                    resource_cache.clear_image_cache()
                    self.__init__()
                except:
                    # If we can't recover, exit
                    self.running = False
        
        pygame.quit()
        sys.exit()

# GameModeSelector class with enhanced error handling and performance monitoring
class GameModeSelector:
    """Game mode selection screen with error handling and performance optimization"""
    
    def __init__(self, screen, font_manager):
        self.screen = screen
        self.font_manager = font_manager
        self.selected_mode = None
        self.selected_difficulty = None
        self.error_message = None
        self.error_timer = 0
        
        # Performance monitoring
        self.show_perf_overlay = False
        
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
        
        # Add back button
        self.back_button = None
        self._create_back_button()
        
        self.mode_buttons = []
        self.difficulty_buttons = []
        self._create_mode_buttons()
    
    @handle_game_errors
    def _create_back_button(self):
        """Create back button"""
        back_button_size = 50
        self.back_button = GameButton(
            20, 20,
            back_button_size, back_button_size,
            "", self.font_manager,
            icon='back',
            tooltip="Back to main menu (ESC)"
        )
    
    @handle_game_errors
    def _create_mode_buttons(self):
        """Create game mode selection buttons"""
        button_width = min(350, self.screen.get_width() - 100)
        button_height = 80
        start_y = 200

        for i, mode in enumerate(self.modes):
            x = self.screen.get_width() // 2 - button_width // 2
            y = start_y + i * (button_height + 30)
            button = ModeButton(x, y, button_width, button_height, 
                              mode["name"], mode["value"], 
                              mode["color"], mode["hover_color"], self.font_manager)
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
        """Draw the game mode selection screen with performance optimization"""
        with PerformanceProfiler("mode_selector_draw", performance_monitor):
            self.screen.fill((25, 25, 40))
            
            # Draw title
            title = self.font_manager.large.render("Select Game Mode", True, (220, 220, 255))
            title_rect = title.get_rect(center=(self.screen.get_width()//2, 100))
            self.screen.blit(title, title_rect)
            
            # Draw description
            desc = self.font_manager.medium.render("Choose your preferred game mode", True, (180, 180, 200))
            desc_rect = desc.get_rect(center=(self.screen.get_width()//2, 150))
            self.screen.blit(desc, desc_rect)
            
            # Draw back button
            self.back_button.draw(self.screen)
            
            # Draw buttons
            for button in self.mode_buttons:
                button.draw(self.screen)
            
            # Draw performance overlay if enabled
            if self.show_perf_overlay:
                fps_text = self.font_manager.small.render(f"FPS: {pygame.time.Clock().get_fps():.1f}", 
                                                        True, (255, 255, 255))
                self.screen.blit(fps_text, (self.screen.get_width() - 100, 10))
            
            pygame.display.flip()
    
    def draw_difficulty_selection(self):
        """Draw the difficulty selection screen with performance optimization"""
        with PerformanceProfiler("difficulty_selector_draw", performance_monitor):
            self.screen.fill((25, 25, 40))
            
            # Draw title
            title = self.font_manager.large.render("Select Difficulty", True, (220, 220, 255))
            title_rect = title.get_rect(center=(self.screen.get_width()//2, 100))
            self.screen.blit(title, title_rect)
            
            # Draw back button
            self.back_button.draw(self.screen)
            
            # Draw buttons
            for button in self.difficulty_buttons:
                button.draw(self.screen)
            
            # Draw performance overlay if enabled
            if self.show_perf_overlay:
                fps_text = self.font_manager.small.render(f"FPS: {pygame.time.Clock().get_fps():.1f}", 
                                                        True, (255, 255, 255))
                self.screen.blit(fps_text, (self.screen.get_width() - 100, 10))
            
            pygame.display.flip()
    
    def handle_mode_events(self):
        """Handle game mode selection events with performance monitoring"""
        with PerformanceProfiler("mode_selector_events", performance_monitor):
            mouse_pos = pygame.mouse.get_pos()
            
            for button in self.mode_buttons:
                button.update_hover(mouse_pos)
            
            self.back_button.update_hover(mouse_pos)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "back"
                    elif event.key == pygame.K_F2:
                        self.show_perf_overlay = not self.show_perf_overlay
                
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Check back button first
                    if self.back_button.is_clicked(event):
                        return "back"
                    
                    for button in self.mode_buttons:
                        if button.hovered:
                            self.selected_mode = button.value
                            if self.selected_mode == "PVE":
                                self._create_difficulty_buttons()
                            return True
            
            return True
    
    def handle_difficulty_events(self):
        """Handle difficulty selection events with performance monitoring"""
        with PerformanceProfiler("difficulty_selector_events", performance_monitor):
            mouse_pos = pygame.mouse.get_pos()
            
            for button in self.difficulty_buttons:
                button.update_hover(mouse_pos)
            
            self.back_button.update_hover(mouse_pos)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "back"
                    elif event.key == pygame.K_F2:
                        self.show_perf_overlay = not self.show_perf_overlay
                
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.back_button.is_clicked(event):
                        return "back"
                    
                    for button in self.difficulty_buttons:
                        if button.hovered:
                            self.selected_difficulty = button.value
                            return True
            
            return True
    
    def get_game_mode(self):
        """Run the game mode selector and return selected mode with performance monitoring"""
        clock = pygame.time.Clock()
        
        while self.selected_mode is None:
            # Performance monitoring
            performance_monitor.start_frame()
            
            result = self.handle_mode_events()
            if result == "back":
                return "back"
            elif not result:
                return "PVE"
            
            self.draw_mode_selection()
            
            # End performance monitoring
            performance_monitor.end_frame()
            clock.tick(60)
        
        return self.selected_mode
    
    def get_difficulty(self):
        """Run the difficulty selector and return selected difficulty with performance monitoring"""
        if self.selected_mode != "PVE":
            return None
            
        clock = pygame.time.Clock()
        
        while self.selected_difficulty is None:
            # Performance monitoring
            performance_monitor.start_frame()
            
            result = self.handle_difficulty_events()
            if result == "back":
                return "back"
            elif not result:
                return 2
            
            self.draw_difficulty_selection()
            
            # End performance monitoring
            performance_monitor.end_frame()
            clock.tick(60)
        
        return self.selected_difficulty

class ModeButton:
    """Game mode selection button with performance optimization"""
    
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
        # Performance optimization: cache rendered text
        self._text_surface = None
        self._text_surface_needs_update = True
    
    def update_hover(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)
    
    def draw(self, surface):
        with PerformanceProfiler("mode_button_draw", performance_monitor):
            color = self.hover_color if self.hovered else self.color
            pygame.draw.rect(surface, color, self.rect, border_radius=15)
            
            # Cache text surface for performance
            if self._text_surface_needs_update or self._text_surface is None:
                self._text_surface = self.font_manager.large.render(self.text, True, (255, 255, 255))
                self._text_surface_needs_update = False
            
            text_rect = self._text_surface.get_rect(center=self.rect.center)
            surface.blit(self._text_surface, text_rect)
            
            # Draw tooltip (only if performance allows)
            if self.hovered and self.tooltip and performance_monitor.get_performance_stats().get('fps', 60) > 30:
                self.tooltip_timer += 1
                if self.tooltip_timer > 30:
                    tooltip_font = pygame.font.SysFont('Arial', 14)
                    tooltip_text = tooltip_font.render(self.tooltip, True, (255, 255, 255))
                    tooltip_rect = tooltip_text.get_rect()
                    
                    tooltip_x = self.rect.centerx - tooltip_rect.width // 2
                    tooltip_y = self.rect.top - tooltip_rect.height - 8
                    
                    tooltip_bg = pygame.Rect(tooltip_x - 6, tooltip_y - 4,
                                           tooltip_rect.width + 12, tooltip_rect.height + 8)
                    pygame.draw.rect(surface, (40, 40, 60), tooltip_bg, border_radius=6)
                    pygame.draw.rect(surface, ACCENT_COLOR, tooltip_bg, 1, border_radius=6)
                    surface.blit(tooltip_text, (tooltip_x, tooltip_y))
            else:
                self.tooltip_timer = 0

class DifficultyButton(ModeButton):
    """Difficulty selection button with performance optimization"""
    pass