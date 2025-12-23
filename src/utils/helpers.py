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
    def __init__(self, screen_height):
        self.screen_height = screen_height
        self.small = None
        self.medium = None
        self.large = None
        
    def initialize_fonts(self):
        """Initialize fonts with default settings"""
        try:
            # 尝试加载字体文件
            import os
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_dir))
            
            # 查找字体文件
            possible_fonts = [
                os.path.join(project_root, 'assets', 'fonts', 'Arial.ttf'),
                os.path.join(project_root, 'fonts', 'arial.ttf'),
                os.path.join(current_dir, 'arial.ttf'),
                'arial.ttf'
            ]
            
            font_path = None
            for path in possible_fonts:
                if os.path.exists(path):
                    font_path = path
                    break
            
            if font_path:
                # 计算字体大小
                font_size_small = max(18, int(self.screen_height * 0.02))
                font_size_medium = max(24, int(self.screen_height * 0.03))
                font_size_large = max(36, int(self.screen_height * 0.04))
                
                self.small = pygame.font.Font(font_path, font_size_small)
                self.medium = pygame.font.Font(font_path, font_size_medium)
                self.large = pygame.font.Font(font_path, font_size_large)
            else:
                # 使用系统默认字体
                self.small = pygame.font.SysFont(None, 24)
                self.medium = pygame.font.SysFont(None, 32)
                self.large = pygame.font.SysFont(None, 48)
                
        except Exception as e:
            print(f"Error loading fonts: {e}")
            # 使用默认字体
            self.small = pygame.font.SysFont(None, 24)
            self.medium = pygame.font.SysFont(None, 32)
            self.large = pygame.font.SysFont(None, 48)
    
    def ensure_initialized(self):
        """Ensure fonts are initialized (alias for initialize_fonts)"""
        if self.small is None or self.medium is None or self.large is None:
            self.initialize_fonts()
    
    def get_font(self, size_name):
        """Get font by size name"""
        self.ensure_initialized()
        if size_name == 'small':
            return self.small
        elif size_name == 'medium':
            return self.medium
        elif size_name == 'large':
            return self.large
        else:
            return self.medium