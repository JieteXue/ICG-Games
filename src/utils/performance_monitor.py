"""
Performance monitoring and optimization utilities
"""

import time
import pygame
from typing import Dict, List, Optional
from collections import deque

class PerformanceMonitor:
    """Monitor game performance and FPS"""
    
    def __init__(self, max_samples: int = 100):
        self.max_samples = max_samples
        self.frame_times: deque = deque(maxlen=max_samples)
        self.update_times: deque = deque(maxlen=max_samples)
        self.draw_times: deque = deque(maxlen=max_samples)
        self.event_times: deque = deque(maxlen=max_samples)
        
        self.current_frame_start = 0
        self.fps = 0
        self.frame_count = 0
        self.last_fps_update = 0
        
        self.memory_usage_samples: deque = deque(maxlen=50)
        self.performance_warnings = []
        
        self.enabled = True
    
    def start_frame(self):
        """Mark the start of a frame"""
        if not self.enabled:
            return
        
        self.current_frame_start = time.perf_counter()
    
    def record_event_time(self, event_time: float):
        """Record event processing time"""
        if self.enabled:
            self.event_times.append(event_time)
    
    def record_update_time(self, update_time: float):
        """Record update processing time"""
        if self.enabled:
            self.update_times.append(update_time)
    
    def record_draw_time(self, draw_time: float):
        """Record draw processing time"""
        if self.enabled:
            self.draw_times.append(draw_time)
    
    def end_frame(self):
        """Mark the end of a frame and calculate FPS"""
        if not self.enabled:
            return
        
        frame_time = time.perf_counter() - self.current_frame_start
        self.frame_times.append(frame_time)
        
        self.frame_count += 1
        current_time = pygame.time.get_ticks() / 1000.0
        
        # Update FPS every second
        if current_time - self.last_fps_update >= 1.0:
            self.fps = self.frame_count / (current_time - self.last_fps_update)
            self.frame_count = 0
            self.last_fps_update = current_time
            
            # Check for performance issues
            self._check_performance()
    
    def _check_performance(self):
        """Check for performance issues"""
        if len(self.frame_times) < 10:
            return
        
        avg_frame_time = sum(self.frame_times) / len(self.frame_times)
        avg_fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0
        
        self.performance_warnings = []
        
        if avg_fps < 30:
            self.performance_warnings.append(f"Low FPS: {avg_fps:.1f}")
        
        if avg_frame_time > 0.033:  # More than 30ms per frame
            self.performance_warnings.append(f"High frame time: {avg_frame_time*1000:.1f}ms")
        
        # Check for spikes
        if len(self.frame_times) >= 20:
            recent_times = list(self.frame_times)[-10:]
            if max(recent_times) > avg_frame_time * 2:
                self.performance_warnings.append("Frame time spikes detected")
    
    def get_performance_stats(self) -> Dict[str, float]:
        """Get current performance statistics"""
        if not self.frame_times:
            return {'fps': 0, 'frame_time': 0}
        
        avg_frame_time = sum(self.frame_times) / len(self.frame_times)
        avg_fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0
        
        stats = {
            'fps': avg_fps,
            'frame_time_ms': avg_frame_time * 1000,
            'frame_time_avg': avg_frame_time,
            'frame_time_min': min(self.frame_times) if self.frame_times else 0,
            'frame_time_max': max(self.frame_times) if self.frame_times else 0,
        }
        
        if self.update_times:
            stats['update_time_ms'] = sum(self.update_times) / len(self.update_times) * 1000
        
        if self.draw_times:
            stats['draw_time_ms'] = sum(self.draw_times) / len(self.draw_times) * 1000
        
        if self.event_times:
            stats['event_time_ms'] = sum(self.event_times) / len(self.event_times) * 1000
        
        return stats
    
    def get_warnings(self) -> List[str]:
        """Get performance warnings"""
        return self.performance_warnings.copy()
    
    def draw_performance_overlay(self, surface: pygame.Surface, font: pygame.font.Font):
        """Draw performance overlay on screen"""
        if not self.enabled:
            return
        
        stats = self.get_performance_stats()
        warnings = self.get_warnings()
        
        # Create overlay surface
        overlay_height = 80 + len(warnings) * 20
        overlay = pygame.Surface((200, overlay_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        
        # Draw stats
        y_pos = 10
        lines = [
            f"FPS: {stats['fps']:.1f}",
            f"Frame: {stats['frame_time_ms']:.1f}ms",
            f"Update: {stats.get('update_time_ms', 0):.1f}ms",
            f"Draw: {stats.get('draw_time_ms', 0):.1f}ms",
        ]
        
        for line in lines:
            text = font.render(line, True, (255, 255, 255))
            overlay.blit(text, (10, y_pos))
            y_pos += 15
        
        # Draw warnings
        if warnings:
            y_pos += 5
            warning_font = pygame.font.SysFont('Arial', 12)
            for warning in warnings:
                text = warning_font.render(warning, True, (255, 200, 100))
                overlay.blit(text, (10, y_pos))
                y_pos += 15
        
        # Draw overlay in top-right corner
        surface.blit(overlay, (surface.get_width() - 210, 10))

class PerformanceProfiler:
    """Context manager for profiling code sections"""
    
    def __init__(self, name: str, monitor: PerformanceMonitor):
        self.name = name
        self.monitor = monitor
        self.start_time = 0
    
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = time.perf_counter() - self.start_time
        
        # Record based on section name
        if 'update' in self.name.lower():
            self.monitor.record_update_time(elapsed)
        elif 'draw' in self.name.lower():
            self.monitor.record_draw_time(elapsed)
        elif 'event' in self.name.lower():
            self.monitor.record_event_time(elapsed)

# Global performance monitor instance
performance_monitor = PerformanceMonitor()