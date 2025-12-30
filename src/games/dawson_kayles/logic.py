"""
Dawson-Kayles Game Logic - 添加提示功能
"""

import random
from typing import List, Tuple, Dict
from utils.constants import DIFFICULTY_RANDOM_RATES, DIFFICULTY_POSITION_RANGES_FOR_DAWSON_KAYLES

class DawsonKaylesAutoPlayer:
    """Handles AI logic for Dawson-Kayles game"""
    
    def __init__(self, towers):
        self.towers = towers
    
    def this_turn_random(self, difficulty):
        """Determine if AI should make a random move based on difficulty"""
        return random.random() < DIFFICULTY_RANDOM_RATES.get(difficulty, 0.3)
    
    def move_instruction(self, difficulty):
        """Generate move instruction for AI"""
        available_moves = self.get_available_moves(self.towers)
        
        if not available_moves:
            return None
        
        # For higher difficulties, try to find winning moves
        if difficulty >= 3 and not self.this_turn_random(difficulty):
            # Try to find a move that leaves opponent in losing position
            winning_moves = self.find_winning_moves(self.towers)
            if winning_moves:
                return random.choice(winning_moves)
        
        # Make a random move
        return random.choice(available_moves)
    
    def get_available_moves(self, towers):
        """Get all available moves for given tower configuration"""
        moves = []
        for i in range(len(towers) - 1):
            if towers[i] == 1 and towers[i + 1] == 1:
                moves.append(i)
        return moves
    
    def find_winning_moves(self, towers):
        """Find moves that leave opponent in losing position"""
        winning_moves = []
        available_moves = self.get_available_moves(towers)
        
        for move in available_moves:
            # Create new configuration after this move
            new_towers = list(towers)
            new_towers[move] = 0
            new_towers[move + 1] = 0
            
            # Check if this leaves opponent with no winning moves
            new_available = self.get_available_moves(new_towers)
            if not new_available:
                winning_moves.append(move)
            elif not self.has_winning_move(new_towers, new_available):
                winning_moves.append(move)
        
        return winning_moves
    
    def has_winning_move(self, towers, available_moves):
        """Check if there's a winning move from current position"""
        for move in available_moves:
            new_towers = list(towers)
            new_towers[move] = 0
            new_towers[move + 1] = 0
            new_available = self.get_available_moves(new_towers)
            if not new_available:
                return True
        return False
    
    def analyze_move(self, towers, move):
        """Analyze the quality of a move, return score (0-100) and description"""
        if move not in self.get_available_moves(towers):
            return 0, "Invalid move"
        
        # Execute the move
        new_towers = list(towers)
        new_towers[move] = 0
        new_towers[move + 1] = 0
        
        # Check if game ends immediately
        new_available = self.get_available_moves(new_towers)
        if not new_available:
            return 100, "Winning move - no further moves available"
        
        # Check if leaves opponent in losing position
        opponent_winning_moves = self.find_winning_moves(new_towers)
        if not opponent_winning_moves:
            # Opponent has no winning moves, this is good
            # Calculate ratio of opponent's moves that lead to our loss
            opponent_losing_moves = []
            total_moves = len(new_available)
            
            for opp_move in new_available:
                opp_new_towers = list(new_towers)
                opp_new_towers[opp_move] = 0
                opp_new_towers[opp_move + 1] = 0
                
                # Check if after opponent's move, we have winning moves
                my_next_available = self.get_available_moves(opp_new_towers)
                my_winning_moves = self.find_winning_moves(opp_new_towers)
                
                if not my_winning_moves:
                    # Opponent's move would leave us in losing position
                    opponent_losing_moves.append(opp_move)
            
            losing_ratio = len(opponent_losing_moves) / total_moves if total_moves > 0 else 0
            score = int(80 * (1 - losing_ratio))  # Lower ratio is better
            
            if losing_ratio == 0:
                desc = f"Excellent move - opponent has no forced win ({total_moves} possible responses)"
            else:
                desc = f"Good move - opponent has {len(opponent_losing_moves)}/{total_moves} responses that force our loss"
            
            return max(score, 20), desc
        
        else:
            # Opponent has winning moves, this is bad
            # Calculate ratio of opponent's winning moves
            total_moves = len(new_available)
            opponent_winning_count = len(opponent_winning_moves)
            winning_ratio = opponent_winning_count / total_moves if total_moves > 0 else 1
            
            # Score: lower winning ratio is better
            score = int(40 * (1 - winning_ratio))
            
            if winning_ratio == 1:
                desc = f"Losing position - opponent has winning response"
            else:
                desc = f"Poor position - opponent has {opponent_winning_count}/{total_moves} winning responses"
            
            return max(score, 10), desc

