# [file name]: redeem_dialog.py
# [file content begin]
"""
Redeem CDKEY Dialog Component
"""
import pygame
from utils.constants import *

class RedeemDialog:
    """Dialog for redeeming CDKEY"""
    
    def __init__(self, screen, font_manager, music_manager):
        self.screen = screen
        self.font_manager = font_manager
        self.music_manager = music_manager
        self.visible = False
        
        # Dialog dimensions
        self.width = 500
        self.height = 300
        self.x = (SCREEN_WIDTH - self.width) // 2
        self.y = (SCREEN_HEIGHT - self.height) // 2
        
        # Input box
        input_width = 200
        input_height = 40
        self.input_box = pygame.Rect(
            self.x + (self.width - input_width) // 2,
            self.y + 120,
            input_width,
            input_height
        )
        
        # Text and state
        self.input_text = ""
        self.active = False
        self.message = ""
        self.message_color = (255, 255, 255)
        
        # Buttons
        button_width = 80
        button_height = 35
        self.submit_button = pygame.Rect(
            self.x + (self.width - button_width) // 2,
            self.y + 180,
            button_width,
            button_height
        )
        
        self.close_button = pygame.Rect(
            self.x + self.width - 40,
            self.y + 20,
            20,
            20
        )
    
    def show(self):
        """Show the dialog"""
        self.visible = True
        self.input_text = ""
        self.message = ""
        self.active = True
    
    def hide(self):
        """Hide the dialog"""
        self.visible = False
        self.active = False
    
    def toggle(self):
        """Toggle visibility"""
        if self.visible:
            self.hide()
        else:
            self.show()
    
    def handle_event(self, event, mouse_pos):
        """Handle events for the dialog"""
        if not self.visible:
            return None
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check close button
            if self.close_button.collidepoint(mouse_pos):
                self.hide()
                return "closed"
            
            # Check input box
            if self.input_box.collidepoint(mouse_pos):
                self.active = True
                return "input_active"
            else:
                self.active = False
            
            # Check submit button
            if self.submit_button.collidepoint(mouse_pos):
                self._process_cdkey()
                return "submitted"
        
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self._process_cdkey()
                return "submitted"
            elif event.key == pygame.K_ESCAPE:
                self.hide()
                return "closed"
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            else:
                # Add character if it's printable
                if event.unicode.isprintable() and len(self.input_text) < 20:
                    self.input_text += event.unicode
        
        return None
    
    def _process_cdkey(self):
        """Process the CDKEY input"""
        cdkey = self.input_text.strip()
        
        # Check if quantum is already unlocked
        if self.music_manager.is_music_unlocked(3):
            self.message = "CDKEY used!"
            self.message_color = (255, 100, 100)
            return
        
        # Check if CDKEY is correct
        if cdkey == "XLY303":
            # Unlock quantum music
            if self.music_manager.unlock_music(3):
                self.message = "quantum unlocked!"
                self.message_color = (100, 255, 100)
            else:
                self.message = "Error unlocking music"
                self.message_color = (255, 100, 100)
        else:
            self.message = "invalid key"
            self.message_color = (255, 100, 100)
    
    def draw(self):
        """Draw the dialog"""
        if not self.visible:
            return
        
        # Draw semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Draw dialog background
        dialog_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(self.screen, (30, 40, 60), dialog_rect, border_radius=15)
        pygame.draw.rect(self.screen, ACCENT_COLOR, dialog_rect, 2, border_radius=15)
        
        # Draw title
        title = self.font_manager.large.render("Redeem CDKEY", True, (220, 220, 255))
        title_rect = title.get_rect(center=(self.x + self.width // 2, self.y + 50))
        self.screen.blit(title, title_rect)
        
        # Draw instruction
        instruction = self.font_manager.small.render("Input your CDKEY:", True, (180, 200, 220))
        inst_rect = instruction.get_rect(center=(self.x + self.width // 2, self.y + 90))
        self.screen.blit(instruction, inst_rect)
        
        # Draw input box
        input_color = (50, 60, 80) if not self.active else (70, 80, 100)
        pygame.draw.rect(self.screen, input_color, self.input_box, border_radius=8)
        pygame.draw.rect(self.screen, ACCENT_COLOR, self.input_box, 2, border_radius=8)
        
        # Draw input text
        if self.input_text:
            text_surface = self.font_manager.medium.render(self.input_text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(midleft=(self.input_box.left + 10, self.input_box.centery))
            self.screen.blit(text_surface, text_rect)
        
        # Draw cursor if active
        if self.active:
            cursor_x = self.input_box.left + 10
            if self.input_text:
                cursor_width = self.font_manager.medium.size(self.input_text)[0]
                cursor_x += cursor_width
            pygame.draw.line(self.screen, (255, 255, 255),
                           (cursor_x, self.input_box.top + 10),
                           (cursor_x, self.input_box.bottom - 10), 2)
        
        # Draw submit button
        mouse_pos = pygame.mouse.get_pos()
        submit_hovered = self.submit_button.collidepoint(mouse_pos)
        
        submit_color = (60, 100, 180) if submit_hovered else (40, 80, 140)
        pygame.draw.rect(self.screen, submit_color, self.submit_button, border_radius=8)
        pygame.draw.rect(self.screen, ACCENT_COLOR, self.submit_button, 2, border_radius=8)
        
        submit_text = self.font_manager.small.render("Submit", True, (255, 255, 255))
        submit_rect = submit_text.get_rect(center=self.submit_button.center)
        self.screen.blit(submit_text, submit_rect)
        
        # Draw message
        if self.message:
            message_surface = self.font_manager.small.render(self.message, True, self.message_color)
            message_rect = message_surface.get_rect(center=(self.x + self.width // 2, self.y + 230))
            self.screen.blit(message_surface, message_rect)
        
        # Draw close button
        close_hovered = self.close_button.collidepoint(mouse_pos)
        close_color = (200, 70, 70) if close_hovered else (180, 50, 50)
        pygame.draw.rect(self.screen, close_color, self.close_button, border_radius=4)
        
        # Draw X
        offset = 6
        pygame.draw.line(self.screen, (255, 255, 255),
                       (self.close_button.centerx - offset, self.close_button.centery - offset),
                       (self.close_button.centerx + offset, self.close_button.centery + offset), 2)
        pygame.draw.line(self.screen, (255, 255, 255),
                       (self.close_button.centerx - offset, self.close_button.centery + offset),
                       (self.close_button.centerx + offset, self.close_button.centery - offset), 2)
# [file content end]