"""
Settings Panel Component for Game Settings
"""

import pygame
import webbrowser
from utils.constants import *

class SettingsPanel:
    """Settings panel overlay for game configuration"""
    
    def __init__(self, screen, font_manager):
        self.screen = screen
        self.font_manager = font_manager
        self.visible = False
        
        # Panel dimensions
        self.panel_width = 600
        self.panel_height = 470
        self.panel_x = (SCREEN_WIDTH - self.panel_width) // 2
        self.panel_y = (SCREEN_HEIGHT - self.panel_height) // 2
        self.button_offset_x = 450
        
        # Panel rectangle with rounded corners
        self.panel_rect = pygame.Rect(
            self.panel_x, 
            self.panel_y, 
            self.panel_width, 
            self.panel_height
        )
        
        # Back button
        back_button_width = 100
        back_button_height = 40
        self.back_button_rect = pygame.Rect(
            self.panel_x + 20,
            self.panel_y + 15,
            back_button_width,
            back_button_height
        )
        
        # Settings options
        self.settings = {
            'background_music': True,  # 背景音乐
            'sound_effects': True,     # 音效
            'winning_hints': False,    # 胜负提示 (默认关闭) - 名称更改
        }
        
        # Sponsor URL
        self.sponsor_url = "https://github.com/JieteXue/ICG-Games"
        
        # Create setting buttons
        self.setting_buttons = []
        self.create_setting_buttons()
    
    def create_setting_buttons(self):
        """Create toggle buttons for each setting"""
        setting_options = [
            {
                'name': 'background_music',
                'label': 'Background Music',
                'description': 'Toggle background music',
                'default_state': True
            },
            {
                'name': 'sound_effects',
                'label': 'Sound Effects',
                'description': 'Toggle game sound effects',
                'default_state': True
            },
            {
                'name': 'winning_hints',
                'label': 'Winning Hints',  # 名称更改
                'description': 'A Tip from AI to gain advantage',  # 描述更改
                'default_state': False  # 默认关闭
            }
        ]
        
        start_y = self.panel_y + 120
        button_spacing = 90
        
        for i, option in enumerate(setting_options):
            button_x = self.panel_x + self.button_offset_x
            button_y = start_y + i * button_spacing
            
            # Create toggle button
            button = ToggleButton(
                button_x, button_y, 
                80, 35,  # width, height
                option['label'],
                option['default_state'],
                self.font_manager
            )
            self.setting_buttons.append(button)
    
    def toggle_visibility(self):
        """Toggle the visibility of the settings panel"""
        self.visible = not self.visible
        return "settings" if self.visible else "back_from_settings"
    
    def show(self):
        """Show the settings panel"""
        self.visible = True
    
    def hide(self):
        """Hide the settings panel"""
        self.visible = False
    
    def handle_event(self, event, mouse_pos):
        """Handle events for the settings panel"""
        if not self.visible:
            return None
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check if click is outside the panel
            if not self.panel_rect.collidepoint(mouse_pos):
                self.hide()
                return "back_from_settings"
            
            # Check back button
            if self.back_button_rect.collidepoint(mouse_pos):
                self.hide()
                return "back_from_settings"
            
            # Check setting toggle buttons
            for i, button in enumerate(self.setting_buttons):
                if button.rect.collidepoint(mouse_pos):
                    button.toggle()
                    
                    # Update the setting value
                    if i == 0:
                        self.settings['background_music'] = button.is_on
                    elif i == 1:
                        self.settings['sound_effects'] = button.is_on
                    elif i == 2:
                        self.settings['winning_hints'] = button.is_on
                    
                    return f"setting_changed_{button.label.lower().replace(' ', '_')}"
            
            # Check sponsor button
            sponsor_rect = pygame.Rect(
                self.panel_x + self.button_offset_x,
                self.panel_y + 120 + 3 * 90,  # 4th row
                80, 35
            )
            if sponsor_rect.collidepoint(mouse_pos):
                # Open sponsor URL in browser
                try:
                    webbrowser.open(self.sponsor_url)
                    return "sponsor_clicked"
                except:
                    print(f"Could not open URL: {self.sponsor_url}")
                    return "sponsor_error"
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_s:
                self.hide()
                return "back_from_settings"
        
        return None
    
    def draw(self):
        """Draw the settings panel"""
        if not self.visible:
            return
        
        # Draw semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Dark overlay with transparency
        self.screen.blit(overlay, (0, 0))
        
        # Draw panel background with rounded corners
        pygame.draw.rect(self.screen, (15, 25, 40), self.panel_rect, border_radius=15)
        pygame.draw.rect(self.screen, ACCENT_COLOR, self.panel_rect, 3, border_radius=15)
        
        # Panel header with gradient and rounded corners
        header_rect = pygame.Rect(self.panel_x, self.panel_y, 
                                self.panel_width, 70)
        
        # Draw header background with rounded top corners
        header_surface = pygame.Surface((self.panel_width, 70), pygame.SRCALPHA)
        pygame.draw.rect(header_surface, (25, 35, 60), 
                        (0, 0, self.panel_width, 70), 
                        border_radius=15, border_top_left_radius=15, border_top_right_radius=15)
        
        # Add gradient effect
        for i in range(header_rect.height):
            alpha = int(200 * (1 - i / header_rect.height))
            pygame.draw.line(header_surface, (25, 35, 60, alpha),
                           (0, i),
                           (self.panel_width, i), 1)
        
        self.screen.blit(header_surface, (self.panel_x, self.panel_y))
        
        # Draw header border
        pygame.draw.rect(self.screen, ACCENT_COLOR, 
                        (self.panel_x, self.panel_y, self.panel_width, 70), 
                        2, border_top_left_radius=15, border_top_right_radius=15)
        
        # Panel title
        title = self.font_manager.large.render("SETTINGS", True, (0, 255, 220))
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, self.panel_y + 40))
        self.screen.blit(title, title_rect)
        
        # Draw back button
        self._draw_back_button()
        
        # Draw settings options
        self._draw_settings_options()
    
    def _draw_back_button(self):
        """Draw the back button"""
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.back_button_rect.collidepoint(mouse_pos)
        
        # Button background
        button_color = BUTTON_HOVER_COLOR if is_hovered else (60, 70, 100)
        pygame.draw.rect(self.screen, button_color, self.back_button_rect, 
                        border_radius=8)
        pygame.draw.rect(self.screen, ACCENT_COLOR, self.back_button_rect, 
                        2, border_radius=8)
        
        # Button text
        back_text = self.font_manager.small.render("Back", True, (255, 255, 255))
        text_rect = back_text.get_rect(center=self.back_button_rect.center)
        self.screen.blit(back_text, text_rect)
        
        # Tooltip on hover
        if is_hovered:
            tooltip = self.font_manager.small.render("Return to sidebar", 
                                                    True, (200, 220, 255))
            tooltip_rect = tooltip.get_rect(midleft=(self.back_button_rect.right + 10, 
                                                    self.back_button_rect.centery))
            pygame.draw.rect(self.screen, (40, 50, 70), 
                           (tooltip_rect.x - 5, tooltip_rect.y - 3,
                            tooltip_rect.width + 10, tooltip_rect.height + 6),
                           border_radius=4)
            pygame.draw.rect(self.screen, (100, 150, 200),
                           (tooltip_rect.x - 5, tooltip_rect.y - 3,
                            tooltip_rect.width + 10, tooltip_rect.height + 6),
                           1, border_radius=4)
            self.screen.blit(tooltip, tooltip_rect)
    
    def _draw_settings_options(self):
        """Draw all settings options"""
        setting_labels = [
            "Background Music",
            "Sound Effects", 
            "Winning Hints",  # 名称更改
            "Sponsor Us"
        ]
        
        setting_descriptions = [
            "Toggle background music on/off",
            "Toggle game sound effects on/off",
            "A Tip from AI to gain advantage",  # 描述更改
            "Visit our sponsor's website"
        ]
        
        start_y = self.panel_y + 120
        row_spacing = 90
        
        for i, (label, description) in enumerate(zip(setting_labels, setting_descriptions)):
            # Label
            label_text = self.font_manager.medium.render(label, True, (220, 240, 255))
            label_x = self.panel_x + 40
            label_y = start_y + i * row_spacing
            self.screen.blit(label_text, (label_x, label_y))
            
            # Description
            desc_text = self.font_manager.small.render(description, True, (150, 170, 190))
            self.screen.blit(desc_text, (label_x, label_y + 30))
            
            # Draw button
            if i < 3:  # First three are toggle buttons
                self.setting_buttons[i].draw(self.screen)
            else:  # Fourth is a sponsor button
                self._draw_sponsor_button(start_y + i * row_spacing)
    
    def _draw_sponsor_button(self, y_pos):
        """Draw the sponsor button"""
        button_rect = pygame.Rect(self.panel_x + self.button_offset_x, y_pos, 80, 35)
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = button_rect.collidepoint(mouse_pos)
        
        # Button with sponsor styling
        if is_hovered:
            button_color = (50, 180, 80)  # Brighter green when hovered
        else:
            button_color = (40, 160, 70)  # Normal green
        
        pygame.draw.rect(self.screen, button_color, button_rect, border_radius=8)
        pygame.draw.rect(self.screen, (200, 255, 200), button_rect, 2, border_radius=8)
        
        # GO text
        go_text = self.font_manager.small.render("GO", True, (255, 255, 255))
        go_rect = go_text.get_rect(center=button_rect.center)
        self.screen.blit(go_text, go_rect)
        
        # URL hint
        if is_hovered:
            url_text = self.font_manager.small.render(self.sponsor_url, 
                                                     True, (150, 200, 150))
            url_rect = url_text.get_rect(midright=(button_rect.right + 30, 
                                                 button_rect.centery - 40))
            self.screen.blit(url_text, url_rect)
    
    def get_settings(self):
        """Get current settings values"""
        return self.settings.copy()
    
    def set_settings(self, settings):
        """Update settings values"""
        self.settings.update(settings)
        
        # Update toggle buttons
        for i, (key, value) in enumerate(self.settings.items()):
            if i < len(self.setting_buttons):
                self.setting_buttons[i].set_state(value)


