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

        # If nim-sum is already 0, any move will make it non-zero (losing position)
        if current_nim_sum == 0:
            return None

        # Find a move that makes nim-sum zero
        for i in range(len(self.positions)):
            if self.positions[i] > 0:
                # We need to find count such that: positions[i] XOR count = current_nim_sum XOR positions[i]
                # This means: count = positions[i] - (current_nim_sum XOR positions[i])
                target = current_nim_sum ^ self.positions[i]
                if target < self.positions[i]:
                    count = self.positions[i] - target
                    if 1 <= count <= self.positions[i]:
                        return i, count
        return None

    def move_instruction(self, difficulty):
        """Generate move instruction for AI"""
        # Try to find a winning move first
        winning_move = self.find_winning_move()

        # For higher difficulties, use winning moves more often
        if winning_move and not self.this_turn_random(difficulty):
            return winning_move
        else:
            # Make a random move
            available_moves = []
            for i in range(len(self.positions)):
                if self.positions[i] > 0:
                    available_moves.append(i)

            if available_moves:
                position_idx = random.choice(available_moves)
                # Prefer taking more cards to end game faster
                if difficulty >= 3:  # Hard and Insane take more cards
                    count = random.randint(max(1, self.positions[position_idx] // 2), self.positions[position_idx])
                else:
                    count = random.randint(1, self.positions[position_idx])
                return position_idx, count

            # Fallback
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

    def calculate_nim_sum(self):
        """Calculate the XOR (nim-sum) of all positions"""
        nim_sum = 0
        for count in self.positions:
            nim_sum ^= count
        return nim_sum

    def judge_win(self):
        """Determine if current position is winning using XOR (nim-sum)"""
        return self.calculate_nim_sum() != 0

    def generate_winning_position(self, min_pos, max_pos):
        """Generate a position where nim-sum != 0 (winning position for first player)"""
        while True:
            n = random.randint(min_pos, max_pos)
            self.positions = [random.randint(1, 10) for _ in range(n)]
            
            # Ensure it's a winning position (nim-sum != 0)
            if self.calculate_nim_sum() != 0:
                return

    def generate_losing_position(self, min_pos, max_pos):
        """Generate a position where nim-sum == 0 (losing position for first player)"""
        while True:
            n = random.randint(min_pos, max_pos)
            self.positions = [random.randint(1, 10) for _ in range(n)]
            
            # Ensure it's a losing position (nim-sum == 0)
            if self.calculate_nim_sum() == 0:
                return

    def initialize_game(self, game_mode, difficulty=None):
        """Initialize a new game with difficulty-based position count"""
        self.game_mode = game_mode
        self.difficulty = difficulty

        # Set position count based on game mode and difficulty
        if self.game_mode == "PVP":
            # PvP mode: fixed medium difficulty
            min_pos, max_pos = (4, 6)
            # PvP mode: randomly choose winning or losing position
            if random.choice([True, False]):
                self.generate_winning_position(min_pos, max_pos)
            else:
                self.generate_losing_position(min_pos, max_pos)
        else:
            # PvE mode: use difficulty-based ranges
            min_pos, max_pos = DIFFICULTY_POSITION_RANGES.get(self.difficulty, (4, 6))
            # PvE mode: ALWAYS generate winning position for player
            self.generate_winning_position(min_pos, max_pos)

        self.selected_position_index = None
        self.selected_count = 1
        self.game_over = False
        self.winner = None
        self.current_player = "Player 1"

        if self.game_mode == "PVE":
            self.auto_player = AutoPlayer(self.positions)

        # Show initial game state with mode info
        nim_sum = self.calculate_nim_sum()
        if self.game_mode == "PVP":
            mode_info = " (Player vs Player)"
        else:
            difficulty_names = ["Easy", "Normal", "Hard", "Insane"]
            mode_info = f" (Player vs AI - {difficulty_names[self.difficulty-1]})"

        position_info = f" | {len(self.positions)} positions"

        if nim_sum == 0:
            self.message = f"Game Started! {self.current_player} is in a losing position.{mode_info}{position_info}"
        else:
            self.message = f"Game Started! {self.current_player} is in a winning position.{mode_info}{position_info}"

    def make_move(self, position_idx, count):
        """Execute a move and return success status"""
        if (0 <= position_idx < len(self.positions) and
            1 <= count <= self.positions[position_idx]):

            self.positions[position_idx] -= count
            self.message = f"{self.current_player} took {count} cards from position {position_idx + 1}."

            # Update AI's positions reference if in PvE mode
            if self.game_mode == "PVE":
                self.auto_player.positions = self.positions

            # Check if game is over
            if not any(self.positions):
                self.game_over = True
                self.winner = self.current_player
                self.message = f"Game Over! {self.current_player} Wins!"
                return True

            # Show position analysis after move (only in PvE mode)
            if self.game_mode == "PVE":
                nim_sum = self.calculate_nim_sum()
                if self.current_player == "Player 1":
                    if nim_sum == 0:
                        self.message += " You left a losing position for AI."
                    else:
                        self.message += " You left a winning position for AI."
                else:
                    if nim_sum == 0:
                        self.message += " AI left you in a losing position."
                    else:
                        self.message += " AI left you in a winning position."

            # Switch player
            self.switch_player()
            return True
        return False

    def switch_player(self):
        """Switch between players"""
        if self.game_mode == "PVE":
            if self.current_player == "Player 1":
                self.current_player = "AI"
                # Add analysis for AI's turn
                nim_sum = self.calculate_nim_sum()
                if nim_sum == 0:
                    self.message += " AI is in a losing position."
                else:
                    self.message += " AI is in a winning position."
            else:
                self.current_player = "Player 1"
                # Add analysis for player's turn
                nim_sum = self.calculate_nim_sum()
                if nim_sum == 0:
                    self.message += " You're in a losing position."
                else:
                    self.message += " You're in a winning position."
        else:
            # PvP mode
            if self.current_player == "Player 1":
                self.current_player = "Player 2"
                self.message += f" {self.current_player}'s turn."
            else:
                self.current_player = "Player 1"
                self.message += f" {self.current_player}'s turn."

    def ai_make_move(self):
        """Let AI make a move (only in PvE mode)"""
        if self.game_mode == "PVE" and self.current_player == "AI" and not self.game_over:
            position_idx, count = self.auto_player.move_instruction(self.difficulty)
            if self.make_move(position_idx, count):
                return True
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