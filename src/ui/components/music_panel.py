"""
Music Panel Component for Music Selection
"""

import pygame
import os
from utils.constants import *

class MusicPanel:
    """Music selection panel overlay"""
    
    def __init__(self, screen, font_manager, music_manager):
        self.screen = screen
        self.font_manager = font_manager
        self.music_manager = music_manager
        self.visible = False
        
        # Panel dimensions
        self.panel_width = 400
        self.panel_height = 300
        self.panel_x = (SCREEN_WIDTH - self.panel_width) // 2
        self.panel_y = (SCREEN_HEIGHT - self.panel_height) // 2
        
        # Music list
        self.music_list = [
            {"id": 0, "name": "Flower Dance", "artist": "Jaycd", "unlocked": True},
            {"id": 1, "name": "reminisce", "artist": "Aqualina", "unlocked": True},
            {"id": 2, "name": "Summer", "artist": "CNK", "unlocked": True},
            {"id": 3, "name": "quantum", "artist": "bbrother", "unlocked": False}
        ]
        
        self.selected_index = 0
        self.music_buttons = []
        self.create_music_buttons()
    
    def create_music_buttons(self):
        """Create music selection buttons"""
        start_y = self.panel_y + 100
        button_height = 50
        button_spacing = 10
        
        for i, music in enumerate(self.music_list):
            button_y = start_y + i * (button_height + button_spacing)
            button = MusicButton(
                self.panel_x + 50,
                button_y,
                self.panel_width - 100,
                button_height,
                music,
                self.font_manager,
                i == self.selected_index
            )
            self.music_buttons.append(button)
    
    def show(self):
        """Show the music panel"""
        self.visible = True
        # 加载当前选择的音乐索引
        self.selected_index = self.music_manager.get_current_music_index()
        self.update_selection()
    
    def hide(self):
        """Hide the music panel"""
        self.visible = False
    
    def toggle_visibility(self):
        """Toggle the visibility of the music panel"""
        self.visible = not self.visible
        if self.visible:
            self.selected_index = self.music_manager.get_current_music_index()
            self.update_selection()
    
    def handle_event(self, event, mouse_pos):
        """Handle events for the music panel"""
        if not self.visible:
            return None
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check music buttons
            for i, button in enumerate(self.music_buttons):
                if button.rect.collidepoint(mouse_pos):
                    if button.music["unlocked"]:
                        self.selected_index = i
                        self.update_selection()
                        # Play the selected music
                        self.music_manager.play_music(button.music["id"])
                        return f"music_selected_{button.music['id']}"
                    else:
                        # Show locked message
                        return "music_locked"
            
            # Check if clicked outside panel to close
            if not self.is_mouse_over_panel(mouse_pos):
                self.hide()
                return "music_panel_closed"
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.hide()
                return "music_panel_closed"
            elif event.key == pygame.K_UP:
                # Move selection up
                new_index = max(0, self.selected_index - 1)
                if new_index != self.selected_index:
                    self.selected_index = new_index
                    self.update_selection()
                    return "music_selection_changed"
            elif event.key == pygame.K_DOWN:
                # Move selection down
                new_index = min(len(self.music_list) - 1, self.selected_index + 1)
                if new_index != self.selected_index:
                    self.selected_index = new_index
                    self.update_selection()
                    return "music_selection_changed"
            elif event.key == pygame.K_RETURN:
                # Select current music
                music = self.music_list[self.selected_index]
                if music["unlocked"]:
                    self.music_manager.play_music(music["id"])
                    return f"music_selected_{music['id']}"
                else:
                    return "music_locked"
        
        return None
    
    def update_selection(self):
        """Update selection state of all buttons"""
        for i, button in enumerate(self.music_buttons):
            button.selected = (i == self.selected_index)
    
    def is_mouse_over_panel(self, mouse_pos):
        """Check if mouse is over panel area"""
        panel_rect = pygame.Rect(self.panel_x, self.panel_y, 
                               self.panel_width, self.panel_height)
        return panel_rect.collidepoint(mouse_pos)
    
    def draw(self):
        """Draw the music panel"""
        if not self.visible:
            return
        
        # Draw semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))  # Dark overlay with transparency
        self.screen.blit(overlay, (0, 0))
        
        # Draw panel background
        panel_rect = pygame.Rect(self.panel_x, self.panel_y, 
                               self.panel_width, self.panel_height)
        
        # Main panel background
        pygame.draw.rect(self.screen, (20, 30, 45), panel_rect, border_radius=15)
        pygame.draw.rect(self.screen, ACCENT_COLOR, panel_rect, 3, border_radius=15)
        
        # Panel header
        header_rect = pygame.Rect(self.panel_x, self.panel_y, 
                                self.panel_width, 60)
        pygame.draw.rect(self.screen, (30, 40, 60), header_rect, border_radius=15)
        
        # Panel title
        title = self.font_manager.large.render("MUSIC SELECTION", True, (100, 200, 255))
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, self.panel_y + 30))
        self.screen.blit(title, title_rect)
        
        # Instructions
        instructions = self.font_manager.small.render(
            "Use UP/DOWN arrows to navigate, ENTER to select", 
            True, (180, 200, 220))
        inst_rect = instructions.get_rect(center=(SCREEN_WIDTH//2, self.panel_y + 70))
        self.screen.blit(instructions, inst_rect)
        
        # Draw music buttons
        for button in self.music_buttons:
            button.draw(self.screen)
        
        # Draw currently playing indicator
        current_music = self.music_manager.get_current_music()
        if current_music:
            playing_text = self.font_manager.small.render(
                f"Now Playing: {current_music['name']}", 
                True, (100, 255, 100))
            playing_rect = playing_text.get_rect(center=(SCREEN_WIDTH//2, self.panel_y + self.panel_height - 30))
            self.screen.blit(playing_text, playing_rect)


class MusicButton:
    """Button for music selection"""
    
    def __init__(self, x, y, width, height, music, font_manager, selected=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.music = music
        self.font_manager = font_manager
        self.selected = selected
        self.hovered = False
    
    def update_hover(self, mouse_pos):
        """Update hover state"""
        self.hovered = self.rect.collidepoint(mouse_pos)
    
    def draw(self, surface):
        """Draw the music button"""
        mouse_pos = pygame.mouse.get_pos()
        self.update_hover(mouse_pos)
        
        # Determine button colors based on state
        if self.selected:
            button_color = (60, 100, 180)  # Selected color
            border_color = (100, 180, 255)
        elif not self.music["unlocked"]:
            button_color = (60, 60, 70)  # Locked color
            border_color = (100, 100, 110)
        elif self.hovered:
            button_color = (50, 70, 100)  # Hover color
            border_color = (100, 150, 200)
        else:
            button_color = (40, 50, 70)  # Normal color
            border_color = (80, 120, 160)
        
        # Draw button background
        pygame.draw.rect(surface, button_color, self.rect, border_radius=8)
        pygame.draw.rect(surface, border_color, self.rect, 2, border_radius=8)
        
        # Draw music info
        if self.music["unlocked"]:
            text_color = (240, 250, 255) if self.selected else (220, 230, 240)
            
            # Music name
            name_font = self.font_manager.medium
            name_text = name_font.render(self.music["name"], True, text_color)
            name_rect = name_text.get_rect(left=self.rect.left + 10, centery=self.rect.centery - 8)
            surface.blit(name_text, name_rect)
            
            # Artist
            artist_font = self.font_manager.small
            artist_text = artist_font.render(f"by {self.music['artist']}", True, text_color)
            artist_rect = artist_text.get_rect(left=self.rect.left + 10, centery=self.rect.centery + 12)
            surface.blit(artist_text, artist_rect)
        else:
            # Locked music
            locked_color = (150, 150, 160)
            
            # Music name (locked)
            name_font = self.font_manager.medium
            name_text = name_font.render(self.music["name"], True, locked_color)
            name_rect = name_text.get_rect(left=self.rect.left + 10, centery=self.rect.centery - 8)
            surface.blit(name_text, name_rect)
            
            # Locked message
            locked_font = self.font_manager.small
            locked_text = locked_font.render("Locked - Complete achievements to unlock", True, (200, 100, 100))
            locked_rect = locked_text.get_rect(left=self.rect.left + 10, centery=self.rect.centery + 12)
            surface.blit(locked_text, locked_rect)
        
        # Draw selection indicator
        if self.selected:
            indicator_x = self.rect.right - 30
            indicator_y = self.rect.centery
            pygame.draw.circle(surface, (100, 255, 100), (indicator_x, indicator_y), 8)
        
        # Draw lock icon for locked music
        if not self.music["unlocked"]:
            lock_x = self.rect.right - 30
            lock_y = self.rect.centery
            
            # Draw lock body
            lock_rect = pygame.Rect(lock_x - 8, lock_y - 10, 16, 12)
            pygame.draw.rect(surface, (150, 150, 150), lock_rect, border_radius=3)
            
            # Draw lock shackle
            pygame.draw.arc(surface, (150, 150, 150), 
                          (lock_x - 12, lock_y - 15, 24, 12), 
                          3.14, 0, 3)