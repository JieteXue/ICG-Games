"""
State Machine for managing game states
"""

from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

class State(ABC):
    """Base state class"""
    
    def __init__(self, state_machine):
        self.state_machine = state_machine
        self.enter_time = 0
        
    @abstractmethod
    def enter(self, data: Dict = None):
        """Enter the state"""
        pass
    
    @abstractmethod
    def exit(self):
        """Exit the state"""
        pass
    
    @abstractmethod
    def update(self):
        """Update the state"""
        pass
    
    @abstractmethod
    def draw(self, screen):
        """Draw the state"""
        pass

class StateMachine:
    """State machine manager"""
    
    def __init__(self):
        self.states: Dict[str, State] = {}
        self.current_state: Optional[State] = None
        self.previous_state: Optional[State] = None
    
    def add_state(self, state_name: str, state: State):
        """Add a state to the state machine"""
        self.states[state_name] = state
    
    def change_state(self, state_name: str, data: Dict = None):
        """Change to a different state"""
        if self.current_state:
            self.current_state.exit()
            self.previous_state = self.current_state
        
        if state_name in self.states:
            self.current_state = self.states[state_name]
            self.current_state.enter(data)
    
    def revert_state(self):
        """Revert to the previous state"""
        if self.previous_state:
            temp = self.current_state
            self.current_state = self.previous_state
            self.previous_state = temp
    
    def update(self):
        """Update current state"""
        if self.current_state:
            self.current_state.update()
    
    def draw(self, screen):
        """Draw current state"""
        if self.current_state:
            self.current_state.draw(screen)