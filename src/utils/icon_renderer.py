"""
Simple icon renderer for UI buttons
Uses pygame to draw icons directly
"""

import pygame

class IconRenderer:
    """Renders simple icons using pygame drawing functions"""
    
    @staticmethod
    def render_help_icon(size=32, color=(255, 255, 255)):
        """Render a help/question mark icon"""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Draw circle
        pygame.draw.circle(surface, color, (size//2, size//2), size//2 - 2, 2)
        
        # Draw question mark
        font = pygame.font.SysFont('Arial', size//2, bold=True)
        text = font.render("?", True, color)
        text_rect = text.get_rect(center=(size//2, size//2))
        surface.blit(text, text_rect)
        
        return surface
    
    @staticmethod
    def render_info_icon(size=32, color=(255, 255, 255)):
        """Render an info icon"""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Draw circle
        pygame.draw.circle(surface, color, (size//2, size//2), size//2 - 2, 2)
        
        # Draw 'i'
        font = pygame.font.SysFont('Arial', size//2, bold=True)
        text = font.render("i", True, color)
        text_rect = text.get_rect(center=(size//2, size//2))
        surface.blit(text, text_rect)
        
        return surface
    
    @staticmethod
    def render_performance_icon(size=32, color=(255, 255, 255)):
        """Render a performance/lightning bolt icon"""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Draw simplified lightning bolt
        points = [
            (size//2, size//4),
            (size*3//4, size//2),
            (size//2, size//2),
            (size*3//4, size*3//4),
            (size//2, size*3//4),
            (size//4, size//2)
        ]
        pygame.draw.polygon(surface, color, points)
        
        return surface
    
    @staticmethod
    def render_close_icon(size=32, color=(255, 100, 100)):
        """Render a close/X icon"""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Draw X
        pygame.draw.line(surface, color, 
                        (size//4, size//4), 
                        (size*3//4, size*3//4), 3)
        pygame.draw.line(surface, color, 
                        (size*3//4, size//4), 
                        (size//4, size*3//4), 3)
        
        return surface
    
    @staticmethod
    def render_back_icon(size=32, color=(255, 255, 255)):
        """Render a back/arrow icon"""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Draw arrow
        points = [
            (size*3//4, size//4),
            (size//4, size//2),
            (size*3//4, size*3//4)
        ]
        pygame.draw.polygon(surface, color, points)
        
        return surface
    
    @staticmethod
    def render_game_icon(size=32, color=(255, 255, 255)):
        """Render a game controller icon"""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Draw controller body
        pygame.draw.rect(surface, color, 
                        (size//4, size//4, size//2, size//2), 
                        2, border_radius=size//8)
        
        # Draw buttons
        pygame.draw.circle(surface, color, (size//3, size//3), size//10)
        pygame.draw.circle(surface, color, (size*2//3, size//3), size//10)
        pygame.draw.circle(surface, color, (size//3, size*2//3), size//10)
        pygame.draw.circle(surface, color, (size*2//3, size*2//3), size//10)
        
        return surface
    
    @staticmethod
    def render_controls_icon(size=32, color=(255, 255, 255)):
        """Render a keyboard/mouse controls icon"""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Draw keyboard
        pygame.draw.rect(surface, color, 
                        (size//4, size//3, size//2, size//6), 
                        2, border_radius=size//16)
        
        # Draw mouse
        pygame.draw.rect(surface, color, 
                        (size//2 - size//8, size*2//3, 
                         size//4, size//6), 
                         2, border_radius=size//16)
        
        return surface
    
    @staticmethod
    def get_icon(icon_name, size=32, color=(255, 255, 255)):
        """Get icon by name"""
        icon_map = {
            'help': IconRenderer.render_help_icon,
            'info': IconRenderer.render_info_icon,
            'performance': IconRenderer.render_performance_icon,
            'close': IconRenderer.render_close_icon,
            'back': IconRenderer.render_back_icon,
            'game': IconRenderer.render_game_icon,
            'controls': IconRenderer.render_controls_icon,
            'game_small': lambda s, c: IconRenderer.render_game_icon(s*3//4, c),
            'control_small': lambda s, c: IconRenderer.render_controls_icon(s*3//4, c)
        }
        
        if icon_name in icon_map:
            return icon_map[icon_name](size, color)
        
        # Default to help icon
        return IconRenderer.render_help_icon(size, color)