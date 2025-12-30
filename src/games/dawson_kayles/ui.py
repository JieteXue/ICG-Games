"""
Dawson-Kayles Game UI Components - 添加提示功能
"""

import pygame
import math
import random
from utils.constants import *
from utils.helpers import wrap_text
from ui.components.input_box import InputBox  # 新增导入
from ui.components.scrollables import ScrollablePanel  # 新增导入

class TowerButton:
    """炮塔按钮类 - 完全兼容原始接口"""
    
    def __init__(self, x, y, width, height, tower_id, font_manager):
        self.rect = pygame.Rect(x, y, width, height)
        self.tower_id = tower_id
        self.font_manager = font_manager
        self.hovered = False
        self.selected = False
        self.enabled = True
        self.pulse_angle = random.uniform(0, math.pi * 2)
        
    def draw(self, surface, tower_state, player_owner=None, is_highlighted=False):
        """绘制炮塔 - 保持原始风格"""
        # 基础颜色
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
        
        # 绘制炮塔底座
        pygame.draw.rect(surface, base_color, self.rect, border_radius=8)
        pygame.draw.rect(surface, accent_color, self.rect, 3, border_radius=8)
        
        # 炮塔主体
        body_width = self.rect.width - 20
        body_height = 40
        body_rect = pygame.Rect(
            self.rect.centerx - body_width // 2,
            self.rect.top + 20,
            body_width,
            body_height
        )
        pygame.draw.rect(surface, base_color, body_rect)
        pygame.draw.rect(surface, accent_color, body_rect, 2)
        
        # 炮塔顶部
        top_radius = min(body_width, body_height) // 2 - 2  # 确保圆形适合矩形
        top_center = (body_rect.centerx, body_rect.centery)
        pygame.draw.circle(surface, accent_color, top_center, top_radius, 2)
        
        # 炮塔编号
        id_text = self.font_manager.small.render(str(self.tower_id), True, (220, 240, 255))
        text_pos = (self.rect.centerx - 5, self.rect.bottom - 25)
        surface.blit(id_text, text_pos)
        
        # 高亮显示可用移动
        if is_highlighted and tower_state == 1:
            highlight_rect = self.rect.inflate(12, 12)
            pygame.draw.rect(surface, (0, 255, 200, 100), highlight_rect, 3, border_radius=12)
    
    def update_hover(self, mouse_pos):
        """更新悬停状态"""
        self.hovered = self.rect.collidepoint(mouse_pos) and self.enabled
    
    def is_clicked(self, event):
        """检查是否被点击"""
        return (event.type == pygame.MOUSEBUTTONDOWN and 
                event.button == 1 and 
                self.hovered and 
                self.enabled)


