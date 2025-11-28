
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
        
        for i in range(1, n - 1):  # 只能选择中间位置
            if coins[i-1] >= 1 and coins[i+1] >= 1:
                if coins[i-1] - 1 >= 0 and coins[i+1] - 1 >= 0:
                    valid_positions.append(i)
        return valid_positions
    
    def judge_win(self, coins):
        """Determine if current position is winning for the player to move"""
        return self._judge_win_internal(tuple(coins))
    
    @staticmethod
    @lru_cache(maxsize=None)
    def _judge_win_internal(state):
        """递归判断：当前玩家是否能强制获胜"""
        state_list = list(state)
        n = len(state_list)
        
        has_legal_move = False
        for i in range(1, n - 1):
            # 检查是否为合法移动
            if state_list[i-1] >= 1 and state_list[i+1] >= 1:
                has_legal_move = True
                # 模拟移动
                new_state = state_list.copy()
                new_state[i] += 1
                new_state[i-1] -= 1
                new_state[i+1] -= 1
                
                # 确保移动后硬币数非负
                if new_state[i-1] >= 0 and new_state[i+1] >= 0:
                    # 关键：如果存在一个移动能让对手处于必败局面，则当前玩家必胜
                    if not TakeCoinsAutoPlayer._judge_win_internal(tuple(new_state)):
                        return True
        # 如果没有合法移动，当前玩家输；或者有移动但无法让对手必败，当前玩家输
        return False
    
    def find_winning_move(self):
        """寻找能让对手处于必败局面的移动"""
        valid_positions = self.get_valid_positions(self.coins)
        
        for pos in valid_positions:
            # 模拟移动
            new_coins = self.coins.copy()
            new_coins[pos] += 1
            new_coins[pos-1] -= 1
            new_coins[pos+1] -= 1
            
            # 检查移动后对手是否处于必败局面
            if not self.judge_win(new_coins):
                return pos
        
        return None
    
    def move_instruction(self, difficulty):
        """生成AI移动指令"""
        # 首先尝试寻找必胜移动
        winning_move = self.find_winning_move()
        
        if winning_move and not self.this_turn_random(difficulty):
            return winning_move
        else:
            # 随机移动
            valid_positions = self.get_valid_positions(self.coins)
            if valid_positions:
                return random.choice(valid_positions)
            return None

