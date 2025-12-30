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
        """Get all valid factors for the current number - 确保移动后值不小于阈值"""
        if number <= 1 or number <= self.threshold:
            return []
        
        factors = set()
        i = 1
        while i * i <= number:
            if number % i == 0:
                if i < number and (number - i) >= self.threshold:
                    factors.add(i)
                other_factor = number // i
                if other_factor < number and other_factor != i and (number - other_factor) >= self.threshold:
                    factors.add(other_factor)
            i += 1
        
        return sorted(factors)
    
    def _get_all_factors(self, number):
        """获取所有真因子（不检查阈值） - 用于fallback情况"""
        if number <= 1:
            return []
        
        factors = []
        i = 1
        while i * i <= number:
            if number % i == 0:
                if i < number:
                    factors.append(i)
                other_factor = number // i
                if other_factor != i and other_factor < number:
                    factors.append(other_factor)
            i += 1
        
        return sorted(factors)
    
    def find_winning_move(self):
        """Find a move that leaves opponent in losing position"""
        valid_factors = self.get_valid_factors(self.current_value)
        
        for factor in valid_factors:
            new_value = self.current_value - factor
            if new_value < self.threshold:
                continue
            
            # Check if this move leaves opponent in losing position
            if new_value < len(self.winning_positions) and not self.winning_positions[new_value]:
                return factor
        
        return None
    
    def move_instruction(self, difficulty):
        """Generate move instruction for AI - 更健壮的版本"""
        # 首先获取所有有效移动（不会导致立即失败的）
        valid_factors = self.get_valid_factors(self.current_value)
        
        # 如果没有有效移动，说明所有移动都会导致失败
        if not valid_factors:
            # 这种情况应该很少见，但需要处理
            all_factors = self._get_all_factors(self.current_value)
            if all_factors:
                # 选择一个最小的因子，尽量拖延
                return min(all_factors)
            else:
                # 完全没有因子可选，返回1作为fallback
                return 1
        
        # 尝试寻找必胜移动
        winning_move = self.find_winning_move()
        
        # 对于高难度，更频繁使用必胜移动
        if winning_move and not self.this_turn_random(difficulty):
            return winning_move
        else:
            # 随机选择，但根据难度调整策略
            if difficulty >= 3:  # Hard and Insane
                # 偏好大因子以快速结束游戏
                valid_factors.sort()
                start_index = max(0, len(valid_factors) - len(valid_factors) // 3)
                # 确保切片不会为空
                candidates = valid_factors[start_index:]
                return random.choice(candidates) if candidates else valid_factors[-1]
            else:
                # 简单和普通难度：完全随机选择
                return random.choice(valid_factors)
    
    def analyze_move(self, current_value, threshold, factor):
        """分析移动的优劣，返回分数(0-100)和描述"""
        if factor not in self.get_valid_factors(current_value):
            return 0, "Invalid move"
        
        # 执行移动
        new_value = current_value - factor
        
        # 检查是否会立即失败
        if new_value < threshold:
            return 10, f"Danger: This move reduces value to {new_value} < threshold {threshold} - immediate loss!"
        
        # 检查是否为必胜位置
        if new_value < len(self.winning_positions) and not self.winning_positions[new_value]:
            return 100, "Winning move - leaves opponent in losing position"
        
        # 对于非必胜位置，评估对手的响应
        opponent_factors = self.get_valid_factors(new_value)
        if not opponent_factors:
            # 对手没有有效移动，这应该是必胜位置
            return 90, "Excellent move - opponent has no valid moves"
        
        # 计算对手有多少必胜移动
        opponent_winning_moves = []
        for opp_factor in opponent_factors:
            opp_new_value = new_value - opp_factor
            if opp_new_value < threshold:
                continue
            if opp_new_value < len(self.winning_positions) and not self.winning_positions[opp_new_value]:
                opponent_winning_moves.append(opp_factor)
        
        total_moves = len(opponent_factors)
        winning_count = len(opponent_winning_moves)
        
        if winning_count == total_moves:
            # 所有对手移动都是必胜的
            return 20, f"Dangerous move - opponent has {winning_count} winning responses"
        elif winning_count == 0:
            # 对手没有必胜移动
            # 进一步分析：检查对手移动后，我们是否有必胜移动
            safe_count = 0
            for opp_factor in opponent_factors:
                opp_new_value = new_value - opp_factor
                if opp_new_value < threshold:
                    continue
                # 检查对手移动后，我们是否有必胜移动
                our_factors_after = self.get_valid_factors(opp_new_value)
                has_winning = False
                for our_factor in our_factors_after:
                    final_value = opp_new_value - our_factor
                    if final_value < threshold:
                        continue
                    if final_value < len(self.winning_positions) and not self.winning_positions[final_value]:
                        has_winning = True
                        break
                
                if not has_winning:
                    safe_count += 1
            
            safe_ratio = safe_count / total_moves if total_moves > 0 else 0
            score = 60 + int(30 * safe_ratio)
            return score, f"Good move - opponent has {safe_count}/{total_moves} safe responses"
        else:
            # 部分对手移动是必胜的
            losing_ratio = winning_count / total_moves
            score = max(30, 80 - int(50 * losing_ratio))
            return score, f"Risky move - opponent has {winning_count}/{total_moves} winning responses"

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
        self.winning_hints_enabled = False  # 新增：提示功能开关
    
    def calculate_winning_positions(self):
        """Calculate winning positions using dynamic programming"""
        n = self.initial_n
        k = self.threshold_k
        
        # 增加数组大小以避免索引越界
        self.winning_positions = [False] * (n + 100)
        
        # 设置基础情况
        for i in range(k):
            if i < len(self.winning_positions):
                self.winning_positions[i] = False

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
                    continue
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
                if n // i < n and n // i != i:
                    factors.add(n // i)
            i += 1
        
        return sorted(factors)
    
    def update_valid_factors(self):
        """Update list of valid factors for current value - 修复版本"""
        # 首先获取所有因子
        all_factors = self._get_factors_optimized(self.current_value)
        
        # 过滤掉会导致立即失败的因子
        self.valid_factors = [f for f in all_factors 
                            if (self.current_value - f) >= self.threshold_k]
        
        # 如果当前值已经小于阈值，游戏应该结束
        if self.current_value < self.threshold_k and not self.game_over:
            self.game_over = True
            # 当前玩家输，因为当前值已经低于阈值
            self.winner = "AI" if self.current_player == "Player 1" else "Player 1"
            self.message = f"Game Over! Current value {self.current_value} < threshold {self.threshold_k}. {self.current_player} loses!"
    
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
        # 只考虑不会导致立即失败的因子
        valid_factors = [f for f in factors if (value - f) >= self.threshold_k]
        
        for factor in valid_factors:
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
        # 只考虑不会导致立即失败的因子
        valid_factors = [f for f in factors if (value - f) >= self.threshold_k]
        
        for factor in valid_factors:
            new_val = value - factor
            if new_val < self.threshold_k:
                continue
            if not self.judge_win_single(new_val):
                return True
        return False
    
    def initialize_game(self, game_mode, difficulty=None, winning_hints=False):  # 修改：添加winning_hints参数
        """Initialize a new game - ensure player starts in winning position in PvE"""
        self.game_mode = game_mode
        self.difficulty = difficulty
        self.winning_hints_enabled = winning_hints  # 新增：存储提示设置
        
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
        
        max_attempts = 100
        attempt_count = 0
        
        while attempt_count < max_attempts:
            attempt_count += 1
            self.initial_n = random.randint(min_n, max_n)
            
            # 调整阈值范围，确保游戏有足够的回合
            min_k = max(10, int(math.sqrt(self.initial_n) * 1.5))
            max_k = min(self.initial_n - 20, int(self.initial_n * 0.7))
            
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
                # 检查是否为玩家胜利局面
                is_winning_position = self.judge_win()
                if is_winning_position and self.valid_factors:
                    break
            else:
                if self.valid_factors:
                    break
        
        # 如果没找到合适的配置，使用一个安全的默认值
        if attempt_count >= max_attempts:
            self.initial_n = random.randint(200, 300)
            self.threshold_k = random.randint(50, 100)
            self.current_value = self.initial_n
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
        self.message = f"Game Started! n={self.initial_n}, k={self.threshold_k}. You are in a {position_state} position.{mode_info}"
        
        # 新增：如果提示功能开启，显示提示信息
        if self.winning_hints_enabled:
            self.message += " [Winning Hints: ON]"
    
    def make_move(self, factor):
        """Execute a move and return success status"""
        # 验证因子是否有效
        if factor not in self.valid_factors:
            self.message = f"Invalid factor: {factor}. Please select a valid factor."
            return False
        
        new_value = self.current_value - factor
        
        # 检查是否会导致立即失败（理论上不应该发生，因为valid_factors已经过滤过了）
        if new_value < self.threshold_k:
            self.game_over = True
            self.winner = "AI" if self.current_player == "Player 1" else "Player 1"
            self.message = f"{self.current_player} subtracted {factor}, resulting in {new_value} < {self.threshold_k}. {self.current_player} loses!"
            return True
        
        self.current_value = new_value
        self.message = f"{self.current_player} subtracted {factor}, new value: {self.current_value}."
        
        # 更新AI状态
        if self.game_mode == "PVE":
            self.auto_player.current_value = self.current_value
        
        self.update_valid_factors()
        
        # 检查游戏是否结束（没有有效移动）
        if not self.valid_factors and not self.game_over:
            self.game_over = True
            self.winner = self.current_player
            self.message = f"Game Over! {self.current_player} Wins! No valid moves left."
            return True
        
        # 切换玩家
        self.switch_player()
        
        # 更新局面分析
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
            # 确保AI有有效移动
            if not self.valid_factors:
                self.game_over = True
                self.winner = "Player 1"
                self.message = f"Game Over! Player 1 Wins! AI has no valid moves."
                return True
            
            factor = self.auto_player.move_instruction(self.difficulty)
            
            # 验证AI选择的因子是否有效
            if factor in self.valid_factors:
                return self.make_move(factor)
            else:
                # AI选择了无效因子，尝试选择一个有效因子
                if self.valid_factors:
                    # 选择第一个有效因子
                    factor = self.valid_factors[0]
                    return self.make_move(factor)
                else:
                    # 没有有效移动，游戏结束
                    self.game_over = True
                    self.winner = "Player 1"
                    self.message = f"Game Over! Player 1 Wins! AI has no valid moves."
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
        
        self.message = f"Invalid factor: {factor}. Please select a valid factor."
        return False
    
    # ========== 新增：提示功能 ==========
    
    def get_winning_hint(self):
        """提供当前游戏局面的提示"""
        if self.game_over:
            return "Game is already over!"
        
        # 检查是否是玩家的回合（PvE模式下AI回合不给提示）
        if self.game_mode == "PVE" and self.current_player == "AI":
            return "It's AI's turn. Wait for your turn to get hints."
        
        # 获取所有可用移动
        available_factors = self.valid_factors
        if not available_factors:
            return "No available moves!"
        
        # 确定当前局面类型
        is_winning_position = self.judge_win()
        
        if is_winning_position:
            # 必胜局面 - 寻找最佳必胜移动
            best_factor = None
            best_score = -1
            best_desc = ""
            moves_analysis = []
            
            for factor in available_factors:
                if self.auto_player:
                    score, desc = self.auto_player.analyze_move(
                        self.current_value, self.threshold_k, factor
                    )
                    moves_analysis.append((factor, score, desc))
                    
                    if score > best_score:
                        best_score = score
                        best_factor = factor
                        best_desc = desc
            
            if best_factor is not None:
                hint = f"WINNING POSITION\n"
                hint += f"Current position is WINNING!\n\n"
                hint += f"Recommended move: Subtract {best_factor}\n"
                hint += f"New value: {self.current_value - best_factor}\n"
                hint += f"Score: {best_score}/100\n"
                hint += f"Description: {best_desc}\n\n"
                
                
                hint += "\nStrategy: Choose moves that leave opponent in losing position."
            else:
                hint = "WINNING POSITION\n"
                hint += "Current position is winning, but no obvious best move found.\n"
                hint += f"Available factors: {available_factors}\n"
                hint += "Suggest selecting a random valid factor."
        else:
            # 必败局面 - 寻找最不坏的移动
            best_factor = None
            best_score = -1
            best_desc = ""
            moves_analysis = []
            
            for factor in available_factors:
                if self.auto_player:
                    score, desc = self.auto_player.analyze_move(
                        self.current_value, self.threshold_k, factor
                    )
                    moves_analysis.append((factor, score, desc))
                    
                    if score > best_score:
                        best_score = score
                        best_factor = factor
                        best_desc = desc
            
            if best_factor is not None:
                hint = f"LOSING POSITION\n"
                hint += f"Current position is LOSING. There is no guaranteed winning strategy.\n"
                hint += f"You need opponent to make a mistake.\n\n"
                hint += f"Recommended move: Subtract {best_factor}\n"
                hint += f"New value: {self.current_value - best_factor}\n"
                hint += f"Score: {best_score}/100\n"
                hint += f"Description: {best_desc}\n\n"
                
                
                hint += "\nStrategy: Choose the move with highest probability of opponent error, and hope for a mistake."
            else:
                hint = "LOSING POSITION\n"
                hint += "Current position is losing.\n"
                hint += f"Available factors: {available_factors}\n"
                hint += "Suggest selecting a random valid factor and hope opponent makes a mistake."
        
        # 添加游戏状态信息
        hint += f"\n\nCURRENT GAME STATE\n"
        hint += f"Current value: {self.current_value}\n"
        hint += f"Threshold: {self.threshold_k}\n"
        hint += f"Available factors: {len(available_factors)}\n"
        hint += f"Current player: {self.current_player}\n"
        hint += f"Game mode: {self.game_mode}\n"
        
        return hint
    
    def toggle_winning_hints(self, enabled):
        """启用或禁用提示功能"""
        self.winning_hints_enabled = enabled
        if enabled:
            return "Winning hints enabled! Click on hint button for guidance."
        else:
            return "Winning hints disabled."
    
    def get_position_analysis(self):
        """提供当前游戏局面分析"""
        if self.game_over:
            return "Game over!"
        
        analysis = f"GAME STATE ANALYSIS\n"
        analysis += f"• Current value: {self.current_value}\n"
        analysis += f"• Threshold: {self.threshold_k}\n"
        analysis += f"• Current position: "
        analysis += "WINNING position" if self.judge_win() else "LOSING position"
        analysis += f"\n"
        analysis += f"• Current player: {self.current_player}\n"
        
        # 可用因子
        available_factors = self.valid_factors
        analysis += f"• Available factors: {available_factors}\n"
        analysis += f"• Number of factors: {len(available_factors)}\n"
        
        # 策略建议
        if self.judge_win():
            analysis += "\n✅ You are in a WINNING position!\n"
            analysis += "   Try to find a move that leaves opponent in losing position.\n"
            analysis += "   Subtract a factor that creates a non-winning value for opponent."
        else:
            analysis += "\n⚠️  You are in a LOSING position!\n"
            analysis += "   You need opponent to make a mistake.\n"
            analysis += "   Choose moves with highest probability of opponent error."
        
        return analysis