"""
Split Cards Game Logic
"""

import random
from utils.constants import *  # Using relative imports

class SplitCardsLogic:
    """Game logic for Split Cards game"""
    
    def __init__(self):
        self.card_piles = []  # List of card piles
        self.max_take = 0  # Maximum number of cards that can be taken at once
        self.selected_pile_index = None  # Index of selected pile
        self.selected_action = None  # 'take' or 'split'
        self.selected_count = 1  # Number of cards to take or split point
        self.split_position = 0  # For split action, where to split
        self.game_over = False
        self.winner = None
        self.message = ""
        self.difficulty = None
        self.game_mode = None
        self.current_player = "Player 1"
        self.auto_player = None
        self.winning_hints_enabled = False  # New attribute for winning hints feature
    
    def calculate_sg_value(self, n, k):
        """Calculate Sprague-Grundy value for a pile"""
        if n % (2**k) == 0:
            return n - 1
        elif n % (2**k) == 2**k - 1:
            return n + 1
        else:
            return n
    
    def is_winning_position(self):
        """Check if current position is winning using SG theory"""
        if not self.card_piles:
            return False
        
        sg = 0
        for pile in self.card_piles:
            sg ^= self.calculate_sg_value(pile, self.max_take)
        
        return sg != 0
    
    def get_valid_moves(self):
        """Get all valid moves for current position"""
        moves = []
        
        # Take moves
        for i, pile in enumerate(self.card_piles):
            if pile > 0:
                for take_count in range(1, min(self.max_take, pile) + 1):
                    moves.append({
                        'type': 'take',
                        'pile_index': i,
                        'count': take_count
                    })
        
        # Split moves
        for i, pile in enumerate(self.card_piles):
            if pile > 1:  # Can only split piles with more than 1 card
                for split_point in range(1, pile):  # Split into two non-empty piles
                    moves.append({
                        'type': 'split',
                        'pile_index': i,
                        'left_count': split_point,
                        'right_count': pile - split_point
                    })
        
        return moves
    
    def find_winning_move(self):
        """Find a winning move using SG theory"""
        valid_moves = self.get_valid_moves()
        
        for move in valid_moves:
            # Simulate the move
            if move['type'] == 'take':
                new_piles = self.card_piles.copy()
                new_piles[move['pile_index']] -= move['count']
                if new_piles[move['pile_index']] == 0:
                    new_piles.pop(move['pile_index'])
            else:  # split
                new_piles = self.card_piles.copy()
                old_pile = new_piles.pop(move['pile_index'])
                new_piles.append(move['left_count'])
                new_piles.append(move['right_count'])
            
            # Check if resulting position is losing for opponent
            temp_logic = SplitCardsLogic()
            temp_logic.card_piles = new_piles
            temp_logic.max_take = self.max_take
            if not temp_logic.is_winning_position():
                return move
        
        return None
    
    def initialize_game(self, game_mode, difficulty=None, winning_hints=False):
        """Initialize a new game with winning hints support"""
        self.game_mode = game_mode
        self.difficulty = difficulty
        self.winning_hints_enabled = winning_hints
        
        # Reset all state attributes
        self.selected_pile_index = None
        self.selected_action = None
        self.selected_count = 1
        self.split_position = 0
        self.game_over = False
        self.winner = None
        self.current_player = "Player 1"
        
        # Set parameters based on difficulty
        if self.game_mode == "PVP":
            # PvP mode: medium settings
            self.max_take = random.randint(3, 6)
            initial_pile = random.randint(15, 25)
            self.card_piles = [initial_pile]
        else:
            # PvE mode: difficulty-based settings
            difficulty_ranges = {
                1: {'max_take': (2, 4), 'initial_pile': (10, 15)},  # Easy
                2: {'max_take': (3, 6), 'initial_pile': (15, 20)},  # Normal
                3: {'max_take': (4, 8), 'initial_pile': (20, 25)},  # Hard
                4: {'max_take': (5, 10), 'initial_pile': (25, 50)}  # Insane
            }
            
            ranges = difficulty_ranges.get(self.difficulty, difficulty_ranges[2])
            self.max_take = random.randint(ranges['max_take'][0], ranges['max_take'][1])
            initial_pile = random.randint(ranges['initial_pile'][0], ranges['initial_pile'][1])
            self.card_piles = [initial_pile]
        
        # Ensure it's a winning position for first player in PvE
        if self.game_mode == "PVE" and not self.is_winning_position():
            # Adjust max_take to make it winning
            while not self.is_winning_position() and self.max_take > 1:
                self.max_take -= 1
        
        # Set up AI for PvE mode
        if self.game_mode == "PVE":
            self.auto_player = SplitCardsAI(self)
        
        # Set initial message
        if self.winning_hints_enabled:
            self.message = f"Game Started! {initial_pile} cards in one pile. Max take: {self.max_take}. Winning Hints enabled. {self.current_player}'s turn."
        else:
            self.message = f"Game Started! {initial_pile} cards in one pile. Max take: {self.max_take}. {self.current_player}'s turn."
    
    def make_move(self, move_info):
        """Execute a move"""
        if self.game_over:
            return False
        
        move_type = move_info.get('type')
        
        if move_type == 'take':
            pile_idx = move_info.get('pile_index')
            count = move_info.get('count')
            
            if (0 <= pile_idx < len(self.card_piles) and 
                1 <= count <= min(self.max_take, self.card_piles[pile_idx])):
                
                self.card_piles[pile_idx] -= count
                self.message = f"{self.current_player} took {count} card(s) from pile {pile_idx + 1}."
                
                # Remove empty piles
                if self.card_piles[pile_idx] == 0:
                    self.card_piles.pop(pile_idx)
        elif move_type == 'split':
            pile_idx = move_info.get('pile_index')
            left_count = move_info.get('left_count')
            right_count = move_info.get('right_count')
            
            if (0 <= pile_idx < len(self.card_piles) and
                left_count > 0 and right_count > 0 and
                left_count + right_count == self.card_piles[pile_idx]):
                
                # Remove the original pile and add two new piles
                self.card_piles.pop(pile_idx)
                self.card_piles.append(left_count)
                self.card_piles.append(right_count)
                self.message = f"{self.current_player} split pile {pile_idx + 1} into piles of {left_count} and {right_count} cards."
        else:
            return False
        
        # Check if game is over (no cards left)
        if not any(self.card_piles):
            self.game_over = True
            self.winner = self.current_player
            self.message = f"Game Over! {self.current_player} Wins!"
            return True
        
        # Switch player
        self.switch_player()
        return True
    
    def switch_player(self):
        """Switch between players"""
        if self.game_mode == "PVE":
            if self.current_player == "Player 1":
                self.current_player = "AI"
                if not self.game_over:
                    self.message += f" AI's turn. {len(self.card_piles)} piles remaining."
            else:
                self.current_player = "Player 1"
                if not self.game_over:
                    self.message += f" Your turn. {len(self.card_piles)} piles remaining."
        else:
            # PvP mode
            if self.current_player == "Player 1":
                self.current_player = "Player 2"
                if not self.game_over:
                    self.message += f" {self.current_player}'s turn. {len(self.card_piles)} piles remaining."
            else:
                self.current_player = "Player 1"
                if not self.game_over:
                    self.message += f" {self.current_player}'s turn. {len(self.card_piles)} piles remaining."
    
    def ai_make_move(self):
        """Let AI make a move (only in PvE mode)"""
        if (self.game_mode == "PVE" and 
            self.current_player == "AI" and 
            not self.game_over):
            
            move = self.auto_player.get_move()
            if move:
                return self.make_move(move)
        return False
    
    def get_winning_hint(self):
        """Get winning hint analysis"""
        if not hasattr(self, 'winning_hints_enabled') or not self.winning_hints_enabled:
            return "Winning hints are disabled. Enable them in settings to get AI suggestions."
        
        if self.game_over:
            return f"Game Over! {self.winner} wins!\n\nRestart the game to play again."
        
        # Check if it's a winning position
        is_winning = self.is_winning_position()
        
        hint = ""
        if is_winning:
            hint += "WINNING POSITION - Optimal Move:\n\n"
            
            # Find a winning move
            winning_move = self.find_winning_move()
            if winning_move:
                if winning_move['type'] == 'take':
                    hint += f"ACTION: Take {winning_move['count']} card(s) from Pile {winning_move['pile_index'] + 1}\n\n"
                    hint += f"Steps:\n"
                    hint += f"1. Click on Pile {winning_move['pile_index'] + 1}\n"
                    hint += f"2. Click 'Take Cards' button\n"
                    hint += f"3. Set number to {winning_move['count']} (use arrows or type directly)\n"
                    hint += f"4. Click 'Confirm Move' or press ENTER\n"
                else:  # split
                    hint += f"ACTION: Split Pile {winning_move['pile_index'] + 1} into {winning_move['left_count']} and {winning_move['right_count']} cards\n\n"
                    hint += f"Steps:\n"
                    hint += f"1. Click on Pile {winning_move['pile_index'] + 1}\n"
                    hint += f"2. Click 'Split Pile' button\n"
                    hint += f"3. Set split point to {winning_move['left_count']} (use arrows or type directly)\n"
                    hint += f"4. Click 'Confirm Move' or press ENTER\n"
                
                hint += f"\nReason: This move leaves opponent in a losing position."
            else:
                hint += "No winning move found. All moves lead to opponent advantage.\n"
                hint += "Try any move and hope for opponent mistake."
        
        else:
            hint += "LOSING POSITION - Best Defense:\n\n"
            
            # Find best defensive move (most complex position)
            valid_moves = self.get_valid_moves()
            best_move = None
            max_complexity = 0
            
            for move in valid_moves:
                # Calculate complexity: number of piles after move
                if move['type'] == 'take':
                    new_piles = len(self.card_piles)
                    if self.card_piles[move['pile_index']] - move['count'] == 0:
                        new_piles -= 1
                else:  # split
                    new_piles = len(self.card_piles) + 1  # One pile becomes two
                
                if new_piles > max_complexity:
                    max_complexity = new_piles
                    best_move = move
            
            if best_move:
                if best_move['type'] == 'take':
                    hint += f"ACTION: Take {best_move['count']} card(s) from Pile {best_move['pile_index'] + 1}\n\n"
                    hint += f"Steps:\n"
                    hint += f"1. Click on Pile {best_move['pile_index'] + 1}\n"
                    hint += f"2. Click 'Take Cards' button\n"
                    hint += f"3. Set number to {best_move['count']} (use arrows or type directly)\n"
                    hint += f"4. Click 'Confirm Move' or press ENTER\n"
                else:  # split
                    hint += f"ACTION: Split Pile {best_move['pile_index'] + 1} into {best_move['left_count']} and {best_move['right_count']} cards\n\n"
                    hint += f"Steps:\n"
                    hint += f"1. Click on Pile {best_move['pile_index'] + 1}\n"
                    hint += f"2. Click 'Split Pile' button\n"
                    hint += f"3. Set split point to {best_move['left_count']} (use arrows or type directly)\n"
                    hint += f"4. Click 'Confirm Move' or press ENTER\n"
                
                hint += f"\nReason: This creates {max_complexity} piles, giving opponent more chances to make mistakes."
        
        # Add quick summary
        hint += f"\n\nCurrent: Piles: {self.card_piles}, Max take: {self.max_take}"
        
        return hint


