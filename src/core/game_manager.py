"""
Universal Game Manager Base Class - Updated with performance monitoring
"""

import pygame
from abc import ABC, abstractmethod
from .base_game import BaseGame
from utils.constants import *
from ui.menus import GameModeSelector
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
        
        # Common states
        self.buttons = {}
        self.ai_timer = 0
        self.ai_delay_frames = 30  # Default, can be overridden
        
        # Game configuration
        self.game_config = None
        self.user_prefs = config_manager.get_user_preferences()
        
        # Performance monitoring
        self.show_perf_overlay = False
        self.perf_update_timer = 0
        
        # Ensure fonts are initialized
        self.font_manager.initialize_fonts()
    
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
    def update_ai_turn(self):
        """Universal AI turn update with configurable delay"""
        if (hasattr(self.logic, 'game_mode') and 
            self.logic.game_mode == "PVE" and 
            hasattr(self.logic, 'current_player') and
            self.logic.current_player == "AI" and 
            not self.logic.game_over):
            
            self.ai_timer += 1
            if self.ai_timer > self.ai_delay_frames:
                with PerformanceProfiler("ai_update", performance_monitor):
                    self.logic.ai_make_move()
                self.ai_timer = 0
    
    @handle_game_errors
    def update_button_states(self):
        """Universal button states update"""
        if hasattr(self.logic, 'game_mode') and hasattr(self.logic, 'current_player'):
            if self.logic.game_mode == "PVE":
                buttons_enabled = (self.logic.current_player == "Player 1")
            else:
                buttons_enabled = True
            
            # Update control buttons
            if "confirm" in self.buttons:
                can_confirm = hasattr(self.logic, 'selected_position') or hasattr(self.logic, 'selected_factor')
                self.buttons["confirm"].enabled = buttons_enabled and can_confirm
    
    @handle_game_errors
    def draw_navigation_buttons(self):
        """Universal navigation buttons drawing"""
        nav_buttons = ["back", "home", "refresh"]
        for btn_name in nav_buttons:
            if btn_name in self.buttons:
                self.buttons[btn_name].draw(self.screen)
    
    @handle_game_errors
    def handle_navigation_events(self, event):
        """Universal navigation events handling"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if "refresh" in self.buttons and self.buttons["refresh"].is_clicked(event):
                # Restart game logic
                game_mode = getattr(self.logic, 'game_mode', "PVE")
                difficulty = getattr(self.logic, 'difficulty', 2)
                self.logic.initialize_game(game_mode, difficulty)
                if hasattr(self.ui, 'scroll_offset'):
                    self.ui.scroll_offset = 0
                return "refresh"
            
            if "back" in self.buttons and self.buttons["back"].is_clicked(event):
                return "back"
            elif "home" in self.buttons and self.buttons["home"].is_clicked(event):
                return "home"
        
        # Toggle performance overlay with F2
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_F2:
            self.show_perf_overlay = not self.show_perf_overlay
        
        return None
    
    @handle_game_errors
    def handle_events(self):
        """Default event handling - subclasses should override"""
        with PerformanceProfiler("event_handling", performance_monitor):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_F2:
                    self.show_perf_overlay = not self.show_perf_overlay
        
        return True
    
    @handle_game_errors
    def update(self):
        """Default update - subclasses should override"""
        pass
    
    @handle_game_errors
    def draw(self):
        """Default draw - subclasses should override"""
        self.screen.fill(BACKGROUND_COLOR)
        
        # Draw performance overlay if enabled
        if self.show_perf_overlay:
            performance_monitor.draw_performance_overlay(self.screen, self.font_manager.small)
    
    @handle_game_errors
    def run(self):
        """Universal game loop with performance monitoring"""
        if self.should_return_to_menu:
            return
        
        self.running = True
        while self.running:
            # Start frame timing
            performance_monitor.start_frame()
            
            try:
                # Handle events with timing
                with PerformanceProfiler("event_processing", performance_monitor):
                    if not self.handle_events():
                        break
                
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