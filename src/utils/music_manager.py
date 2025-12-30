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
        
        # 获取当前文件所在目录，然后找到 assets 目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)  # src 目录
        assets_dir = os.path.join(project_root, "..", "assets", "music")
        
        # 构建绝对路径
        self.music_library = [
            {"id": 0, "name": "solari", "artist": "Ryuichi Sakamoto", "path": os.path.join(assets_dir, "ryuichi_sakamoto_solari.mp3")},
            {"id": 1, "name": "reminisce", "artist": "Aqualina", "path": os.path.join(assets_dir, "aqualina_reminisce.mp3")},
            {"id": 2, "name": "music for airports", "artist": "Specialists", "path": os.path.join(assets_dir, "specialists_music_for_airports.mp3")},
            {"id": 3, "name": "quantum", "artist": "bbrother", "path": os.path.join(assets_dir, "bbrother_quantum.mp3")}
        ]
        
        print(f"🎵 Music library initialized: {len(self.music_library)} tracks")
        for music in self.music_library:
            if os.path.exists(music["path"]):
                print(f"  ✓ {music['name']} - {music['artist']}")
            else:
                print(f"  ✗ {music['name']} - File not found: {music['path']}")
        
        # Load settings from config
        self.load_settings()

    
    def load_settings(self):
        """Load music settings from config"""
        prefs = config_manager.get_user_preferences()
        self.music_enabled = prefs.music_enabled
        self.music_volume = prefs.music_volume
        self.current_music_index = prefs.selected_music
        
        # Set volume
        pygame.mixer.init()
        pygame.mixer.music.set_volume(self.music_volume)
        print(f"🎵 Music settings loaded: enabled={self.music_enabled}, volume={self.music_volume}, index={self.current_music_index}")
    
    def save_settings(self):
        """Save music settings to config"""
        prefs = config_manager.get_user_preferences()
        prefs.music_enabled = self.music_enabled
        prefs.music_volume = self.music_volume
        prefs.selected_music = self.current_music_index
        config_manager.update_user_preferences(prefs)
        print(f"🎵 Music settings saved: enabled={self.music_enabled}, volume={self.music_volume}, index={self.current_music_index}")
    
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
            print("🎵 Music is disabled, not playing")
            return False
        
        if 0 <= music_index < len(self.music_library):
            try:
                music_path = self.music_library[music_index]["path"]
                self.current_music_index = music_index
                
                # 检查文件是否存在
                if not os.path.exists(music_path):
                    print(f"❌ Music file not found: {music_path}")
                    return False
                
                # 加载并播放音乐
                print(f"🎵 Loading music: {self.music_library[music_index]['name']}")
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.play(-1)  # -1 表示无限循环
                print(f"🎵 Now playing: {self.music_library[music_index]['name']} by {self.music_library[music_index]['artist']}")
                
                self.save_settings()
                return True
            except Exception as e:
                print(f"❌ Error playing music: {e}")
                import traceback
                traceback.print_exc()
                return False
        else:
            print(f"❌ Invalid music index: {music_index}")
        return False
    
    def stop_music(self):
        """Stop current music"""
        pygame.mixer.music.stop()
        print("🎵 Music stopped")
    
    def pause_music(self):
        """Pause current music"""
        pygame.mixer.music.pause()
        print("🎵 Music paused")
    
    def unpause_music(self):
        """Unpause current music"""
        pygame.mixer.music.unpause()
        print("🎵 Music unpaused")
    
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