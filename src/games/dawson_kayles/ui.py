# [file name]: src/games/dawson_kayles/ui.py
"""
Dawson-Kayles Game UI Components
"""

import pygame
import math
import random
from utils.constants import *
from utils.helpers import wrap_text

class TowerButton:
    
    def __init__(self, x, y, width, height, tower_id, font_manager):
        self.rect = pygame.Rect(x, y, width, height)
        self.tower_id = tower_id
        self.font_manager = font_manager
        self.hovered = False
        self.selected = False
        self.enabled = True
        self.pulse_angle = random.uniform(0, math.pi * 2) if 'random' in dir() else 0
        
    def draw(self, surface, tower_state, player_owner=None, is_highlighted=False):
        """绘制科技风格炮塔"""
        # 炮塔基础颜色
        base_color = (40, 45, 60)
        accent_color = (0, 200, 255)
        
        # 根据状态调整颜色
        if tower_state == 0:  # 已连接
            if player_owner == 1:
                base_color = (0, 80, 120)      # 玩家1 - 深青色
                accent_color = (0, 255, 220)   # 玩家1 - 青色霓虹
            elif player_owner == 2:
                base_color = (120, 60, 0)      # 玩家2/AI - 深橙色
                accent_color = (255, 180, 50)  # 玩家2/AI - 橙色霓虹
            else:
                base_color = (50, 50, 65)      # 默认禁用颜色
                accent_color = (100, 100, 120)
        else:  # 可用
            base_color = (30, 35, 50)          # 可用炮塔基座
            accent_color = (0, 200, 255)       # 激活炮塔 - 亮蓝色
        
        # 绘制炮塔底座（3D效果）
        self._draw_tower_base(surface, base_color, accent_color)
        
        # 绘制炮塔主体（圆柱体）
        self._draw_tower_body(surface, base_color, accent_color)
        
        # 绘制炮塔顶部（雷达/能量核心）
        self._draw_tower_top(surface, accent_color, tower_state)
        
        # 炮塔编号（发光效果）
        self._draw_tower_id(surface)
        
        # 高亮显示可用移动
        if is_highlighted and tower_state == 1:
            self._draw_highlight(surface)
    
    def _draw_tower_base(self, surface, base_color, accent_color):
        """绘制炮塔底座"""
        # 底座阴影
        shadow_rect = pygame.Rect(
            self.rect.left + 4,
            self.rect.top + 4,
            self.rect.width,
            self.rect.height
        )
        pygame.draw.rect(surface, (0, 0, 0, 100), shadow_rect, border_radius=8)
        
        # 底座主体
        pygame.draw.rect(surface, base_color, self.rect, border_radius=8)
        
        # 底座边框（发光效果）
        border_width = 3
        pygame.draw.rect(surface, accent_color, self.rect, border_width, border_radius=8)
        
        # 底座细节（科技线条）
        line_y = self.rect.bottom - 15
        pygame.draw.line(
            surface,
            accent_color,
            (self.rect.left + 10, line_y),
            (self.rect.right - 10, line_y),
            2
        )
    
    def _draw_tower_body(self, surface, base_color, accent_color):
        """绘制炮塔主体"""
        body_width = self.rect.width - 20
        body_height = 40
        body_rect = pygame.Rect(
            self.rect.centerx - body_width // 2,
            self.rect.top + 20,
            body_width,
            body_height
        )
        
        # 主体渐变效果
        for i in range(body_height):
            color_intensity = 1.0 - i / body_height * 0.5
            line_color = (
                int(base_color[0] * color_intensity),
                int(base_color[1] * color_intensity),
                int(base_color[2] * color_intensity)
            )
            pygame.draw.line(
                surface,
                line_color,
                (body_rect.left, body_rect.top + i),
                (body_rect.right, body_rect.top + i),
                1
            )
        
        # 主体边框
        pygame.draw.rect(surface, accent_color, body_rect, 2)
        
        # 科技细节（垂直线条）
        detail_count = 3
        for i in range(1, detail_count + 1):
            x = body_rect.left + (body_rect.width // (detail_count + 1)) * i
            pygame.draw.line(
                surface,
                accent_color,
                (x, body_rect.top),
                (x, body_rect.bottom),
                1
            )
    
    def _draw_tower_top(self, surface, accent_color, tower_state):
        """绘制炮塔顶部"""
        top_radius = self.rect.width // 4
        top_center = (self.rect.centerx, self.rect.top + top_radius + 15)
        
        # 雷达圆环
        pygame.draw.circle(surface, accent_color, top_center, top_radius, 2)
        
        # 内部同心圆
        inner_radius = top_radius - 4
        pygame.draw.circle(surface, accent_color, top_center, inner_radius, 1)
        
        # 十字准心
        pygame.draw.line(
            surface,
            accent_color,
            (top_center[0] - inner_radius, top_center[1]),
            (top_center[0] + inner_radius, top_center[1]),
            1
        )
        pygame.draw.line(
            surface,
            accent_color,
            (top_center[0], top_center[1] - inner_radius),
            (top_center[0], top_center[1] + inner_radius),
            1
        )
        
        # 如果可用，绘制脉冲效果
        if tower_state == 1:
            self.pulse_angle += 0.1
            pulse_radius = top_radius + math.sin(self.pulse_angle) * 3 + 3
            
            # 脉冲发光效果
            glow_surf = pygame.Surface((pulse_radius * 2, pulse_radius * 2), pygame.SRCALPHA)
            for i in range(3):
                alpha = 80 - i * 20
                radius = pulse_radius - i * 2
                pygame.draw.circle(glow_surf, (*accent_color[:3], alpha), 
                                 (pulse_radius, pulse_radius), radius, 2)
            surface.blit(glow_surf, (top_center[0] - pulse_radius, top_center[1] - pulse_radius))
    
    def _draw_tower_id(self, surface):
        """绘制炮塔编号"""
        id_text = self.font_manager.small.render(str(self.tower_id), True, (220, 240, 255))
        text_shadow = self.font_manager.small.render(str(self.tower_id), True, (0, 0, 0, 150))
        
        # 文字阴影
        text_pos = (self.rect.centerx - 5, self.rect.bottom - 25)
        surface.blit(text_shadow, (text_pos[0] + 1, text_pos[1] + 1))
        surface.blit(id_text, text_pos)
        
        # 编号背景光晕
        text_rect = id_text.get_rect(center=(self.rect.centerx, self.rect.bottom - 25))
        glow_radius = max(text_rect.width, text_rect.height) // 2 + 2
        glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (0, 150, 200, 30), (glow_radius, glow_radius), glow_radius)
        surface.blit(glow_surf, (text_rect.centerx - glow_radius, text_rect.centery - glow_radius))
    
    def _draw_highlight(self, surface):
        """绘制高亮效果"""
        highlight_rect = self.rect.inflate(12, 12)
        
        # 多层发光边框
        for i in range(3, 0, -1):
            alpha = 100 - (3 - i) * 30
            color = (0, 255, 200, alpha)
            temp_surf = pygame.Surface((highlight_rect.width, highlight_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(temp_surf, color, 
                           pygame.Rect(0, 0, highlight_rect.width, highlight_rect.height), 
                           i * 2, border_radius=12)
            surface.blit(temp_surf, highlight_rect)
    
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
    """Dawson-Kayles游戏UI管理器 - 科技风格"""
    
    def __init__(self, screen, font_manager):
        self.screen = screen
        self.font_manager = font_manager
        self.scroll_offset = 0
        self.visible_tower_count = 10
        self.highlighted_towers = set()
        self.time = 0
        self.grid_offset = 0
        
    def draw_background(self):
        """绘制科技风格背景"""
        # 深空背景
        self.screen.fill((5, 10, 20))
        self.time += 0.5
        self.grid_offset = (self.grid_offset + 0.3) % 40
        
        # 绘制动态网格
        self._draw_dynamic_grid()
        
        # 绘制星空效果
        self._draw_stars()
        
        # 绘制底部科技面板
        self._draw_tech_panel()
    
    def _draw_dynamic_grid(self):
        """绘制动态网格线"""
        grid_color = (20, 30, 50)
        grid_highlight = (30, 80, 120, 50)
        
        # 主要网格
        for x in range(-40, SCREEN_WIDTH + 40, 40):
            x_pos = (x + self.grid_offset) % (SCREEN_WIDTH + 80) - 40
            pygame.draw.line(self.screen, grid_color, (x_pos, 0), (x_pos, SCREEN_HEIGHT), 1)
        
        for y in range(-40, SCREEN_HEIGHT + 40, 40):
            y_pos = (y + self.grid_offset) % (SCREEN_HEIGHT + 80) - 40
            pygame.draw.line(self.screen, grid_color, (0, y_pos), (SCREEN_WIDTH, y_pos), 1)
        
        # 中心动态网格线
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        
        # 水平脉冲线
        pulse_width = abs(math.sin(self.time * 0.02)) * 20 + 5
        pygame.draw.line(self.screen, grid_highlight, 
                        (center_x - 300, center_y),
                        (center_x + 300, center_y),
                        int(pulse_width))
    
    def _draw_stars(self):
        """绘制星空效果"""
        for i in range(50):
            x = (i * 73) % SCREEN_WIDTH
            y = (i * 37) % SCREEN_HEIGHT
            size = (math.sin(self.time * 0.05 + i) + 1) * 0.5 + 0.5
            brightness = 150 + int(math.sin(self.time * 0.03 + i) * 50)
            
            pygame.draw.circle(self.screen, (brightness, brightness, brightness), 
                             (int(x), int(y)), int(size))
    
    def _draw_tech_panel(self):
        """绘制底部科技面板"""
        panel_height = 120
        panel_rect = pygame.Rect(0, SCREEN_HEIGHT - panel_height, SCREEN_WIDTH, panel_height)
        
        # 面板渐变
        for i in range(panel_height):
            alpha = int(200 * (1 - i / panel_height))
            pygame.draw.line(self.screen, (10, 20, 40, alpha),
                           (0, SCREEN_HEIGHT - panel_height + i),
                           (SCREEN_WIDTH, SCREEN_HEIGHT - panel_height + i),
                           1)
        
        # 面板顶部边框
        pygame.draw.line(self.screen, (0, 150, 255),
                        (0, SCREEN_HEIGHT - panel_height),
                        (SCREEN_WIDTH, SCREEN_HEIGHT - panel_height),
                        3)
        
        # 面板装饰线
        for i in range(0, SCREEN_WIDTH, 40):
            pygame.draw.line(self.screen, (0, 100, 200, 100),
                           (i, SCREEN_HEIGHT - panel_height + 10),
                           (i, SCREEN_HEIGHT - panel_height + 30),
                           1)
    
    def draw_game_info(self, game_logic):
        """绘制游戏信息面板"""
        # 顶部科技面板
        header_height = 200
        self._draw_header_panel(header_height)
        
        # 游戏标题（霓虹效果）
        self._draw_title()
        
        # 游戏模式信息
        self._draw_game_mode(game_logic)
        
        # 当前玩家信息
        self._draw_current_player(game_logic)
        
        # 游戏状态
        self._draw_game_status(game_logic)
        
        # 游戏消息
        self._draw_game_message(game_logic)
        
        # 胜负状态指示器
        if not game_logic.game_over:
            self._draw_position_indicator(game_logic)
    
    def _draw_header_panel(self, height):
        """绘制顶部面板"""
        # 面板渐变背景
        for i in range(height):
            alpha = int(180 * (1 - abs(i - height/2) / (height/2)))
            color = (15, 25, 40, alpha)
            pygame.draw.line(self.screen, color, (0, i), (SCREEN_WIDTH, i), 1)
        
        # 面板底部发光边框
        border_y = height
        for i in range(5):
            alpha = 200 - i * 40
            pygame.draw.line(self.screen, (0, 150, 255, alpha),
                           (0, border_y + i),
                           (SCREEN_WIDTH, border_y + i),
                           1)
        
        # 面板装饰元素
        self._draw_header_decoration(height)
    
    def _draw_header_decoration(self, height):
        """绘制面板装饰"""
        # 左右科技柱
        for x in [50, SCREEN_WIDTH - 50]:
            for y in range(20, height - 20, 15):
                pygame.draw.line(self.screen, (0, 120, 200),
                               (x, y), (x, y + 8), 2)
        
        # 中央扫描线
        scan_width = int(abs(math.sin(self.time * 0.03)) * 400 + 100)
        scan_rect = pygame.Rect(
            SCREEN_WIDTH//2 - scan_width//2,
            height - 30,
            scan_width,
            3
        )
        
        scan_surf = pygame.Surface((scan_width, 10), pygame.SRCALPHA)
        for i in range(scan_width):
            alpha = int(abs(math.sin(i/20 + self.time)) * 200)
            pygame.draw.line(scan_surf, (0, 255, 200, alpha),
                           (i, 0), (i, 3), 1)
        self.screen.blit(scan_surf, scan_rect)
    
    def _draw_title(self):
        """绘制游戏标题"""
        title = self.font_manager.large.render("LASER DEFENSE SYSTEM", True, (0, 255, 220))
        subtitle = self.font_manager.medium.render("DAWSON-KAYLES PROTOCOL", True, (100, 200, 255))
        
        # 标题发光效果
        for i in range(3, 0, -1):
            glow_color = (0, 150, 200, 100 - i * 30)
            glow_surf = pygame.Surface((title.get_width() + i*8, title.get_height() + i*8), pygame.SRCALPHA)
            glow_text = self.font_manager.large.render("LASER DEFENSE SYSTEM", True, glow_color)
            glow_surf.blit(glow_text, (i*4, i*4))
            self.screen.blit(glow_surf, (SCREEN_WIDTH//2 - glow_surf.get_width()//2, 15 - i))
        
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 15))
        self.screen.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, 55))
    
    def _draw_game_mode(self, game_logic):
        """绘制游戏模式信息"""
        difficulty_names = ["EASY", "NORMAL", "HARD", "INSANE"]
        
        if game_logic.game_mode == "PVP":
            mode_text = "MODE: PLAYER VS PLAYER"
            mode_color = (0, 255, 150)
        else:
            mode_text = f"MODE: PLAYER VS AI - {difficulty_names[game_logic.difficulty-1]}"
            mode_color = (255, 150, 0)
        
        mode_info = self.font_manager.small.render(mode_text, True, mode_color)
        
        # 模式信息背景
        mode_bg = pygame.Rect(20, 165, mode_info.get_width() + 20, mode_info.get_height() + 8)
        pygame.draw.rect(self.screen, (20, 30, 50, 200), mode_bg, border_radius=6)
        pygame.draw.rect(self.screen, mode_color, mode_bg, 2, border_radius=6)
        
        self.screen.blit(mode_info, (30, 168))
    
    def _draw_current_player(self, game_logic):
        """绘制当前玩家信息"""
        player_colors = {
            "Player 1": (0, 255, 200),    # 青色
            "Player 2": (255, 220, 50),   # 黄色
            "AI": (255, 100, 100)         # 红色
        }
        
        player_color = player_colors.get(game_logic.current_player, (255, 255, 255))
        player_text = self.font_manager.small.render(f"ACTIVE: {game_logic.current_player}", True, player_color)
        
        # 玩家信息面板
        player_bg = pygame.Rect(
            SCREEN_WIDTH - player_text.get_width() - 50,
            163,
            player_text.get_width() + 30,
            player_text.get_height() + 10
        )
        
        # 面板发光效果
        glow_surf = pygame.Surface((player_bg.width + 10, player_bg.height + 10), pygame.SRCALPHA)
        pygame.draw.rect(glow_surf, (*player_color[:3], 50), 
                        pygame.Rect(5, 5, player_bg.width, player_bg.height), 
                        border_radius=10)
        self.screen.blit(glow_surf, (player_bg.x - 5, player_bg.y - 5))
        
        # 面板主体
        pygame.draw.rect(self.screen, (25, 35, 55), player_bg, border_radius=8)
        pygame.draw.rect(self.screen, player_color, player_bg, 3, border_radius=8)
        
        # 玩家状态指示灯
        pygame.draw.circle(self.screen, player_color, 
                          (player_bg.left + 15, player_bg.centery), 4)
        
        self.screen.blit(player_text, (SCREEN_WIDTH - player_text.get_width() - 30, 168))
    
    def _draw_game_status(self, game_logic):
        """绘制游戏状态"""
        towers_remaining = sum(game_logic.towers)
        available_moves = len(game_logic.get_available_moves())
        
        status_text = f"TOWERS: {towers_remaining} | MOVES: {available_moves}"
        status = self.font_manager.large.render(status_text, True, (0, 220, 255))
        
        # 状态栏背景
        status_bg = pygame.Rect(
            SCREEN_WIDTH//2 - status.get_width()//2 - 15,
            90,
            status.get_width() + 30,
            status.get_height() + 10
        )
        
        # 渐变背景
        for i in range(status_bg.height):
            alpha = int(100 * (1 - abs(i - status_bg.height/2) / status_bg.height))
            pygame.draw.line(self.screen, (0, 50, 80, alpha),
                           (status_bg.left, status_bg.top + i),
                           (status_bg.right, status_bg.top + i),
                           1)
        
        pygame.draw.rect(self.screen, (0, 100, 150, 100), status_bg, border_radius=8)
        pygame.draw.rect(self.screen, (0, 200, 255), status_bg, 2, border_radius=8)
        
        self.screen.blit(status, (SCREEN_WIDTH//2 - status.get_width()//2, 95))
    
    def _draw_game_message(self, game_logic):
        """绘制游戏消息"""
        message_color = (WIN_COLOR if game_logic.game_over and game_logic.winner == "Player 1" 
                        else LOSE_COLOR if game_logic.game_over and game_logic.winner == "AI"
                        else (255, 220, 50) if game_logic.game_over and game_logic.winner == "Player 2"
                        else (180, 220, 255))
        
        message_lines = wrap_text(game_logic.message, self.font_manager.medium, SCREEN_WIDTH - 100)
        
        for i, line in enumerate(message_lines):
            message_text = self.font_manager.medium.render(line, True, message_color)
            
            # 消息面板（只在第一行显示背景）
            if i == 0:
                message_bg = pygame.Rect(
                    SCREEN_WIDTH//2 - message_text.get_width()//2 - 15,
                    125 + i * 25,
                    message_text.get_width() + 30,
                    len(message_lines) * 25 + 5
                )
                
                # 消息面板发光
                glow_surf = pygame.Surface((message_bg.width + 10, message_bg.height + 10), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (*message_color[:3], 30), 
                                pygame.Rect(5, 5, message_bg.width, message_bg.height), 
                                border_radius=10)
                self.screen.blit(glow_surf, (message_bg.x - 5, message_bg.y - 5))
                
                pygame.draw.rect(self.screen, (25, 35, 55, 220), message_bg, border_radius=8)
                pygame.draw.rect(self.screen, message_color, message_bg, 2, border_radius=8)
            
            self.screen.blit(message_text, (SCREEN_WIDTH//2 - message_text.get_width()//2, 130 + i * 25))
    
    def _draw_position_indicator(self, game_logic):
        """绘制位置指示器"""
        game_state = "WINNING POSITION" if game_logic.judge_win() else "LOSING POSITION"
        state_color = WIN_COLOR if game_logic.judge_win() else LOSE_COLOR
        
        state_text = self.font_manager.small.render(game_state, True, state_color)
        
        state_bg = pygame.Rect(
            SCREEN_WIDTH//2 - state_text.get_width()//2 - 10,
            175,
            state_text.get_width() + 20,
            state_text.get_height() + 8
        )
        
        # 脉冲效果
        pulse = abs(math.sin(self.time * 0.05)) * 0.3 + 0.7
        pulse_color = (
            int(state_color[0] * pulse),
            int(state_color[1] * pulse),
            int(state_color[2] * pulse)
        )
        
        # 指示器发光
        glow_surf = pygame.Surface((state_bg.width + 20, state_bg.height + 20), pygame.SRCALPHA)
        pygame.draw.rect(glow_surf, (*state_color[:3], 80), 
                        pygame.Rect(10, 10, state_bg.width, state_bg.height), 
                        border_radius=8)
        self.screen.blit(glow_surf, (state_bg.x - 10, state_bg.y - 10))
        
        pygame.draw.rect(self.screen, (30, 40, 65), state_bg, border_radius=8)
        pygame.draw.rect(self.screen, pulse_color, state_bg, 3, border_radius=8)
        
        self.screen.blit(state_text, (SCREEN_WIDTH//2 - state_text.get_width()//2, 178))
    
    # 保持原有的方法，但更新激光绘制效果
    def draw_towers_and_lasers(self, game_logic, tower_buttons):
        """绘制炮塔和激光"""
        # 先绘制激光（需要更炫酷的效果）
        self._draw_all_lasers(game_logic, tower_buttons)
        
        # 然后绘制炮塔
        for button in tower_buttons:
            owner = self._get_tower_owner(game_logic, button.tower_id)
            is_highlighted = button.tower_id in self.highlighted_towers
            button.draw(self.screen, game_logic.towers[button.tower_id], owner, is_highlighted)
    
    def _draw_all_lasers(self, game_logic, tower_buttons):
        """绘制所有激光连接 - 科技风格"""
        tower_positions = {}
        for button in tower_buttons:
            tower_positions[button.tower_id] = button.rect
        
        for start_idx, end_idx, player in game_logic.lasers:
            if start_idx in tower_positions and end_idx in tower_positions:
                self._draw_laser_beam(tower_positions[start_idx], tower_positions[end_idx], player)
    
    def _draw_laser_beam(self, start_rect, end_rect, player):
        """绘制单个激光光束"""
        # 激光连接点
        start_x = start_rect.centerx
        start_y = start_rect.top + 15
        end_x = end_rect.centerx
        end_y = end_rect.top + 15
        
        # 激光颜色
        laser_color = (0, 255, 220) if player == 1 else (255, 180, 50)
        
        # 计算激光长度和角度
        dx = end_x - start_x
        dy = end_y - start_y
        length = math.sqrt(dx*dx + dy*dy)
        angle = math.atan2(dy, dx)
        
        # 绘制多层激光效果
        for i in range(3):
            width = 12 - i * 3
            alpha = 255 - i * 80
            
            # 创建激光表面
            laser_surf = pygame.Surface((int(length), width), pygame.SRCALPHA)
            
            # 绘制渐变激光
            for j in range(width):
                color_factor = 1.0 - j / width * 0.5
                line_color = (
                    int(laser_color[0] * color_factor),
                    int(laser_color[1] * color_factor),
                    int(laser_color[2] * color_factor),
                    alpha
                )
                pygame.draw.line(laser_surf, line_color,
                               (0, j), (int(length), j), 1)
            
            # 旋转并放置激光
            rotated_laser = pygame.transform.rotate(laser_surf, -math.degrees(angle))
            laser_rect = rotated_laser.get_rect(center=((start_x+end_x)//2, (start_y+end_y)//2))
            self.screen.blit(rotated_laser, laser_rect)
        
        # 激光端点效果
        self._draw_laser_endpoint(start_x, start_y, laser_color)
        self._draw_laser_endpoint(end_x, end_y, laser_color)
        
        # 激光能量流动效果
        self._draw_energy_flow(start_x, start_y, end_x, end_y, laser_color)
    
    def _draw_laser_endpoint(self, x, y, color):
        """绘制激光端点"""
        # 端点核心
        pygame.draw.circle(self.screen, color, (x, y), 6)
        
        # 端点发光
        for i in range(3, 0, -1):
            radius = 6 + i * 2
            alpha = 150 - i * 50
            surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*color[:3], alpha), (radius, radius), radius)
            self.screen.blit(surf, (x - radius, y - radius))
    
    def _draw_energy_flow(self, start_x, start_y, end_x, end_y, color):
        """绘制能量流动效果"""
        flow_pos = (self.time * 50) % 100 / 100  # 0-1之间的流动位置
        
        # 计算流动点位置
        flow_x = start_x + (end_x - start_x) * flow_pos
        flow_y = start_y + (end_y - start_y) * flow_pos
        
        # 流动点（能量球）
        pygame.draw.circle(self.screen, color, (int(flow_x), int(flow_y)), 3)
        
        # 流动轨迹
        trail_length = 20
        for i in range(trail_length):
            alpha = 200 - i * 10
            pos = flow_pos - i * 0.02
            if pos < 0:
                continue
            
            trail_x = start_x + (end_x - start_x) * pos
            trail_y = start_y + (end_y - start_y) * pos
            
            pygame.draw.circle(self.screen, (*color[:3], alpha), 
                             (int(trail_x), int(trail_y)), 2)
    
    # 保持原有方法但更新视觉效果
    def create_tower_buttons(self, num_towers):
        """创建炮塔按钮"""
        buttons = []
        tower_width = 70
        tower_height = 120
        spacing = 25
        
        total_width = min(num_towers, self.visible_tower_count) * (tower_width + spacing) - spacing
        start_x = (SCREEN_WIDTH - total_width) // 2
        y_position = 280
        
        start_index = self.scroll_offset
        end_index = min(self.scroll_offset + self.visible_tower_count, num_towers)
        
        for i in range(start_index, end_index):
            x = start_x + (i - start_index) * (tower_width + spacing)
            button = TowerButton(x, y_position, tower_width, tower_height, i, self.font_manager)
            buttons.append(button)
        
        return buttons
    
    # 更新控制按钮样式
    def create_control_buttons(self):
        """创建科技风格控制按钮"""
        class TechButton:
            def __init__(self, x, y, width, height, text, font_manager, icon=None, tooltip=""):
                self.rect = pygame.Rect(x, y, width, height)
                self.text = text
                self.font_manager = font_manager
                self.hovered = False
                self.enabled = True
                self.icon = icon
                self.tooltip = tooltip
                self.corner_radius = 10
                self.glow_alpha = 0
            
            def update_hover(self, mouse_pos):
                old_hovered = self.hovered
                self.hovered = self.rect.collidepoint(mouse_pos) and self.enabled
                if self.hovered and not old_hovered:
                    self.glow_alpha = 100
            
            def is_clicked(self, event):
                return (event.type == pygame.MOUSEBUTTONDOWN and 
                        event.button == 1 and 
                        self.hovered and 
                        self.enabled)
            
            def draw(self, surface):
                # 发光效果
                if self.glow_alpha > 0:
                    glow_surf = pygame.Surface((self.rect.width + 20, self.rect.height + 20), pygame.SRCALPHA)
                    pygame.draw.rect(glow_surf, (0, 150, 255, self.glow_alpha),
                                   pygame.Rect(10, 10, self.rect.width, self.rect.height),
                                   border_radius=self.corner_radius + 5)
                    surface.blit(glow_surf, (self.rect.x - 10, self.rect.y - 10))
                    self.glow_alpha = max(0, self.glow_alpha - 5)
                
                # 按钮阴影
                shadow_rect = self.rect.move(3, 3)
                pygame.draw.rect(surface, (0, 0, 0, 100), shadow_rect, 
                               border_radius=self.corner_radius)
                
                # 按钮主体
                if not self.enabled:
                    base_color = (60, 65, 80)
                    border_color = (80, 85, 100)
                elif self.hovered:
                    base_color = (40, 100, 150)
                    border_color = (0, 200, 255)
                else:
                    base_color = (30, 40, 60)
                    border_color = (0, 150, 220)
                
                pygame.draw.rect(surface, base_color, self.rect, 
                               border_radius=self.corner_radius)
                
                # 按钮边框（发光）
                pygame.draw.rect(surface, border_color, self.rect, 3, 
                               border_radius=self.corner_radius)
                
                # 按钮内发光
                inner_rect = self.rect.inflate(-8, -8)
                pygame.draw.rect(surface, (0, 100, 180, 50), inner_rect,
                               border_radius=self.corner_radius - 2)
                
                # 图标或文字
                if self.icon:
                    self._draw_tech_icon(surface)
                else:
                    self._draw_tech_text(surface)
            
            def _draw_tech_icon(self, surface):
                icon_color = (220, 240, 255) if self.enabled else (120, 130, 140)
                
                if self.icon == 'back':
                    # 返回箭头（三角形）
                    points = [
                        (self.rect.centerx - 5, self.rect.centery),
                        (self.rect.centerx + 5, self.rect.centery - 7),
                        (self.rect.centerx + 5, self.rect.centery + 7)
                    ]
                    pygame.draw.polygon(surface, icon_color, points)
                    
                    # 箭头线
                    pygame.draw.line(surface, icon_color,
                                   (self.rect.centerx , self.rect.centery),
                                   (self.rect.centerx - 3, self.rect.centery),
                                   3)
                
                elif self.icon == 'home':
                    # 房屋图标
                    # 屋顶
                    roof_points = [
                        (self.rect.centerx, self.rect.centery - 8),
                        (self.rect.centerx - 8, self.rect.centery),
                        (self.rect.centerx + 8, self.rect.centery)
                    ]
                    pygame.draw.polygon(surface, icon_color, roof_points)
                    
                    # 房屋主体
                    house_rect = pygame.Rect(
                        self.rect.centerx - 6,
                        self.rect.centery,
                        12,
                        8
                    )
                    pygame.draw.rect(surface, icon_color, house_rect, 2)
                    
                    # 门
                    pygame.draw.rect(surface, icon_color,
                                   (self.rect.centerx - 2, self.rect.centery + 2, 4, 6))
                
                elif self.icon == 'refresh':
                    # 刷新图标（环形箭头）
                    center = self.rect.center
                    radius = 10
                    
                    # 圆形
                    pygame.draw.circle(surface, icon_color, center, radius, 2)
                    
                    # 箭头
                    arrow_points = [
                        (center[0] + radius - 7, center[1] - 3),
                        (center[0] + radius , center[1]),
                        (center[0] + radius , center[1] - 8)
                    ]
                    pygame.draw.polygon(surface, icon_color, arrow_points)
            
            def _draw_tech_text(self, surface):
                text_color = (240, 250, 255) if self.enabled else (120, 130, 140)
                
                # 文字阴影
                if self.enabled:
                    shadow = self.font_manager.small.render(self.text, True, (0, 0, 0, 150))
                    shadow_rect = shadow.get_rect(center=(self.rect.centerx + 1, self.rect.centery + 1))
                    surface.blit(shadow, shadow_rect)
                
                # 主要文字
                text_surface = self.font_manager.small.render(self.text, True, text_color)
                text_rect = text_surface.get_rect(center=self.rect.center)
                surface.blit(text_surface, text_rect)
                
                # 文字发光效果
                if self.hovered and self.enabled:
                    glow = self.font_manager.small.render(self.text, True, (0, 200, 255, 100))
                    glow_rect = glow.get_rect(center=self.rect.center)
                    surface.blit(glow, glow_rect)
        
        nav_button_size = 55
        
        buttons = {
            "back": TechButton(25, 25, nav_button_size, nav_button_size, "", 
                              self.font_manager, icon='back', 
                              tooltip="Back to mode selection"),
            "home": TechButton(25 + nav_button_size + 15, 25, nav_button_size, nav_button_size, "", 
                               self.font_manager, icon='home', 
                               tooltip="Back to main menu"),
            "restart": TechButton(SCREEN_WIDTH//2 - 120, 560, 240, 60, "NEW GAME", 
                                self.font_manager, tooltip="Start a new game"),
            "refresh": TechButton(SCREEN_WIDTH - 25 - nav_button_size, 25, 
                                nav_button_size, nav_button_size, "", 
                                self.font_manager, icon='refresh', 
                                tooltip="Restart current game")
        }
        
        return buttons
    
    # 其他方法保持不变（只更新了视觉效果）
    def draw_scrollbar(self, total_towers):
        """绘制科技风格滚动条"""
        if total_towers <= self.visible_tower_count:
            return
        
        scrollbar_width = SCREEN_WIDTH - 100
        scrollbar_x = 50
        scrollbar_y = 450
        
        # 滚动条背景（科技风格）
        pygame.draw.rect(self.screen, (25, 35, 50), 
                        (scrollbar_x, scrollbar_y, scrollbar_width, 12), border_radius=6)
        
        # 计算滑块
        visible_ratio = self.visible_tower_count / total_towers
        slider_width = max(40, scrollbar_width * visible_ratio)
        max_scroll = total_towers - self.visible_tower_count
        
        if max_scroll > 0:
            scroll_ratio = self.scroll_offset / max_scroll
            slider_x = scrollbar_x + scroll_ratio * (scrollbar_width - slider_width)
        else:
            slider_x = scrollbar_x
        
        # 滑块（发光效果）
        slider_color = (0, 180, 255)
        pygame.draw.rect(self.screen, slider_color, 
                        (slider_x, scrollbar_y, slider_width, 12), border_radius=6)
        
        # 滑块内发光
        inner_slider = pygame.Rect(slider_x + 2, scrollbar_y + 2, 
                                 slider_width - 4, 8)
        pygame.draw.rect(self.screen, (100, 220, 255), inner_slider, border_radius=4)
        
        # 滚动条端点
        for x in [scrollbar_x, scrollbar_x + scrollbar_width]:
            pygame.draw.circle(self.screen, (0, 150, 220), (x, scrollbar_y + 6), 4)
    
    def create_scroll_buttons(self, total_towers):
        """创建科技风格滚动按钮"""
        class TechScrollButton:
            def __init__(self, x, y, width, height, text, font_manager):
                self.rect = pygame.Rect(x, y, width, height)
                self.text = text
                self.font_manager = font_manager
                self.hovered = False
                self.enabled = True
                self.pulse = 0
            
            def draw(self, surface):
                """绘制滚动按钮"""
                # 脉冲效果
                self.pulse = (self.pulse + 0.1) % (math.pi * 2)
                pulse_intensity = abs(math.sin(self.pulse)) * 0.3 + 0.7
                
                # 发光效果
                if self.hovered and self.enabled:
                    glow_surf = pygame.Surface((self.rect.width + 20, self.rect.height + 20), pygame.SRCALPHA)
                    pygame.draw.rect(glow_surf, (0, 150, 255, 80),
                                   pygame.Rect(10, 10, self.rect.width, self.rect.height),
                                   border_radius=10)
                    surface.blit(glow_surf, (self.rect.x - 10, self.rect.y - 10))
                
                # 按钮主体
                if not self.enabled:
                    base_color = (60, 65, 80)
                    border_color = (80, 85, 100)
                elif self.hovered:
                    base_color = (40, 100, 150)
                    border_color = (0, 200, 255)
                else:
                    base_color = (30, 40, 60)
                    border_color = (0, 150, 220)
                
                # 应用脉冲
                if self.enabled:
                    border_color = (
                        int(border_color[0] * pulse_intensity),
                        int(border_color[1] * pulse_intensity),
                        int(border_color[2] * pulse_intensity)
                    )
                
                pygame.draw.rect(surface, base_color, self.rect, border_radius=10)
                pygame.draw.rect(surface, border_color, self.rect, 3, border_radius=10)
                
                # 箭头
                arrow_color = (220, 240, 255) if self.enabled else (120, 130, 140)
                arrow_font = pygame.font.SysFont('Arial', 24, bold=True)
                arrow_text = arrow_font.render(self.text, True, arrow_color)
                arrow_rect = arrow_text.get_rect(center=self.rect.center)
                surface.blit(arrow_text, arrow_rect)
            
            def update_hover(self, mouse_pos):
                self.hovered = self.rect.collidepoint(mouse_pos) and self.enabled
            
            def is_clicked(self, event):
                return (event.type == pygame.MOUSEBUTTONDOWN and 
                        event.button == 1 and 
                        self.hovered and 
                        self.enabled)
        
        buttons = []
        
        if total_towers > self.visible_tower_count:
            # 左滚动按钮
            left_button = TechScrollButton(80, 280, 50, 50, "◀", self.font_manager)
            left_button.enabled = (self.scroll_offset > 0)
            buttons.append(left_button)
            
            # 右滚动按钮
            right_button = TechScrollButton(SCREEN_WIDTH - 130, 280, 50, 50, "▶", self.font_manager)
            right_button.enabled = (self.scroll_offset + self.visible_tower_count < total_towers)
            buttons.append(right_button)
        
        return buttons
    
    def create_game_over_buttons(self):
        """创建游戏结束按钮（为了兼容性）"""
        return self.create_control_buttons()
    
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
        """绘制科技风格操作提示"""
        hint_y = 610
        hints = [
            "CLICK ADJACENT TOWERS TO CONNECT LASERS",
            "LAST PLAYER TO MAKE A MOVE WINS THE GAME",
            "USE MOUSE WHEEL OR ARROW KEYS TO SCROLL",
            "CONNECTED TOWERS DISPLAY PLAYER COLORS"
        ]
        
        for i, hint in enumerate(hints):
            # 提示文字
            hint_text = self.font_manager.small.render(hint, True, (150, 200, 255))
            
            # 提示背景
            hint_bg = pygame.Rect(
                SCREEN_WIDTH//2 - hint_text.get_width()//2 - 10,
                hint_y + i * 22,
                hint_text.get_width() + 20,
                hint_text.get_height() + 4
            )
            
            pygame.draw.rect(self.screen, (20, 30, 50, 150), hint_bg, border_radius=6)
            pygame.draw.rect(self.screen, (0, 100, 180), hint_bg, 1, border_radius=6)
            
            self.screen.blit(hint_text, (SCREEN_WIDTH//2 - hint_text.get_width()//2, hint_y + 2 + i * 22))
    
    def _get_tower_owner(self, game_logic, tower_id):
        """获取炮塔的所有者"""
        for start_idx, end_idx, player in game_logic.lasers:
            if start_idx == tower_id or end_idx == tower_id:
                return player
        return None