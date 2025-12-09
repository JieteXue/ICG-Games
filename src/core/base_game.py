"""
Base game class that all games should inherit from
"""

import pygame
from abc import ABC, abstractmethod

class BaseGame(ABC):
    """Abstract base class for all games"""
    
    def __init__(self, screen, font_manager):
        self.screen = screen
        self.font_manager = font_manager
        self.running = True
        self.clock = pygame.time.Clock()
        self.key_repeat_enabled = True
        
    @abstractmethod
    def handle_events(self):
        """Handle game events - must be implemented by subclass"""
        pass
    
    @abstractmethod
    def update(self):
        """Update game state - must be implemented by subclass"""
        pass
    
    @abstractmethod
    def draw(self):
        """Draw game - must be implemented by subclass"""
        pass
    
    @abstractmethod
    def get_game_info(self):
        """Return game information for display"""
        pass
    
    def update_key_repeat(self):
        """Update key repeat state - subclasses can override this"""
        if hasattr(self, 'input_handler') and hasattr(self.input_handler, 'update_key_repeat'):
            self.input_handler.update_key_repeat()
    
    def run(self):
        """Main game loop with built-in key repeat support"""
        self.running = True
        while self.running:
            if not self.handle_events():
                break
            self.update()
            
            if self.key_repeat_enabled:
                self.update_key_repeat()
                
            self.draw()
            self.clock.tick(60)