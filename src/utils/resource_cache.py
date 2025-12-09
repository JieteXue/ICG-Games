"""
Resource caching system for efficient asset loading
"""

import pygame
import os
from typing import Dict, Any, Optional

class ResourceCache:
    """Singleton resource cache for images, fonts, and other assets"""
    
    _instance: Optional['ResourceCache'] = None
    
    def __new__(cls) -> 'ResourceCache':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the cache"""
        self.images: Dict[str, pygame.Surface] = {}
        self.sounds: Dict[str, Any] = {}
        self.fonts: Dict[str, pygame.font.Font] = {}
        self.cache_hits = 0
        self.cache_misses = 0
    
    def get_image(self, path: str, convert_alpha: bool = True) -> Optional[pygame.Surface]:
        """Get an image from cache or load it"""
        if not path or not os.path.exists(path):
            print(f"Warning: Image file not found: {path}")
            return None
        
        if path in self.images:
            self.cache_hits += 1
            return self.images[path]
        
        self.cache_misses += 1
        try:
            if convert_alpha:
                image = pygame.image.load(path).convert_alpha()
            else:
                image = pygame.image.load(path).convert()
            
            self.images[path] = image
            return image
        except pygame.error as e:
            print(f"Error loading image {path}: {e}")
            return None
    
    def preload_images(self, image_paths: Dict[str, str]):
        """Preload multiple images"""
        for key, path in image_paths.items():
            if os.path.exists(path):
                self.get_image(path)
    
    def clear_image_cache(self):
        """Clear the image cache"""
        self.images.clear()
        print("Image cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            'images_cached': len(self.images),
            'sounds_cached': len(self.sounds),
            'fonts_cached': len(self.fonts),
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'hit_rate': self.cache_hits / (self.cache_hits + self.cache_misses) 
                       if (self.cache_hits + self.cache_misses) > 0 else 0
        }
    
    def optimize_memory(self, max_images: int = 50):
        """Optimize memory usage by removing least recently used images"""
        if len(self.images) > max_images:
            # Simple strategy: keep most recently added
            keys = list(self.images.keys())
            for key in keys[:-max_images]:
                del self.images[key]
            print(f"Optimized image cache: kept {max_images} images")

# Global instance
resource_cache = ResourceCache()