class DawsonKaylesLogic:
    """Game logic for Dawson-Kayles (Tech Tower Defense theme)"""
    
    def __init__(self):
        self.num_towers = 0
        self.towers = []  # 1表示炮塔可用，0表示已被连接
        self.lasers = []  # 存储激光连接 [(start_idx, end_idx, player)]
        self.current_player = "Player 1"
        self.game_over = False
        self.winner = None
        self.message = ""
        self.game_mode = None
        self.difficulty = None
        self.winning_cache = {}  # 缓存胜负状态
        self.auto_player = None
        self.winning_hints_enabled = False  # 新增：提示功能开关
    
    def initialize_game(self, game_mode, difficulty=None, winning_hints=False):  # 修改：添加winning_hints参数
        """Initialize a new game"""
        self.game_mode = game_mode
        self.difficulty = difficulty
        self.winning_hints_enabled = winning_hints  # 新增：存储提示设置
        self.winning_cache = {}  # 清空缓存
        
        # 根据难度设置炮塔数量
        if self.game_mode == "PVP":
            # PvP模式：固定范围
            min_towers, max_towers = (8, 15)
            self.num_towers = random.randint(min_towers, max_towers)
            self.towers = [1 for _ in range(self.num_towers)]
            self.message = f"Game Started! {self.num_towers} towers deployed. Player 1's turn."
        else:
            # PvE模式：根据难度使用范围
            min_towers, max_towers = DIFFICULTY_POSITION_RANGES_FOR_DAWSON_KAYLES.get(self.difficulty, (8, 15))
            
            # 如果是PVE模式，确保初始状态是Winning position
            max_attempts = 100  # 最大尝试次数，避免无限循环
            attempts = 0
            
            while attempts < max_attempts:
                self.num_towers = random.randint(min_towers, max_towers)
                self.towers = [1 for _ in range(self.num_towers)]
                
                # 检查当前状态是否为Winning position
                self.winning_cache = {}  # 清空缓存以便重新计算
                is_winning = self.judge_win()
                
                if is_winning:
                    # 找到Winning position，跳出循环
                    break
                else:
                    attempts += 1
                    # 如果是最后一次尝试，记录信息
                    if attempts == max_attempts:
                        self.message = f"Warning: Could not find winning position after {max_attempts} attempts. Using current position."
            
            difficulty_names = ["Easy", "Normal", "Hard", "Insane"]
            self.message = f"Game Started! {self.num_towers} towers deployed. Player 1's turn. Difficulty: {difficulty_names[self.difficulty-1]}"
            self.auto_player = DawsonKaylesAutoPlayer(self.towers)
        
        # 新增：如果提示功能开启，显示提示信息
        if self.winning_hints_enabled:
            self.message += " [Winning Hints: ON]"
        
        self.lasers = []
        self.current_player = "Player 1"
        self.game_over = False
        self.winner = None
    
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
            self.message = f"Invalid move. Cannot connect tower {start_index} and {start_index+1}."
            return False
        
        # 添加激光连接
        player_num = 1 if self.current_player == "Player 1" else 2
        self.lasers.append((start_index, start_index + 1, player_num))
        
        # 标记炮塔为已使用
        self.towers[start_index] = 0
        self.towers[start_index + 1] = 0
        
        # 更新AI状态
        if self.game_mode == "PVE":
            self.auto_player.towers = self.towers
        
        # 检查游戏是否结束
        if not self.get_available_moves():
            self.game_over = True
            # 修改胜负规则：最后完成配对的玩家获胜
            self.winner = self.current_player
            
            if self.game_mode == "PVE":
                if self.winner == "Player 1":
                    self.message = f"Game Over! Player 1 wins! No more moves available."
                else:
                    self.message = f"Game Over! AI wins! No more moves available."
            else:
                self.message = f"Game Over! Player {player_num} wins! No more moves available."
        else:
            # 切换玩家
            self.switch_player()
            
            if self.game_mode == "PVE":
                if self.current_player == "AI":
                    self.message = f"Laser connected between towers {start_index} and {start_index + 1}. AI's turn."
                else:
                    self.message = f"Laser connected between towers {start_index} and {start_index + 1}. Player 1's turn."
            else:
                self.message = f"Laser connected between towers {start_index} and {start_index + 1}. {self.current_player}'s turn."
        
        return True
    
    def switch_player(self):
        """切换玩家"""
        if self.game_mode == "PVE":
            if self.current_player == "Player 1":
                self.current_player = "AI"
            else:
                self.current_player = "Player 1"
        else:
            # PvP模式
            if self.current_player == "Player 1":
                self.current_player = "Player 2"
            else:
                self.current_player = "Player 1"
    
    def ai_make_move(self):
        """AI执行移动（PvE模式）"""
        if self.game_mode != "PVE" or self.current_player != "AI" or self.game_over:
            return False
        
        available_moves = self.get_available_moves()
        if not available_moves:
            return False
        
        # AI选择移动
        move = self.auto_player.move_instruction(self.difficulty)
        if move is not None and move in available_moves:
            return self.make_move(move)
        
        # 如果AI没有找到有效移动，随机选择一个
        if available_moves:
            move = random.choice(available_moves)
            return self.make_move(move)
        
        return False
    
    def select_position(self, position):
        """选择位置（为了与其他游戏接口一致）"""
        if position in self.get_available_moves():
            # 对于Dawson-Kayles，选择位置就是直接执行移动
            return self.make_move(position)
        return False
    
    def judge_win(self):
        """判断当前局面对于当前玩家是否为必胜局面"""
        return self._judge_win_state(tuple(self.towers))
    
    def _judge_win_state(self, towers_tuple):
        """递归判断给定状态是否为必胜（对于当前要行动的玩家）"""
        if towers_tuple in self.winning_cache:
            return self.winning_cache[towers_tuple]
        
        # 获取所有可用移动
        available_moves = []
        for i in range(len(towers_tuple) - 1):
            if towers_tuple[i] == 1 and towers_tuple[i + 1] == 1:
                available_moves.append(i)
        
        # 如果没有可用移动，则必败（无法行动）
        if not available_moves:
            self.winning_cache[towers_tuple] = False
            return False
        
        # 尝试每一个移动
        for move in available_moves:
            # 执行这个移动
            new_towers = list(towers_tuple)
            new_towers[move] = 0
            new_towers[move + 1] = 0
            new_towers_tuple = tuple(new_towers)
            # 如果对手在移动后的状态下必败，那么当前状态必胜
            if not self._judge_win_state(new_towers_tuple):
                self.winning_cache[towers_tuple] = True
                return True
        
        # 如果所有移动都不能让对手必败，则当前状态必败
        self.winning_cache[towers_tuple] = False
        return False
    
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
            'message': self.message,
            'winning_position': self.judge_win()
        }
    
    def validate_input_move(self, tower_n):
        """验证输入框的移动是否有效"""
        if tower_n < 1 or tower_n >= len(self.towers):
            return False, f"Please check if your input is out of range. Valid range: 1 to {len(self.towers)-1}"
        
        move_index = tower_n - 1
        
        if self.towers[move_index] == 0 or self.towers[move_index + 1] == 0:
            return False, "Please check if the tower has been connected."
        
        if move_index not in self.get_available_moves():
            return False, f"Cannot connect tower {tower_n} and {tower_n+1}. They must be adjacent and available."
        
        return True, ""
    
    # ========== 新增：提示功能 ==========
    
    def get_winning_hint(self):
        """
        Provide hints for the current game position.
        Returns a string with the hint message.
        """
        if self.game_over:
            return "Game is already over!"
            
        # Check if it's a player's turn (not AI's turn in PvE)
        if self.game_mode == "PVE" and self.current_player == "AI":
            return "It's AI's turn. Wait for your turn to get hints."
            
        # Get all available moves
        available_moves = self.get_available_moves()
        if not available_moves:
            return "No available moves!"
        
        # Determine current position type
        is_winning_position = self.judge_win()
        
        if is_winning_position:
            # Winning position - find the best winning move
            best_move = None
            best_score = -1
            best_desc = ""
            
            for move in available_moves:
                # Execute this move
                new_towers = list(self.towers)
                new_towers[move] = 0
                new_towers[move + 1] = 0
                
                # Check if opponent is in losing position after this move
                temp_auto_player = DawsonKaylesAutoPlayer(new_towers)
                opponent_winning_moves = temp_auto_player.find_winning_moves(new_towers)
                
                if not opponent_winning_moves:
                    # Opponent has no winning moves, this is the best move
                    best_move = move
                    best_score = 100
                    best_desc = "Winning move - leaves opponent in losing position"
                    break
                else:
                    # Opponent has winning moves, but we need to evaluate which is least bad
                    # Calculate ratio of opponent's winning moves
                    new_available = temp_auto_player.get_available_moves(new_towers)
                    total_moves = len(new_available)
                    opponent_winning_count = len(opponent_winning_moves)
                    
                    if total_moves > 0:
                        score = 80 - (opponent_winning_count / total_moves * 60)
                        if score > best_score:
                            best_score = score
                            best_move = move
                            best_desc = f"Good move - opponent has {opponent_winning_count}/{total_moves} winning responses"
            
            if best_move is not None:
                hint = f"WINNING POSITION\n"
                hint += f"Current position is WINNING!\n\n"
                hint += f"Recommended move: Connect towers {best_move} and {best_move+1}\n"
                hint += f"Score: {int(best_score)}/100\n"
                hint += f"Description: {best_desc}\n\n"
                
                
                hint += "\nStrategy: Prefer moves that leave opponent with no winning responses."
            else:
                hint = "WINNING POSITION\n"
                hint += "Current position is winning, but no obvious best move found.\n"
                hint += f"Available moves: {available_moves}\n"
                hint += "Suggest randomly selecting an available move."
                
        else:
            # Losing position - find the least bad move
            best_move = None
            best_score = -1
            best_desc = ""
            moves_analysis = []
            
            for move in available_moves:
                temp_auto_player = DawsonKaylesAutoPlayer(self.towers)
                score, desc = temp_auto_player.analyze_move(self.towers, move)
                moves_analysis.append((move, score, desc))
                
                if score > best_score:
                    best_score = score
                    best_move = move
                    best_desc = desc
            
            if best_move is not None:
                hint = f"LOSING POSITION\n"
                hint += f"Current position is LOSING. There is no guaranteed winning strategy.\n"
                hint += f"You need opponent to make a mistake.\n\n"
                hint += f"Recommended move: Connect towers {best_move} and {best_move+1}\n"
                hint += f"Score: {best_score}/100\n"
                hint += f"Description: {best_desc}\n\n"
                
                # Add detailed analysis
                hint += "Detailed move analysis:\n"
                for move, score, desc in sorted(moves_analysis, key=lambda x: x[1], reverse=True):
                    if move == best_move:
                        hint += f"  ★ Move {move}: {desc} (Score: {score})\n"
                    else:
                        hint += f"  - Move {move}: {desc} (Score: {score})\n"
                
                hint += "\nStrategy: Choose the move with highest probability of opponent error, and hope for a mistake."
            else:
                hint = "LOSING POSITION\n"
                hint += "Current position is losing.\n"
                hint += f"Available moves: {available_moves}\n"
                hint += "Suggest randomly selecting an available move and hope opponent makes a mistake."
        
        # Add game state information
        hint += f"\n\nCURRENT GAME STATE\n"
        hint += f"Total towers: {len(self.towers)}\n"
        hint += f"Available moves: {len(available_moves)}\n"
        hint += f"Current player: {self.current_player}\n"
        hint += f"Game mode: {self.game_mode}\n"
        
        return hint
    def toggle_winning_hints(self, enabled):
        """Enable or disable winning hints feature"""
        self.winning_hints_enabled = enabled
        if enabled:
            return "Winning hints enabled! Click on hint button for guidance."
        else:
            return "Winning hints disabled."
    
    def get_position_analysis(self):
        """
        Provide analysis of current game state.
        Returns a string with analysis.
        """
        if self.game_over:
            return "Game over!"
            
        analysis = f"GAME STATE ANALYSIS\n"
        analysis += f"• Tower configuration: {self.towers}\n"
        analysis += f"• Current position: "
        analysis += "WINNING position" if self.judge_win() else "LOSING position"
        analysis += f"\n"
        analysis += f"• Current player: {self.current_player}\n"
        
        # Calculate remaining available towers
        remaining_towers = sum(self.towers)
        analysis += f"• Remaining available towers: {remaining_towers}\n"
        
        # Available moves
        available_moves = self.get_available_moves()
        analysis += f"• Available moves: {[f'{m}->{m+1}' for m in available_moves]}\n"
        analysis += f"• Number of moves: {len(available_moves)}\n"
        
        # Laser connections
        analysis += f"• Laser connections: {len(self.lasers)}\n"
        
        # Strategy advice
        if self.judge_win():
            analysis += "\n✅ You are in a WINNING position!\n"
            analysis += "   Try to find a move that leaves opponent in losing position.\n"
            analysis += "   Prefer moves that give opponent no winning responses."
        else:
            analysis += "\n⚠️  You are in a LOSING position!\n"
            analysis += "   You need opponent to make a mistake.\n"
            analysis += "   Choose moves with highest probability of opponent error."
            
        return analysis