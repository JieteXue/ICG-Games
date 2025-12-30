"""
Music Manager for handling background music
"""

import pygame
import os
from utils.config_manager import config_manager

class MusicManager:
    """Manages background music playback"""
    
    def __init__(self):
        self.current_music_index = -1
        self.music_enabled = True
        self.music_volume = 0.5
        
        # Music list with file paths (using placeholder paths)
        self.music_library = [
            {"id": 0, "name": "Tranquil Forest", "artist": "Nature Sounds", "path": "assets/music/tranquil_forest.mp3"},
            {"id": 1, "name": "Epic Adventure", "artist": "Orchestral", "path": "assets/music/epic_adventure.mp3"},
            {"id": 2, "name": "Chill Vibes", "artist": "Lo-fi Beats", "path": "assets/music/chill_vibes.mp3"},
            {"id": 3, "name": "Mystery Dungeon", "artist": "Secret Track", "path": "assets/music/mystery_dungeon.mp3"}
        ]
        
        # Load settings from config
        self.load_settings()
    
    def load_settings(self):
        """Load music settings from config"""
        prefs = config_manager.get_user_preferences()
        self.music_enabled = prefs.music_enabled
        self.music_volume = prefs.music_volume
        self.current_music_index = prefs.selected_music
        
        # Set volume
        pygame.mixer.music.set_volume(self.music_volume)
    
    def save_settings(self):
        """Save music settings to config"""
        prefs = config_manager.get_user_preferences()
        prefs.music_enabled = self.music_enabled
        prefs.music_volume = self.music_volume
        prefs.selected_music = self.current_music_index
        config_manager.update_user_preferences(prefs)
    
    def toggle_music(self):
        """Toggle music on/off"""
        self.music_enabled = not self.music_enabled
        
        if self.music_enabled:
            if self.current_music_index >= 0:
                self.play_music(self.current_music_index)
        else:
            pygame.mixer.music.stop()
        
        self.save_settings()
        return self.music_enabled
    
    def set_volume(self, volume):
        """Set music volume (0.0 to 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
        self.save_settings()
    
    def play_music(self, music_index):
        """Play music by index"""
        if not self.music_enabled:
            return False
        
        if 0 <= music_index < len(self.music_library):
            try:
                # For now, we'll just simulate music playback
                # In a real implementation, you would load and play actual music files
                self.current_music_index = music_index
                
                # Set music to loop
                # pygame.mixer.music.load(self.music_library[music_index]["path"])
                # pygame.mixer.music.play(-1)  # -1 means loop indefinitely
                
                self.save_settings()
                return True
            except Exception as e:
                print(f"Error playing music: {e}")
                return False
        return False
    
    def stop_music(self):
        """Stop current music"""
        pygame.mixer.music.stop()
    
    def pause_music(self):
        """Pause current music"""
        pygame.mixer.music.pause()
    
    def unpause_music(self):
        """Unpause current music"""
        pygame.mixer.music.unpause()
    
    def get_current_music(self):
        """Get currently playing music info"""
        if 0 <= self.current_music_index < len(self.music_library):
            return self.music_library[self.current_music_index]
        return None
    
    def get_current_music_index(self):
        """Get current music index"""
        return self.current_music_index
    
    def is_music_enabled(self):
        """Check if music is enabled"""
        return self.music_enabled
    
    def get_music_list(self):
        """Get list of all music"""
        return self.music_library.copy()
    
    def unlock_music(self, music_index):
        """Unlock a music track"""
        prefs = config_manager.get_user_preferences()
        if music_index not in prefs.unlocked_music:
            prefs.unlocked_music.append(music_index)
            config_manager.update_user_preferences(prefs)
            return True
        return False
    
    def is_music_unlocked(self, music_index):
        """Check if music is unlocked"""
        prefs = config_manager.get_user_preferences()
        return music_index in prefs.unlocked_music

# Global music manager instance
music_manager = MusicManager()