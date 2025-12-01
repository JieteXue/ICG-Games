"""
Dawson-Kayles Game Logic
"""

import random
from typing import List, Tuple

class DawsonKaylesLogic:
    """Game logic for Dawson-Kayles (Tech Tower Defense theme)"""
    
    def __init__(self):
        self.num_towers = 0
        self.towers = []  # 1表示炮塔可用，0表示已被连接
        self.lasers = []  # 存储激光连接 [(start_idx, end_idx, player)]
        self.current_player = 1
        self.game_over = False
        self.winner = None
        self.message = ""
        self.game_mode = None
        self.difficulty = None
    
    def initialize_game(self, game_mode, difficulty=None):
        """Initialize a new game"""
        self.game_mode = game_mode
        self.difficulty = difficulty
        
        # 随机生成8-20个炮塔
        self.num_towers = random.randint(8, 20)
        self.towers = [1 for _ in range(self.num_towers)]
        self.lasers = []
        self.current_player = 1
        self.game_over = False
        self.winner = None
        
        if self.game_mode == "PVE":
            self.message = f"Game Started! {self.num_towers} towers deployed. Player 1's turn."
        else:
            self.message = f"Game Started! {self.num_towers} towers deployed. Player 1's turn."
    
    def get_available_moves(self):
        """获取所有可用的移动（相邻炮塔对）"""
        moves = []
        for i in range(len(self.towers) - 1):
            if self.towers[i] == 1 and self.towers[i + 1] == 1:
                moves.append(i)
        return moves
    
    def make_move(self, start_index):
        """执行移动（连接两个相邻炮塔）"""
        if start_index not in self.get_available_moves():
            return False
        
        # 添加激光连接
        self.lasers.append((start_index, start_index + 1, self.current_player))
        
        # 标记炮塔为已使用
        self.towers[start_index] = 0
        self.towers[start_index + 1] = 0
        
        # 检查游戏是否结束
        if not self.get_available_moves():
            self.game_over = True
            self.winner = 3 - self.current_player  # 对方获胜
            self.message = f"Game Over! Player {self.winner} wins! No more moves available."
        else:
            # 切换玩家
            self.current_player = 3 - self.current_player
            if self.game_mode == "PVE":
                if self.current_player == 2:  # AI的回合
                    self.message = f"Laser connected between towers {start_index} and {start_index + 1}. AI's turn."
                else:
                    self.message = f"Laser connected between towers {start_index} and {start_index + 1}. Player 1's turn."
            else:
                self.message = f"Laser connected between towers {start_index} and {start_index + 1}. Player {self.current_player}'s turn."
        
        return True
    
    def ai_make_move(self):
        """AI执行移动（PvE模式）"""
        if self.game_mode != "PVE" or self.current_player != 2 or self.game_over:
            return False
        
        available_moves = self.get_available_moves()
        if not available_moves:
            return False
        
        # 简单的AI策略：随机选择一个可用移动
        move = random.choice(available_moves)
        return self.make_move(move)
    
    def get_game_state(self):
        """返回游戏状态信息"""
        return {
            'num_towers': self.num_towers,
            'towers': self.towers.copy(),
            'lasers': self.lasers.copy(),
            'current_player': self.current_player,
            'game_over': self.game_over,
            'winner': self.winner,
            'available_moves': self.get_available_moves(),
            'message': self.message
        }