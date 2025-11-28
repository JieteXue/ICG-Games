import pygame
import sys
import random
from typing import List, Tuple, Optional

pygame.init()


COLORS = {
    'background': (25, 35, 45),      # 深蓝色背景
    'panel': (20, 25, 50),           # 面板深蓝
    'tower_base': (100, 120, 180),   # 炮塔基座
    'tower_active': (0, 200, 255),   # 激活炮塔 - 亮蓝色
    'tower_inactive': (60, 80, 120), # 未激活炮塔 - 暗蓝色
    'laser_player1': (0, 255, 200),  # 玩家1激光 - 青蓝色
    'laser_player2': (255, 100, 0),  # 玩家2激光 - 橙红色
    'highlight': (255, 255, 100),    # 高亮黄色
    'text': (220, 220, 255),         # 浅蓝色文字
    'button': (40, 60, 120),         # 按钮蓝色
    'button_hover': (60, 90, 160),   # 悬停按钮
    'scrollbar': (80, 100, 150),     # 滚动条
    'grid': (30, 40, 70)             # 网格线
}

# 游戏配置
TOWER_WIDTH = 80
TOWER_HEIGHT = 120
TOWER_SPACING = 20
SCREEN_MARGIN = 50
BUTTON_WIDTH = 150
BUTTON_HEIGHT = 40
FONT_SIZE = 24
SCROLLBAR_HEIGHT = 20

