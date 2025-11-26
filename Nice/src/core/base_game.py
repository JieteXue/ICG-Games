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
    
    def run(self):
        """Main game loop"""
        self.running = True
        while self.running:
            if not self.handle_events():
                break
            self.update()
            self.draw()
            self.clock.tick(60)