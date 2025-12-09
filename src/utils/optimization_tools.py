"""
Optimization tools for game performance
"""

import gc
import sys
import pygame
from typing import List, Dict, Any

class MemoryOptimizer:
    """Optimize memory usage during gameplay"""
    
    def __init__(self):
        self.last_gc_time = 0
        self.gc_interval = 10000  # 10 seconds
        self.memory_threshold_mb = 100  # Warn if memory > 100MB
        self.enabled = True
    
    def optimize_memory(self, force: bool = False):
        """Run garbage collection and optimize memory"""
        if not self.enabled:
            return
        
        current_time = pygame.time.get_ticks()
        
        if force or (current_time - self.last_gc_time > self.gc_interval):
            # Run garbage collection
            gc.collect()
            self.last_gc_time = current_time
            
            # Get memory usage
            memory_usage = self.get_memory_usage_mb()
            
            if memory_usage > self.memory_threshold_mb:
                print(f"⚠️ High memory usage: {memory_usage:.1f}MB")
            
            return memory_usage
        
        return None
    
    def get_memory_usage_mb(self) -> float:
        """Get current memory usage in MB"""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except ImportError:
            # Fallback to less accurate method
            return 0.0
    
    def clear_unused_surfaces(self, surface_cache: Dict[str, pygame.Surface], 
                             max_age_seconds: int = 300):
        """Clear unused surfaces from cache"""
        if not self.enabled:
            return
        
        current_time = pygame.time.get_ticks() / 1000
        
        # Simple strategy: if cache too large, clear oldest entries
        max_cache_size = 50
        if len(surface_cache) > max_cache_size:
            # Keep only recent entries (simplified)
            keys_to_remove = list(surface_cache.keys())[:-max_cache_size]
            for key in keys_to_remove:
                del surface_cache[key]

class RenderOptimizer:
    """Optimize rendering performance"""
    
    def __init__(self):
        self.render_calls = 0
        self.batch_render = True
        self.use_dirty_rects = False
        self.dirty_rects = []
    
    def begin_frame(self):
        """Begin a new render frame"""
        self.render_calls = 0
        if self.use_dirty_rects:
            self.dirty_rects = []
    
    def track_render_call(self, rect: pygame.Rect = None):
        """Track a render call for optimization"""
        self.render_calls += 1
        
        if self.use_dirty_rects and rect:
            self.dirty_rects.append(rect)
    
    def should_use_dirty_rects(self, avg_fps: float) -> bool:
        """Determine if dirty rects should be used based on FPS"""
        # Use dirty rects if FPS is low
        return avg_fps < 30
    
    def get_dirty_rects(self) -> List[pygame.Rect]:
        """Get dirty rectangles for update"""
        if not self.dirty_rects:
            return None
        
        # Merge overlapping rectangles
        merged_rects = []
        for rect in self.dirty_rects:
            merged = False
            for i, merged_rect in enumerate(merged_rects):
                if merged_rect.colliderect(rect):
                    merged_rects[i] = merged_rect.union(rect)
                    merged = True
                    break
            
            if not merged:
                merged_rects.append(rect)
        
        return merged_rects

class AssetOptimizer:
    """Optimize asset loading and usage"""
    
    def __init__(self):
        self.asset_priorities = {}  # asset_path -> priority
        self.loaded_assets = {}     # asset_path -> last_used_time
        self.max_assets = 100       # Maximum number of assets to keep loaded
    
    def prioritize_asset(self, asset_path: str, priority: int = 1):
        """Set priority for an asset (higher = more likely to stay loaded)"""
        self.asset_priorities[asset_path] = priority
    
    def mark_asset_used(self, asset_path: str):
        """Mark an asset as recently used"""
        if asset_path in self.loaded_assets:
            self.loaded_assets[asset_path] = pygame.time.get_ticks()
    
    def optimize_asset_cache(self, current_assets: Dict[str, Any]) -> List[str]:
        """Optimize asset cache and return assets to unload"""
        current_time = pygame.time.get_ticks()
        assets_to_unload = []
        
        for asset_path, asset in list(current_assets.items()):
            if asset_path in self.loaded_assets:
                last_used = self.loaded_assets[asset_path]
                age_seconds = (current_time - last_used) / 1000
                
                # Determine if asset should be unloaded
                priority = self.asset_priorities.get(asset_path, 0)
                
                # Unload criteria:
                # 1. Too many assets loaded
                # 2. Low priority and old
                # 3. Very old regardless of priority
                if (len(current_assets) > self.max_assets and priority == 0) or \
                   (priority == 0 and age_seconds > 300) or \
                   (age_seconds > 600):  # 10 minutes
                    
                    assets_to_unload.append(asset_path)
                    del self.loaded_assets[asset_path]
        
        return assets_to_unload
    
    def preload_important_assets(self, asset_paths: List[str], priorities: List[int] = None):
        """Preload important assets with given priorities"""
        if priorities and len(priorities) == len(asset_paths):
            for path, priority in zip(asset_paths, priorities):
                self.prioritize_asset(path, priority)
        else:
            for path in asset_paths:
                self.prioritize_asset(path, 1)

# Global optimizer instances
memory_optimizer = MemoryOptimizer()
render_optimizer = RenderOptimizer()
asset_optimizer = AssetOptimizer()

def optimize_game_performance():
    """Run all optimization routines"""
    # Optimize memory
    memory_usage = memory_optimizer.optimize_memory()
    
    # Get performance stats to decide optimization strategy
    from .performance_monitor import performance_monitor
    stats = performance_monitor.get_performance_stats()
    
    # Adjust rendering strategy based on performance
    if stats.get('fps', 60) < 30:
        render_optimizer.use_dirty_rects = True
    else:
        render_optimizer.use_dirty_rects = False
    
    return {
        'memory_mb': memory_usage,
        'fps': stats.get('fps', 0),
        'using_dirty_rects': render_optimizer.use_dirty_rects
    }