class TakeCoinsLogic:
    """Take Coins游戏逻辑 - 无法移动的玩家输"""
    
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
    
    def judge_win(self, coins=None):
        """判断当前局面是否对当前玩家有利"""
        if coins is None:
            coins = self.coins
        return self._judge_win_internal(tuple(coins))
    
    @staticmethod
    @lru_cache(maxsize=None)
    def _judge_win_internal(state):
        """递归判断：当前玩家是否能强制获胜"""
        state_list = list(state)
        n = len(state_list)
        
        has_legal_move = False
        for i in range(1, n - 1):
            if state_list[i-1] >= 1 and state_list[i+1] >= 1:
                has_legal_move = True
                new_state = state_list.copy()
                new_state[i] += 1
                new_state[i-1] -= 1
                new_state[i+1] -= 1
                
                if new_state[i-1] >= 0 and new_state[i+1] >= 0:
                    if not TakeCoinsLogic._judge_win_internal(tuple(new_state)):
                        return True
        return False
    
    def initialize_game(self, game_mode, difficulty=None, num_positions=None):
        """初始化游戏 - PvE模式下确保玩家处于必胜局面"""
        self.game_mode = game_mode
        self.difficulty = difficulty
        
        # 生成位置数量
        if num_positions is None:
            if game_mode == "PVP":
                num_positions = random.randint(8, 12)
            else:
                difficulty_ranges = {
                    1: (8, 10), 2: (9, 11), 3: (10, 12), 4: (11, 14)
                }
                min_n, max_n = difficulty_ranges.get(difficulty, (8, 12))
                num_positions = random.randint(min_n, max_n)
        
        # 对于PvE模式，确保玩家处于必胜局面
        max_attempts = 100
        attempt_count = 0
        
        while attempt_count < max_attempts:
            attempt_count += 1
            self.coins = [random.randint(1, 3) for _ in range(num_positions)]
            self.update_valid_positions()
            
            if self.valid_positions:  # 确保有合法移动
                if self.game_mode == "PVE":
                    # 检查当前玩家（Player 1）是否能强制获胜
                    if self.judge_win():
                        break  # 找到玩家必胜局面
                else:
                    break  # PvP模式不关心初始胜负
        
        # 备用方案
        if attempt_count >= max_attempts:
            self.coins = [random.randint(1, 3) for _ in range(num_positions)]
            self.update_valid_positions()
            while not self.valid_positions:
                self.coins = [random.randint(1, 3) for _ in range(num_positions)]
                self.update_valid_positions()
        
        self.selected_position = None
        self.game_over = False
        self.winner = None
        self.current_player = "Player 1"
        
        if self.game_mode == "PVE":
            self.auto_player = TakeCoinsAutoPlayer(self.coins)
        
        self.update_valid_positions()
        
        # 设置初始消息
        if self.game_mode == "PVP":
            mode_info = " (Player vs Player)"
        else:
            difficulty_names = ["Easy", "Normal", "Hard", "Insane"]
            mode_info = f" (Player vs AI - {difficulty_names[self.difficulty-1]})"
        
        # 显示当前玩家的局面状态
        is_winning = self.judge_win()
        position_state = "winning" if is_winning else "losing"
        self.message = f"Game Started! {len(self.coins)} positions. {self.current_player} is in a {position_state} position.{mode_info}"
    
    def update_valid_positions(self):
        """更新合法移动位置列表"""
        self.valid_positions = []
        n = len(self.coins)

        for i in range(1, n - 1):
            if self.coins[i-1] >= 1 and self.coins[i+1] >= 1:
                if self.coins[i-1] - 1 >= 0 and self.coins[i+1] - 1 >= 0:
                    self.valid_positions.append(i)

        # 检查游戏是否结束
        if not self.valid_positions and not self.game_over:
            self.game_over = True
            # 当前玩家无法移动，所以当前玩家输
            if self.game_mode == "PVE":
                self.winner = "AI" if self.current_player == "Player 1" else "Player 1"
            else:
                self.winner = "Player 2" if self.current_player == "Player 1" else "Player 1"
            self.message = f"Game Over! {self.winner} Wins! {self.current_player} has no valid moves."
    
    # 其他方法保持不变...
    def select_position(self, position):
        """选择移动位置"""
        if position == 0 or position == len(self.coins) - 1:
            self.message = f"Cannot select boundary position {position}."
            return False
            
        if position in self.valid_positions:
            self.selected_position = position
            if self.game_mode == "PVE":
                self.message = f"Selected position: {position}, press confirm to make move."
            else:
                self.message = f"{self.current_player} selected position: {position}, press confirm to make move."
            return True
        
        if position < 0 or position >= len(self.coins):
            self.message = f"Invalid position: {position}. Position out of range."
        elif self.coins[position-1] < 1 or self.coins[position+1] < 1:
            self.message = f"Invalid position: {position}. Neighbors don't have enough coins."
        else:
            self.message = f"Invalid position: {position}. Please select a valid position."
        return False
    
    def make_move(self):
        """执行移动"""
        if self.selected_position is None or self.selected_position not in self.valid_positions:
            self.message = "No valid position selected!"
            return False
        
        i = self.selected_position
        
        # 验证移动
        if i == 0 or i == len(self.coins) - 1:
            self.message = "Cannot move at boundary positions!"
            return False
            
        if not (self.coins[i-1] >= 1 and self.coins[i+1] >= 1):
            self.message = "Invalid move: Not enough coins in adjacent positions!"
            return False
        
        # 执行移动
        self.coins[i] += 1
        self.coins[i-1] -= 1
        self.coins[i+1] -= 1
        
        self.message = f"{self.current_player} moved at position {i}."
        
        # 更新AI状态
        if self.game_mode == "PVE":
            self.auto_player.coins = self.coins
        
        if not self.game_over:
            # 切换玩家
            self.switch_player()
            
            # 更新合法移动和检查游戏结束
            self.update_valid_positions()
            
            # 更新局面分析
            is_winning = self.judge_win()
            if self.game_mode == "PVE":
                if self.current_player == "Player 1":
                    state_msg = "winning" if is_winning else "losing"
                    self.message += f" You are in a {state_msg} position."
                else:
                    state_msg = "winning" if is_winning else "losing"
                    self.message += f" AI is in a {state_msg} position."
        
        self.selected_position = None
        return True
    
    def switch_player(self):
        """切换玩家"""
        if self.game_mode == "PVE":
            self.current_player = "AI" if self.current_player == "Player 1" else "Player 1"
        else:
            self.current_player = "Player 2" if self.current_player == "Player 1" else "Player 1"
            self.message += f" {self.current_player}'s turn."
    
    def ai_make_move(self):
        """AI移动"""
        if self.game_mode == "PVE" and self.current_player == "AI" and not self.game_over:
            position = self.auto_player.move_instruction(self.difficulty)
            if position is not None:
                self.select_position(position)
                if self.make_move():
                    return True
                else:
                    # 如果AI选择的移动无效，尝试其他移动
                    valid_positions = self.get_valid_positions()
                    if valid_positions:
                        position = random.choice(valid_positions)
                        self.select_position(position)
                        return self.make_move()
        return False
    
    def get_valid_positions(self):
        """获取合法移动位置"""
        positions = []
        n = len(self.coins)
        for i in range(1, n - 1):
            if self.coins[i-1] >= 1 and self.coins[i+1] >= 1:
                if self.coins[i-1] - 1 >= 0 and self.coins[i+1] - 1 >= 0:
                    positions.append(i)
        return positions