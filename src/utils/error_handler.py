"""
Unified error handling system for the game framework
"""

import sys
import traceback
from typing import Callable, Any
from functools import wraps

class GameError(Exception):
    """Base exception for game-related errors"""
    def __init__(self, message: str, error_code: int = 0):
        super().__init__(message)
        self.error_code = error_code
        self.user_message = message

class ResourceError(GameError):
    """Exception for resource loading errors"""
    pass

class LogicError(GameError):
    """Exception for game logic errors"""
    pass

class UIError(GameError):
    """Exception for UI rendering errors"""
    pass

def handle_game_errors(func: Callable) -> Callable:
    """
    Decorator for unified error handling in game functions
    
    Usage:
        @handle_game_errors
        def game_function():
            # Function that might raise exceptions
            pass
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except GameError as e:
            # Game-specific errors - log and show user-friendly message
            print(f"⚠️ Game Error [{e.error_code}]: {e}")
            if hasattr(args[0], 'message') if args else False:
                args[0].message = f"Error: {e.user_message}"
            return None
        except Exception as e:  # 合并所有其他异常
            # 首先检查是否是 pygame 错误
            error_msg = str(e).lower()
            if 'pygame' in error_msg or 'display' in error_msg or 'surface' in error_msg:
                # Pygame-related errors
                print(f"⚠️ Pygame Error: {e}")
                return None
            else:
                # Unexpected errors
                print(f"💥 Unexpected Error in {func.__name__}: {e}")
                traceback.print_exc()
                return None
    
    return wrapper

def safe_execute(func: Callable, default_return: Any = None) -> Any:
    """
    Safely execute a function and return default value on error
    
    Args:
        func: Function to execute
        default_return: Value to return on error
        
    Returns:
        Function result or default_return on error
    """
    try:
        return func()
    except Exception as e:
        print(f"⚠️ Error in safe_execute: {e}")
        return default_return

class ErrorReporter:
    """Error reporting and logging system"""
    
    def __init__(self, log_file: str = "game_errors.log"):
        self.log_file = log_file
        self.errors = []
        self.warnings = []
    
    def log_error(self, error_type: str, message: str, details: str = ""):
        """Log an error"""
        error_entry = {
            'type': error_type,
            'message': message,
            'details': details,
            'timestamp': self._get_timestamp()
        }
        self.errors.append(error_entry)
        self._write_to_log(error_entry)
    
    def log_warning(self, warning_type: str, message: str):
        """Log a warning"""
        warning_entry = {
            'type': warning_type,
            'message': message,
            'timestamp': self._get_timestamp()
        }
        self.warnings.append(warning_entry)
        print(f"⚠️ {warning_type}: {message}")
    
    def _write_to_log(self, entry: dict):
        """Write entry to log file"""
        try:
            with open(self.log_file, 'a') as f:
                f.write(f"[{entry['timestamp']}] {entry['type']}: {entry['message']}\n")
                if entry.get('details'):
                    f.write(f"  Details: {entry['details']}\n")
        except Exception as e:
            print(f"Failed to write to log file: {e}")
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def get_error_summary(self) -> dict:
        """Get error statistics"""
        return {
            'total_errors': len(self.errors),
            'total_warnings': len(self.warnings),
            'recent_errors': self.errors[-10:] if self.errors else [],
            'recent_warnings': self.warnings[-10:] if self.warnings else []
        }
    
    def clear_logs(self):
        """Clear error logs"""
        self.errors.clear()
        self.warnings.clear()
        try:
            open(self.log_file, 'w').close()
        except Exception:
            pass

# Global error reporter instance
error_reporter = ErrorReporter()

# Convenience functions
def log_resource_error(message: str, resource_path: str = ""):
    """Log a resource loading error"""
    error_reporter.log_error("RESOURCE", message, resource_path)

def log_logic_error(message: str, game_state: str = ""):
    """Log a game logic error"""
    error_reporter.log_error("LOGIC", message, game_state)

def log_ui_error(message: str, component: str = ""):
    """Log a UI rendering error"""
    error_reporter.log_error("UI", message, component)

def log_warning(message: str, category: str = "GENERAL"):
    """Log a warning"""
    error_reporter.log_warning(category, message)