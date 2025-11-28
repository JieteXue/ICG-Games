# [file name]: games/take_coins/logic.py
"""
Take Coins Game Logic - Player who cannot move loses
"""

import random
import copy
from functools import lru_cache

class TakeCoinsAutoPlayer:
    """Handles AI logic for Take Coins game"""
    
    def __init__(self, coins):
        self.coins = coins
    
    def this_turn_random(self, difficulty):
        """Determine if AI should make a random move based on difficulty"""
        random_rates = {1: 0.6, 2: 0.4, 3: 0.2, 4: 0.1}
        return random.random() < random_rates.get(difficulty, 0.4)
    
    def get_valid_positions(self, coins):
        """Get all valid positions for the current coin configuration"""
        valid_positions = []
        n = len(coins)
        
        # Can only select middle positions (not first or last due to boundary)
        for i in range(1, n - 1):  # From 1 to n-2, exclude boundaries
            # Check if neighbors have enough coins (at least 1)
            if coins[i-1] >= 1 and coins[i+1] >= 1:
                # Check if coin counts remain valid after move
                if coins[i-1] - 1 >= 0 and coins[i+1] - 1 >= 0:
                    valid_positions.append(i)
        
        return valid_positions
    
    def find_winning_move(self):
        """Find a move that leaves opponent with no valid moves"""
        valid_positions = self.get_valid_positions(self.coins)
        
        for pos in valid_positions:
            # Simulate the move
            new_coins = self.coins.copy()
            new_coins[pos] += 1
            new_coins[pos-1] -= 1
            new_coins[pos+1] -= 1
            
            # Check if opponent has no valid moves after this move
            opponent_valid_moves = self.get_valid_positions(new_coins)
            is_losing_for_opponent = (len(opponent_valid_moves) == 0)
            
            if is_losing_for_opponent:
                return pos
        
        return None
    
    def move_instruction(self, difficulty):
        """Generate move instruction for AI"""
        # Try to find a winning move first
        winning_move = self.find_winning_move()
        
        # For higher difficulties, use winning moves more often
        if winning_move and not self.this_turn_random(difficulty):
            return winning_move
        else:
            # Make a random valid move
            valid_positions = self.get_valid_positions(self.coins)
            if valid_positions:
                return random.choice(valid_positions)
            
            return None

