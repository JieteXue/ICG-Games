"""
Split Cards Game UI Components
神秘魔术风格的卡牌分割游戏界面
"""

import pygame
import math
import random
from typing import List, Dict, Tuple, Optional
from ui.buttons import Button
from utils.constants import *
from utils.helpers import wrap_text

class MagicCard:
    """魔法卡牌组件"""
    
    def __init__(self, x: int, y: int, card_count: int, pile_index: int, font_manager, is_selected=False):
        self.x = x
        self.y = y
        self.card_count = card_count
        self.pile_index = pile_index
        self.font_manager = font_manager
        self.hovered = False
        self.selected = is_selected  # 添加选中状态参数
        self.sparkle_timer = 0
        self.glow_intensity = 0
        self.glow_direction = 1
        
        # 卡牌尺寸
        self.width = 80
        self.height = 120
        self.spacing = 10
        
        # 颜色设置（神秘紫色系）
        self.colors = {
            'normal': (80, 40, 120),      # 深紫色
            'highlight': (120, 60, 180),   # 亮紫色
            'selected': (200, 100, 255),   # 选中紫色 - 更亮
            'glow': (180, 100, 255, 50),   # 发光效果
            'border': (200, 140, 255),     # 边框
            'text': (220, 180, 255)        # 文字
        }
    
    def update(self):
        """更新动画效果"""
        # 更新闪光效果
        self.sparkle_timer = (self.sparkle_timer + 1) % 60
        
        # 更新发光强度
        self.glow_intensity += 0.1 * self.glow_direction
        if self.glow_intensity >= 1.0:
            self.glow_intensity = 1.0
            self.glow_direction = -1
        elif self.glow_intensity <= 0.3:
            self.glow_intensity = 0.3
            self.glow_direction = 1
    
    def draw(self, surface):
        """绘制卡牌堆"""
        # 计算实际绘制位置
        draw_x = self.x - self.width // 2
        draw_y = self.y - self.height // 2
        
        # 绘制卡牌阴影
        shadow_offset = 5
        shadow_rect = pygame.Rect(
            draw_x + shadow_offset,
            draw_y + shadow_offset,
            self.width,
            self.height
        )
        pygame.draw.rect(surface, (20, 10, 40), shadow_rect, border_radius=12)
        
        # 确定卡牌颜色 - 优先显示选中状态
        if self.selected:
            base_color = self.colors['selected']
            # 选中状态有更强的发光效果
            glow_surf = pygame.Surface((self.width + 30, self.height + 30), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*self.colors['selected'][:3], 80), 
                            (15, 15, self.width, self.height), border_radius=12)
            surface.blit(glow_surf, (draw_x - 15, draw_y - 15))
        elif self.hovered:
            base_color = self.colors['highlight']
        else:
            base_color = self.colors['normal']
        
        # 绘制卡牌
        card_rect = pygame.Rect(draw_x, draw_y, self.width, self.height)
        pygame.draw.rect(surface, base_color, card_rect, border_radius=12)
        
        # 绘制边框 - 选中状态有更粗的边框
        border_width = 4 if self.selected else 3
        border_color = self.colors['border']
        if self.selected:
            border_color = (255, 200, 255)  # 选中状态使用更亮的边框
        pygame.draw.rect(surface, border_color, card_rect, border_width, border_radius=12)
        
        # 绘制发光效果（非选中状态也有，但更弱）
        if not self.selected and (self.hovered or self.card_count > 0):
            glow_alpha = int(50 * self.glow_intensity)
            glow_surf = pygame.Surface((self.width + 10, self.height + 10), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*self.colors['glow'][:3], glow_alpha), 
                            (5, 5, self.width, self.height), border_radius=12)
            surface.blit(glow_surf, (draw_x - 5, draw_y - 5))
        
        # 绘制卡牌数量（堆叠效果）- 如果牌数为0，不绘制卡牌堆叠
        if self.card_count > 0:
            max_visible = min(self.card_count, 5)
            for i in range(max_visible):
                offset_x = random.randint(-3, 3) if i > 0 else 0
                offset_y = i * 3
                
                # 绘制单个卡牌轮廓
                single_card_rect = pygame.Rect(
                    draw_x + offset_x,
                    draw_y + offset_y,
                    self.width,
                    self.height
                )
                pygame.draw.rect(surface, (40, 20, 80), single_card_rect, 1, border_radius=12)
        else:
            # 牌堆为空，绘制一个空的卡牌轮廓
            empty_color = (60, 40, 80, 150)  # 半透明的空牌堆颜色
            empty_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.rect(empty_surf, empty_color, (0, 0, self.width, self.height), border_radius=12)
            pygame.draw.rect(empty_surf, (100, 80, 120), (0, 0, self.width, self.height), 2, border_radius=12)
            surface.blit(empty_surf, (draw_x, draw_y))
            
            # 绘制"空"字
            empty_text = self.font_manager.small.render("Empty", True, (150, 120, 180))
            empty_rect = empty_text.get_rect(center=(self.x, self.y))
            surface.blit(empty_text, empty_rect)
            return  # 空的牌堆不需要绘制数量和闪光效果
        
        # 绘制牌堆编号
        pile_text = self.font_manager.small.render(f"Pile {self.pile_index + 1}", True, self.colors['text'])
        text_x = self.x - pile_text.get_width() // 2
        text_y = draw_y + self.height + 5
        surface.blit(pile_text, (text_x, text_y))
        
        # 绘制牌数
        count_text = self.font_manager.large.render(str(self.card_count), True, self.colors['text'])
        count_shadow = self.font_manager.large.render(str(self.card_count), True, (40, 20, 80))
        
        # 文字阴影
        surface.blit(count_shadow, (self.x - count_text.get_width()//2 + 2, self.y - count_text.get_height()//2 + 2))
        surface.blit(count_text, (self.x - count_text.get_width()//2, self.y - count_text.get_height()//2))
        
        # 绘制闪光效果
        if self.sparkle_timer < 15 and self.card_count > 0:
            sparkle_size = 4
            sparkle_x = draw_x + random.randint(10, self.width - 10)
            sparkle_y = draw_y + random.randint(10, self.height - 10)
            pygame.draw.circle(surface, (255, 255, 200), (sparkle_x, sparkle_y), sparkle_size)
    
    def update_hover(self, mouse_pos: Tuple[int, int]):
        """更新悬停状态"""
        draw_x = self.x - self.width // 2
        draw_y = self.y - self.height // 2
        card_rect = pygame.Rect(draw_x, draw_y, self.width, self.height)
        self.hovered = card_rect.collidepoint(mouse_pos)
    
    def is_clicked(self, event) -> bool:
        """检查是否被点击"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            draw_x = self.x - self.width // 2
            draw_y = self.y - self.height // 2
            card_rect = pygame.Rect(draw_x, draw_y, self.width, self.height)
            return card_rect.collidepoint(event.pos)
        return False

class MagicEffect:
    """魔法效果动画"""
    
    def __init__(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int], effect_type: str = "sparkle"):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.effect_type = effect_type
        self.progress = 0.0
        self.speed = 0.02
        self.active = True
        
        # 效果参数
        self.particles = []
        if effect_type == "sparkle":
            self._create_sparkle_particles()
        elif effect_type == "beam":
            self._create_beam_particles()
    
    def _create_sparkle_particles(self):
        """创建闪光粒子"""
        for _ in range(20):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 5)
            size = random.uniform(2, 4)
            lifetime = random.uniform(30, 60)
            
            self.particles.append({
                'x': self.start_pos[0],
                'y': self.start_pos[1],
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'size': size,
                'lifetime': lifetime,
                'max_lifetime': lifetime,
                'color': (random.randint(200, 255), random.randint(200, 255), random.randint(100, 200))
            })
    
    def _create_beam_particles(self):
        """创建光束粒子"""
        for _ in range(30):
            t = random.uniform(0, 1)
            x = self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * t
            y = self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * t
            
            angle = math.atan2(self.end_pos[1] - self.start_pos[1], 
                              self.end_pos[0] - self.start_pos[0])
            offset_angle = angle + random.uniform(-0.2, 0.2)
            speed = random.uniform(1, 3)
            lifetime = random.uniform(20, 40)
            
            self.particles.append({
                'x': x,
                'y': y,
                'vx': math.cos(offset_angle) * speed,
                'vy': math.sin(offset_angle) * speed,
                'size': random.uniform(3, 6),
                'lifetime': lifetime,
                'max_lifetime': lifetime,
                'color': (random.randint(150, 255), random.randint(100, 200), random.randint(200, 255))
            })
    
    def update(self):
        """更新效果"""
        self.progress += self.speed
        
        # 更新粒子
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['lifetime'] -= 1
            
            if particle['lifetime'] <= 0:
                self.particles.remove(particle)
        
        # 检查效果是否结束
        if self.progress >= 1.0 and not self.particles:
            self.active = False
    
    def draw(self, surface):
        """绘制效果"""
        # 绘制轨迹线（对于光束效果）
        if self.effect_type == "beam":
            alpha = int(255 * (1 - self.progress))
            points = []
            for i in range(10):
                t = i / 9
                x = self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * t
                y = self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * t
                points.append((int(x), int(y)))
            
            if len(points) >= 2:
                pygame.draw.lines(surface, (200, 150, 255, alpha), False, points, 3)
        
        # 绘制粒子
        for particle in self.particles:
            alpha = int(255 * (particle['lifetime'] / particle['max_lifetime']))
            color_with_alpha = (*particle['color'], alpha)
            
            particle_surf = pygame.Surface((int(particle['size'] * 2), int(particle['size'] * 2)), pygame.SRCALPHA)
            pygame.draw.circle(particle_surf, color_with_alpha, 
                              (int(particle['size']), int(particle['size'])), int(particle['size']))
            surface.blit(particle_surf, (int(particle['x'] - particle['size']), int(particle['y'] - particle['size'])))

class SplitCardsUI:
    """Split Cards游戏UI管理器"""
    
    def __init__(self, screen, font_manager):
        self.screen = screen
        self.font_manager = font_manager
        
        # UI状态
        self.selected_pile = None
        self.selected_action = None  # 'take' 或 'split'
        self.highlighted_piles = set()
        self.magic_effects = []
        self.max_effects = 10  # 最大同时显示的效果数量
        
        # 颜色方案（神秘魔术风格）
        self.colors = {
            'background': (15, 10, 30),      # 深紫色背景
            'grid': (30, 20, 50),           # 网格线
            'title': (200, 180, 255),       # 标题
            'accent': (160, 100, 220),      # 强调色
            'player1': (100, 200, 255),     # 玩家1 - 蓝色
            'player2': (255, 100, 150),     # 玩家2/AI - 粉色
            'win': (100, 255, 150),         # 胜利色
            'lose': (255, 100, 100),        # 失败色
            'hint': (180, 160, 220)         # 提示色
        }
    
    def add_magic_effect(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int], effect_type: str = "sparkle"):
        """添加魔法效果"""
        # 清理旧效果（移除不活跃的）
        self._cleanup_effects()
        
        # 如果效果数量过多，移除最早的效果
        if len(self.magic_effects) >= self.max_effects:
            self.magic_effects.pop(0)
        
        effect = MagicEffect(start_pos, end_pos, effect_type)
        self.magic_effects.append(effect)
    
    def _cleanup_effects(self):
        """清理不活跃的魔法效果"""
        # 移除不活跃的效果
        self.magic_effects = [effect for effect in self.magic_effects if effect.active]
    
    def draw_magic_effects(self):
        """绘制魔法效果"""
        # 更新并绘制所有效果
        for effect in self.magic_effects:
            effect.update()
            effect.draw(self.screen)
        
        # 每帧结束后自动清理
        self._cleanup_effects()
    
    def draw_background(self):
        """绘制神秘背景"""
        # 渐变背景
        for y in range(0, SCREEN_HEIGHT, 2):
            alpha = 255 - int(y / SCREEN_HEIGHT * 100)
            color = (self.colors['background'][0], 
                    self.colors['background'][1], 
                    self.colors['background'][2], 
                    alpha)
            
            pygame.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y))
        
        # 绘制魔法阵图案
        center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        radius = 150
        
        # 外圈
        pygame.draw.circle(self.screen, (40, 30, 70, 50), (center_x, center_y), radius, 2)
        pygame.draw.circle(self.screen, (60, 40, 100, 30), (center_x, center_y), radius + 20, 1)
        
        # 魔法符文
        for i in range(8):
            angle = i * math.pi / 4
            x1 = center_x + math.cos(angle) * (radius - 20)
            y1 = center_y + math.sin(angle) * (radius - 20)
            x2 = center_x + math.cos(angle) * (radius + 20)
            y2 = center_y + math.sin(angle) * (radius + 20)
            
            pygame.draw.line(self.screen, (80, 60, 140, 80), (x1, y1), (x2, y2), 2)
        
        # 星光效果
        for _ in range(20):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            size = random.randint(1, 3)
            brightness = random.randint(100, 200)
            pygame.draw.circle(self.screen, (brightness, brightness, 200), (x, y), size)
    
    def draw_game_info(self, game_logic):
        """绘制游戏信息面板"""
        # 头部背景
        header_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 180)
        pygame.draw.rect(self.screen, (25, 20, 40, 200), header_rect)
        pygame.draw.line(self.screen, self.colors['accent'], (0, 180), (SCREEN_WIDTH, 180), 3)
        
        # 游戏标题
        title = self.font_manager.large.render("MAGIC CARDS SPLIT", True, self.colors['title'])
        title_shadow = self.font_manager.large.render("MAGIC CARDS SPLIT", True, (40, 30, 70))
        self.screen.blit(title_shadow, (SCREEN_WIDTH//2 - title.get_width()//2 + 3, 18))
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 15))
        
        # 游戏规则说明
        rules = f"Rules: Take 1-{game_logic.k} cards or split a pile. Last card wins!"
        rules_text = self.font_manager.small.render(rules, True, self.colors['hint'])
        self.screen.blit(rules_text, (SCREEN_WIDTH//2 - rules_text.get_width()//2, 50))
        
        # 游戏模式和难度
        difficulty_names = ["Easy", "Normal", "Hard", "Insane"]
        
        if game_logic.game_mode == "PVP":
            mode_text = "Mode: Player vs Player"
        else:
            mode_text = f"Mode: Player vs AI - {difficulty_names[game_logic.difficulty-1]}"
        
        mode_info = self.font_manager.small.render(mode_text, True, self.colors['accent'])
        self.screen.blit(mode_info, (20, 145))
        
        # 当前玩家信息
        if game_logic.current_player == 1:
            player_name = "Player 1"
            player_color = self.colors['player1']
        else:
            player_name = "AI" if game_logic.game_mode == "PVE" else "Player 2"
            player_color = self.colors['player2']
        
        # 当前玩家显示框
        player_text = self.font_manager.medium.render(f"Current Magician: {player_name}", True, player_color)
        player_bg = pygame.Rect(SCREEN_WIDTH - player_text.get_width() - 40, 45, 
                              player_text.get_width() + 20, player_text.get_height() + 10)
        pygame.draw.rect(self.screen, (40, 30, 60), player_bg, border_radius=8)
        pygame.draw.rect(self.screen, player_color, player_bg, 2, border_radius=8)
        self.screen.blit(player_text, (SCREEN_WIDTH - player_text.get_width() - 30, 50))
        
        # 当前游戏状态
        total_cards = sum(game_logic.cards)
        piles_count = len(game_logic.cards)
        status_text = self.font_manager.medium.render(
            f"Total Cards: {total_cards} | Piles: {piles_count} | Moves: {len(game_logic.get_available_moves())}", 
            True, self.colors['hint']
        )
        self.screen.blit(status_text, (SCREEN_WIDTH//2 - status_text.get_width()//2, 80))
        
        # 游戏消息
        if game_logic.game_over:
            if game_logic.winner == 1:
                message_color = self.colors['win']
                message = "Player 1 wins the magic duel! ✨"
            else:
                message_color = self.colors['lose'] if game_logic.game_mode == "PVE" else self.colors['player2']
                message = "AI wins the magic duel! " if game_logic.game_mode == "PVE" else "Player 2 wins the magic duel! ✨"
        else:
            message_color = self.colors['hint']
            message = game_logic.message
        
        message_lines = wrap_text(message, self.font_manager.medium, SCREEN_WIDTH - 100)
        for i, line in enumerate(message_lines):
            message_text = self.font_manager.medium.render(line, True, message_color)
            message_bg_width = message_text.get_width() + 30
            message_bg = pygame.Rect(SCREEN_WIDTH//2 - message_bg_width//2, 110 + i * 25, 
                                   message_bg_width, message_text.get_height() + 6)
            
            if i == 0:
                pygame.draw.rect(self.screen, (40, 30, 60), message_bg, border_radius=8)
                pygame.draw.rect(self.screen, self.colors['accent'], message_bg, 2, border_radius=8)
            
            self.screen.blit(message_text, (SCREEN_WIDTH//2 - message_text.get_width()//2, 113 + i * 25))
        
        # 胜负状态指示器 - 只在游戏进行中显示
        if not game_logic.game_over:
            game_state = "Winning Position" if game_logic.judge_win() else "Losing Position"
            state_color = self.colors['win'] if game_logic.judge_win() else self.colors['lose']
            state_text = self.font_manager.small.render(game_state, True, state_color)
            
            state_bg = pygame.Rect(SCREEN_WIDTH//2 - state_text.get_width()//2 - 10, 155, 
                                 state_text.get_width() + 20, state_text.get_height() + 6)
            pygame.draw.rect(self.screen, (40, 30, 60), state_bg, border_radius=6)
            pygame.draw.rect(self.screen, state_color, state_bg, 2, border_radius=6)
            self.screen.blit(state_text, (SCREEN_WIDTH//2 - state_text.get_width()//2, 158))
    
    def draw_card_piles(self, card_piles: List[MagicCard]):
        """绘制所有卡牌堆"""
        for card_pile in card_piles:
            card_pile.update()
            card_pile.draw(self.screen)
    
    def draw_action_buttons(self, game_logic):
        """绘制动作按钮（拿牌/分割）"""
        if self.selected_pile is None or game_logic.selected_pile is None:
            return
        
        selected_pile_size = game_logic.cards[game_logic.selected_pile]
        
        # 动作面板背景
        action_panel_y = 400
        action_panel_height = 200
        panel_rect = pygame.Rect(50, action_panel_y, SCREEN_WIDTH - 100, action_panel_height)
        pygame.draw.rect(self.screen, (30, 25, 50, 200), panel_rect, border_radius=15)
        pygame.draw.rect(self.screen, self.colors['accent'], panel_rect, 2, border_radius=15)
        
        # 面板标题
        panel_title = self.font_manager.medium.render(f"Actions for Pile {game_logic.selected_pile + 1}", True, self.colors['title'])
        self.screen.blit(panel_title, (SCREEN_WIDTH//2 - panel_title.get_width()//2, action_panel_y + 10))
        
        # 如果没有选择动作类型，显示两个大按钮
        if not self.selected_action:
            # 拿牌按钮
            take_btn_rect = pygame.Rect(SCREEN_WIDTH//2 - 210, action_panel_y + 50, 180, 60)
            pygame.draw.rect(self.screen, self.colors['player1'], take_btn_rect, border_radius=10)
            pygame.draw.rect(self.screen, self.colors['accent'], take_btn_rect, 3, border_radius=10)
            take_text = self.font_manager.medium.render("Take Cards", True, (255, 255, 255))
            self.screen.blit(take_text, (take_btn_rect.centerx - take_text.get_width()//2, take_btn_rect.centery - take_text.get_height()//2))
            
            # 分割按钮（只有在牌堆至少有2张牌时才可用）
            split_btn_color = self.colors['player2'] if selected_pile_size >= 2 else (100, 100, 120)
            split_btn_rect = pygame.Rect(SCREEN_WIDTH//2 + 30, action_panel_y + 50, 180, 60)
            pygame.draw.rect(self.screen, split_btn_color, split_btn_rect, border_radius=10)
            pygame.draw.rect(self.screen, self.colors['accent'], split_btn_rect, 3, border_radius=10)
            split_text = self.font_manager.medium.render("Split Pile", True, (255, 255, 255))
            self.screen.blit(split_text, (split_btn_rect.centerx - split_text.get_width()//2, split_btn_rect.centery - split_text.get_height()//2))
            
            # 如果牌堆太小不能分割，显示提示
            if selected_pile_size < 2:
                warning_text = self.font_manager.small.render("(Need at least 2 cards to split)", True, (200, 100, 100))
                self.screen.blit(warning_text, (split_btn_rect.centerx - warning_text.get_width()//2, split_btn_rect.bottom + 5))
        
        # 如果选择了拿牌动作
        elif self.selected_action == 'take':
            take_y = action_panel_y + 50
            take_title = self.font_manager.small.render("Take Cards:", True, self.colors['player1'])
            self.screen.blit(take_title, (100, take_y))
            
            # 获取当前选择的拿牌数量
            selected_take_count = game_logic.get_selection_param('take_count', 1)
            
            # 绘制拿牌数量按钮
            max_take = min(selected_pile_size, game_logic.k)
            for i in range(max_take):
                take_count = i + 1
                btn_x = 120 + i * 60
                btn_y = take_y + 30
                btn_width = 50
                btn_height = 40
                
                # 按钮状态 - 检查是否被选中
                is_selected = (selected_take_count == take_count)
                
                # 绘制按钮
                btn_rect = pygame.Rect(btn_x, btn_y, btn_width, btn_height)
                
                # 选中状态使用特殊颜色
                if is_selected:
                    btn_color = self.colors['player1']
                    border_color = (255, 255, 200)
                else:
                    btn_color = (60, 50, 100)
                    border_color = self.colors['accent']
                
                pygame.draw.rect(self.screen, btn_color, btn_rect, border_radius=8)
                pygame.draw.rect(self.screen, border_color, btn_rect, 3 if is_selected else 2, border_radius=8)
                
                # 按钮文本
                count_text = self.font_manager.medium.render(str(take_count), True, (255, 255, 255))
                if is_selected:
                    # 选中状态文本加粗效果
                    count_shadow = self.font_manager.medium.render(str(take_count), True, (0, 0, 0, 100))
                    self.screen.blit(count_shadow, (btn_x + btn_width//2 - count_text.get_width()//2 + 1, 
                                                  btn_y + btn_height//2 - count_text.get_height()//2 + 1))
                
                self.screen.blit(count_text, (btn_x + btn_width//2 - count_text.get_width()//2, 
                                             btn_y + btn_height//2 - count_text.get_height()//2))
        
        # 如果选择了分割动作
        elif self.selected_action == 'split':
            split_y = action_panel_y + 50
            split_title = self.font_manager.small.render("Split Pile:", True, self.colors['player2'])
            self.screen.blit(split_title, (100, split_y))
            
            # 获取当前分割点
            current_split = game_logic.split_point
            second_part = selected_pile_size - current_split
            
            # 显示当前分割方案
            plan_text = f"Current split plan: {current_split} | {second_part}"
            plan_display = self.font_manager.medium.render(plan_text, True, self.colors['player2'])
            self.screen.blit(plan_display, (SCREEN_WIDTH//2 - plan_display.get_width()//2, split_y + 30))
            
            # 绘制调节按钮 - 确保坐标与game.py中的检测一致
            button_width = 80
            button_height = 50
            center_x = SCREEN_WIDTH // 2
            
            # 减少按钮
            minus_btn_rect = pygame.Rect(center_x - 140, split_y + 70, button_width, button_height)
            minus_enabled = current_split > 1
            minus_color = self.colors['player2'] if minus_enabled else (100, 100, 120)
            pygame.draw.rect(self.screen, minus_color, minus_btn_rect, border_radius=8)
            pygame.draw.rect(self.screen, self.colors['accent'], minus_btn_rect, 3, border_radius=8)
            minus_text = self.font_manager.large.render("-", True, (255, 255, 255) if minus_enabled else (150, 150, 150))
            self.screen.blit(minus_text, (minus_btn_rect.centerx - minus_text.get_width()//2, minus_btn_rect.centery - minus_text.get_height()//2))
            
            # 增加按钮
            plus_btn_rect = pygame.Rect(center_x + 60, split_y + 70, button_width, button_height)
            plus_enabled = current_split < selected_pile_size - 1
            plus_color = self.colors['player2'] if plus_enabled else (100, 100, 120)
            pygame.draw.rect(self.screen, plus_color, plus_btn_rect, border_radius=8)
            pygame.draw.rect(self.screen, self.colors['accent'], plus_btn_rect, 3, border_radius=8)
            plus_text = self.font_manager.large.render("+", True, (255, 255, 255) if plus_enabled else (150, 150, 150))
            self.screen.blit(plus_text, (plus_btn_rect.centerx - plus_text.get_width()//2, plus_btn_rect.centery - plus_text.get_height()//2))
            
            # 添加键盘提示
            hint_text = self.font_manager.small.render("Use ←/→ keys or click +/- to adjust", True, self.colors['hint'])
            self.screen.blit(hint_text, (SCREEN_WIDTH//2 - hint_text.get_width()//2, split_y + 130))
    
    def draw_control_buttons(self):
        """绘制控制按钮"""
        buttons = {}
        
        # 返回按钮
        buttons['back'] = Button(20, 20, 50, 50, "", self.font_manager, icon='back',
                                tooltip="Back to mode selection")
        
        # 主页按钮
        buttons['home'] = Button(80, 20, 50, 50, "", self.font_manager, icon='home',
                                tooltip="Back to main menu")
        
        # 确认按钮（当有选中动作时）
        if self.selected_action:
            buttons['confirm'] = Button(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 80, 130, 50,
                                       "Cast Spell", self.font_manager,
                                       tooltip="Confirm your magical action")
        
        # 取消按钮（当有选中牌堆时）
        if self.selected_pile is not None:
            buttons['cancel'] = Button(SCREEN_WIDTH - 300, SCREEN_HEIGHT - 80, 130, 50,
                                      "Cancel", self.font_manager,
                                      tooltip="Cancel current selection")
        
        return buttons
    
    def draw_hints(self):
        """绘制操作提示"""
        hint_y = SCREEN_HEIGHT - 40
        hints = [
            "Click on a card pile to select it for magic",
            "Choose to take cards or split the pile",
            "Last magician to take a card wins the duel",
            "Use strategy to outwit your opponent"
        ]
        
        for i, hint in enumerate(hints):
            hint_text = self.font_manager.small.render(hint, True, self.colors['hint'])
            self.screen.blit(hint_text, (SCREEN_WIDTH//2 - hint_text.get_width()//2, hint_y - (len(hints) - i) * 20))
    
    def create_card_piles(self, game_logic) -> List[MagicCard]:
        """根据游戏逻辑创建卡牌堆UI对象"""
        card_piles = []
        piles_count = len(game_logic.cards)
        
        # 计算布局
        if piles_count <= 5:
            # 单行布局
            start_x = SCREEN_WIDTH // (piles_count + 1)
            spacing = start_x
            y_position = 250
        else:
            # 两行布局
            start_x = 100
            spacing = (SCREEN_WIDTH - 200) // (piles_count // 2 + 1)
            y_position = [250, 350]
        
        # 创建卡牌堆
        if piles_count <= 5:
            for i, card_count in enumerate(game_logic.cards):
                x = start_x + i * spacing
                # 检查这个牌堆是否被选中
                is_selected = (game_logic.selected_pile == i)
                card_pile = MagicCard(x, y_position, card_count, i, self.font_manager, is_selected)
                card_piles.append(card_pile)
        else:
            # 两行布局
            first_row = (piles_count + 1) // 2
            second_row = piles_count // 2
            
            # 第一行
            for i in range(first_row):
                x = start_x + i * spacing
                is_selected = (game_logic.selected_pile == i)
                card_pile = MagicCard(x, y_position[0], game_logic.cards[i], i, self.font_manager, is_selected)
                card_piles.append(card_pile)
            
            # 第二行
            for i in range(second_row):
                x = start_x + i * spacing
                pile_index = first_row + i
                is_selected = (game_logic.selected_pile == pile_index)
                card_pile = MagicCard(x, y_position[1], game_logic.cards[pile_index], pile_index, self.font_manager, is_selected)
                card_piles.append(card_pile)
        
        return card_piles
    
    def update_selection(self, game_logic):
        """更新选中状态"""
        self.selected_pile = game_logic.selected_pile
        self.selected_action = game_logic.selected_action
        
        # 如果选择了分割动作但还没有分割点，设置默认值
        if self.selected_action == 'split' and self.selected_pile is not None:
            pile_size = game_logic.cards[self.selected_pile]
            if pile_size >= 2:
                # 设置默认分割点为1
                game_logic.split_point = 1
                game_logic.set_selection(self.selected_pile, 'split', split_point=1)
    
    def reset_selection(self):
        """重置选择状态"""
        self.selected_pile = None
        self.selected_action = None
    
    def create_game_over_buttons(self, font_manager):
        """创建游戏结束按钮"""
        from ui.buttons import Button
        buttons = {
            "restart": Button(
                SCREEN_WIDTH//2 - 120, 550, 240, 60, "New Magic Duel", 
                font_manager, tooltip="Start a new magical duel"
            )
        }
        return buttons