"""
Card Nim Game Logic
"""

import random
from utils.constants import *

class AutoPlayer:
    """Handles AI logic for the card game"""
    def __init__(self, positions):
        self.positions = positions

    def this_turn_random(self, difficulty):
        """Determine if AI should make a random move based on difficulty"""
        return random.random() < DIFFICULTY_RANDOM_RATES.get(difficulty, 0.3)
    
    def calculate_nim_sum(self, positions):
        """Calculate the XOR (nim-sum) of all positions"""
        nim_sum = 0
        for count in positions:
            nim_sum ^= count
        return nim_sum
    
    def find_winning_move(self):
        """Find a move that makes the nim-sum zero (winning move)"""
        current_nim_sum = self.calculate_nim_sum(self.positions)
        
        if current_nim_sum == 0:
            return None
        
        for i in range(len(self.positions)):
            if self.positions[i] > 0:
                target = current_nim_sum ^ self.positions[i]
                if target < self.positions[i]:
                    count = self.positions[i] - target
                    if 1 <= count <= self.positions[i]:
                        return i, count
        return None
    
    def move_instruction(self, difficulty):
        """Generate move instruction for AI"""
        winning_move = self.find_winning_move()
        
        if winning_move and not self.this_turn_random(difficulty):
            return winning_move
        else:
            available_moves = []
            for i in range(len(self.positions)):
                if self.positions[i] > 0:
                    available_moves.append(i)
            
            if available_moves:
                position_idx = random.choice(available_moves)
                if difficulty >= 3:
                    count = random.randint(max(1, self.positions[position_idx] // 2), self.positions[position_idx])
                else:
                    count = random.randint(1, self.positions[position_idx])
                return position_idx, count
            
            return 0, 1

class CardNimLogic:
    """Game logic for Card Nim"""
    
    def __init__(self):
        self.positions = []
        self.selected_position_index = None
        self.selected_count = 1
        self.game_over = False
        self.winner = None
        self.message = ""
        self.difficulty = None
        self.game_mode = None
        self.current_player = "Player 1"
        self.auto_player = None
    
    def initialize_game(self, game_mode, difficulty=None):
        """Initialize game with specified mode"""
        self.game_mode = game_mode
        self.difficulty = difficulty
        
        if self.game_mode == "PVP":
            min_pos, max_pos = (4, 6)
        else:
            min_pos, max_pos = DIFFICULTY_POSITION_RANGES.get(self.difficulty, (4, 6))
        
        n = random.randint(min_pos, max_pos)
        self.positions = [random.randint(1, 10) for _ in range(n)]
        self.selected_position_index = None
        self.selected_count = 1
        self.game_over = False
        self.winner = None
        self.current_player = "Player 1"
        
        if self.game_mode == "PVE":
            self.auto_player = AutoPlayer(self.positions)
        
        # Set initial message
        self._set_initial_message(n)
    
    def _set_initial_message(self, position_count):
        """Set the initial game message"""
        nim_sum = self.calculate_nim_sum()
        
        if self.game_mode == "PVP":
            mode_info = " (Player vs Player)"
        else:
            mode_info = f" (Player vs AI - {DIFFICULTY_NAMES[self.difficulty-1]})"
        
        position_info = f" | {position_count} positions"
        
        if nim_sum == 0:
            self.message = f"Game Started! {self.current_player} is in a losing position.{mode_info}{position_info}"
        else:
            self.message = f"Game Started! {self.current_player} is in a winning position.{mode_info}{position_info}"
    
    def calculate_nim_sum(self):
        """Calculate XOR of all positions"""
        nim_sum = 0
        for count in self.positions:
            nim_sum ^= count
        return nim_sum
    
    def make_move(self, position_idx, count):
        """Execute a move"""
        if (0 <= position_idx < len(self.positions) and 
            1 <= count <= self.positions[position_idx]):
            
            self.positions[position_idx] -= count
            self.message = f"{self.current_player} took {count} cards from position {position_idx + 1}."
            
            if self.game_mode == "PVE":
                self.auto_player.positions = self.positions
            
            if not any(self.positions):
                self.game_over = True
                self.winner = self.current_player
                self.message = f"Game Over! {self.current_player} Wins!"
                return True
            
            self.switch_player()
            return True
        return False
    
    def switch_player(self):
        """Switch between players"""
        if self.game_mode == "PVE":
            self.current_player = "AI" if self.current_player == "Player 1" else "Player 1"
        else:
            self.current_player = "Player 2" if self.current_player == "Player 1" else "Player 1"
    
    def ai_make_move(self):
        """Let AI make a move"""
        if (self.game_mode == "PVE" and 
            self.current_player == "AI" and 
            not self.game_over):
            
            position_idx, count = self.auto_player.move_instruction(self.difficulty)
            return self.make_move(position_idx, count)
        return False
    
    def select_position(self, position_idx):
        """Select a position for taking cards"""
        if 0 <= position_idx < len(self.positions) and self.positions[position_idx] > 0:
            self.selected_position_index = position_idx
            self.selected_count = 1
            
            if self.game_mode == "PVE":
                self.message = f"Selected position {position_idx + 1}, please select number of cards and press confirm."
            else:
                self.message = f"{self.current_player} selected position {position_idx + 1}, adjust cards and confirm."
            return True
        return False