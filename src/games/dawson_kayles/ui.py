"""
Dawson-Kayles Game UI Components
"""

import pygame
from ui.buttons import Button
from utils.constants import *
from utils.helpers import wrap_text

class TowerButton:
    """炮塔按钮组件"""
    
    def __init__(self, x, y, width, height, tower_id, font_manager):
        self.rect = pygame.Rect(x, y, width, height)
        self.tower_id = tower_id
        self.font_manager = font_manager
        self.hovered = False
        self.selected = False
        self.enabled = True
    
    def draw(self, surface, tower_state, player_owner=None, is_highlighted=False):
        """
        绘制炮塔
        
        Args:
            surface: 绘制表面
            tower_state: 炮塔状态 (0=不可用, 1=可用)
            player_owner: 炮塔所有者 (1=玩家1, 2=玩家2/AI, None=未连接)
            is_highlighted: 是否高亮显示
        """
        # 根据炮塔状态和所有者选择颜色
        if tower_state == 0:  # 不可用
            if player_owner == 1:
                base_color = (0, 180, 0)      # 玩家1 - 深绿色
                top_color = (0, 255, 100)     # 玩家1 - 亮绿色
            elif player_owner == 2:
                base_color = (220, 120, 0)    # 玩家2/AI - 深橙色
                top_color = (255, 180, 50)    # 玩家2/AI - 亮橙色
            else:
                base_color = (80, 80, 100)    # 默认禁用颜色
                top_color = (100, 100, 120)
        else:  # 可用
            base_color = (100, 120, 180)      # 可用炮塔基座
            top_color = (0, 200, 255)         # 激活炮塔 - 亮蓝色
        
        # 绘制炮塔基座
        pygame.draw.rect(surface, base_color, self.rect, border_radius=8)
        
        # 炮塔顶部（雷达/发射器）
        top_radius = self.rect.width // 3
        top_center = (self.rect.centerx, self.rect.top + top_radius + 5)
        
        pygame.draw.circle(surface, top_color, top_center, top_radius, 2)
        
        # 如果可用，绘制发光效果
        if tower_state == 1:
            glow_radius = top_radius + 3
            glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*top_color[:3], 50), (glow_radius, glow_radius), glow_radius)
            surface.blit(glow_surf, (top_center[0] - glow_radius, top_center[1] - glow_radius))
        
        # 炮塔编号
        id_text = self.font_manager.small.render(str(self.tower_id), True, TEXT_COLOR)
        surface.blit(id_text, (self.rect.centerx - 5, self.rect.bottom - 25))
        
        # 高亮显示可用移动
        if is_highlighted and tower_state == 1:
            highlight_rect = self.rect.inflate(10, 10)
            pygame.draw.rect(surface, HIGHLIGHT_COLOR, highlight_rect, 3, border_radius=10)
    
    def update_hover(self, mouse_pos):
        """更新悬停状态"""
        self.hovered = self.rect.collidepoint(mouse_pos) and self.enabled
    
    def is_clicked(self, event):
        """检查是否被点击"""
        return (event.type == pygame.MOUSEBUTTONDOWN and 
                event.button == 1 and 
                self.hovered and 
                self.enabled)

