"""
Splash screen animation for ICG Games
"""

import pygame
import sys
import os
import time
import math
import random

class PygameSplash:
    """Startup animation window using Pygame"""
    
    def __init__(self):
        self.screen = None
        self.clock = None
        self.progress = 0
        self.status = "Starting..."
        self.loaded_games = [False] * 5  # 5 games
        self.animation_time = 0
        
    def create_window(self):
        """Create startup window"""
        # Initialize pygame (if not yet initialized)
        if not pygame.get_init():
            pygame.init()
            
        # Set window size
        width, height = 600, 400
        
        # Create window
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("ICG Games - Starting...")
        
        # Create clock object
        self.clock = pygame.time.Clock()
        
        # Set window icon (if available)
        try:
            icon = pygame.Surface((32, 32))
            icon.fill((52, 152, 219))
            pygame.display.set_icon(icon)
        except:
            pass
        
        return self.screen
    
    def draw_window(self):
        """Draw window content"""
        if not self.screen:
            return
            
        width, height = self.screen.get_size()
        
        # Background color
        bg_color = (44, 62, 80)  # Dark blue
        text_color = (236, 240, 241)  # White
        accent_color = (52, 152, 219)  # Blue
        success_color = (46, 204, 113)  # Green
        gray_color = (127, 140, 141)  # Gray
        
        # Fill background
        self.screen.fill(bg_color)
        
        # Use default font
        try:
            title_font = pygame.font.Font(None, 48)
            subtitle_font = pygame.font.Font(None, 24)
            status_font = pygame.font.Font(None, 20)
            small_font = pygame.font.Font(None, 16)
        except:
            title_font = pygame.font.Font(pygame.font.get_default_font(), 48)
            subtitle_font = pygame.font.Font(pygame.font.get_default_font(), 24)
            status_font = pygame.font.Font(pygame.font.get_default_font(), 20)
            small_font = pygame.font.Font(pygame.font.get_default_font(), 16)
        
        # Title
        title_text = title_font.render("ICG Games", True, text_color)
        title_rect = title_text.get_rect(center=(width//2, 60))
        self.screen.blit(title_text, title_rect)
        
        # Subtitle
        subtitle_text = subtitle_font.render("Impartial Combinatorial Games Collection", True, accent_color)
        subtitle_rect = subtitle_text.get_rect(center=(width//2, 100))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Separator line
        pygame.draw.line(self.screen, accent_color, (50, 130), (width-50, 130), 2)
        
        # Game icons area
        game_names = ["Take Coins", "Split Cards", "Card Nim", "Laser Defense", "Subtract Factor"]
        icon_y = 170
        
        for i, name in enumerate(game_names):
            x = width//2 - 200 + i * 100
            
            # 根据进度判断是否显示打勾
            should_show_check = self.progress >= ((i + 1) * 20)
            
            if not should_show_check:
                # Rotating loading circle
                angle = self.animation_time * 2 + i * 0.5
                radius = 15
                center_x = x
                center_y = icon_y
                
                # Draw rotating points
                point_angle = angle
                for _ in range(3):
                    point_x = center_x + math.cos(point_angle) * radius
                    point_y = center_y + math.sin(point_angle) * radius
                    pygame.draw.circle(self.screen, accent_color, (int(point_x), int(point_y)), 4)
                    point_angle += math.pi * 2 / 3
                
                # Game name (gray)
                name_text = small_font.render(name, True, gray_color)
                name_rect = name_text.get_rect(center=(x, icon_y + 40))
                self.screen.blit(name_text, name_rect)
            else:
                # Loaded game (green circle)
                pygame.draw.circle(self.screen, success_color, (x, icon_y), 20, 3)
                
                # Draw checkmark
                pygame.draw.line(self.screen, success_color, 
                               (x - 8, icon_y - 2), (x - 2, icon_y + 4), 3)
                pygame.draw.line(self.screen, success_color,
                               (x - 2, icon_y + 4), (x + 8, icon_y - 8), 3)
                
                # Game name (green)
                name_text = small_font.render(name, True, success_color)
                name_rect = name_text.get_rect(center=(x, icon_y + 40))
                self.screen.blit(name_text, name_rect)
        
        # Progress bar background
        progress_y = 250
        progress_width = width - 100
        pygame.draw.rect(self.screen, (52, 73, 94), (50, progress_y, progress_width, 20), border_radius=10)
        
        # Progress bar foreground
        if self.progress > 0:
            bar_width = progress_width * (self.progress / 100)
            
            # Add progress bar animation effect
            pulse = math.sin(self.animation_time * 3) * 0.1 + 0.9
            bar_color = (
                int(52 * pulse),
                int(152 * pulse),
                int(219 * pulse)
            )
            
            pygame.draw.rect(self.screen, bar_color, (50, progress_y, bar_width, 20), border_radius=10)
        
        # Progress text
        progress_text = status_font.render(f"Progress: {int(self.progress)}%", True, accent_color)
        progress_rect = progress_text.get_rect(center=(width//2, progress_y + 35))
        self.screen.blit(progress_text, progress_rect)
        
        # Status text
        status_text = status_font.render(self.status, True, text_color)
        status_rect = status_text.get_rect(center=(width//2, progress_y + 55))
        self.screen.blit(status_text, status_rect)
        
        # Bottom info
        version_text = small_font.render("Version 1.0.0 | © 2025 ICG Games", True, gray_color)
        self.screen.blit(version_text, (20, height - 40))
        
        # Loading tips
        tips = ["Optimizing game performance...", "Preparing game resources...", 
                "Initializing AI opponent...", "Setting game rules..."]
        tip_index = int(self.animation_time * 0.5) % len(tips)
        tip_text = small_font.render(f"Tip: {tips[tip_index]}", True, (149, 165, 166))
        tip_rect = tip_text.get_rect(right=width - 20, bottom=height - 40)
        self.screen.blit(tip_text, tip_rect)
        
        # Update display
        pygame.display.flip()
    
    def update_progress(self, progress, status, game_index=None):
        """Update progress"""
        self.progress = progress
        self.status = status
        
        if game_index is not None and game_index < len(self.loaded_games):
            self.loaded_games[game_index] = True
        
        # Draw updates
        self.draw_window()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
        
        return True
    
    def run_animation(self):
        """Run animation loop with spacebar skip functionality"""
        self.create_window()
        
        # Animation steps
        steps = [
            (20, "Loading Take Coins game module..."),
            (40, "Loading Split Cards game module..."),
            (60, "Loading Card Nim game module..."),
            (80, "Loading Laser Defense game module..."),
            (100, "Loading Subtract Factor game module...")
        ]
        
        running = True
        start_time = time.time()
        skip_animation = False
        
        for target_progress, status in steps:
            while self.progress < target_progress and running and not skip_animation:
                # Update time
                self.animation_time = (time.time() - start_time) * 2

                # 改进的随机增量：更大的波动范围 + 偶尔的跳跃
                if random.random() < 0.15:  # 15%的概率出现大跳跃
                    random_increment = random.uniform(3.0, 8.0)
                else:
                    random_increment = random.uniform(0.1, 3.0)
                
                # 在接近目标时减慢
                remaining = target_progress - self.progress
                if remaining < 5:
                    random_increment = random_increment * (remaining / 5)
                
                self.progress = min(target_progress, self.progress + random_increment)
                self.status = status
                
                # Draw window
                self.draw_window()
                
                # Control frame rate
                self.clock.tick(60)
                
                # Handle events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            running = False
                        elif event.key == pygame.K_SPACE:
                            skip_animation = True
                            print("Space pressed - skipping animation")
                
                if not skip_animation:
                    time.sleep(0.02)
            
            # If skipping animation, immediately complete
            if skip_animation:
                self.progress = 100
                self.status = "Skipping to main menu..."
                self.draw_window()
                time.sleep(0.5)
                break
            
            if not running:
                break
        
        # Brief pause after completion
        if running and not skip_animation:
            for _ in range(30):
                self.animation_time = (time.time() - start_time) * 2
                self.draw_window()
                self.clock.tick(60)
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            running = False
                        elif event.key == pygame.K_SPACE:
                            skip_animation = True
                            break
                
                if not running or skip_animation:
                    break
                
                time.sleep(0.033)
        
        return running
    
    def close(self):
        """Close window with fade out effect"""
        if self.screen:
            # Fade out effect
            for alpha in range(255, 0, -10):
                fade_surface = pygame.Surface(self.screen.get_size())
                fade_surface.fill((44, 62, 80))
                fade_surface.set_alpha(alpha)
                self.screen.blit(fade_surface, (0, 0))
                pygame.display.flip()
                time.sleep(0.01)
            
            # Close display
            pygame.display.quit()