class TakeCoinsLogic:
    """Game logic for Take Coins - Player who cannot move loses"""
    
    def __init__(self):
        self.coins = []
        self.selected_position = None
        self.game_over = False
        self.winner = None
        self.message = ""
        self.difficulty = None
        self.game_mode = None
        self.current_player = "Player 1"
        self.auto_player = None
        self.valid_positions = []
    
    def initialize_game(self, game_mode, difficulty=None, num_positions=None):
        """Initialize a new game"""
        self.game_mode = game_mode
        self.difficulty = difficulty
        
        # Generate random coin configuration
        if num_positions is None:
            if game_mode == "PVP":
                num_positions = random.randint(8, 12)
            else:
                # Adjust based on difficulty
                difficulty_ranges = {
                    1: (8, 10),   # Easy
                    2: (9, 11),   # Normal  
                    3: (10, 12),  # Hard
                    4: (11, 14)   # Insane
                }
                min_n, max_n = difficulty_ranges.get(difficulty, (8, 12))
                num_positions = random.randint(min_n, max_n)
        
        # Ensure initial configuration has at least one valid move
        while True:
            self.coins = [random.randint(1, 3) for _ in range(num_positions)]
            self.update_valid_positions()
            if self.valid_positions:  # Ensure at least one valid move
                break
        
        self.selected_position = None
        self.game_over = False
        self.winner = None
        self.current_player = "Player 1"
        
        if self.game_mode == "PVE":
            self.auto_player = TakeCoinsAutoPlayer(self.coins)
        
        self.update_valid_positions()
        
        # Set initial message
        if self.game_mode == "PVP":
            mode_info = " (Player vs Player)"
        else:
            difficulty_names = ["Easy", "Normal", "Hard", "Insane"]
            mode_info = f" (Player vs AI - {difficulty_names[self.difficulty-1]})"
        
        self.message = f"Game Started! {len(self.coins)} positions. {self.current_player}'s turn.{mode_info}"
    
    def update_valid_positions(self):
        """Update list of valid positions with proper boundary handling"""
        self.valid_positions = []
        n = len(self.coins)

        # Can only select middle positions (not first or last due to boundary)
        for i in range(1, n - 1):  # From 1 to n-2, exclude boundaries
            # Check if neighbors have enough coins (at least 1)
            if self.coins[i-1] >= 1 and self.coins[i+1] >= 1:
                # Check if coin counts remain valid after move
                if self.coins[i-1] - 1 >= 0 and self.coins[i+1] - 1 >= 0:
                    self.valid_positions.append(i)

        if not self.valid_positions and not self.game_over:
            self.game_over = True
            # 当前玩家无法移动，所以当前玩家输，对手获胜
            if self.game_mode == "PVE":
                self.winner = "Player 1" if self.current_player == "AI" else "AI"
            else:
                self.winner = "Player 1" if self.current_player == "Player 2" else "Player 2"
            self.message = f"Game Over! {self.winner} Wins! {self.current_player} has no valid moves."
    
    def judge_win(self):
        """Determine if current position is winning"""
        # Correct: If current player has valid moves, it's an advantageous position
        # If current player has no valid moves, it's a losing position
        has_valid_moves = len(self.valid_positions) > 0
        return has_valid_moves
    
    def select_position(self, position):
        """Select a position for the move"""
        # Boundary positions (first and last) cannot be selected
        if position == 0 or position == len(self.coins) - 1:
            self.message = f"Cannot select boundary position {position}. Must select middle positions."
            return False
            
        if position in self.valid_positions:
            self.selected_position = position
            
            if self.game_mode == "PVE":
                self.message = f"Selected position: {position}, press confirm to make move."
            else:
                self.message = f"{self.current_player} selected position: {position}, press confirm to make move."
            return True
        
        # Check why invalid
        if position < 0 or position >= len(self.coins):
            self.message = f"Invalid position: {position}. Position out of range."
        elif self.coins[position-1] < 1 or self.coins[position+1] < 1:
            self.message = f"Invalid position: {position}. Neighbors don't have enough coins."
        else:
            self.message = f"Invalid position: {position}. Please select a valid position."
        
        return False
    
    # 在 TakeCoinsLogic 类的 make_move 方法中修复：

    def make_move(self):
        """Execute the selected move with proper validation"""
        if (self.selected_position is None or 
            self.selected_position not in self.valid_positions):
            self.message = "No valid position selected!"
            return False
        
        i = self.selected_position
        
        # Validate move again
        if i == 0 or i == len(self.coins) - 1:
            self.message = "Cannot move at boundary positions!"
            return False
            
        if not (self.coins[i-1] >= 1 and self.coins[i+1] >= 1):
            self.message = "Invalid move: Not enough coins in adjacent positions!"
            return False
        
        if not (self.coins[i-1] - 1 >= 0 and self.coins[i+1] - 1 >= 0):
            self.message = "Invalid move: Move would create negative coins!"
            return False
        
        # Apply the move
        self.coins[i] += 1
        self.coins[i-1] -= 1
        self.coins[i+1] -= 1
        
        self.message = f"{self.current_player} moved at position {i}."
        
        # Update AI's state if in PvE mode
        if self.game_mode == "PVE":
            self.auto_player.coins = self.coins
        
        # 修复：先切换玩家，再检查游戏结束
        if not self.game_over:
            # Switch player first
            self.switch_player()
            
            # Then update valid positions and check game over
            self.update_valid_positions()
            
            # Update position analysis
            has_valid_moves = len(self.valid_positions) > 0
            if self.game_mode == "PVE":
                if self.current_player == "Player 1":
                    if has_valid_moves:
                        self.message += f" You have valid moves."
                    else:
                        self.message += f" You have no valid moves!"
                else:
                    if has_valid_moves:
                        self.message += f" AI has valid moves."
                    else:
                        self.message += f" AI has no valid moves!"
        
        self.selected_position = None
        return True
    
    def switch_player(self):
        """Switch between players"""
        if self.game_mode == "PVE":
            if self.current_player == "Player 1":
                self.current_player = "AI"
            else:
                self.current_player = "Player 1"
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
            position = self.auto_player.move_instruction(self.difficulty)
            if position is not None:
                self.select_position(position)
                if self.make_move():
                    return True
                else:
                    # If AI's chosen move is invalid, try another move
                    valid_positions = self.get_valid_positions()
                    if valid_positions:
                        position = random.choice(valid_positions)
                        self.select_position(position)
                        return self.make_move()
        return False
    
    def get_valid_positions(self):
        """Public method to get valid positions"""
        positions = []
        n = len(self.coins)
        
        for i in range(1, n - 1):  # Exclude boundaries
            if self.coins[i-1] >= 1 and self.coins[i+1] >= 1:
                if self.coins[i-1] - 1 >= 0 and self.coins[i+1] - 1 >= 0:
                    positions.append(i)
        
        return positions