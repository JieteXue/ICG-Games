"""
Split Cards Game Logic
神秘魔术风格的卡牌分割游戏逻辑
"""

import random
import math
from typing import List, Dict, Tuple, Optional

class SplitCardsLogic:
    """Split Cards游戏逻辑"""
    
    def __init__(self):
        self.k = 0  # 每次最多可以拿的牌数
        self.n = 0  # 初始牌数
        self.cards = []  # 牌堆列表，每个元素表示一堆牌的数量
        self.current_player = 1
        self.game_over = False
        self.winner = None
        self.message = ""
        self.game_mode = None
        self.difficulty = None
        self.move_history = []  # 移动历史记录
        self.selected_pile = None  # 选中的牌堆索引
        self.selected_action = None  # 选中的动作类型 ('take' 或 'split')
        # 移除selected_take_count和selected_split_point属性，使用字典存储临时选择
        self._temp_selection = {}  # 临时存储选择参数
    
    def initialize_game(self, game_mode: str, difficulty: Optional[int] = None):
        """初始化新游戏"""
        self.game_mode = game_mode
        self.difficulty = difficulty
        
        # 随机生成初始牌数和最大拿牌数
        self.n = random.randint(6, 20)  # 初始牌数
        self.k = random.randint(2, 5)   # 每次最多拿牌数
        self.cards = [self.n]  # 初始只有一堆牌
        self.current_player = 1
        self.game_over = False
        self.winner = None
        self.move_history = []
        self.selected_pile = None
        self.selected_action = None
        self._temp_selection = {}
        
        # 根据模式设置消息
        if game_mode == "PVE":
            difficulty_names = ["Easy", "Normal", "Hard", "Insane"]
            diff_name = difficulty_names[difficulty-1] if difficulty else "Normal"
            self.message = f"Magic begins! {self.n} cards in a pile. You can take 1-{self.k} cards or split a pile. Player 1's turn. Difficulty: {diff_name}"
        else:
            self.message = f"Magic begins! {self.n} cards in a pile. You can take 1-{self.k} cards or split a pile. Player 1's turn."
    
    def get_available_moves(self) -> List[Dict]:
        """获取所有可用的移动"""
        moves = []
        
        for i, pile_size in enumerate(self.cards):
            # 拿牌动作
            for take_count in range(1, min(pile_size, self.k) + 1):
                moves.append({
                    'type': 'take',
                    'pile_index': i,
                    'take_count': take_count,
                    'description': f"Take {take_count} card{'s' if take_count > 1 else ''} from pile {i+1}"
                })
            
            # 分割动作（如果牌堆有2张或更多牌）
            if pile_size >= 2:
                # 所有可能的分割方式
                for split_point in range(1, pile_size):
                    moves.append({
                        'type': 'split',
                        'pile_index': i,
                        'split_point': split_point,
                        'new_pile_1': split_point,
                        'new_pile_2': pile_size - split_point,
                        'description': f"Split pile {i+1} into {split_point} and {pile_size - split_point} cards"
                    })
        
        return moves
    
    def set_selection(self, pile_index: Optional[int] = None, action: Optional[str] = None, **kwargs):
        """设置选择参数"""
        self.selected_pile = pile_index
        self.selected_action = action
        self._temp_selection = kwargs
    
    def get_selection_param(self, key: str, default=None):
        """获取选择参数"""
        return self._temp_selection.get(key, default)
    
    def make_move(self, move_info: Dict) -> bool:
        """执行移动"""
        move_type = move_info['type']
        pile_index = move_info['pile_index']
        
        if move_type == 'take':
            take_count = move_info['take_count']
            # 检查是否有效
            if pile_index >= len(self.cards) or take_count > self.cards[pile_index] or take_count > self.k:
                return False
            
            # 记录移动
            self.move_history.append({
                'player': self.current_player,
                'type': 'take',
                'pile': pile_index,
                'count': take_count,
                'old_state': self.cards.copy()
            })
            
            # 执行拿牌
            self.cards[pile_index] -= take_count
            
            # 如果牌堆空了，移除它
            if self.cards[pile_index] == 0:
                self.cards.pop(pile_index)
            
            # 检查游戏是否结束
            self._check_game_over()
            
            if not self.game_over:
                # 切换玩家
                self.current_player = 3 - self.current_player
                self._update_message_after_move(move_info)
            
            return True
            
        elif move_type == 'split':
            split_point = move_info['split_point']
            pile_size = self.cards[pile_index]
            
            # 检查是否有效
            if pile_index >= len(self.cards) or split_point <= 0 or split_point >= pile_size:
                return False
            
            # 记录移动
            self.move_history.append({
                'player': self.current_player,
                'type': 'split',
                'pile': pile_index,
                'split_point': split_point,
                'old_state': self.cards.copy()
            })
            
            # 执行分割
            self.cards[pile_index] = split_point
            self.cards.insert(pile_index + 1, pile_size - split_point)
            
            # 切换玩家
            self.current_player = 3 - self.current_player
            self._update_message_after_move(move_info)
            
            return True
        
        return False
    
    def _check_game_over(self):
        """检查游戏是否结束"""
        if not self.cards:  # 所有牌都被拿完了
            self.game_over = True
            self.winner = self.current_player  # 最后拿牌的玩家获胜
    
    def _update_message_after_move(self, move_info: Dict):
        """移动后更新消息"""
        move_type = move_info['type']
        
        if move_type == 'take':
            player_name = "Player 1" if self.current_player == 1 else ("AI" if self.game_mode == "PVE" else "Player 2")
            action_desc = move_info['description']
            self.message = f"{action_desc}. {player_name}'s turn."
        elif move_type == 'split':
            player_name = "Player 1" if self.current_player == 1 else ("AI" if self.game_mode == "PVE" else "Player 2")
            action_desc = move_info['description']
            self.message = f"{action_desc}. {player_name}'s turn."
    
    def ai_make_move(self) -> bool:
        """AI执行移动（PvE模式）"""
        if self.game_mode != "PVE" or self.current_player != 2 or self.game_over:
            return False
        
        available_moves = self.get_available_moves()
        if not available_moves:
            return False
        
        # 根据难度选择AI策略
        if self.difficulty == 1:  # Easy
            # 完全随机
            move = random.choice(available_moves)
        elif self.difficulty == 2:  # Normal
            # 倾向于拿牌而不是分割
            take_moves = [m for m in available_moves if m['type'] == 'take']
            if take_moves:
                move = random.choice(take_moves)
            else:
                move = random.choice(available_moves)
        elif self.difficulty == 3:  # Hard
            # 尝试寻找必胜策略
            move = self._find_best_move(available_moves)
        else:  # Insane
            # 使用更复杂的策略
            move = self._find_optimal_move(available_moves)
        
        return self.make_move(move)
    
    def _find_best_move(self, available_moves: List[Dict]) -> Dict:
        """寻找最佳移动（Hard难度）"""
        # 简单的策略：优先拿完一个牌堆
        for move in available_moves:
            if move['type'] == 'take':
                pile_idx = move['pile_index']
                if move['take_count'] == self.cards[pile_idx]:
                    return move  # 可以拿完整个牌堆
        
        # 否则随机选择一个移动
        return random.choice(available_moves)
    
    def _find_optimal_move(self, available_moves: List[Dict]) -> Dict:
        """寻找最优移动（Insane难度）"""
        # 这里可以实现更复杂的Nim策略计算
        # 暂时使用Hard难度的策略
        return self._find_best_move(available_moves)
    
    def judge_win(self) -> bool:
        """判断当前玩家是否处于必胜局面"""
        # 简化版的必胜判断，可以后续完善
        total_cards = sum(self.cards)
        if total_cards == 0:
            return False  # 游戏结束
        
        # 简单的启发式判断：如果只剩一个牌堆且牌数小于等于k，则必胜
        if len(self.cards) == 1 and self.cards[0] <= self.k:
            return True
        
        return False
    
    def get_game_state(self) -> Dict:
        """返回游戏状态信息"""
        return {
            'n': self.n,
            'k': self.k,
            'cards': self.cards.copy(),
            'current_player': self.current_player,
            'game_over': self.game_over,
            'winner': self.winner,
            'available_moves': len(self.get_available_moves()),
            'message': self.message,
            'winning_position': self.judge_win(),
            'total_cards': sum(self.cards)
        }
    
    def get_card_piles_info(self) -> List[Dict]:
        """获取牌堆的详细信息"""
        piles_info = []
        for i, count in enumerate(self.cards):
            piles_info.append({
                'index': i,
                'count': count,
                'position': (0, 0),  # 将在UI中设置
                'can_take': count > 0,
                'can_split': count >= 2
            })
        return piles_info