class TechTowerGame:
    def __init__(self):
        self.num_towers = random.randint(8, 20)
        self.towers = [1 for _ in range(self.num_towers)]  # 1表示炮塔可用
        self.lasers = []  # 存储激光连接 [(start_idx, end_idx, player)]
        self.current_player = 1
        self.selected_tower = None
        self.scroll_offset = 0
        self.max_scroll = 0
        
        # 计算屏幕和内容尺寸
        self.content_width = self.num_towers * (TOWER_WIDTH + TOWER_SPACING) - TOWER_SPACING + 2 * SCREEN_MARGIN
        self.screen_width = min(1200, self.content_width)
        self.screen_height = 700
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Laser Defense - Tech Tower Game")
        
        # 计算最大滚动距离
        if self.content_width > self.screen_width:
            self.max_scroll = self.content_width - self.screen_width
        
        self.font = pygame.font.SysFont('consolas', FONT_SIZE)
        self.title_font = pygame.font.SysFont('consolas', 32, bold=True)
        self.small_font = pygame.font.SysFont('consolas', 18)
        
        # 预计算炮塔位置
        self.tower_positions = self._calculate_tower_positions()
        
    def _calculate_tower_positions(self):
        """计算所有炮塔的位置"""
        positions = []
        for i in range(self.num_towers):
            x = SCREEN_MARGIN + i * (TOWER_WIDTH + TOWER_SPACING) - self.scroll_offset
            y = 200
            positions.append((x, y))
        return positions
    
    def draw_grid_background(self):
        """绘制科技风格的网格背景"""
        grid_size = 40
        for x in range(0, self.screen_width, grid_size):
            pygame.draw.line(self.screen, COLORS['grid'], (x, 0), (x, self.screen_height), 1)
        for y in range(0, self.screen_height, grid_size):
            pygame.draw.line(self.screen, COLORS['grid'], (0, y), (self.screen_width, y), 1)
    
    def draw_tower(self, x, y, is_active, tower_id):
        """绘制单个炮塔"""
        # 炮塔基座
        base_rect = pygame.Rect(x, y, TOWER_WIDTH, TOWER_HEIGHT)
        color = COLORS['tower_active'] if is_active else COLORS['tower_inactive']
        pygame.draw.rect(self.screen, COLORS['tower_base'], base_rect)
        pygame.draw.rect(self.screen, color, base_rect, 3)
        
        # 炮塔顶部（雷达/发射器）
        top_radius = TOWER_WIDTH // 3
        top_center = (x + TOWER_WIDTH // 2, y + top_radius + 5)
        pygame.draw.circle(self.screen, color, top_center, top_radius, 2)
        
        # 炮塔编号
        id_text = self.small_font.render(str(tower_id), True, COLORS['text'])
        self.screen.blit(id_text, (x + TOWER_WIDTH // 2 - 5, y + TOWER_HEIGHT - 25))
        
        # 如果激活，绘制发光效果
        if is_active:
            glow_radius = top_radius + 3
            glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*color[:3], 50), (glow_radius, glow_radius), glow_radius)
            self.screen.blit(glow_surf, (top_center[0] - glow_radius, top_center[1] - glow_radius))
    
    def draw_laser(self, start_idx, end_idx, player):
        """绘制激光连接"""
        start_x = self.tower_positions[start_idx][0] + TOWER_WIDTH // 2
        start_y = self.tower_positions[start_idx][1] + 20
        end_x = self.tower_positions[end_idx][0] + TOWER_WIDTH // 2
        end_y = self.tower_positions[end_idx][1] + 20
        
        laser_color = COLORS['laser_player1'] if player == 1 else COLORS['laser_player2']
        
        # 绘制激光光束
        pygame.draw.line(self.screen, laser_color, (start_x, start_y), (end_x, end_y), 4)
        
        # 添加激光发光效果
        glow_surf = pygame.Surface((abs(end_x - start_x) + 10, 10), pygame.SRCALPHA)
        pygame.draw.line(glow_surf, (*laser_color[:3], 80), (5, 5), (glow_surf.get_width() - 5, 5), 8)
        self.screen.blit(glow_surf, (min(start_x, end_x) - 5, start_y - 5))
    
    def draw_scrollbar(self):
        """绘制滚动条"""
        if self.max_scroll <= 0:
            return
            
        scrollbar_width = self.screen_width - 100
        scrollbar_x = 50
        scrollbar_y = self.screen_height - SCROLLBAR_HEIGHT - 10
        
        # 滚动条背景
        pygame.draw.rect(self.screen, COLORS['panel'], 
                        (scrollbar_x, scrollbar_y, scrollbar_width, SCROLLBAR_HEIGHT))
        
        # 计算滑块位置
        slider_width = max(30, scrollbar_width * self.screen_width / self.content_width)
        slider_x = scrollbar_x + (self.scroll_offset / self.max_scroll) * (scrollbar_width - slider_width)
        
        # 绘制滑块
        pygame.draw.rect(self.screen, COLORS['scrollbar'], 
                        (slider_x, scrollbar_y, slider_width, SCROLLBAR_HEIGHT))
    
    def draw_ui(self):
        """绘制用户界面"""
        # 绘制标题
        title = self.title_font.render("LASER DEFENSE SYSTEM", True, COLORS['text'])
        self.screen.blit(title, (self.screen_width // 2 - title.get_width() // 2, 20))
        
        # 绘制当前玩家信息
        player_text = self.font.render(f"Player {self.current_player} Turn", True, 
                                     COLORS['laser_player1'] if self.current_player == 1 else COLORS['laser_player2'])
        self.screen.blit(player_text, (SCREEN_MARGIN, 80))
        
        # 绘制游戏状态
        moves = self.get_available_moves()
        if not moves:
            winner = 2 if self.current_player == 1 else 1
            status_text = self.font.render(f"GAME OVER! Player {winner} WINS!", True, COLORS['highlight'])
            self.screen.blit(status_text, (self.screen_width // 2 - status_text.get_width() // 2, 120))
        else:
            status_text = self.font.render(f"Available moves: {len(moves)}", True, COLORS['text'])
            self.screen.blit(status_text, (SCREEN_MARGIN, 120))
        
        # 绘制重新开始按钮
        self.draw_button("NEW GAME", self.screen_width - BUTTON_WIDTH - SCREEN_MARGIN, 
                        self.screen_height - BUTTON_HEIGHT - 20)
    
    def draw_button(self, text, x, y):
        """绘制按钮"""
        mouse_pos = pygame.mouse.get_pos()
        button_rect = pygame.Rect(x, y, BUTTON_WIDTH, BUTTON_HEIGHT)
        
        # 检查鼠标悬停
        if button_rect.collidepoint(mouse_pos):
            color = COLORS['button_hover']
        else:
            color = COLORS['button']
        
        pygame.draw.rect(self.screen, color, button_rect, border_radius=5)
        pygame.draw.rect(self.screen, COLORS['text'], button_rect, 2, border_radius=5)
        
        text_surf = self.font.render(text, True, COLORS['text'])
        text_rect = text_surf.get_rect(center=button_rect.center)
        self.screen.blit(text_surf, text_rect)
        
        return button_rect
    
    def draw(self):
        """绘制整个游戏界面"""
        self.screen.fill(COLORS['background'])
        self.draw_grid_background()
        
        # 更新炮塔位置
        self.tower_positions = self._calculate_tower_positions()
        
        # 绘制所有激光
        for start_idx, end_idx, player in self.lasers:
            self.draw_laser(start_idx, end_idx, player)
        
        # 绘制所有炮塔
        for i, (x, y) in enumerate(self.tower_positions):
            is_active = self.towers[i] == 1
            self.draw_tower(x, y, is_active, i)
            
            # 高亮选中的炮塔
            if self.selected_tower == i:
                highlight_rect = pygame.Rect(x-5, y-5, TOWER_WIDTH+10, TOWER_HEIGHT+10)
                pygame.draw.rect(self.screen, COLORS['highlight'], highlight_rect, 3)
        
        self.draw_ui()
        self.draw_scrollbar()
    
    def get_available_moves(self):
        """获取所有可用的移动"""
        moves = []
        for i in range(len(self.towers) - 1):
            if self.towers[i] == 1 and self.towers[i + 1] == 1:
                moves.append(i)
        return moves
    
    def handle_click(self, pos):
        """处理鼠标点击"""
        x, y = pos
        
        # 检查是否点击重新开始按钮
        button_rect = pygame.Rect(
            self.screen_width - BUTTON_WIDTH - SCREEN_MARGIN,
            self.screen_height - BUTTON_HEIGHT - 20,
            BUTTON_WIDTH, BUTTON_HEIGHT
        )
        if button_rect.collidepoint(pos):
            self.__init__()  # 重新初始化游戏
            return
        
        # 检查是否点击炮塔
        for i, (tower_x, tower_y) in enumerate(self.tower_positions):
            tower_rect = pygame.Rect(tower_x, tower_y, TOWER_WIDTH, TOWER_HEIGHT)
            if tower_rect.collidepoint(x, y) and self.towers[i] == 1:
                self.handle_tower_click(i)
                break
    
    def handle_tower_click(self, index):
        """处理炮塔点击"""
        if self.selected_tower is None:
            # 第一次选择炮塔
            self.selected_tower = index
        else:
            # 第二次选择炮塔
            if abs(self.selected_tower - index) == 1:
                # 检查是否相邻且都可用
                if self.towers[self.selected_tower] == 1 and self.towers[index] == 1:
                    # 连接激光
                    self.lasers.append((self.selected_tower, index, self.current_player))
                    self.towers[self.selected_tower] = 0
                    self.towers[index] = 0
                    
                    # 切换玩家
                    self.current_player = 3 - self.current_player  # 1->2, 2->1
            
            # 重置选择
            self.selected_tower = None
    
    def handle_scroll(self, event):
        """处理滚动事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # 滚轮上滚
                self.scroll_offset = max(0, self.scroll_offset - 50)
            elif event.button == 5:  # 滚轮下滚
                self.scroll_offset = min(self.max_scroll, self.scroll_offset + 50)
    
    def run(self):
        """运行游戏主循环"""
        clock = pygame.time.Clock()
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button in [4, 5]:  # 鼠标滚轮
                        self.handle_scroll(event)
                    elif event.button == 1:  # 左键点击
                        self.handle_click(event.pos)
            
            self.draw()
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()
        sys.exit()

# 主程序
if __name__ == "__main__":
    game = TechTowerGame()
    game.run()