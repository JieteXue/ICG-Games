"""
Universal Game Manager Base Class - Updated with sidebar integration
"""

import pygame
from abc import ABC, abstractmethod
from .base_game import BaseGame
from utils.constants import *
from ui.menus import GameModeSelector
from ui.components import Sidebar  # 修改：只导入 Sidebar
from ui import InfoDialog  # 修改：从 ui 导入 InfoDialog
from utils.config_manager import config_manager
from utils.error_handler import handle_game_errors, log_logic_error
from utils.resource_cache import resource_cache
from utils.performance_monitor import performance_monitor, PerformanceProfiler

class GameManager(BaseGame):
    """Universal Game Manager - contains common functionality for all games"""
    
    def __init__(self, screen, font_manager):
        super().__init__(screen, font_manager)
        self.should_return_to_menu = False
        
        # Common components
        self.logic = None
        self.ui = None
        self.input_handler = None
        
        # New sidebar and info dialog components
        self.sidebar = Sidebar(screen, font_manager)  # 新增
        self.info_dialog = InfoDialog(screen, font_manager)  # 新增
        
        # Common states
        self.buttons = {}
        self.ai_timer = 0
        self.ai_delay_frames = 30
        
        # Game configuration
        self.game_config = None
        self.user_prefs = config_manager.get_user_preferences()
        
        # Performance monitoring
        self.show_perf_overlay = False
        self.perf_update_timer = 0
        
        # Ensure fonts are initialized
        self.font_manager.initialize_fonts()
        
        # Game instructions (to be set by specific games)
        self.game_instructions = ""
    
    def set_game_instructions(self, instructions):
        """Set game instructions for the info dialog"""
        self.game_instructions = instructions
        self.info_dialog.instructions = instructions
    
    @handle_game_errors
    def initialize_game_settings(self):
        """Universal game settings initialization with config manager"""
        try:
            selector = GameModeSelector(self.screen, self.font_manager)
            game_mode = selector.get_game_mode()
            
            if game_mode == "back":
                self.should_return_to_menu = True
                return
            
            if game_mode == "PVE":
                difficulty = selector.get_difficulty()
                if difficulty == "back":
                    self.should_return_to_menu = True
                    return
                
                # Load game configuration
                game_id = self._get_game_id()
                if game_id:
                    self.game_config = config_manager.get_game_config(game_id)
                    if self.game_config:
                        # Configure AI delay based on difficulty
                        difficulty_settings = config_manager.get_difficulty_settings(game_id, difficulty)
                        ai_delay_ms = difficulty_settings.get('ai_delay_ms', 500)
                        self.ai_delay_frames = max(10, ai_delay_ms // (1000 // CARD_GAME_FPS))
                
                self.logic.initialize_game("PVE", difficulty)
            else:
                self.logic.initialize_game("PVP")
                
        except Exception as e:
            log_logic_error(f"Error initializing game settings: {e}", str(self.__class__))
            print(f"Error initializing game settings: {e}")
            self.logic.initialize_game("PVE", 2)
    
    def _get_game_id(self) -> str:
        """Get the game ID from the class name or other identifier"""
        # Default implementation, can be overridden
        class_name = self.__class__.__name__.lower()
        if 'game' in class_name:
            return class_name.replace('game', '').strip('_')
        return class_name
    
    @abstractmethod
    def create_components(self):
        """Create game-specific components - must be implemented by subclass"""
        pass
    
    @handle_game_errors
    def handle_events(self):
        """Default event handling with sidebar integration"""
        with PerformanceProfiler("event_handling", performance_monitor):
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                
                # Handle sidebar events first
                sidebar_result = self.sidebar.handle_event(event, mouse_pos)
                if sidebar_result:
                    return self._handle_sidebar_action(sidebar_result)
                
                # Handle info dialog events
                if self.info_dialog.visible:
                    dialog_result = self.info_dialog.handle_event(event, mouse_pos)
                    if dialog_result in ["close", "close_outside"]:
                        continue  # Dialog was closed, continue with other events
                    elif dialog_result:
                        return True  # Event was handled by dialog
                
                # Handle other events (ESC for back, F2 for performance, etc.)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "back"
                    elif event.key == pygame.K_F2:
                        self.show_perf_overlay = not self.show_perf_overlay
                    elif event.key == pygame.K_i and not self.info_dialog.visible:
                        # Show info dialog when I key is pressed
                        game_name = getattr(self, 'game_name', self._get_game_id().title())
                        self.info_dialog.show(game_name, self.game_instructions)
                        return True
                
                # Handle game-specific events if not in dialog
                if not self.info_dialog.visible:
                    # Delegate to subclass or specific handler
                    result = self._handle_game_specific_events(event)
                    if result is not None:
                        return result
            
            return True
    def _handle_sidebar_action(self, action):
        """处理侧边栏按钮点击"""
        if action == "toggle":
            return True
        elif action == "back":
            self.initialize_game_settings()
            return True
        elif action == "home":
            return False  # 返回主菜单
        elif action == "refresh":
            # 重启游戏
            game_mode = getattr(self.logic, 'game_mode', "PVE")
            difficulty = getattr(self.logic, 'difficulty', 2)
            winning_hints = getattr(self.logic, 'winning_hints_enabled', False)
            self.logic.initialize_game(game_mode, difficulty, winning_hints)
            return True
        elif action == "info":
            self.showing_instructions = True
            return True
        elif action == "settings_opened":
            return True  # 设置面板已打开，不需要额外处理
        elif action == "settings_closed":
            return True  # 设置面板已关闭
        elif action == "music_panel_toggled":
            return True
        elif action == "music_panel_closed":
            return True
        elif action.startswith("music_selected_"):
            music_id = int(action.replace("music_selected_", ""))
            print(f"Music {music_id} selected")
            return True
        elif action == "music_locked":
            # 显示解锁提示
            self.logic.message = "This music is locked! Complete achievements to unlock."
            return True
        elif action.startswith("setting_changed_"):
            # 处理设置变化
            setting_name = action.replace("setting_changed_", "")
            if setting_name == "winning_hints":
                # 获取当前的winning_hints值
                winning_hints = self.sidebar.settings_panel.settings.get('winning_hints', False)
                # 更新游戏逻辑中的设置
                self.logic.winning_hints_enabled = winning_hints
                # 显示反馈消息
                if winning_hints:
                    self.logic.message = "Winning Hints enabled! Click on hint button for guidance."
                else:
                    self.logic.message = "Winning Hints disabled."
            elif setting_name == "background_music":
                # 处理背景音乐开关
                music_enabled = self.sidebar.settings_panel.settings.get('background_music', True)
                if music_enabled:
                    # 启用音乐
                    from utils.music_manager import music_manager
                    if music_manager.is_music_enabled() and music_manager.get_current_music_index() >= 0:
                        # 重新播放音乐
                        music_manager.play_music(music_manager.get_current_music_index())
                    self.logic.message = "Background music enabled"
                else:
                    # 禁用音乐
                    from utils.music_manager import music_manager
                    music_manager.stop_music()
                    self.logic.message = "Background music disabled"
            return True
        elif action == "sponsor_clicked":
            print("Sponsor link clicked")
            return True
        return True
    
    def _handle_game_specific_events(self, event):
        """Handle game-specific events - to be overridden by subclasses"""
        return None
    
    @handle_game_errors
    def update(self):
        """Update game state with sidebar"""
        self.sidebar.update()
        
        if not self.logic.game_over:
            self.update_ai_turn()
            self.update_button_states()
    
    @handle_game_errors
    def draw(self):
        """Draw game interface with sidebar"""
        self.screen.fill(BACKGROUND_COLOR)
        
        # Draw sidebar (always on top)
        self.sidebar.draw()
        
        # Draw game content (adjust for sidebar width)
        content_offset = self.sidebar.current_width
        self._draw_game_content(content_offset)
        
        # Draw info dialog if visible (on top of everything)
        if self.info_dialog.visible:
            self.info_dialog.draw()
        
        # Draw performance overlay if enabled
        if self.show_perf_overlay:
            performance_monitor.draw_performance_overlay(self.screen, self.font_manager.small)
    
    def _draw_game_content(self, offset):
        """Draw game-specific content - to be overridden by subclasses"""
        pass
    
    @handle_game_errors
    def run(self):
        """Universal game loop with sidebar support"""
        if self.should_return_to_menu:
            return
        
        self.running = True
        while self.running:
            # Start frame timing
            performance_monitor.start_frame()
            
            try:
                # Handle events with timing
                with PerformanceProfiler("event_processing", performance_monitor):
                    result = self.handle_events()
                    
                    if result == False:
                        break
                    elif result == "back":
                        self.initialize_game_settings()
                        continue
                    elif result == "home":
                        break
                    elif result == "refresh":
                        # Recreate components for refresh
                        self.create_components()
                        continue
                
                # Update game state with timing
                with PerformanceProfiler("game_update", performance_monitor):
                    self.update()
                
                # Update key repeat if enabled
                if self.key_repeat_enabled:
                    self.update_key_repeat()
                
                # Draw with timing
                with PerformanceProfiler("game_draw", performance_monitor):
                    self.draw()
                
                # End frame timing
                performance_monitor.end_frame()
                
                # Cap frame rate
                self.clock.tick(CARD_GAME_FPS)
                
            except Exception as e:
                log_logic_error(f"Error in game loop: {e}", str(self.__class__))
                # Try to recover
                self.screen.fill((50, 0, 0))
                error_text = self.font_manager.medium.render("Game Error - Trying to recover...", 
                                                           True, (255, 255, 255))
                self.screen.blit(error_text, (SCREEN_WIDTH//2 - error_text.get_width()//2, 
                                           SCREEN_HEIGHT//2))
                pygame.display.flip()
                pygame.time.wait(1000)
                
                # Try to restart the game
                try:
                    if hasattr(self.logic, 'initialize_game'):
                        game_mode = getattr(self.logic, 'game_mode', "PVE")
                        difficulty = getattr(self.logic, 'difficulty', 2)
                        self.logic.initialize_game(game_mode, difficulty)
                except:
                    # If we can't recover, exit
                    break
    
    def get_performance_stats(self):
        """Get performance statistics for this game"""
        return performance_monitor.get_performance_stats()