class DawsonKaylesUI:
    """Dawson-Kayles游戏UI管理器"""
    
    def __init__(self, screen, font_manager):
        self.screen = screen
        self.font_manager = font_manager
        self.scroll_offset = 0
        self.visible_tower_count = 10  # 可见的炮塔数量
        self.selected_tower = None
        self.highlighted_towers = set()
    
    def draw_background(self):
        """绘制科技风格背景"""
        self.screen.fill((10, 15, 30))  # 深蓝色背景
        
        # 绘制网格线
        grid_color = (30, 40, 70)
        for x in range(0, SCREEN_WIDTH, 40):
            pygame.draw.line(self.screen, grid_color, (x, 0), (x, SCREEN_HEIGHT), 1)
        for y in range(0, SCREEN_HEIGHT, 40):
            pygame.draw.line(self.screen, grid_color, (0, y), (SCREEN_WIDTH, y), 1)
    
    def draw_game_info(self, game_logic):
        """绘制游戏信息面板（模仿Subtract Factor Game的样式）"""
        # 头部背景
        header_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 180)
        pygame.draw.rect(self.screen, (35, 45, 60), header_rect)
        pygame.draw.line(self.screen, ACCENT_COLOR, (0, 180), (SCREEN_WIDTH, 180), 3)
        
        # 游戏标题
        title = self.font_manager.large.render("Laser Defense - Dawson-Kayles", True, TEXT_COLOR)
        title_shadow = self.font_manager.large.render("Laser Defense - Dawson-Kayles", True, SHADOW_COLOR)
        self.screen.blit(title_shadow, (SCREEN_WIDTH//2 - title.get_width()//2 + 2, 15))
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 13))
        
        # 游戏模式和难度信息
        difficulty_names = ["Easy", "Normal", "Hard", "Insane"]
        
        if game_logic.game_mode == "PVP":
            mode_text = "Mode: Player vs Player"
        else:
            mode_text = f"Mode: Player vs AI - {difficulty_names[game_logic.difficulty-1]}"
        
        mode_info = self.font_manager.small.render(mode_text, True, ACCENT_COLOR)
        self.screen.blit(mode_info, (20, 145))
        
        # 当前玩家信息
        player_colors = {
            1: WIN_COLOR,  # 玩家1 - 绿色
            2: (255, 200, 50) if game_logic.game_mode == "PVP" else LOSE_COLOR  # 玩家2或AI
        }
        
        player_name = "Player 1" if game_logic.current_player == 1 else ("AI" if game_logic.game_mode == "PVE" else "Player 2")
        player_color = player_colors[game_logic.current_player]
        
        # 当前玩家显示框
        player_text = self.font_manager.small.render(f"Current Player: {player_name}", True, player_color)
        player_bg = pygame.Rect(SCREEN_WIDTH - player_text.get_width() - 40, 45, 
                              player_text.get_width() + 20, player_text.get_height() + 10)
        pygame.draw.rect(self.screen, (40, 50, 65), player_bg, border_radius=8)
        pygame.draw.rect(self.screen, player_color, player_bg, 2, border_radius=8)
        self.screen.blit(player_text, (SCREEN_WIDTH - player_text.get_width() - 30, 50))
        
        # 当前游戏状态
        towers_remaining = sum(game_logic.towers)
        status_text = self.font_manager.large.render(f"Towers Remaining: {towers_remaining} | Available Moves: {len(game_logic.get_available_moves())}", 
                                                    True, HIGHLIGHT_COLOR)
        self.screen.blit(status_text, (SCREEN_WIDTH//2 - status_text.get_width()//2, 60))
        
        # 游戏消息
        message_color = (WIN_COLOR if game_logic.game_over and game_logic.winner == 1 
                        else LOSE_COLOR if game_logic.game_over and game_logic.winner == 2
                        else (255, 200, 50) if game_logic.game_over and game_logic.winner == "Player 2"
                        else TEXT_COLOR)
        
        message_lines = wrap_text(game_logic.message, self.font_manager.medium, SCREEN_WIDTH - 100)
        for i, line in enumerate(message_lines):
            message_text = self.font_manager.medium.render(line, True, message_color)
            message_bg_width = message_text.get_width() + 30
            message_bg = pygame.Rect(SCREEN_WIDTH//2 - message_bg_width//2, 110 + i * 25, 
                                   message_bg_width, message_text.get_height() + 6)
            
            if i == 0:
                pygame.draw.rect(self.screen, (40, 50, 65), message_bg, border_radius=8)
                pygame.draw.rect(self.screen, ACCENT_COLOR, message_bg, 2, border_radius=8)
            
            self.screen.blit(message_text, (SCREEN_WIDTH//2 - message_text.get_width()//2, 113 + i * 25))
        
        # 胜负状态指示器（Winning/Losing Position）
        if not game_logic.game_over:
            game_state = "Winning Position" if game_logic.judge_win() else "Losing Position"
            state_color = WIN_COLOR if game_logic.judge_win() else LOSE_COLOR
            state_text = self.font_manager.small.render(game_state, True, state_color)
            
            state_bg = pygame.Rect(SCREEN_WIDTH//2 - state_text.get_width()//2 - 10, 155, 
                                 state_text.get_width() + 20, state_text.get_height() + 6)
            pygame.draw.rect(self.screen, (40, 50, 65), state_bg, border_radius=6)
            pygame.draw.rect(self.screen, state_color, state_bg, 2, border_radius=6)
            self.screen.blit(state_text, (SCREEN_WIDTH//2 - state_text.get_width()//2, 158))
    
    def draw_towers_and_lasers(self, game_logic, tower_buttons):
        """绘制炮塔和激光"""
        # 先绘制激光
        self._draw_all_lasers(game_logic, tower_buttons)
        
        # 然后绘制炮塔
        for button in tower_buttons:
            # 确定炮塔的所有者
            owner = self._get_tower_owner(game_logic, button.tower_id)
            
            # 确定炮塔是否高亮
            is_highlighted = button.tower_id in self.highlighted_towers
            
            # 绘制炮塔
            button.draw(self.screen, game_logic.towers[button.tower_id], owner, is_highlighted)
    
    def _get_tower_owner(self, game_logic, tower_id):
        """获取炮塔的所有者"""
        for start_idx, end_idx, player in game_logic.lasers:
            if start_idx == tower_id or end_idx == tower_id:
                return player
        return None
    
    def _draw_all_lasers(self, game_logic, tower_buttons):
        """绘制所有激光连接"""
        # 创建炮塔位置映射
        tower_positions = {}
        for button in tower_buttons:
            tower_positions[button.tower_id] = button.rect
        
        # 绘制每条激光
        for start_idx, end_idx, player in game_logic.lasers:
            if start_idx in tower_positions and end_idx in tower_positions:
                self._draw_laser(tower_positions[start_idx], tower_positions[end_idx], player)
    
    def _draw_laser(self, start_rect, end_rect, player):
        """绘制单个激光连接"""
        # 激光连接点（从炮塔顶部向上一点）
        start_x = start_rect.centerx
        start_y = start_rect.top + 10  # 从炮塔顶部向上10像素
        end_x = end_rect.centerx
        end_y = end_rect.top + 10
        
        # 激光颜色
        laser_color = (0, 255, 200) if player == 1 else (255, 100, 0)  # 玩家1青蓝，玩家2橙色
        
        # 绘制粗激光光束（10像素宽）
        pygame.draw.line(self.screen, laser_color, (start_x, start_y), (end_x, end_y), 10)
        
        # 添加激光发光效果
        glow_surf = pygame.Surface((abs(end_x - start_x) + 20, 20), pygame.SRCALPHA)
        pygame.draw.line(glow_surf, (*laser_color[:3], 80), (10, 10), (glow_surf.get_width() - 10, 10), 12)
        self.screen.blit(glow_surf, (min(start_x, end_x) - 10, start_y - 10))
    
    def draw_scrollbar(self, total_towers):
        """绘制滚动条"""
        if total_towers <= self.visible_tower_count:
            return
        
        scrollbar_width = SCREEN_WIDTH - 100
        scrollbar_x = 50
        scrollbar_y = 450
        
        # 滚动条背景
        pygame.draw.rect(self.screen, (35, 45, 60), 
                        (scrollbar_x, scrollbar_y, scrollbar_width, 15), border_radius=7)
        
        # 计算滑块位置和大小
        visible_ratio = self.visible_tower_count / total_towers
        slider_width = max(30, scrollbar_width * visible_ratio)
        max_scroll = total_towers - self.visible_tower_count
        
        if max_scroll > 0:
            scroll_ratio = self.scroll_offset / max_scroll
            slider_x = scrollbar_x + scroll_ratio * (scrollbar_width - slider_width)
        else:
            slider_x = scrollbar_x
        
        # 绘制滑块
        pygame.draw.rect(self.screen, ACCENT_COLOR, 
                        (slider_x, scrollbar_y, slider_width, 15), border_radius=7)
    
    def create_tower_buttons(self, num_towers):
        """创建炮塔按钮"""
        buttons = []
        tower_width = 60
        tower_height = 100
        spacing = 20
        
        # 计算起始位置
        total_width = min(num_towers, self.visible_tower_count) * (tower_width + spacing) - spacing
        start_x = (SCREEN_WIDTH - total_width) // 2
        y_position = 250
        
        # 创建可见范围内的炮塔按钮
        start_index = self.scroll_offset
        end_index = min(self.scroll_offset + self.visible_tower_count, num_towers)
        
        for i in range(start_index, end_index):
            x = start_x + (i - start_index) * (tower_width + spacing)
            button = TowerButton(x, y_position, tower_width, tower_height, i, self.font_manager)
            buttons.append(button)
        
        return buttons
    
    def create_control_buttons(self):
        """创建控制按钮"""
        buttons = {
            "back": Button(20, 20, 50, 50, "", self.font_manager, icon='back', 
                          tooltip="Back to mode selection"),
            "home": Button(80, 20, 50, 50, "", self.font_manager, icon='home', 
                          tooltip="Back to main menu")
        }
        return buttons
    
    def create_game_over_buttons(self):
        """创建游戏结束时的按钮"""
        return {
            "restart": Button(SCREEN_WIDTH//2 - 120, 550, 240, 60, "New Game", self.font_manager, 
                            tooltip="Start a new game")
        }
    
    def scroll_left(self, total_towers):
        """向左滚动"""
        if self.scroll_offset > 0:
            self.scroll_offset -= 1
    
    def scroll_right(self, total_towers):
        """向右滚动"""
        if self.scroll_offset + self.visible_tower_count < total_towers:
            self.scroll_offset += 1
    
    def handle_mouse_wheel(self, event, total_towers):
        """处理鼠标滚轮滚动"""
        if event.type == pygame.MOUSEWHEEL:
            if event.y > 0:  # 向上滚动，向左移动
                self.scroll_left(total_towers)
            elif event.y < 0:  # 向下滚动，向右移动
                self.scroll_right(total_towers)
            return True
        return False
    
    def update_highlighted_towers(self, available_moves, selected_tower):
        """更新高亮显示的炮塔"""
        self.highlighted_towers.clear()
        
        if selected_tower is not None:
            # 高亮显示与选中炮塔相邻的可用炮塔对
            for move in available_moves:
                if move == selected_tower or move + 1 == selected_tower:
                    self.highlighted_towers.add(move)
                    self.highlighted_towers.add(move + 1)
        else:
            # 高亮显示所有可用炮塔对
            for move in available_moves:
                self.highlighted_towers.add(move)
                self.highlighted_towers.add(move + 1)
    
    def draw_hints(self):
        """绘制操作提示"""
        hint_y = 600
        hints = [
            "Click on adjacent towers to connect lasers",
            "Last player to make a move wins the game",
            "Use mouse wheel to scroll through towers",
            "Connected towers are colored by player"
        ]
        
        for i, hint in enumerate(hints):
            hint_text = self.font_manager.small.render(hint, True, (150, 170, 190))
            self.screen.blit(hint_text, (SCREEN_WIDTH//2 - hint_text.get_width()//2, hint_y + i * 20))