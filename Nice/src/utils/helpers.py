"""
Utility functions and helpers
"""

import pygame

def wrap_text(text, font, max_width):
    """Wrap text to fit within max_width"""
    words = text.split(' ')
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        test_width = font.size(test_line)[0]
        
        if test_width <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return lines

class FontManager:
    """Manages all fonts in the game"""
    def __init__(self, screen_height=None):
        # 延迟初始化字体，直到pygame完全初始化
        self._screen_height = screen_height
        self._fonts_initialized = False
        self.large = None
        self.medium = None
        self.small = None
    
    def initialize_fonts(self):
        """初始化字体（在pygame初始化后调用）"""
        if self._fonts_initialized:
            return
            
        if self._screen_height:
            self.large = pygame.font.SysFont('Arial', max(28, self._screen_height // 25), bold=True)
            self.medium = pygame.font.SysFont('Arial', max(18, self._screen_height // 32))
            self.small = pygame.font.SysFont('Arial', max(14, self._screen_height // 40))
        else:
            # 后备字体大小
            self.large = pygame.font.SysFont('Arial', 32, bold=True)
            self.medium = pygame.font.SysFont('Arial', 24)
            self.small = pygame.font.SysFont('Arial', 16)
        
        self._fonts_initialized = True
    
    def ensure_initialized(self):
        """确保字体已初始化"""
        if not self._fonts_initialized:
            self.initialize_fonts()