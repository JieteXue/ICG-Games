"""
Universal Key Repeat Manager with double-click support
"""

import pygame

class KeyRepeatManager:
    """Manages key repeat behavior and double-click detection"""
    
    def __init__(self):
        self.key_repeat_timer = 0
        self.initial_repeat_delay = 20  # Frames for initial repeat
        self.continuous_repeat_delay = 3  # Frames for continuous repeat
        self.last_key = None
        self.is_initial_repeat = True
        self.enabled_keys = {
            pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN,
            pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d  # WASD support
        }
        
        # Double-click support
        self.last_click_time = 0
        self.double_click_delay = 500  # Milliseconds
        self.last_click_position = None
    
    def handle_key_event(self, event, callback_dict):
        """
        Handle keyboard events
        
        Args:
            event: pygame keyboard event
            callback_dict: key to callback function mapping
        """
        if event.type == pygame.KEYDOWN:
            if event.key in self.enabled_keys and event.key in callback_dict:
                callback_dict[event.key]()
                self.last_key = event.key
                self.key_repeat_timer = 0
                self.is_initial_repeat = True
        
        elif event.type == pygame.KEYUP:
            if event.key in self.enabled_keys and event.key == self.last_key:
                self._reset_state()
    
    def handle_mouse_click(self, event, position, callback_dict):
        """
        Handle mouse click events with double-click support
        
        Args:
            event: pygame mouse event
            position: click position identifier
            callback_dict: callback functions dictionary
                {'single_click': single_callback, 'double_click': double_callback}
        """
        if (event.type == pygame.MOUSEBUTTONDOWN and 
            event.button == 1 and 
            'single_click' in callback_dict):
            
            current_time = pygame.time.get_ticks()
            
            # Check for double-click
            is_double_click = (current_time - self.last_click_time < self.double_click_delay and 
                             position == self.last_click_position)
            
            if is_double_click and 'double_click' in callback_dict:
                callback_dict['double_click']()
                self.last_click_time = 0
                self.last_click_position = None
            else:
                callback_dict['single_click']()
                self.last_click_time = current_time
                self.last_click_position = position
    
    def update(self, callback_dict):
        """
        Update key repeat state (call each frame)
        
        Args:
            callback_dict: key to callback function mapping
        """
        if self.last_key is not None and self.last_key in callback_dict:
            self.key_repeat_timer += 1
            
            current_delay = (self.initial_repeat_delay 
                           if self.is_initial_repeat 
                           else self.continuous_repeat_delay)
            
            if self.key_repeat_timer >= current_delay:
                callback_dict[self.last_key]()
                self.key_repeat_timer = 0
                if self.is_initial_repeat:
                    self.is_initial_repeat = False
    
    def _reset_state(self):
        """Reset state"""
        self.last_key = None
        self.key_repeat_timer = 0
        self.is_initial_repeat = True
    
    def add_enabled_key(self, key):
        """Add supported key"""
        self.enabled_keys.add(key)
    
    def remove_enabled_key(self, key):
        """Remove supported key"""
        self.enabled_keys.discard(key)
    
    def set_delays(self, initial_delay=20, continuous_delay=5):
        """Set delay times"""
        self.initial_repeat_delay = initial_delay
        self.continuous_repeat_delay = continuous_delay