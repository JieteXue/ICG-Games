"""
TopBar Component for Main Menu
顶部工具栏，包含设置按钮等
"""

import pygame
from utils.constants import *

class TopBar:
    """顶部工具栏，显示在主菜单左上角"""
    
    def __init__(self, screen, font_manager, music_manager=None):
        self.screen = screen
        self.font_manager = font_manager
        self.music_manager = music_manager
        
        # 顶部工具栏尺寸
        self.height = 50
        self.width = SCREEN_WIDTH
        
        # 设置按钮
        button_width = 120
        button_height = 40
        self.settings_button_rect = pygame.Rect(
            20,  # 左边距
            5,   # 上边距
            button_width,
            button_height
        )
        
        # 音乐状态指示器
        self.music_indicator_rect = pygame.Rect(
            self.settings_button_rect.right + 15,
            10,
            30,
            30
        )
        
        # 设置面板引用（由外部传入）
        self.settings_panel = None
    
    def set_settings_panel(self, settings_panel):
        """设置settings_panel引用"""
        self.settings_panel = settings_panel
    
    def handle_event(self, event, mouse_pos):
        """处理事件"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # 检查设置按钮
            if self.settings_button_rect.collidepoint(mouse_pos):
                if self.settings_panel:
                    self.settings_panel.show()
                    return "open_settings"
                else:
                    print("⚠️ Settings panel not set for TopBar")
            
            # 检查音乐状态指示器（点击可快速切换音乐）
            if self.music_indicator_rect.collidepoint(mouse_pos):
                if self.music_manager:
                    new_state = self.music_manager.toggle_music()
                    print(f"🎵 Music toggled from TopBar: {new_state}")
                    return "music_toggled"
        
        return None
    
    def draw(self):
        """绘制顶部工具栏"""
        # 绘制背景
        topbar_rect = pygame.Rect(0, 0, self.width, self.height)
        pygame.draw.rect(self.screen, (20, 30, 45), topbar_rect)
        
        # 绘制底部分隔线
        pygame.draw.line(self.screen, ACCENT_COLOR, 
                        (0, self.height), 
                        (self.width, self.height), 2)
        
        # 绘制设置按钮
        self._draw_settings_button()
        
        # 绘制音乐状态指示器
        self._draw_music_indicator()
        
        # 绘制标题
        self._draw_title()
    
    def _draw_settings_button(self):
        """绘制设置按钮"""
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.settings_button_rect.collidepoint(mouse_pos)
        
        # 按钮颜色
        button_color = BUTTON_HOVER_COLOR if is_hovered else (60, 70, 100)
        
        # 绘制按钮背景
        pygame.draw.rect(self.screen, button_color, self.settings_button_rect, border_radius=8)
        pygame.draw.rect(self.screen, ACCENT_COLOR, self.settings_button_rect, 2, border_radius=8)
        
        # 绘制齿轮图标
        gear_center_x = self.settings_button_rect.left + 25
        gear_center_y = self.settings_button_rect.centery
        self._draw_gear_icon(gear_center_x, gear_center_y)
        
        # 绘制"Settings"文字
        settings_text = self.font_manager.small.render("Settings", True, (255, 255, 255))
        text_x = self.settings_button_rect.left + 45
        text_y = self.settings_button_rect.centery - settings_text.get_height() // 2
        self.screen.blit(settings_text, (text_x, text_y))
        
        # 悬停提示
        if is_hovered:
            tooltip = self.font_manager.small.render("Game settings", True, (200, 220, 255))
            tooltip_rect = tooltip.get_rect(midleft=(self.settings_button_rect.right + 10, 
                                                    self.settings_button_rect.centery))
            pygame.draw.rect(self.screen, (40, 50, 70), 
                           (tooltip_rect.x - 5, tooltip_rect.y - 3,
                            tooltip_rect.width + 10, tooltip_rect.height + 6),
                           border_radius=4)
            pygame.draw.rect(self.screen, (100, 150, 200),
                           (tooltip_rect.x - 5, tooltip_rect.y - 3,
                            tooltip_rect.width + 10, tooltip_rect.height + 6),
                           1, border_radius=4)
            self.screen.blit(tooltip, tooltip_rect)
    
    def _draw_gear_icon(self, center_x, center_y):
        """绘制齿轮图标"""
        # 绘制齿轮外圈
        radius = 10
        pygame.draw.circle(self.screen, (220, 220, 240), (center_x, center_y), radius)
        pygame.draw.circle(self.screen, (100, 150, 200), (center_x, center_y), radius, 2)
        
        # 绘制齿轮齿
        for i in range(6):
            angle = i * 60  # 60度间隔
            x1 = center_x + (radius-2) * pygame.math.Vector2(1, 0).rotate(angle).x
            y1 = center_y + (radius-2) * pygame.math.Vector2(1, 0).rotate(angle).y
            x2 = center_x + (radius+5) * pygame.math.Vector2(1, 0).rotate(angle).x
            y2 = center_y + (radius+5) * pygame.math.Vector2(1, 0).rotate(angle).y
            pygame.draw.line(self.screen, (100, 150, 200), (x1, y1), (x2, y2), 2)
        
        # 绘制中心孔
        pygame.draw.circle(self.screen, (60, 70, 100), (center_x, center_y), 4)
    
    def _draw_music_indicator(self):
        """绘制音乐状态指示器"""
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.music_indicator_rect.collidepoint(mouse_pos)
        
        # 根据音乐状态选择颜色
        if self.music_manager and self.music_manager.is_music_enabled():
            indicator_color = (100, 200, 100)  # 绿色表示音乐开启
            border_color = (150, 255, 150)
        else:
            indicator_color = (200, 100, 100)  # 红色表示音乐关闭
            border_color = (255, 150, 150)
        
        # 绘制指示器
        pygame.draw.rect(self.screen, indicator_color, self.music_indicator_rect, border_radius=6)
        pygame.draw.rect(self.screen, border_color, self.music_indicator_rect, 2, border_radius=6)
        
        # 绘制音符图标
        if self.music_manager and self.music_manager.is_music_enabled():
            self._draw_music_note(self.music_indicator_rect.centerx, 
                                 self.music_indicator_rect.centery)
        else:
            self._draw_music_off(self.music_indicator_rect.centerx, 
                                self.music_indicator_rect.centery)
        
        # 悬停提示
        if is_hovered:
            status = "ON" if (self.music_manager and self.music_manager.is_music_enabled()) else "OFF"
            tooltip = self.font_manager.small.render(f"Click to toggle music ({status})", 
                                                    True, (200, 220, 255))
            tooltip_rect = tooltip.get_rect(midleft=(self.music_indicator_rect.right + 10, 
                                                    self.music_indicator_rect.centery))
            pygame.draw.rect(self.screen, (40, 50, 70), 
                           (tooltip_rect.x - 5, tooltip_rect.y - 3,
                            tooltip_rect.width + 10, tooltip_rect.height + 6),
                           border_radius=4)
            pygame.draw.rect(self.screen, (100, 150, 200),
                           (tooltip_rect.x - 5, tooltip_rect.y - 3,
                            tooltip_rect.width + 10, tooltip_rect.height + 6),
                           1, border_radius=4)
            self.screen.blit(tooltip, tooltip_rect)
    
    def _draw_music_note(self, center_x, center_y):
        """绘制音符图标（音乐开启状态）"""
        # 绘制音符主体
        note_rect = pygame.Rect(center_x - 6, center_y - 8, 12, 16)
        pygame.draw.ellipse(self.screen, (255, 255, 255), note_rect)
        
        # 绘制音符杆
        pygame.draw.line(self.screen, (255, 255, 255), 
                        (center_x + 6, center_y - 8), 
                        (center_x + 6, center_y - 16), 3)
        
        # 绘制音符旗
        pygame.draw.line(self.screen, (255, 255, 255), 
                        (center_x + 6, center_y - 16), 
                        (center_x + 12, center_y - 20), 2)
    
    def _draw_music_off(self, center_x, center_y):
        """绘制静音图标（音乐关闭状态）"""
        # 绘制音符主体（灰色）
        note_rect = pygame.Rect(center_x - 6, center_y - 8, 12, 16)
        pygame.draw.ellipse(self.screen, (150, 150, 150), note_rect)
        
        # 绘制禁止符号
        pygame.draw.line(self.screen, (255, 100, 100), 
                        (center_x - 8, center_y - 8), 
                        (center_x + 8, center_y + 8), 3)
    
    def _draw_title(self):
        """绘制标题"""
        title_text = self.font_manager.large.render("ICG GAMES", True, (0, 200, 255))
        title_x = SCREEN_WIDTH // 2 - title_text.get_width() // 2
        title_y = self.height // 2 - title_text.get_height() // 2
        self.screen.blit(title_text, (title_x, title_y))