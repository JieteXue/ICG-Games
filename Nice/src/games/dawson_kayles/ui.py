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
    
    def draw(self, surface, is_active, is_highlighted):
        """绘制炮塔"""
        # 炮塔基座
        base_color = (100, 120, 180)  # 炮塔基座颜色
        if not is_active:
            base_color = (60, 80, 120)  # 未激活的炮塔
        
        pygame.draw.rect(surface, base_color, self.rect, border_radius=8)
        
        # 炮塔顶部（雷达/发射器）
        top_radius = self.rect.width // 3
        top_center = (self.rect.centerx, self.rect.top + top_radius + 5)
        
        if is_active:
            top_color = (0, 200, 255)  # 激活炮塔 - 亮蓝色
        else:
            top_color = (60, 80, 120)  # 未激活炮塔
        
        pygame.draw.circle(surface, top_color, top_center, top_radius, 2)
        
        # 如果激活，绘制发光效果
        if is_active:
            glow_radius = top_radius + 3
            glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*top_color[:3], 50), (glow_radius, glow_radius), glow_radius)
            surface.blit(glow_surf, (top_center[0] - glow_radius, top_center[1] - glow_radius))
        
        # 炮塔编号
        id_text = self.font_manager.small.render(str(self.tower_id), True, TEXT_COLOR)
        surface.blit(id_text, (self.rect.centerx - 5, self.rect.bottom - 25))
        
        # 高亮显示
        if is_highlighted and is_active:
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
        """绘制游戏信息面板"""
        # 头部背景
        header_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 150)
        pygame.draw.rect(self.screen, (35, 45, 60), header_rect)
        pygame.draw.line(self.screen, ACCENT_COLOR, (0, 150), (SCREEN_WIDTH, 150), 3)
        
        # 游戏标题
        title = self.font_manager.large.render("Laser Defense - Dawson-Kayles", True, TEXT_COLOR)
        title_shadow = self.font_manager.large.render("Laser Defense - Dawson-Kayles", True, SHADOW_COLOR)
        self.screen.blit(title_shadow, (SCREEN_WIDTH//2 - title.get_width()//2 + 2, 15))
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 13))
        
        # 游戏模式信息
        if game_logic.game_mode == "PVP":
            mode_text = "Mode: Player vs Player"
        else:
            difficulty_names = ["Easy", "Normal", "Hard", "Insane"]
            mode_text = f"Mode: Player vs AI - {difficulty_names[game_logic.difficulty-1]}"
        
        mode_info = self.font_manager.small.render(mode_text, True, ACCENT_COLOR)
        self.screen.blit(mode_info, (20, 60))
        
        # 当前玩家信息
        player_colors = {
            1: (0, 200, 255),  # 玩家1 - 蓝色
            2: (255, 100, 0)   # 玩家2/AI - 橙色
        }
        player_name = "Player 1" if game_logic.current_player == 1 else "AI" if game_logic.game_mode == "PVE" else "Player 2"
        player_color = player_colors[game_logic.current_player]
        
        player_text = self.font_manager.medium.render(f"Current: {player_name}", True, player_color)
        player_bg = pygame.Rect(SCREEN_WIDTH - player_text.get_width() - 40, 50, 
                              player_text.get_width() + 20, player_text.get_height() + 10)
        pygame.draw.rect(self.screen, (40, 50, 65), player_bg, border_radius=8)
        pygame.draw.rect(self.screen, player_color, player_bg, 2, border_radius=8)
        self.screen.blit(player_text, (SCREEN_WIDTH - player_text.get_width() - 30, 55))
        
        # 游戏状态消息
        message_color = (WIN_COLOR if game_logic.game_over and game_logic.winner == 1 
                        else LOSE_COLOR if game_logic.game_over and game_logic.winner == 2
                        else TEXT_COLOR)
        
        message_lines = wrap_text(game_logic.message, self.font_manager.medium, SCREEN_WIDTH - 100)
        for i, line in enumerate(message_lines):
            message_text = self.font_manager.medium.render(line, True, message_color)
            message_bg_width = message_text.get_width() + 30
            message_bg = pygame.Rect(SCREEN_WIDTH//2 - message_bg_width//2, 90 + i * 25, 
                                   message_bg_width, message_text.get_height() + 6)
            
            if i == 0:
                pygame.draw.rect(self.screen, (40, 50, 65), message_bg, border_radius=8)
                pygame.draw.rect(self.screen, ACCENT_COLOR, message_bg, 2, border_radius=8)
            
            self.screen.blit(message_text, (SCREEN_WIDTH//2 - message_text.get_width()//2, 93 + i * 25))
    
    def draw_towers(self, game_logic, tower_buttons):
        """绘制炮塔和激光"""
        # 先绘制所有激光
        for start_idx, end_idx, player in game_logic.lasers:
            self._draw_laser(start_idx, end_idx, player, tower_buttons)
        
        # 然后绘制所有炮塔
        for button in tower_buttons:
            is_active = game_logic.towers[button.tower_id] == 1
            is_highlighted = button.tower_id in self.highlighted_towers
            button.draw(self.screen, is_active, is_highlighted)
    
    def _draw_laser(self, start_idx, end_idx, player, tower_buttons):
        """绘制激光连接"""
        if start_idx >= len(tower_buttons) or end_idx >= len(tower_buttons):
            return
        
        start_button = tower_buttons[start_idx]
        end_button = tower_buttons[end_idx]
        
        start_x = start_button.rect.centerx
        start_y = start_button.rect.centery
        end_x = end_button.rect.centerx
        end_y = end_button.rect.centery
        
        laser_color = (0, 255, 200) if player == 1 else (255, 100, 0)  # 玩家1青蓝，玩家2橙色
        
        # 绘制激光光束
        pygame.draw.line(self.screen, laser_color, (start_x, start_y), (end_x, end_y), 4)
        
        # 添加激光发光效果
        glow_surf = pygame.Surface((abs(end_x - start_x) + 10, 10), pygame.SRCALPHA)
        pygame.draw.line(glow_surf, (*laser_color[:3], 80), (5, 5), (glow_surf.get_width() - 5, 5), 8)
        self.screen.blit(glow_surf, (min(start_x, end_x) - 5, start_y - 5))
    
    def draw_control_panel(self, control_buttons, game_logic):
        """绘制控制面板"""
        control_y = 500
        control_width = 400
        control_x = (SCREEN_WIDTH - control_width) // 2
        
        # 控制面板背景
        control_bg = pygame.Rect(control_x - 20, control_y, control_width + 40, 120)
        pygame.draw.rect(self.screen, (35, 45, 60), control_bg, border_radius=15)
        pygame.draw.rect(self.screen, ACCENT_COLOR, control_bg, 3, border_radius=15)
        
        # 绘制控制按钮
        for button in control_buttons.values():
            button.draw(self.screen)
        
        # 可用移动信息
        available_moves = len(game_logic.get_available_moves())
        moves_text = self.font_manager.small.render(f"Available moves: {available_moves}", True, TEXT_COLOR)
        self.screen.blit(moves_text, (control_x, control_y + 80))
    
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
        slider_width = max(30, scrollbar_width * self.visible_tower_count / total_towers)
        slider_x = scrollbar_x + (self.scroll_offset / (total_towers - self.visible_tower_count)) * (scrollbar_width - slider_width)
        
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
            "restart": Button(SCREEN_WIDTH//2 - 120, 550, 240, 60, "New Game", self.font_manager, 
                            tooltip="Start a new game"),
            "back": Button(20, 20, 50, 50, "", self.font_manager, icon='back', 
                          tooltip="Back to mode selection"),
            "home": Button(80, 20, 50, 50, "", self.font_manager, icon='home', 
                          tooltip="Back to main menu")
        }
        return buttons
    
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