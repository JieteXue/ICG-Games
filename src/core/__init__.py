"""
Core modules for ICG Games framework
"""

from .base_game import BaseGame
from .game_manager import GameManager
from .game_registry import GameRegistry, game_registry
from .event_system import EventType, Event, EventManager
from .state_machine import State, StateMachine

__all__ = [
    'BaseGame', 'GameManager', 'GameRegistry', 'game_registry',
    'EventType', 'Event', 'EventManager', 'State', 'StateMachine'
]