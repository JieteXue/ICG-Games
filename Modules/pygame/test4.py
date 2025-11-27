import pygame
import sys
import random
from typing import List, Tuple, Optional

# 初始化Pygame
pygame.init()

# 颜色定义 - 自然生态色调
COLORS = {
    'background': (240, 235, 200),  # 浅米色背景
    'grid_line': (180, 160, 120),   # 木质色调
    'empty_cell': (210, 180, 140),  # 沙土色
    'player1': (76, 153, 0),        # 深绿色 - 玩家1的植物
    'player2': (255, 128, 0),       # 橘黄色 - 玩家2的植物
    'highlight': (255, 255, 100, 128),  # 高亮黄色，带透明度
    'text': (60, 30, 10),           # 深棕色文字
    'button': (150, 180, 100),      # 浅绿色按钮
    'button_hover': (170, 200, 120) # 悬停状态的按钮
}

# 游戏配置
CELL_SIZE = 60
CELL_MARGIN = 5
BOARD_MARGIN = 50
BUTTON_WIDTH = 120
BUTTON_HEIGHT = 40
FONT_SIZE = 24

class DawsonKaylesUI:
    def __init__(self, game_logic):
        self.game_logic = game_logic
        self.board = game_logic.initial_setting()
        self.current_player = 1  # 玩家1开始
        self.selected_cell = None
        self.highlighted_moves = []
        
        # 计算屏幕尺寸
        self.screen_width = max(800, len(self.board) * (CELL_SIZE + CELL_MARGIN) + 2 * BOARD_MARGIN)
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("自然生态棋 - Dawson's Kayles")
        
        self.font = pygame.font.SysFont('microsoftyahei', FONT_SIZE)
        self.title_font = pygame.font.SysFont('microsoftyahei', 36, bold=True)
        
        # 加载植物图像（简化版，用图形代替）
        self.plant_images = self._create_plant_images()
        
    def _create_plant_images(self):
        """创建植物图像"""
        images = {}
        size = (CELL_SIZE - 10, CELL_SIZE - 10)
        
        # 玩家1的植物（绿色）
        surf1 = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.circle(surf1, COLORS['player1'], (size[0]//2, size[1]//2), size[0]//3)
        pygame.draw.rect(surf1, (100, 80, 0), (size[0]//2-2, size[1]//2, 4, size[1]//2))
        images[1] = surf1
        
        # 玩家2的植物（橘色）
        surf2 = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.circle(surf2, COLORS['player2'], (size[0]//2, size[1]//2), size[0]//3)
        pygame.draw.polygon(surf2, (200, 100, 0), [
            (size[0]//2, size[1]//2),
            (size[0]//2-8, size[1]-5),
            (size[0]//2+8, size[1]-5)
        ])
        images[2] = surf2
        
        return images
    
    def draw_board(self):
        """绘制游戏棋盘"""
        self.screen.fill(COLORS['background'])
        
        # 绘制标题
        title = self.title_font.render("自然生态棋 - 双瓶采集", True, COLORS['text'])
        self.screen.blit(title, (self.screen_width//2 - title.get_width()//2, 10))
        
        # 绘制当前玩家信息
        player_text = self.font.render(f"当前玩家: {'玩家1(绿植)' if self.current_player == 1 else '玩家2(橘植)'}", 
                                     True, COLORS['text'])
        self.screen.blit(player_text, (BOARD_MARGIN, 60))
        
        # 绘制瓶子（格子）
        for i in range(len(self.board)):
            x = BOARD_MARGIN + i * (CELL_SIZE + CELL_MARGIN)
            y = 150
            
            # 绘制格子背景
            color = COLORS['empty_cell'] if self.board[i] == 1 else (200, 200, 200)
            pygame.draw.rect(self.screen, color, (x, y, CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(self.screen, COLORS['grid_line'], (x, y, CELL_SIZE, CELL_SIZE), 2)
            
            # 绘制瓶子编号
            num_text = self.font.render(str(i), True, COLORS['text'])
            self.screen.blit(num_text, (x + CELL_SIZE//2 - 5, y - 25))
            
            # 如果瓶子存在，绘制植物
            if self.board[i] == 1:
                if i in self.highlighted_moves:
                    # 高亮可移动的瓶子
                    highlight_surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                    highlight_surf.fill(COLORS['highlight'])
                    self.screen.blit(highlight_surf, (x, y))
                
                # 绘制植物
                plant_x = x + 5
                plant_y = y + 5
                self.screen.blit(self.plant_images[self.current_player], (plant_x, plant_y))
        
        # 绘制游戏状态信息
        moves = self.game_logic.judge_move_global(self.board)
        if not moves:
            winner = 2 if self.current_player == 1 else 1
            status_text = self.font.render(f"游戏结束! 玩家{winner}获胜!", True, (200, 0, 0))
        else:
            status_text = self.font.render(f"可选移动: {moves}", True, COLORS['text'])
        
        self.screen.blit(status_text, (BOARD_MARGIN, 250))
        
        # 绘制重新开始按钮
        self.draw_button("重新开始", self.screen_width - BUTTON_WIDTH - 50, 500)
    
    def draw_button(self, text, x, y):
        """绘制按钮"""
        mouse_pos = pygame.mouse.get_pos()
        button_rect = pygame.Rect(x, y, BUTTON_WIDTH, BUTTON_HEIGHT)
        
        # 检查鼠标悬停
        if button_rect.collidepoint(mouse_pos):
            color = COLORS['button_hover']
        else:
            color = COLORS['button']
        
        pygame.draw.rect(self.screen, color, button_rect, border_radius=10)
        pygame.draw.rect(self.screen, COLORS['text'], button_rect, 2, border_radius=10)
        
        text_surf = self.font.render(text, True, COLORS['text'])
        text_rect = text_surf.get_rect(center=button_rect.center)
        self.screen.blit(text_surf, text_rect)
        
        return button_rect
    
    def handle_click(self, pos):
        """处理鼠标点击"""
        x, y = pos
        
        # 检查是否点击重新开始按钮
        button_rect = pygame.Rect(self.screen_width - BUTTON_WIDTH - 50, 500, BUTTON_WIDTH, BUTTON_HEIGHT)
        if button_rect.collidepoint(pos):
            self.board = self.game_logic.initial_setting()
            self.current_player = 1
            self.highlighted_moves = []
            return
        
        # 检查是否点击瓶子
        if 150 <= y <= 150 + CELL_SIZE:
            for i in range(len(self.board)):
                cell_x = BOARD_MARGIN + i * (CELL_SIZE + CELL_MARGIN)
                if cell_x <= x <= cell_x + CELL_SIZE:
                    self.handle_bottle_click(i)
                    break
    
    def handle_bottle_click(self, index):
        """处理瓶子点击"""
        moves = self.game_logic.judge_move_global(self.board)
        
        if not moves:
            return  # 游戏已结束
            
        if self.selected_cell is None:
            # 第一次点击，高亮相邻的可移动对
            self.highlighted_moves = []
            for move in moves:
                if move == index or move + 1 == index:
                    self.highlighted_moves.extend([move, move + 1])
            self.selected_cell = index
        else:
            # 第二次点击，尝试执行移动
            if abs(self.selected_cell - index) == 1:
                move_index = min(self.selected_cell, index)
                if move_index in moves:
                    # 执行移动
                    self.game_logic.acted_list(self.board, move_index)
                    self.current_player = 3 - self.current_player  # 切换玩家 (1->2, 2->1)
            
            # 重置选择状态
            self.selected_cell = None
            self.highlighted_moves = []
    
    def run(self):
        """运行游戏主循环"""
        clock = pygame.time.Clock()
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # 左键点击
                        self.handle_click(event.pos)
            
            self.draw_board()
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()
        sys.exit()

# 将您的游戏逻辑封装成类
class DawsonKaylesGame:
    def __init__(self):
        pass
    
    def pre_words(self):
        print("We are going to start the game of Dawson's Kayles Taking bottles.\n")
        n = input("Enter the number of initial bottles (larger than 1, or enter directly for random setting): ")
        if n.isdigit(): 
            return int(n)
        return None
    
    def random_list(self, n=-1):
        '''Generate a (random) list of bottles.'''
        if n is None or type(n) != int or n <= 1:
            lst = [1 for i in range(random.randint(5, 10))]
        else:
            lst = [1 for i in range(n)]
        return lst
    
    def initial_setting(self):
        return self.random_list(self.pre_words())
    
    def SG(self, n):
        # Grundy numbers (0-51)
        base_grundy = [
            0, 0, 1, 1, 2, 0, 3, 1, 1, 0, 3, 3, 2, 2, 4, 0, 5, 2, 2, 3, 3,
            0, 1, 1, 3, 0, 2, 1, 1, 0, 4, 5, 2, 4, 0, 1, 1, 2, 0, 3, 1, 1,
            0, 3, 3, 2, 2, 4, 4, 0, 5, 4
        ]
        
        if n < len(base_grundy):
            return base_grundy[n]
        else:
            period = 34
            start_period = 52
            equivalent_n = (n - start_period) % period + (start_period - period)
            return base_grundy[equivalent_n]
    
    def judge_win(self, lst):
        '''Check whether the given list is a winning list.'''
        splits = []
        count = 0
        for i in range(len(lst)):
            if lst[i] == 1:
                count += 1
            else:
                if count != 0:
                    splits.append(count)
                count = 0
        if count != 0:
            splits.append(count)
        sg = 0
        for i in range(len(splits)):
            sg ^= self.SG(splits[i])
        return sg != 0
    
    def judge_move_local(self, lst, i):
        '''Check whether the given action can be moved.'''
        return i >= 0 and i < len(lst) - 1 and lst[i] == 1 and lst[i + 1] == 1
    
    def judge_move_global(self, lst):
        '''Return a list of possible actions'''
        moving = []
        for i in range(len(lst) - 1):
            if self.judge_move_local(lst, i):
                moving.append(i)
        return moving
    
    def acted_list(self, lst, i):
        lst[i] = 0
        lst[i + 1] = 0
        return lst

# 主程序
if __name__ == "__main__":
    game_logic = DawsonKaylesGame()
    ui = DawsonKaylesUI(game_logic)
    ui.run()