class SplitCardsAI:
    """AI logic for Split Cards game"""
    
    def __init__(self, game_logic):
        self.game_logic = game_logic
        self.difficulty = game_logic.difficulty
    
    def get_move(self):
        """Get AI move based on difficulty"""
        valid_moves = self.game_logic.get_valid_moves()
        
        if not valid_moves:
            return None
        
        # Based on difficulty, choose strategy
        if self.difficulty == 1:  # Easy: mostly random
            if random.random() < 0.7:  # 70% random
                return random.choice(valid_moves)
            else:
                return self.find_winning_move(valid_moves)
        elif self.difficulty == 2:  # Normal: mixed
            if random.random() < 0.5:  # 50% random
                return random.choice(valid_moves)
            else:
                return self.find_winning_move(valid_moves)
        elif self.difficulty == 3:  # Hard: mostly optimal
            if random.random() < 0.2:  # 20% random
                return random.choice(valid_moves)
            else:
                return self.find_winning_move(valid_moves)
        else:  # Insane: always optimal
            return self.find_winning_move(valid_moves)
    
    def find_winning_move(self, valid_moves):
        """Find a winning move if exists, otherwise random"""
        for move in valid_moves:
            # Test if this move leads to a losing position for opponent
            test_game = SplitCardsLogic()
            test_game.card_piles = self.game_logic.card_piles.copy()
            test_game.max_take = self.game_logic.max_take
            
            if move['type'] == 'take':
                test_game.card_piles[move['pile_index']] -= move['count']
                if test_game.card_piles[move['pile_index']] == 0:
                    test_game.card_piles.pop(move['pile_index'])
            else:  # split
                pile_idx = move['pile_index']
                test_game.card_piles.pop(pile_idx)
                test_game.card_piles.append(move['left_count'])
                test_game.card_piles.append(move['right_count'])
            
            if not test_game.is_winning_position():
                return move
        
        # No winning move found, return random
        return random.choice(valid_moves)