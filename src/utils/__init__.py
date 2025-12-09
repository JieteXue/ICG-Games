"""
Utilities package
"""

from .constants import *
from .helpers import wrap_text, FontManager
from .key_repeat import KeyRepeatManager
from .config import GameConfig, ConfigManager
from .error_handler import (
    GameError, ResourceError, LogicError, UIError,
    handle_game_errors, safe_execute, 
    error_reporter, log_resource_error, log_logic_error, 
    log_ui_error, log_warning
)
from .resource_cache import resource_cache
from .config_manager import (
    GameConfig as EnhancedGameConfig,
    UserPreferences,
    config_manager
)
from .performance_monitor import (
    PerformanceMonitor,
    PerformanceProfiler,
    performance_monitor
)
from .optimization_tools import (
    MemoryOptimizer,
    RenderOptimizer,
    AssetOptimizer,
    memory_optimizer,
    render_optimizer,
    asset_optimizer,
    optimize_game_performance
)

__all__ = [
    'wrap_text', 'FontManager', 'KeyRepeatManager',
    'GameConfig', 'ConfigManager',
    'GameError', 'ResourceError', 'LogicError', 'UIError',
    'handle_game_errors', 'safe_execute',
    'error_reporter', 'log_resource_error', 'log_logic_error',
    'log_ui_error', 'log_warning',
    'resource_cache',
    'EnhancedGameConfig', 'UserPreferences', 'config_manager',
    'PerformanceMonitor', 'PerformanceProfiler', 'performance_monitor',
    'MemoryOptimizer', 'RenderOptimizer', 'AssetOptimizer',
    'memory_optimizer', 'render_optimizer', 'asset_optimizer',
    'optimize_game_performance'
]