class ToggleButton:
    """Toggle button for settings (ON/OFF)"""
    
    def __init__(self, x, y, width, height, label, initial_state, font_manager):
        self.rect = pygame.Rect(x, y, width, height)
        self.label = label
        self.is_on = initial_state
        self.font_manager = font_manager
        self.hovered = False
    
    def toggle(self):
        """Toggle the button state"""
        self.is_on = not self.is_on
    
    def set_state(self, state):
        """Set the button state"""
        self.is_on = state
    
    def update_hover(self, mouse_pos):
        """Update hover state"""
        self.hovered = self.rect.collidepoint(mouse_pos)
    
    def draw(self, surface):
        """Draw the toggle button"""
        mouse_pos = pygame.mouse.get_pos()
        self.update_hover(mouse_pos)
        
        # Button colors based on state
        if self.is_on:
            # ON state - green
            if self.hovered:
                button_color = (50, 180, 80)  # Brighter green when hovered
            else:
                button_color = (40, 160, 70)  # Normal green
            border_color = (100, 220, 100)
        else:
            # OFF state - red
            if self.hovered:
                button_color = (180, 60, 60)  # Brighter red when hovered
            else:
                button_color = (160, 40, 40)  # Normal red
            border_color = (220, 100, 100)
        
        # Draw button
        pygame.draw.rect(surface, button_color, self.rect, border_radius=8)
        pygame.draw.rect(surface, border_color, self.rect, 2, border_radius=8)
        
        # Draw ON/OFF text
        state_text = "ON" if self.is_on else "OFF"
        text_color = (255, 255, 255)
        text_surface = self.font_manager.small.render(state_text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
        # Hover effect
        if self.hovered:
            glow_rect = self.rect.inflate(6, 6)
            pygame.draw.rect(surface, (*border_color[:3], 50), glow_rect, 
                           2, border_radius=10)