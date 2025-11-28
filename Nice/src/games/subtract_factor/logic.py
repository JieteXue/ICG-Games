"""
Subtract Factor Game Logic
"""

import random
import math
from utils.constants import *

class SubtractFactorAutoPlayer:
    """Handles AI logic for Subtract Factor game"""
    
    def __init__(self, current_value, threshold, winning_positions):
        self.current_value = current_value
        self.threshold = threshold
        self.winning_positions = winning_positions
    
    def this_turn_random(self, difficulty):
        """Determine if AI should make a random move based on difficulty"""
        return random.random() < DIFFICULTY_RANDOM_RATES.get(difficulty, 0.3)
    
    def get_valid_factors(self, number):
        """Get all valid factors for the current number"""
        if number <= 1:
            return []
        
        factors = set()
        i = 1
        while i * i <= number:
            if number % i == 0:
                if i < number:  # d must be less than m
                    factors.add(i)
                if number // i < number:  # d must be less than m
                    factors.add(number // i)
            i += 1
        
        return sorted(factors)
    
    def find_winning_move(self):
        """Find a move that leaves opponent in losing position"""
        valid_factors = self.get_valid_factors(self.current_value)
        
        for factor in valid_factors:
            new_value = self.current_value - factor
            if new_value < self.threshold:
                continue  # This move would lose immediately
            
            # Check if this move leaves opponent in losing position
            if new_value < len(self.winning_positions) and not self.winning_positions[new_value]:
                return factor
        
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
            valid_factors = self.get_valid_factors(self.current_value)
            if valid_factors:
                # Prefer larger factors on higher difficulties to end game faster
                if difficulty >= 3:  # Hard and Insane
                    # Sort factors and pick from larger ones
                    valid_factors.sort()
                    start_index = max(0, len(valid_factors) - len(valid_factors) // 3)
                    return random.choice(valid_factors[start_index:])
                else:
                    return random.choice(valid_factors)
            
            # Fallback
            return 1

class SubtractFactorLogic:
    """Game logic for Subtract Factor"""
    
    def __init__(self):
        self.initial_n = 0
        self.threshold_k = 0
        self.current_value = 0
        self.selected_factor = 1
        self.game_over = False
        self.winner = None
        self.message = ""
        self.difficulty = None
        self.game_mode = None
        self.current_player = "Player 1"
        self.auto_player = None
        self.winning_positions = []
        self.valid_factors = []
    
    def calculate_winning_positions(self):
        """Calculate winning positions using dynamic programming"""
        n = self.initial_n
        k = self.threshold_k
        
        # 增加数组大小以避免索引越界
        self.winning_positions = [False] * (n + 100)
        
        # 设置基础情况
        for i in range(k):
            if i < len(self.winning_positions):
                self.winning_positions[i] = False  # 低于阈值的位置是必败位置

        # 从阈值开始计算
        for m in range(k, n + 1):
            if m >= len(self.winning_positions):
                continue
                
            found_winning_move = False
            # Get all valid factors
            factors = self._get_factors_optimized(m)
            
            for factor in factors:
                new_val = m - factor
                if new_val < k:
                    continue  # This move would lose
                if new_val < len(self.winning_positions) and not self.winning_positions[new_val]:
                    found_winning_move = True
                    break
            
            self.winning_positions[m] = found_winning_move
    
    def _get_factors_optimized(self, n):
        """Get all proper factors of n (factors < n)"""
        if n <= 1:
            return []
        
        factors = set()
        i = 1
        while i * i <= n:
            if n % i == 0:
                if i < n:
                    factors.add(i)
                if n // i < n and n // i != i:  # 避免重复且确保小于n
                    factors.add(n // i)
            i += 1
        
        return sorted(factors)
    
    def update_valid_factors(self):
        """Update list of valid factors for current value"""
        self.valid_factors = self._get_factors_optimized(self.current_value)
        # Filter factors that don't immediately lose
        self.valid_factors = [f for f in self.valid_factors 
                            if (self.current_value - f) >= self.threshold_k]
    
    def judge_win(self):
        """Determine if current position is winning"""
        if self.current_value < self.threshold_k:
            return False
        if self.current_value >= len(self.winning_positions):
            # 对于超出预计算范围的值，使用实时计算
            return self._calculate_winning_position(self.current_value)
        return self.winning_positions[self.current_value]
    
    def _calculate_winning_position(self, value):
        """实时计算单个位置的胜负状态"""
        if value < self.threshold_k:
            return False
            
        factors = self._get_factors_optimized(value)
        for factor in factors:
            new_val = value - factor
            if new_val < self.threshold_k:
                continue
            if not self.judge_win_single(new_val):
                return True
        return False
    
    def judge_win_single(self, value):
        """判断单个位置的胜负状态（递归版本）"""
        if value < self.threshold_k:
            return False
            
        factors = self._get_factors_optimized(value)
        for factor in factors:
            new_val = value - factor
            if new_val < self.threshold_k:
                continue
            if not self.judge_win_single(new_val):
                return True
        return False
    
    def initialize_game(self, game_mode, difficulty=None):
        """Initialize a new game with larger numbers"""
        self.game_mode = game_mode
        self.difficulty = difficulty
        
        # 根据难度生成更大的数字范围
        if self.game_mode == "PVP":
            # PvP模式：中等范围
            min_n, max_n = (150, 300)
        else:
            # PvE模式：根据难度使用更大的范围
            difficulty_ranges = {
                1: (120, 200),   # Easy
                2: (150, 250),   # Normal  
                3: (200, 350),   # Hard
                4: (250, 500)    # Insane
            }
            min_n, max_n = difficulty_ranges.get(difficulty, (150, 250))
        
        self.initial_n = random.randint(min_n, max_n)
        
        # 调整阈值范围，确保游戏有足够的回合
        min_k = max(10, int(math.sqrt(self.initial_n) * 1.5))  # 提高最小阈值
        max_k = min(self.initial_n - 20, int(self.initial_n * 0.7))  # 降低最大阈值
        
        # 确保min_k不大于max_k
        if min_k > max_k:
            min_k = max(10, self.initial_n // 3)
            max_k = min(self.initial_n - 10, self.initial_n // 2)
        
        self.threshold_k = random.randint(min_k, max_k)
        
        self.current_value = self.initial_n
        self.selected_factor = 1
        self.game_over = False
        self.winner = None
        self.current_player = "Player 1"
        
        # 计算必胜位置
        self.calculate_winning_positions()
        self.update_valid_factors()
        
        if self.game_mode == "PVE":
            self.auto_player = SubtractFactorAutoPlayer(
                self.current_value, self.threshold_k, self.winning_positions
            )
        
        # 设置初始消息
        if self.game_mode == "PVP":
            mode_info = " (Player vs Player)"
        else:
            difficulty_names = ["Easy", "Normal", "Hard", "Insane"]
            mode_info = f" (Player vs AI - {difficulty_names[self.difficulty-1]})"
        
        position_state = "winning" if self.judge_win() else "losing"
        self.message = f"Game Started! n={self.initial_n}, k={self.threshold_k}. {self.current_player} is in a {position_state} position.{mode_info}"
    
    def make_move(self, factor):
        """Execute a move and return success status"""
        if factor not in self.valid_factors:
            return False
        
        new_value = self.current_value - factor
        
        # Check if this move causes immediate loss
        if new_value < self.threshold_k:
            self.game_over = True
            self.winner = "AI" if self.current_player == "Player 1" else "Player 1"
            self.message = f"{self.current_player} subtracted {factor}, resulting in {new_value} < {self.threshold_k}. {self.current_player} loses!"
            return True
        
        self.current_value = new_value
        self.message = f"{self.current_player} subtracted {factor}, new value: {self.current_value}."
        
        # Update AI's state if in PvE mode
        if self.game_mode == "PVE":
            self.auto_player.current_value = self.current_value
        
        self.update_valid_factors()
        
        # Check if game is over (no valid moves)
        if not self.valid_factors:
            self.game_over = True
            self.winner = self.current_player
            self.message = f"Game Over! {self.current_player} Wins! No valid moves left."
            return True
        
        # Switch player
        self.switch_player()
        
        # Update position analysis
        if self.game_mode == "PVE":
            position_state = "winning" if self.judge_win() else "losing"
            if self.current_player == "Player 1":
                self.message += f" You're in a {position_state} position."
            else:
                self.message += f" AI is in a {position_state} position."
        
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
            factor = self.auto_player.move_instruction(self.difficulty)
            if self.make_move(factor):
                return True
        return False
    
    def select_factor(self, factor):
        """Select a factor for the move"""
        if factor in self.valid_factors:
            self.selected_factor = factor
            
            if self.game_mode == "PVE":
                self.message = f"Selected factor: {factor}, press confirm to make move."
            else:
                self.message = f"{self.current_player} selected factor: {factor}, press confirm to make move."
            return True
        return False