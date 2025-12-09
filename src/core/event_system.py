"""
Event System - Decouple game components
"""

from typing import Callable, Dict, List

class EventType:
    """Event type definitions"""
    GAME_START = "game_start"
    GAME_OVER = "game_over"
    PLAYER_MOVE = "player_move"
    AI_MOVE = "ai_move"
    UI_UPDATE = "ui_update"
    BUTTON_CLICK = "button_click"
    SCROLL = "scroll"
    STATE_CHANGE = "state_change"

class Event:
    """Event class"""
    
    def __init__(self, event_type: str, data: Dict = None):
        self.type = event_type
        self.data = data or {}

class EventManager:
    """Event manager"""
    
    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}
    
    def subscribe(self, event_type: str, callback: Callable):
        """Subscribe to an event"""
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(callback)
    
    def unsubscribe(self, event_type: str, callback: Callable):
        """Unsubscribe from an event"""
        if event_type in self._listeners:
            self._listeners[event_type].remove(callback)
    
    def emit(self, event: Event):
        """Emit an event"""
        if event.type in self._listeners:
            for callback in self._listeners[event.type]:
                callback(event)