"""
Dawson-Kayles Game - Main game class
"""

import pygame
import sys
from core.base_game import BaseGame
from games.dawson_kayles.logic import DawsonKaylesLogic
from games.dawson_kayles.ui import DawsonKaylesUI
from ui.menus import GameModeSelector
from utils.constants import CARD_GAME_FPS
from utils.key_repeat import KeyRepeatManager

class DawsonKaylesInputHandler:
    """Dawson-Kayles游戏输入处理器"""
    
    def __init__(self, game_logic, ui):
        self.game_logic = game_logic
        self.ui = ui
        self.key_repeat_manager = KeyRepeatManager()
    
    def handle_mouse_click(self, event, tower_buttons, control_buttons):
        """处理鼠标点击事件"""
        mouse_pos = pygame.mouse.get_pos()
        
        if self.game_logic.game_over:
            # 检查重新开始按钮
            if control_buttons["restart"].is_clicked(event):
                self.game_logic.initialize_game(self.game_logic.game_mode, self.game_logic.difficulty)
                self.ui.scroll_offset = 0
                self.ui.selected_tower = None
                return None
        else:
            # 检查是否可以交互
            can_interact = False
            if self.game_logic.game_mode == "PVP":
                can_interact = True
            elif self.game_logic.game_mode == "PVE" and self.game_logic.current_player == 1:
                can_interact = True
            
            if can_interact:
                # 检查炮塔点击
                for button in tower_buttons:
                    if button.is_clicked(event) and self.game_logic.towers[button.tower_id] == 1:
                        self.handle_tower_click(button.tower_id)
                        break
        
        # 检查导航按钮
        if "back" in control_buttons and control_buttons["back"].is_clicked(event):
            return "back"
        elif "home" in control_buttons and control_buttons["home"].is_clicked(event):
            return "home"
        
        return None
    
    def handle_tower_click(self, tower_id):
        """处理炮塔点击"""
        if self.ui.selected_tower is None:
            # 第一次选择炮塔
            self.ui.selected_tower = tower_id
        else:
            # 第二次选择炮塔
            if abs(self.ui.selected_tower - tower_id) == 1:
                # 检查是否相邻且都可用
                move_index = min(self.ui.selected_tower, tower_id)
                if move_index in self.game_logic.get_available_moves():
                    # 执行移动
                    self.game_logic.make_move(move_index)
            
            # 重置选择
            self.ui.selected_tower = None
        
        # 更新高亮显示
        self.ui.update_highlighted_towers(self.game_logic.get_available_moves(), self.ui.selected_tower)
    
    def handle_keyboard(self, event):
        """处理键盘事件"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.ui.scroll_left(self.game_logic.num_towers)
            elif event.key == pygame.K_RIGHT:
                self.ui.scroll_right(self.game_logic.num_towers)
    
    def update_key_repeat(self):
        """更新按键重复状态"""
        # 当前版本暂不需要按键重复
        pass

class DawsonKaylesGame(BaseGame):
    """Dawson-Kayles游戏实现"""
    
    def __init__(self, screen, font_manager):
        super().__init__(screen, font_manager)
        self.logic = DawsonKaylesLogic()
        self.ui = DawsonKaylesUI(screen, font_manager)
        self.input_handler = DawsonKaylesInputHandler(self.logic, self.ui)
        
        # 确保字体已初始化
        self.font_manager.initialize_fonts()
        
        # 初始化游戏设置
        self.initialize_game_settings()
        
        # 创建UI组件
        self.control_buttons = self.ui.create_control_buttons()
        self.tower_buttons = []
        self.ai_timer = 0
    
    def initialize_game_settings(self):
        """初始化游戏模式和难度"""
        try:
            # 使用游戏模式选择器
            selector = GameModeSelector(self.screen, self.font_manager)
            game_mode = selector.get_game_mode()
            
            if game_mode == "PVE":
                difficulty = selector.get_difficulty()
                self.logic.initialize_game("PVE", difficulty)
            else:
                self.logic.initialize_game("PVP")
                
        except Exception as e:
            print(f"Error initializing game settings: {e}")
            # 后备初始化
            self.logic.initialize_game("PVE", 2)
    
    def handle_events(self):
        """处理游戏事件"""
        mouse_pos = pygame.mouse.get_pos()
        
        # 更新按钮悬停状态
        for button in self.control_buttons.values():
            button.update_hover(mouse_pos)
        
        for button in self.tower_buttons:
            button.update_hover(mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                result = self.input_handler.handle_mouse_click(
                    event, self.tower_buttons, self.control_buttons
                )
                if result == "back":
                    # 重新初始化游戏设置
                    self.initialize_game_settings()
                    self.ui.scroll_offset = 0
                    self.ui.selected_tower = None
                elif result == "home":
                    # 返回主菜单
                    return False
            
            elif event.type in [pygame.KEYDOWN, pygame.KEYUP]:
                self.input_handler.handle_keyboard(event)
            
            elif event.type == pygame.MOUSEWHEEL:
                # 处理鼠标滚轮滚动
                self.ui.handle_mouse_wheel(event, self.logic.num_towers)
        
        return True
    
    def update(self):
        """更新游戏状态"""
        # 更新炮塔按钮
        self.tower_buttons = self.ui.create_tower_buttons(self.logic.num_towers)
        
        # AI的回合（仅在PvE模式）
        if (self.logic.game_mode == "PVE" and 
            self.logic.current_player == 2 and 
            not self.logic.game_over):
            
            self.ai_timer += 1
            # 添加延迟使AI移动可见
            if self.ai_timer > 30:
                self.logic.ai_make_move()
                self.ai_timer = 0
                self.ui.selected_tower = None
                # 更新高亮显示
                self.ui.update_highlighted_towers(self.logic.get_available_moves(), self.ui.selected_tower)
        
        # 更新高亮显示
        self.ui.update_highlighted_towers(self.logic.get_available_moves(), self.ui.selected_tower)
    
    def draw(self):
        """绘制完整的游戏界面"""
        try:
            # 绘制背景
            self.ui.draw_background()
            
            # 绘制游戏信息
            self.ui.draw_game_info(self.logic)
            
            # 绘制炮塔和激光
            self.ui.draw_towers(self.logic, self.tower_buttons)
            
            # 绘制控制面板
            self.ui.draw_control_panel(self.control_buttons, self.logic)
            
            # 绘制滚动条
            self.ui.draw_scrollbar(self.logic.num_towers)
            
            # 绘制导航按钮
            if "back" in self.control_buttons:
                self.control_buttons["back"].draw(self.screen)
            if "home" in self.control_buttons:
                self.control_buttons["home"].draw(self.screen)
            
            # 绘制重新开始按钮（游戏结束时）
            if self.logic.game_over:
                self.control_buttons["restart"].draw(self.screen)
            
            pygame.display.flip()
            
        except Exception as e:
            print(f"Error in draw: {e}")
            import traceback
            traceback.print_exc()
    
    def get_game_info(self):
        """返回游戏信息"""
        return {
            'name': 'Laser Defense - Dawson-Kayles',
            'description': 'Strategic tower connection game using Dawson-Kayles rules',
            'current_player': f"Player {self.logic.current_player}" if self.logic.current_player == 1 else "AI",
            'game_over': self.logic.game_over,
            'winner': f"Player {self.logic.winner}" if self.logic.winner else None,
            'towers_remaining': sum(self.logic.towers),
            'available_moves': len(self.logic.get_available_moves())
        }
    
    def run(self):
        """运行主游戏循环"""
        self.running = True
        while self.running:
            if not self.handle_events():
                break
            self.update()
            self.draw()
            self.clock.tick(CARD_GAME_FPS)