class ScrollButton:
    """滚动按钮类 - 兼容Take Coins风格"""
    
    def __init__(self, x, y, width, height, text, font_manager):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font_manager = font_manager
        self.hovered = False
        self.enabled = True
    
    def draw(self, surface):
        """绘制滚动按钮"""
        if not self.enabled:
            return
            
        # 使用炮塔的颜色方案
        # 基础颜色：可用炮塔的基座颜色
        base_color = (30, 35, 50)          # 可用炮塔基座
        # 高亮颜色：激活炮塔的颜色
        accent_color = (0, 200, 255)       # 激活炮塔颜色
        
        # 根据悬停状态调整颜色
        if self.hovered:
            color = accent_color  # 悬停时使用激活颜色
            border_color = (255, 255, 255)  # 悬停时边框为白色，更明显
        else:
            color = base_color
            border_color = accent_color
        
        # 绘制按钮主体
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, border_color, self.rect, 2, border_radius=8)
        
        # 绘制箭头
        arrow_color = (255, 255, 255) if self.enabled else (150, 150, 150)
        arrow_font = pygame.font.SysFont('Arial', 24, bold=True)
        arrow_text = arrow_font.render(self.text, True, arrow_color)
        arrow_rect = arrow_text.get_rect(center=self.rect.center)
        surface.blit(arrow_text, arrow_rect)
        
        # 悬停效果
        if self.hovered and self.enabled:
            glow_rect = self.rect.inflate(6, 6)
            pygame.draw.rect(surface, (0, 150, 255, 50), glow_rect, 2, border_radius=10)
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
    """Dawson-Kayles游戏UI管理器 - 添加提示功能"""
    
    def __init__(self, screen, font_manager):
        self.screen = screen
        self.font_manager = font_manager
        self.scroll_offset = 0
        self.visible_tower_count = 8  # 保持与原始代码一致
        self.highlighted_towers = set()
        self.time = 0
        self.grid_offset = 0
        self.scroll_buttons = []  # 添加滚动按钮存储
        self.input_box = None  # 新增：输入框实例
        
        # 新增：提示功能属性
        self.is_hint_tooltip_visible = False  # 工具提示可见性
        self.hint_tooltip_text = ""
        self.hint_tooltip_pos = (0, 0)
        
        # 新增：提示窗口属性
        self.hint_window_visible = False
        self.hint_scrollable_panel = None
        self.hint_close_button = None
        self.hint_window_rect = None

    def draw_background(self):
        """绘制科技风格背景 - 保持原始风格"""
        self.screen.fill((5, 10, 20))
        self.time += 0.5
        self.grid_offset = (self.grid_offset + 0.3) % 40
        
        # 绘制动态网格
        grid_color = (20, 30, 50)
        for x in range(-40, SCREEN_WIDTH + 40, 40):
            x_pos = (x + self.grid_offset) % (SCREEN_WIDTH + 80) - 40
            pygame.draw.line(self.screen, grid_color, (x_pos, 0), (x_pos, SCREEN_HEIGHT), 1)
        
        for y in range(-40, SCREEN_HEIGHT + 40, 40):
            y_pos = (y + self.grid_offset) % (SCREEN_HEIGHT + 80) - 40
            pygame.draw.line(self.screen, grid_color, (0, y_pos), (SCREEN_WIDTH, y_pos), 1)
        
        # 中心动态网格线
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        pulse_width = abs(math.sin(self.time * 0.02)) * 20 + 5
        pygame.draw.line(self.screen, (30, 80, 120, 50), 
                        (center_x - 300, center_y),
                        (center_x + 300, center_y),
                        int(pulse_width))
        
        # 绘制星空效果
        for i in range(50):
            x = (i * 73) % SCREEN_WIDTH
            y = (i * 37) % SCREEN_HEIGHT
            size = (math.sin(self.time * 0.05 + i) + 1) * 0.5 + 0.5
            brightness = 150 + int(math.sin(self.time * 0.03 + i) * 50)
            pygame.draw.circle(self.screen, (brightness, brightness, brightness), 
                             (int(x), int(y)), int(size))
        
        # 绘制底部科技面板
        panel_height = 120
        panel_rect = pygame.Rect(0, SCREEN_HEIGHT - panel_height, SCREEN_WIDTH, panel_height)
        for i in range(panel_height):
            alpha = int(200 * (1 - i / panel_height))
            pygame.draw.line(self.screen, (10, 20, 40, alpha),
                           (0, SCREEN_HEIGHT - panel_height + i),
                           (SCREEN_WIDTH, SCREEN_HEIGHT - panel_height + i),
                           1)
    
    def draw_game_info(self, game_logic):
        """绘制游戏信息面板 - 保持原始布局"""
        # 顶部科技面板
        header_height = 200
        for i in range(header_height):
            alpha = int(180 * (1 - abs(i - header_height/2) / (header_height/2)))
            color = (15, 25, 40, alpha)
            pygame.draw.line(self.screen, color, (0, i), (SCREEN_WIDTH, i), 1)
        
        # 游戏标题（霓虹效果）
        title = self.font_manager.large.render("LASER DEFENSE SYSTEM", True, (0, 255, 220))
        subtitle = self.font_manager.medium.render("DAWSON-KAYLES PROTOCOL", True, (100, 200, 255))
        
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 15))
        self.screen.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, 55))
        
        # 游戏模式信息
        difficulty_names = ["EASY", "NORMAL", "HARD", "INSANE"]
        
        if game_logic.game_mode == "PVP":
            mode_text = "MODE: PLAYER VS PLAYER"
            mode_color = (0, 255, 150)
        else:
            mode_text = f"MODE: PLAYER VS AI - {difficulty_names[game_logic.difficulty-1]}"
            mode_color = (255, 150, 0)
        
        mode_info = self.font_manager.small.render(mode_text, True, mode_color)
        mode_bg = pygame.Rect(20, 165, mode_info.get_width() + 20, mode_info.get_height() + 8)
        pygame.draw.rect(self.screen, (20, 30, 50, 200), mode_bg, border_radius=6)
        pygame.draw.rect(self.screen, mode_color, mode_bg, 2, border_radius=6)
        self.screen.blit(mode_info, (30, 168))
        
        # 当前玩家信息
        player_colors = {
            "Player 1": (0, 255, 200),
            "Player 2": (255, 220, 50),
            "AI": (255, 100, 100)
        }
        
        player_color = player_colors.get(game_logic.current_player, (255, 255, 255))
        player_text = self.font_manager.small.render(f"ACTIVE: {game_logic.current_player}", True, player_color)
        player_bg = pygame.Rect(
            SCREEN_WIDTH - player_text.get_width() - 50,
            163,
            player_text.get_width() + 30,
            player_text.get_height() + 10
        )
        pygame.draw.rect(self.screen, (25, 35, 55), player_bg, border_radius=8)
        pygame.draw.rect(self.screen, player_color, player_bg, 3, border_radius=8)
        pygame.draw.circle(self.screen, player_color, 
                          (player_bg.left + 15, player_bg.centery), 4)
        self.screen.blit(player_text, (SCREEN_WIDTH - player_text.get_width() - 30, 168))
        
        # 游戏状态
        towers_remaining = sum(game_logic.towers)
        available_moves = len(game_logic.get_available_moves())
        
        status_text = f"TOWERS: {towers_remaining} | MOVES: {available_moves}"
        status = self.font_manager.large.render(status_text, True, (0, 220, 255))
        status_bg = pygame.Rect(
            SCREEN_WIDTH//2 - status.get_width()//2 - 15,
            90,
            status.get_width() + 30,
            status.get_height() + 10
        )
        pygame.draw.rect(self.screen, (0, 100, 150, 100), status_bg, border_radius=8)
        pygame.draw.rect(self.screen, (0, 200, 255), status_bg, 2, border_radius=8)
        self.screen.blit(status, (SCREEN_WIDTH//2 - status.get_width()//2, 95))
        
        # 游戏消息
        message_color = (WIN_COLOR if game_logic.game_over and game_logic.winner == "Player 1" 
                        else LOSE_COLOR if game_logic.game_over and game_logic.winner == "AI"
                        else (255, 220, 50) if game_logic.game_over and game_logic.winner == "Player 2"
                        else (180, 220, 255))
        
        message_lines = wrap_text(game_logic.message, self.font_manager.medium, SCREEN_WIDTH - 100)
        for i, line in enumerate(message_lines):
            message_text = self.font_manager.medium.render(line, True, message_color)
            self.screen.blit(message_text, (SCREEN_WIDTH//2 - message_text.get_width()//2, 130 + i * 25))
        
        # 胜负状态指示器
        if not game_logic.game_over:
            game_state = "WINNING POSITION" if game_logic.judge_win() else "LOSING POSITION"
            state_color = WIN_COLOR if game_logic.judge_win() else LOSE_COLOR
            
            state_text = self.font_manager.small.render(game_state, True, state_color)
            state_bg = pygame.Rect(
                SCREEN_WIDTH//2 - state_text.get_width()//2 - 10,
                175,
                state_text.get_width() + 20,
                state_text.get_height() + 8
            )
            pygame.draw.rect(self.screen, (30, 40, 65), state_bg, border_radius=8)
            pygame.draw.rect(self.screen, state_color, state_bg, 3, border_radius=8)
            self.screen.blit(state_text, (SCREEN_WIDTH//2 - state_text.get_width()//2, 178))
    
    def draw_towers_and_lasers(self, game_logic, tower_buttons):
        """绘制炮塔和激光 - 保持原始功能"""
        # 先绘制激光
        self._draw_all_lasers(game_logic, tower_buttons)
        
        # 然后绘制炮塔
        for button in tower_buttons:
            owner = self._get_tower_owner(game_logic, button.tower_id)
            is_highlighted = button.tower_id in self.highlighted_towers
            button.draw(self.screen, game_logic.towers[button.tower_id], owner, is_highlighted)

        # 绘制滚动按钮（如果存在）
        self.draw_scroll_buttons()
    
    def _draw_all_lasers(self, game_logic, tower_buttons):
        """绘制所有激光连接"""
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
        
        # 绘制激光
        pygame.draw.line(self.screen, laser_color, (start_x, start_y), (end_x, end_y), 4)
        
        # 激光端点
        pygame.draw.circle(self.screen, laser_color, (start_x, start_y), 6)
        pygame.draw.circle(self.screen, laser_color, (end_x, end_y), 6)
    
    def draw_scrollbar(self, total_towers):
        """绘制滚动条 - 保持原始功能"""
        if total_towers <= self.visible_tower_count:
            return
        
        scrollbar_width = SCREEN_WIDTH - 100
        scrollbar_x = 50
        scrollbar_y = 450
        
        # 滚动条背景
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
        
        # 滑块
        slider_color = (0, 180, 255)
        pygame.draw.rect(self.screen, slider_color, 
                        (slider_x, scrollbar_y, slider_width, 12), border_radius=6)
        
        # 滚动条端点
        for x in [scrollbar_x, scrollbar_x + scrollbar_width]:
            pygame.draw.circle(self.screen, (0, 150, 220), (x, scrollbar_y + 6), 4)

        for button in self.scroll_buttons:
            button.draw(self.screen)
    
    def draw_control_panel(self, game_logic, buttons=None):  # 修改：添加buttons参数
        """绘制控制面板 - 添加提示按钮"""
        # 将控制面板上移，避免重叠
        control_y = 520  # 从560改为520，上移40像素
        control_width = 500
        control_x = (SCREEN_WIDTH - control_width) // 2
        
        # 控制面板背景（仪表盘风格）
        control_bg = pygame.Rect(control_x - 20, control_y - 15, control_width + 40, 100)
        pygame.draw.rect(self.screen, (20, 30, 50, 180), control_bg, border_radius=12)
        
        # 仪表盘边框
        pygame.draw.rect(self.screen, (0, 200, 255), control_bg, 3, border_radius=12)
        
        # 仪表盘标题 - 位置相应上移
        panel_title = self.font_manager.medium.render("LASER CONTROL PANEL", True, (0, 255, 220))
        self.screen.blit(panel_title, (SCREEN_WIDTH//2 - panel_title.get_width()//2, control_y - 5))
        
        # 获取可用的最大i值
        max_i = len(game_logic.towers) - 2  # i的最大值是n-2
        
        if max_i >= 0 and not game_logic.game_over:
            # 输入框标签（简洁版）
            input_label = self.font_manager.small.render(f"Connect i & i+1 (0 to {max_i}):", 
                                                        True, (180, 220, 255))
            self.screen.blit(input_label, (control_x, control_y + 20))
            
            # 创建或更新输入框
            input_box_width = 80  # 减小宽度
            input_box_height = 40
            input_box_x = control_x + input_label.get_width() + 10
            input_box_y = control_y + 15
            
            if self.input_box is None:
                # 创建输入框
                self.input_box = InputBox(
                    input_box_x, input_box_y,
                    input_box_width, input_box_height,
                    self.font_manager,
                    initial_value="0",
                    max_length=3,
                    validation_type="dawson_kayles",
                    is_numeric=True
                )
            
            # 设置游戏参数
            if self.input_box:
                self.input_box.rect = pygame.Rect(input_box_x, input_box_y, input_box_width, input_box_height)
                self.input_box.set_game_params({
                    'towers': game_logic.towers,
                    'available_moves': game_logic.get_available_moves()
                })
                
            # 绘制输入框
            self.input_box.draw(self.screen)
            
            # 连接按钮
            connect_button_rect = pygame.Rect(input_box_x + input_box_width + 15, input_box_y, 80, input_box_height)
            
            # 按钮背景（科技风格）
            mouse_pos = pygame.mouse.get_pos()
            button_hovered = connect_button_rect.collidepoint(mouse_pos)
            button_color = (0, 150, 220) if button_hovered else (0, 100, 180)
            pygame.draw.rect(self.screen, button_color, connect_button_rect, border_radius=8)
            pygame.draw.rect(self.screen, (0, 255, 220), connect_button_rect, 2, border_radius=8)
            
            # 按钮文字
            connect_text = self.font_manager.small.render("GO", True, (255, 255, 255))  # 改为"GO"
            self.screen.blit(connect_text, (connect_button_rect.centerx - connect_text.get_width()//2, 
                                        connect_button_rect.centery - connect_text.get_height()//2))
            
            # 仪表盘装饰（LED灯间距调整）
            self._draw_control_panel_decoration(control_bg)
            
            # 快捷方式提示（位置相应上移）
            shortcut_hint = self.font_manager.small.render("Press 'C' for quick connect", True, (100, 180, 255))
            self.screen.blit(shortcut_hint, (control_bg.centerx - shortcut_hint.get_width()//2, control_y + 65))
            
            # 新增：绘制提示按钮（如果buttons参数提供）
            if buttons and "hint" in buttons:
                hint_button = buttons["hint"]
                # 设置提示按钮位置（在控制面板右侧） - 位置相应上移
                hint_button.rect = pygame.Rect(
                    control_bg.right + 20,
                    control_bg.centery - 25,
                    50, 50
                )
                hint_button.draw(self.screen)
                
                # 绘制提示按钮的悬停工具提示
                if hint_button.hovered and game_logic.winning_hints_enabled and not self.hint_window_visible:
                    self.show_hint_tooltip("Click for winning hints", pygame.mouse.get_pos())
                elif not hint_button.hovered and self.is_hint_tooltip_visible:
                    # 如果鼠标不在按钮上，但工具提示仍显示，则隐藏它
                    self.hide_hint_tooltip()
            
            # 新增：绘制提示工具提示（如果可见）
            if self.is_hint_tooltip_visible and self.hint_tooltip_text:
                self._draw_hint_tooltip()
            
            # 新增：绘制提示窗口（如果可见）
            if self.hint_window_visible:
                self._draw_hint_window()
            
            return connect_button_rect
        else:
            # 没有可用移动或游戏已结束
            if game_logic.game_over:
                status_text = self.font_manager.small.render("GAME OVER", True, (255, 100, 100))
            else:
                status_text = self.font_manager.small.render("NO MOVES LEFT", True, (255, 100, 100))
            self.screen.blit(status_text, (control_bg.centerx - status_text.get_width()//2, control_y + 20))
            
            # 仪表盘装饰
            self._draw_control_panel_decoration(control_bg)
            
            # 新增：绘制提示按钮（如果buttons参数提供且游戏结束）
            if buttons and "hint" in buttons and game_logic.game_over:
                hint_button = buttons["hint"]
                hint_button.rect = pygame.Rect(
                    control_bg.right + 20,
                    control_bg.centery - 25,
                    50, 50
                )
                hint_button.draw(self.screen)
            
            return None

    def _draw_control_panel_decoration(self, panel_rect):
        """绘制控制面板装饰 - 调整LED灯间距"""
        # 仪表盘角点装饰
        corner_size = 12
        corners = [
            (panel_rect.left, panel_rect.top),  # 左上
            (panel_rect.right - corner_size, panel_rect.top),  # 右上
            (panel_rect.left, panel_rect.bottom - corner_size),  # 左下
            (panel_rect.right - corner_size, panel_rect.bottom - corner_size)  # 右下
        ]
        
        for corner in corners:
            corner_rect = pygame.Rect(corner[0], corner[1], corner_size, corner_size)
            pygame.draw.rect(self.screen, (0, 200, 255), corner_rect, 2)
    
    def create_control_buttons(self):
        """创建控制按钮 - 添加提示按钮"""
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
            
            def update_hover(self, mouse_pos):
                self.hovered = self.rect.collidepoint(mouse_pos) and self.enabled
            
            def is_clicked(self, event):
                return (event.type == pygame.MOUSEBUTTONDOWN and 
                        event.button == 1 and 
                        self.hovered and 
                        self.enabled)
            
            def draw(self, surface):
                # 按钮阴影
                shadow_rect = self.rect.move(2, 2)
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
                pygame.draw.rect(surface, border_color, self.rect, 3, 
                               border_radius=self.corner_radius)
                
                # 图标或文字
                if self.icon:
                    self._draw_tech_icon(surface)
                else:
                    self._draw_tech_text(surface)
            
            def _draw_tech_icon(self, surface):
                icon_color = (220, 240, 255) if self.enabled else (120, 130, 140)
                
                if self.icon == 'back':
                    points = [
                        (self.rect.centerx - 5, self.rect.centery),
                        (self.rect.centerx + 5, self.rect.centery - 7),
                        (self.rect.centerx + 5, self.rect.centery + 7)
                    ]
                    pygame.draw.polygon(surface, icon_color, points)
                    pygame.draw.line(surface, icon_color,
                                   (self.rect.centerx, self.rect.centery),
                                   (self.rect.centerx - 3, self.rect.centery),
                                   3)
                
                elif self.icon == 'home':
                    roof_points = [
                        (self.rect.centerx, self.rect.centery - 8),
                        (self.rect.centerx - 8, self.rect.centery),
                        (self.rect.centerx + 8, self.rect.centery)
                    ]
                    pygame.draw.polygon(surface, icon_color, roof_points)
                    house_rect = pygame.Rect(
                        self.rect.centerx - 6,
                        self.rect.centery,
                        12,
                        8
                    )
                    pygame.draw.rect(surface, icon_color, house_rect, 2)
                    pygame.draw.rect(surface, icon_color,
                                   (self.rect.centerx - 2, self.rect.centery + 2, 4, 6))
                
                elif self.icon == 'refresh':
                    center = self.rect.center
                    radius = 10
                    pygame.draw.circle(surface, icon_color, center, radius, 2)
                    arrow_points = [
                        (center[0] + radius - 7, center[1] - 3),
                        (center[0] + radius, center[1]),
                        (center[0] + radius, center[1] - 8)
                    ]
                    pygame.draw.polygon(surface, icon_color, arrow_points)
                
                elif self.icon == 'hint':  # 新增：提示图标
                    # 绘制灯泡图标
                    center = (self.rect.centerx, self.rect.centery)
                    
                    # 灯泡主体
                    pygame.draw.circle(surface, (255, 255, 180), center, 15)
                    pygame.draw.circle(surface, (255, 255, 100), center, 15, 2)
                    
                    # 灯泡底部
                    bottom_rect = pygame.Rect(
                        center[0] - 8,
                        center[1] + 10,
                        16, 6
                    )
                    pygame.draw.rect(surface, (200, 180, 100), bottom_rect, border_radius=3)
                    
                    # 问号
                    font = pygame.font.SysFont('Arial', 16, bold=True)
                    q_text = font.render("?", True, (60, 60, 80))
                    text_rect = q_text.get_rect(center=center)
                    surface.blit(q_text, text_rect)
                    
                    # 灯泡光晕效果（如果启用）
                    if self.enabled:
                        for i in range(3):
                            radius = 18 + i * 4
                            alpha = 50 - i * 15
                            s = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
                            pygame.draw.circle(s, (255, 255, 150, alpha), (radius, radius), radius)
                            surface.blit(s, (center[0] - radius, center[1] - radius))
            
            def _draw_tech_text(self, surface):
                text_color = (240, 250, 255) if self.enabled else (120, 130, 140)
                text_surface = self.font_manager.small.render(self.text, True, text_color)
                text_rect = text_surface.get_rect(center=self.rect.center)
                surface.blit(text_surface, text_rect)
        
        nav_button_size = 55
        
        # 将"restart"按钮的位置也上移，与控制面板保持一致
        buttons = {
            "back": TechButton(25, 25, nav_button_size, nav_button_size, "", 
                              self.font_manager, icon='back'),
            "home": TechButton(25 + nav_button_size + 15, 25, nav_button_size, nav_button_size, "", 
                               self.font_manager, icon='home'),
            "restart": TechButton(SCREEN_WIDTH//2 - 120, 520, 240, 60, "NEW GAME",  # 从560改为520
                                self.font_manager),
            "refresh": TechButton(SCREEN_WIDTH - 25 - nav_button_size, 25, 
                                nav_button_size, nav_button_size, "", 
                                self.font_manager, icon='refresh'),
            "hint": TechButton(0, 0, 50, 50, "",  # 位置将在draw_control_panel中设置
                              self.font_manager, icon='hint', tooltip="Click for winning hints")  # 新增：提示按钮
        }
        
        return buttons
    
    def create_game_over_buttons(self):
        """创建游戏结束按钮 - 保持兼容性"""
        return self.create_control_buttons()
    
    def create_tower_buttons(self, num_towers):
        """创建炮塔按钮 - 保持原始逻辑"""
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
    
    def create_scroll_buttons(self, total_towers):
        """创建滚动按钮 - 新增功能：左右滑动按钮"""
        buttons = []
        
        # 只有当炮塔数量超过可见数量时才显示滚动按钮
        if total_towers > self.visible_tower_count:
            # 左滚动按钮 - 位于炮塔区域左侧
            left_button = ScrollButton(50, 320, 50, 50, "<", self.font_manager)
            left_button.enabled = (self.scroll_offset > 0)
            buttons.append(left_button)
            
            # 右滚动按钮 - 位于炮塔区域右侧
            right_button = ScrollButton(SCREEN_WIDTH - 100, 320, 50, 50, ">", self.font_manager)
            right_button.enabled = (self.scroll_offset + self.visible_tower_count < total_towers)
            buttons.append(right_button)
        
        # 存储到实例变量
        self.scroll_buttons = buttons
        return buttons
    
    def draw_scroll_buttons(self):
        """绘制滚动按钮"""
        for button in self.scroll_buttons:
            button.draw(self.screen)
    
    def scroll_left(self, total_towers):
        """向左滚动 - 保持原始逻辑"""
        if self.scroll_offset > 0:
            self.scroll_offset -= 1
    
    def scroll_right(self, total_towers):
        """向右滚动 - 保持原始逻辑"""
        if self.scroll_offset + self.visible_tower_count < total_towers:
            self.scroll_offset += 1
    
    def handle_mouse_wheel(self, event, total_towers):
        """处理鼠标滚轮滚动 - 保持原始逻辑"""
        if event.type == pygame.MOUSEWHEEL:
            if event.y > 0:
                self.scroll_left(total_towers)
            elif event.y < 0:
                self.scroll_right(total_towers)
            return True
        return False
    
    def update_highlighted_towers(self, available_moves, selected_tower):
        """更新高亮显示的炮塔 - 保持原始逻辑"""
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
    
    def _get_tower_owner(self, game_logic, tower_id):
        """获取炮塔的所有者 - 保持原始逻辑"""
        for start_idx, end_idx, player in game_logic.lasers:
            if start_idx == tower_id or end_idx == tower_id:
                return player
        return None
    
    def get_input_box(self):
        """获取输入框实例"""
        return self.input_box
    
    def update_input_box(self):
        """更新输入框状态"""
        if self.input_box:
            self.input_box.update()
    
    # ========== 新增：提示功能相关方法 ==========
    
    def _draw_hint_tooltip(self):
        """绘制提示工具提示框"""
        if not self.hint_tooltip_text:
            return
        
        # 分割文本为多行
        max_width = 200
        lines = []
        words = self.hint_tooltip_text.split(' ')
        current_line = ""
        
        for word in words:
            test_line = f"{current_line} {word}".strip()
            test_width = self.font_manager.small.size(test_line)[0]
            
            if test_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        # 计算工具提示框的尺寸
        line_height = 18
        padding = 8
        tooltip_width = max_width + 2 * padding
        tooltip_height = len(lines) * line_height + 2 * padding
        
        # 定位工具提示框（确保在屏幕内）
        tooltip_x = self.hint_tooltip_pos[0]
        tooltip_y = self.hint_tooltip_pos[1] - tooltip_height - 10
        
        # 如果超出屏幕顶部，显示在下方
        if tooltip_y < 50:
            tooltip_y = self.hint_tooltip_pos[1] + 10
        
        # 如果超出屏幕右侧，向左偏移
        if tooltip_x + tooltip_width > SCREEN_WIDTH - 20:
            tooltip_x = SCREEN_WIDTH - tooltip_width - 20
        
        # 绘制工具提示框背景
        tooltip_rect = pygame.Rect(tooltip_x, tooltip_y, tooltip_width, tooltip_height)
        pygame.draw.rect(self.screen, (20, 40, 70, 230), tooltip_rect, border_radius=8)
        pygame.draw.rect(self.screen, (0, 200, 255), tooltip_rect, 2, border_radius=8)
        
        # 绘制文本行
        for i, line in enumerate(lines):
            line_text = self.font_manager.small.render(line, True, (220, 240, 255))
            self.screen.blit(line_text, (tooltip_x + padding, 
                                       tooltip_y + padding + i * line_height))
    
    def show_hint_tooltip(self, text, pos):
        """显示提示工具提示"""
        self.is_hint_tooltip_visible = True
        self.hint_tooltip_text = text
        self.hint_tooltip_pos = pos
    
    def hide_hint_tooltip(self):
        """隐藏提示工具提示"""
        self.is_hint_tooltip_visible = False
        self.hint_tooltip_text = ""
    
    def _draw_hint_window(self):
        """绘制提示窗口"""
        if not self.hint_window_visible:
            return
        
        # 定义窗口大小和位置
        window_width = 500  # 增加宽度以容纳更多内容
        window_height = 400  # 增加高度
        window_x = (SCREEN_WIDTH - window_width) // 2  # 居中显示
        window_y = (SCREEN_HEIGHT - window_height) // 2
        self.hint_window_rect = pygame.Rect(window_x, window_y, window_width, window_height)
        
        # 绘制窗口背景（带透明度的深色背景）
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        
        # 绘制窗口主体
        pygame.draw.rect(self.screen, (15, 25, 40), self.hint_window_rect, border_radius=12)
        pygame.draw.rect(self.screen, (0, 200, 255), self.hint_window_rect, 3, border_radius=12)
        
        # 绘制窗口标题
        title_text = self.font_manager.large.render("WINNING HINT", True, (0, 255, 220))
        title_rect = title_text.get_rect(center=(window_x + window_width//2, window_y + 30))
        self.screen.blit(title_text, title_rect)
        
        # 绘制分隔线
        pygame.draw.line(self.screen, (0, 180, 220),
                        (window_x + 20, window_y + 60),
                        (window_x + window_width - 20, window_y + 60), 2)
        
        # 绘制可滚动面板（如果内容存在）
        if self.hint_scrollable_panel:
            self.hint_scrollable_panel.draw(self.screen)
        
        # 绘制关闭按钮（如果尚未创建）
        if self.hint_close_button is None:
            close_button_rect = pygame.Rect(
                window_x + window_width - 40,
                window_y + 15,
                25, 25
            )
            
            # 使用内联按钮类
            class SimpleButton:
                def __init__(self, rect, text="×"):
                    self.rect = rect
                    self.text = text
                    self.hovered = False
                
                def update_hover(self, mouse_pos):
                    self.hovered = self.rect.collidepoint(mouse_pos)
                
                def draw(self, screen):
                    color = (255, 100, 100) if self.hovered else (200, 80, 80)
                    pygame.draw.rect(screen, color, self.rect, border_radius=4)
                    pygame.draw.rect(screen, (255, 200, 200), self.rect, 1, border_radius=4)
                    
                    font = pygame.font.SysFont('Arial', 20, bold=True)
                    text_surface = font.render(self.text, True, (255, 255, 255))
                    text_rect = text_surface.get_rect(center=self.rect.center)
                    screen.blit(text_surface, text_rect)
            
            self.hint_close_button = SimpleButton(close_button_rect)
        
        # 绘制关闭按钮
        self.hint_close_button.draw(self.screen)
        
        # 绘制关闭提示
        close_hint = self.font_manager.small.render("Press ESC or click X to close", True, (180, 200, 220))
        close_hint_rect = close_hint.get_rect(center=(window_x + window_width//2, window_y + window_height - 20))
        self.screen.blit(close_hint, close_hint_rect)
    
    def show_hint_window(self, hint_text):
        """显示提示窗口"""
        # 创建或重置滚动面板
        window_width = 500
        window_height = 400
        window_x = (SCREEN_WIDTH - window_width) // 2
        window_y = (SCREEN_HEIGHT - window_height) // 2
        
        # 创建可滚动面板
        self.hint_scrollable_panel = ScrollablePanel(
            window_x + 15,  # 内边距
            window_y + 70,  # 标题栏下面
            window_width - 30,  # 减去内边距
            window_height - 100,  # 减去标题栏和按钮高度
            self.font_manager,
            bg_color=(25, 35, 55, 240)
        )
        
        # 分割文本并添加到面板
        # 首先按换行符分割
        paragraphs = hint_text.split('\n')
        
        for para in paragraphs:
            if para.strip():  # 非空段落
                # 再按空格分词，然后按面板宽度自动换行
                words = para.split()
                current_line = ""
                
                for word in words:
                    test_line = f"{current_line} {word}".strip()
                    
                    # 检查测试行的宽度是否超过面板宽度（减去边距）
                    if self.font_manager.small.size(test_line)[0] < (window_width - 40):
                        current_line = test_line
                    else:
                        # 如果超过宽度，添加当前行，开始新行
                        if current_line:
                            self.hint_scrollable_panel.add_line(current_line, (220, 240, 255), 'small')
                        current_line = word
                
                # 添加最后一行
                if current_line:
                    self.hint_scrollable_panel.add_line(current_line, (220, 240, 255), 'small')
                
                # 段落后添加空行
                self.hint_scrollable_panel.add_spacing(6)
            else:
                # 空段落作为更大间距
                self.hint_scrollable_panel.add_spacing(10)
        
        # 显示窗口
        self.hint_window_visible = True
        self.hide_hint_tooltip()  # 隐藏原来的工具提示
    
    def close_hint_window(self):
        """关闭提示窗口"""
        self.hint_window_visible = False
        self.hint_scrollable_panel = None
    
    def handle_hint_window_events(self, event, mouse_pos):
        """处理提示窗口事件"""
        if not self.hint_window_visible:
            return False
        
        # 更新关闭按钮的悬停状态
        if self.hint_close_button:
            self.hint_close_button.update_hover(mouse_pos)
        
        # 处理鼠标点击
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # 检查是否点击了关闭按钮
            if self.hint_close_button and self.hint_close_button.hovered:
                self.close_hint_window()
                return True
            
            # 检查是否点击了窗口外部（关闭窗口）
            if self.hint_window_rect and not self.hint_window_rect.collidepoint(mouse_pos):
                self.close_hint_window()
                return True
        
        # 处理滚动面板事件
        if self.hint_scrollable_panel:
            if self.hint_scrollable_panel.handle_event(event):
                return True
        
        # 处理键盘事件
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:  # ESC键关闭窗口
                self.close_hint_window()
                return True
        
        return False
    
    def update_hint_tooltip(self, mouse_pos):
        """更新提示工具提示状态"""
        # 检查是否需要隐藏提示
        if self.is_hint_tooltip_visible:
            # 如果鼠标移动了，可能需要更新提示位置
            self.hint_tooltip_pos = mouse_pos
            
            # 添加：如果提示窗口已经打开，则隐藏工具提示
            if self.hint_window_visible:
                self.hide_hint_tooltip()
    
    def update_hint_buttons(self, game_logic, mouse_pos):
        """更新提示按钮状态"""
        # 这个方法将在game.py中调用
        pass