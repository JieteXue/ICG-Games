"""
Simple icon renderer for UI buttons
Uses pygame to draw icons directly
"""

import pygame
import math

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
    def render_settings_icon(size=32, color=(255, 255, 255)):
        """Render a settings/gear icon"""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Draw gear
        center = (size // 2, size // 2)
        radius = size // 3
        
        # Draw gear center circle
        pygame.draw.circle(surface, color, center, radius // 2, 2)
        
        # Draw gear teeth
        for i in range(8):
            angle = i * math.pi / 4
            # Outer points
            outer_radius = radius
            x1 = center[0] + outer_radius * math.cos(angle)
            y1 = center[1] + outer_radius * math.sin(angle)
            
            # Inner points
            inner_radius = radius * 0.7
            x2 = center[0] + inner_radius * math.cos(angle)
            y2 = center[1] + inner_radius * math.sin(angle)
            
            # Draw gear tooth as a small rectangle
            tooth_width = size // 12
            pygame.draw.polygon(surface, color, [
                (x1 - tooth_width//2 * math.cos(angle + math.pi/2), 
                 y1 - tooth_width//2 * math.sin(angle + math.pi/2)),
                (x1 + tooth_width//2 * math.cos(angle + math.pi/2), 
                 y1 + tooth_width//2 * math.sin(angle + math.pi/2)),
                (x2 + tooth_width//2 * math.cos(angle + math.pi/2), 
                 y2 + tooth_width//2 * math.sin(angle + math.pi/2)),
                (x2 - tooth_width//2 * math.cos(angle + math.pi/2), 
                 y2 - tooth_width//2 * math.sin(angle + math.pi/2))
            ])
        
        return surface
    
    @staticmethod
    def render_gift_icon(size=32, color=(255, 255, 255)):
        """Render a gift/box icon"""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Draw gift box
        box_width = size // 2
        box_height = size // 2
        box_x = (size - box_width) // 2
        box_y = (size - box_height) // 2
        
        # Draw box
        pygame.draw.rect(surface, color, 
                        (box_x, box_y, box_width, box_height), 
                        2, border_radius=size//16)
        
        # Draw ribbon
        # Horizontal ribbon
        pygame.draw.line(surface, color, 
                        (box_x, box_y + box_height//2),
                        (box_x + box_width, box_y + box_height//2), 3)
        
        # Vertical ribbon
        pygame.draw.line(surface, color,
                        (box_x + box_width//2, box_y),
                        (box_x + box_width//2, box_y + box_height), 3)
        
        # Draw ribbon bow in center
        center_x = box_x + box_width // 2
        center_y = box_y + box_height // 2
        bow_size = size // 8
        
        # Left bow loop
        pygame.draw.ellipse(surface, color,
                           (center_x - bow_size - bow_size//2, 
                            center_y - bow_size//2,
                            bow_size, bow_size))
        
        # Right bow loop
        pygame.draw.ellipse(surface, color,
                           (center_x + bow_size//2, 
                            center_y - bow_size//2,
                            bow_size, bow_size))
        
        # Center knot
        pygame.draw.circle(surface, color, (center_x, center_y), bow_size//3)
        
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
            'control_small': lambda s, c: IconRenderer.render_controls_icon(s*3//4, c),
            # 新增图标映射
            'settings': IconRenderer.render_settings_icon,
            'gift': IconRenderer.render_gift_icon,
        }
        
        if icon_name in icon_map:
            return icon_map[icon_name](size, color)
        
        # Default to help icon
        return IconRenderer.render_help_icon(size, color)