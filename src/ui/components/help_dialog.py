"""
Help Dialog Component
Displays game help and control guides
"""

import pygame
from .scrollables import ScrollablePanel
from .buttons import GameButton, IconButton
from utils.constants import *
from utils.game_help_content import get_game_help, get_controls_help

class HelpDialog:
    """Help dialog displaying game help and control guides"""
    
    def __init__(self, screen_width, screen_height, font_manager):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font_manager = font_manager
        self.visible = False

        # 显著增大对话框
        self.width = min(950, screen_width - 50)  # 增大宽度
        self.height = min(750, screen_height - 50)  # 增大高度

        self.x = (screen_width - self.width) // 2
        self.y = (screen_height - self.height) // 2

        # 优化滚动面板
        self.scroll_panel = ScrollablePanel(
            self.x + 40,  # 更大的左边距
            self.y + 180,  # 更大的顶部间距
            self.width - 80,  # 更大的内容宽度
            self.height - 250,  # 更大的内容高度
            font_manager
        )
        
        # Create tab buttons
        self.tab_buttons = []
        self.current_tab = 0  # 0: Gameplay, 1: Controls
        
        # Tabs definition
        self.tabs = [
            {"id": "gameplay", "name": "Gameplay"},
            {"id": "controls", "name": "Controls"}
        ]
        
        # Create game selection buttons
        self.game_buttons = []
        self.selected_game = "take_coins"
        
        # Create control section buttons
        self.control_sections = []
        
        # Create close button
        self.close_button = None
        
        # 键盘导航相关
        self.keyboard_selected_index = -1  # -1表示没有选中，0: tab, 1: game/control, 2: close
        self.keyboard_sub_index = 0        # 在当前类别中的索引

        # 删除原有的按键重复机制，改为简单模式
        # self.key_repeat_timer = 0
        # self.key_repeat_delay = KEY_REPEAT_DELAYS['initial']
        # self.last_key = None

        # 添加：记录上次处理的按键
        self.last_processed_key = None
        self.key_process_delay = 10  # 处理延迟（帧数）
        self.key_delay_counter = 0
        self._create_buttons()
        
        # Current content
        self.current_content = []

        # 添加当前选择状态
        self.current_selection = {
            'tab': 0,  # 0: Gameplay, 1: Controls
            'game': "take_coins",  # 当前选中的游戏
            'control_section': "keyboard"  # 当前选中的控制部分
        }
        
        # 高亮颜色
        self.highlight_color = KEY_NAVIGATION_COLORS['highlight']
        self.active_border_color = KEY_NAVIGATION_COLORS['active_border']
        self.active_bg_color = KEY_NAVIGATION_COLORS['active_bg']
        self.keyboard_selection_color = KEY_NAVIGATION_COLORS['selection_bg']
        self.keyboard_border_color = KEY_NAVIGATION_COLORS['selection_border']
    
    def _adjust_layout(self):
        """调整布局，确保不拥挤"""
        # 确保tab按钮水平居中
        total_tab_width = len(self.tab_buttons) * 160 + (len(self.tab_buttons) - 1) * 20
        tab_start_x = self.x + (self.width - total_tab_width) // 2

        for i, button in enumerate(self.tab_buttons):
            button.rect.x = tab_start_x + i * (160 + 20)
            button.rect.y = self.y + 60

        # 确保游戏按钮水平居中或换行显示
        total_game_width = len(self.game_buttons) * 140 + (len(self.game_buttons) - 1) * 15
        if total_game_width <= self.width - 80:
            # 一行可以放下，居中显示
            game_start_x = self.x + (self.width - total_game_width) // 2
            for i, button in enumerate(self.game_buttons):
                button.rect.x = game_start_x + i * (140 + 15)
                button.rect.y = self.y + 120
        else:
            # 分两行显示
            buttons_per_row = (self.width - 60) // (140 + 15)
            for i, button in enumerate(self.game_buttons):
                row = i // buttons_per_row
                col = i % buttons_per_row
                button.rect.x = self.x + 30 + col * (140 + 15)
                button.rect.y = self.y + 120 + row * (45 + 10)

        # 调整关闭按钮位置
        self.close_button.rect.x = self.x + self.width - 50 - 30
        self.close_button.rect.y = self.y + 45

    def _create_buttons(self):
        """Create all buttons for the dialog"""
        tab_button_width = 140
        tab_button_height = 40
        tab_start_x = self.x + 20
        
        for i, tab in enumerate(self.tabs):
            x = tab_start_x + i * (tab_button_width + 10)
            y = self.y + 80
            
            # 使用 GameButton 而不是 IconButton
            button = GameButton(
                x, y, tab_button_width, tab_button_height,
                tab["name"], self.font_manager,
                tooltip=f"Switch to {tab['name']} tab"
            )
            button.tab_index = i
            button.is_active = (i == self.current_tab)
            button.keyboard_hovered = False  # 添加键盘悬停状态
            self.tab_buttons.append(button)
        
        # Game selection buttons (only for gameplay tab)
        game_ids = ["take_coins", "split_cards", "card_nim", 
                   "dawson_kayles", "subtract_factor"]
        game_names = ["Take Coins", "Split Cards", "Card Nim", 
                     "Laser Defense", "Subtract Factor"]
        
        game_button_width = 140
        game_button_height = 35
        game_button_start_x = self.x + 20
        game_button_y = self.y + 125
        
        for i, (game_id, game_name) in enumerate(zip(game_ids, game_names)):
            x = game_button_start_x + i * (game_button_width + 10)
            
            # 使用 GameButton 而不是 IconButton
            button = GameButton(
                x, game_button_y, game_button_width, game_button_height,
                game_name, self.font_manager.small,
                tooltip=f"Show help for {game_name}"
            )
            button.game_id = game_id
            button.is_active = (game_id == self.selected_game)
            button.keyboard_hovered = False  # 添加键盘悬停状态
            self.game_buttons.append(button)
        
        # Control section buttons (only for controls tab)
        control_sections = ["keyboard", "mouse", "game_specific"]
        section_names = ["Keyboard", "Mouse", "Game Specific"]
        
        control_button_width = 140
        control_button_height = 35
        control_button_start_x = self.x + 20
        control_button_y = self.y + 125
        
        for i, (section_id, section_name) in enumerate(zip(control_sections, section_names)):
            x = control_button_start_x + i * (control_button_width + 10)
            
            # 使用 GameButton 而不是 IconButton
            button = GameButton(
                x, control_button_y, control_button_width, control_button_height,
                section_name, self.font_manager.small,
                tooltip=f"Show {section_name.lower()} controls"
            )
            button.section_id = section_id
            button.is_active = (i == 0)  # First section active by default
            button.keyboard_hovered = False  # 添加键盘悬停状态
            self.control_sections.append(button)
        
        # Close button
        close_button_size = 40
        self.close_button = GameButton(
            self.x + self.width - close_button_size - 20,
            self.y + 30,
            close_button_size, close_button_size,
            "", self.font_manager,
            icon='close',
            tooltip="Close help (ESC)"
        )
        self.close_button.keyboard_hovered = False  # 添加键盘悬停状态
    
    def show(self):
        """Show the help dialog"""
        self.visible = True
        self._reset_keyboard_navigation()
        self._load_content()

    def _reset_keyboard_navigation(self):
        """重置键盘导航状态"""
        self.keyboard_selected_index = 0  # 默认选中第一个tab按钮
        self.keyboard_sub_index = 0
        self.last_processed_key = None
        self.key_delay_counter = 0

        # 更新悬停状态
        self._update_keyboard_hover()
    
    def hide(self):
        """Hide the help dialog"""
        self.visible = False
        self.keyboard_selected_index = -1
        self.keyboard_sub_index = 0
    
    def toggle(self):
        """Toggle visibility of help dialog"""
        self.visible = not self.visible
        if self.visible:
            self._reset_keyboard_navigation()
            self._load_content()
        else:
            self.keyboard_selected_index = -1
            self.keyboard_sub_index = 0
    
    def _update_keyboard_hover(self):
        """更新键盘悬停状态"""
        # 重置所有按钮的键盘悬停状态
        for button in self.tab_buttons:
            button.keyboard_hovered = False
        
        for button in self.game_buttons:
            button.keyboard_hovered = False
            
        for button in self.control_sections:
            button.keyboard_hovered = False
        
        self.close_button.keyboard_hovered = False
        
        # 根据当前选择设置悬停状态
        if self.keyboard_selected_index == 0:  # Tab按钮
            if 0 <= self.keyboard_sub_index < len(self.tab_buttons):
                self.tab_buttons[self.keyboard_sub_index].keyboard_hovered = True
        elif self.keyboard_selected_index == 1:  # 游戏/控制按钮
            if self.current_tab == 0:  # Gameplay tab
                if 0 <= self.keyboard_sub_index < len(self.game_buttons):
                    self.game_buttons[self.keyboard_sub_index].keyboard_hovered = True
            else:  # Controls tab
                if 0 <= self.keyboard_sub_index < len(self.control_sections):
                    self.control_sections[self.keyboard_sub_index].keyboard_hovered = True
        elif self.keyboard_selected_index == 2:  # 关闭按钮
            self.close_button.keyboard_hovered = True
    
    def _handle_keyboard_navigation(self, keys):
        """处理键盘导航"""
        if not self.visible:
            return False
        
        # 检查是否应该处理键盘重复
        should_handle = False
        if any(keys[key] for key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]):
            if self.key_repeat_timer == 0:
                should_handle = True
                self.key_repeat_timer = self.key_repeat_delay
            else:
                self.key_repeat_timer -= 1
        else:
            self.key_repeat_timer = 0
            self.key_repeat_delay = KEY_REPEAT_DELAYS['initial']
        
        if not should_handle:
            return False
        
        handled = False
        
        # 向上/向下导航
        if keys[pygame.K_UP]:
            if self.keyboard_selected_index > 0:
                self.keyboard_selected_index -= 1
                self.keyboard_sub_index = 0  # 重置子索引
                handled = True
        elif keys[pygame.K_DOWN]:
            if self.keyboard_selected_index < 2:
                self.keyboard_selected_index += 1
                self.keyboard_sub_index = 0  # 重置子索引
                handled = True
        
        # 向左/向右导航（在当前层级内）
        elif keys[pygame.K_LEFT]:
            handled = self._move_left()
        elif keys[pygame.K_RIGHT]:
            handled = self._move_right()
        
        # 回车键选择
        elif keys[pygame.K_RETURN] or keys[pygame.K_SPACE]:
            handled = self._select_current_item()
        
        if handled:
            self._update_keyboard_hover()
        
        return handled
    
    def _handle_simple_keyboard_navigation(self, key):
        """简单的键盘导航处理（每次按键只处理一次）"""
        if not self.visible:
            return False

        # 防重复处理：如果和上次按键相同且在延迟期内，跳过
        if key == self.last_processed_key and self.key_delay_counter > 0:
            self.key_delay_counter -= 1
            return False

        handled = False

        # 如果没有当前选择，初始化到第一个tab
        if self.keyboard_selected_index == -1:
            self.keyboard_selected_index = 0
            self.keyboard_sub_index = 0
            self._update_keyboard_hover()
            handled = True

        # 向上导航
        elif key == pygame.K_UP:
            if self.keyboard_selected_index > 0:
                self.keyboard_selected_index -= 1
                self.keyboard_sub_index = 0  # 重置子索引
                handled = True

        # 向下导航
        elif key == pygame.K_DOWN:
            if self.keyboard_selected_index < 2:
                self.keyboard_selected_index += 1
                self.keyboard_sub_index = 0  # 重置子索引
                handled = True

        # 向左导航
        elif key == pygame.K_LEFT:
            handled = self._move_left()

        # 向右导航
        elif key == pygame.K_RIGHT:
            handled = self._move_right()

        # 回车或空格键选择
        elif key == pygame.K_RETURN or key == pygame.K_SPACE:
            handled = self._select_current_item()

        # 更新状态
        if handled:
            self._update_keyboard_hover()
            self.last_processed_key = key
            self.key_delay_counter = self.key_process_delay

        return handled

    def _move_left(self):
        """向左移动"""
        if self.keyboard_selected_index == 0:  # Tab按钮
            if self.keyboard_sub_index > 0:
                self.keyboard_sub_index -= 1
                return True
        elif self.keyboard_selected_index == 1:  # 游戏/控制按钮
            if self.keyboard_sub_index > 0:
                self.keyboard_sub_index -= 1
                return True
        return False
    
    def _move_right(self):
        """向右移动"""
        if self.keyboard_selected_index == 0:  # Tab按钮
            if self.keyboard_sub_index < len(self.tab_buttons) - 1:
                self.keyboard_sub_index += 1
                return True
        elif self.keyboard_selected_index == 1:  # 游戏/控制按钮
            max_index = len(self.game_buttons) - 1 if self.current_tab == 0 else len(self.control_sections) - 1
            if self.keyboard_sub_index < max_index:
                self.keyboard_sub_index += 1
                return True
        return False
    
    def _select_current_item(self):
        """选择当前项目"""
        if self.keyboard_selected_index == 0:  # Tab按钮
            if 0 <= self.keyboard_sub_index < len(self.tab_buttons):
                # 模拟点击tab按钮
                button = self.tab_buttons[self.keyboard_sub_index]
                # 更新active states
                for btn in self.tab_buttons:
                    btn.is_active = (btn == button)
                self.current_tab = button.tab_index
                self._load_content()
                return True
                
        elif self.keyboard_selected_index == 1:  # 游戏/控制按钮
            if self.current_tab == 0:  # Gameplay tab
                if 0 <= self.keyboard_sub_index < len(self.game_buttons):
                    button = self.game_buttons[self.keyboard_sub_index]
                    # 更新active states
                    for btn in self.game_buttons:
                        btn.is_active = (btn == button)
                    self.selected_game = button.game_id
                    self._load_content()
                    return True
            else:  # Controls tab
                if 0 <= self.keyboard_sub_index < len(self.control_sections):
                    button = self.control_sections[self.keyboard_sub_index]
                    # 更新active states
                    for btn in self.control_sections:
                        btn.is_active = (btn == button)
                    self._load_content()
                    return True
                    
        elif self.keyboard_selected_index == 2:  # 关闭按钮
            self.hide()
            return True
        
        return False
    
    def _load_content(self):
        """Load content based on current selection"""
        self.scroll_panel.clear_content()
        
        if self.current_tab == 0:  # Gameplay tab
            help_data = get_game_help(self.selected_game, "gameplay")
            if help_data:
                # Add title
                self.scroll_panel.add_line(
                    help_data["title"], 
                    (220, 220, 255), 
                    'large',
                    centered=True
                )
                self.scroll_panel.add_spacing(20)
                
                # Add content
                for line in help_data["content"]:
                    if line == "":
                        self.scroll_panel.add_spacing(10)
                    else:
                        color = (200, 200, 220) if line.startswith("•") else (180, 200, 255)
                        font_size = 'small' if line.startswith("•") else 'medium'
                        self.scroll_panel.add_line(line, color, font_size)
        
        else:  # Controls tab
            # Find active control section
            active_section = None
            for btn in self.control_sections:
                if btn.is_active:
                    active_section = btn.section_id
                    break
            
            if active_section:
                content = get_controls_help(active_section)
                # Add title
                title_map = {
                    "keyboard": "Keyboard Controls",
                    "mouse": "Mouse Controls",
                    "game_specific": "Game-Specific Controls"
                }
                self.scroll_panel.add_line(
                    title_map.get(active_section, "Controls"),
                    (220, 220, 255),
                    'large',
                    centered=True
                )
                self.scroll_panel.add_spacing(20)
                
                # Add content
                for line in content:
                    if line == "":
                        self.scroll_panel.add_spacing(10)
                    else:
                        color = (200, 200, 220) if line.startswith("•") else (180, 200, 255)
                        font_size = 'small' if line.startswith("•") else 'medium'
                        self.scroll_panel.add_line(line, color, font_size)
    
    def handle_event(self, event):
        """Handle events for the help dialog"""
        if not self.visible:
            return False
        
        mouse_pos = pygame.mouse.get_pos()
        
        # Update button hover states
        for button in self.tab_buttons:
            button.update_hover(mouse_pos)
        
        if self.current_tab == 0:
            for button in self.game_buttons:
                button.update_hover(mouse_pos)
        else:
            for button in self.control_sections:
                button.update_hover(mouse_pos)
        
        self.close_button.update_hover(mouse_pos)
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # 点击时重置键盘导航
            self.keyboard_selected_index = -1
            self.keyboard_sub_index = 0
            self._update_keyboard_hover()
            
            # Check close button
            if self.close_button.is_clicked(event):
                self.hide()
                return True
            
            # Check tab buttons
            for button in self.tab_buttons:
                if button.is_clicked(event):
                    # Update active states
                    for btn in self.tab_buttons:
                        btn.is_active = (btn == button)
                    self.current_tab = button.tab_index
                    self._load_content()
                    return True
            
            # Check game buttons (if in gameplay tab)
            if self.current_tab == 0:
                for button in self.game_buttons:
                    if button.is_clicked(event):
                        # Update active states
                        for btn in self.game_buttons:
                            btn.is_active = (btn == button)
                        self.selected_game = button.game_id
                        self._load_content()
                        return True
            
            # Check control section buttons (if in controls tab)
            if self.current_tab == 1:
                for button in self.control_sections:
                    if button.is_clicked(event):
                        # Update active states
                        for btn in self.control_sections:
                            btn.is_active = (btn == button)
                        self._load_content()
                        return True
            
            # Check if click was inside scroll panel
            if self.scroll_panel.rect.collidepoint(mouse_pos):
                self.scroll_panel.handle_event(event)
                return True
        
        elif event.type == pygame.MOUSEWHEEL:
            # Handle mouse wheel scrolling
            if self.scroll_panel.rect.collidepoint(mouse_pos):
                self.scroll_panel.handle_event(event)
                return True
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.hide()
                return True
            elif event.key == pygame.K_h:
                self.hide()
                return True
            else:
                # 处理键盘导航 - 简单模式
                return self._handle_simple_keyboard_navigation(event.key)
        
        return False
    
    def draw(self, screen):
        """Draw the help dialog"""
        if not self.visible:
            return
        
        # Draw semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # Draw dialog background
        pygame.draw.rect(screen, (30, 35, 50), 
                        (self.x, self.y, self.width, self.height), 
                        border_radius=15)
        pygame.draw.rect(screen, (60, 70, 100), 
                        (self.x, self.y, self.width, self.height), 
                        2, border_radius=15)
        
        # Draw title
        title = self.font_manager.large.render("Game Help & Guide", True, (220, 220, 255))
        screen.blit(title, (self.x + 20, self.y + 30))
        
        # Draw tab buttons
        for button in self.tab_buttons:
            # 如果按钮有键盘悬停状态，绘制高亮效果
            if button.keyboard_hovered:
                highlight_rect = button.rect.inflate(10, 10)
                highlight_surface = pygame.Surface((highlight_rect.width, highlight_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(highlight_surface, self.keyboard_selection_color, 
                               (0, 0, highlight_rect.width, highlight_rect.height), 
                               border_radius=button.corner_radius + 5)
                screen.blit(highlight_surface, highlight_rect)
                pygame.draw.rect(screen, self.keyboard_border_color, highlight_rect, 2, 
                               border_radius=button.corner_radius + 5)
            
            # Update button color based on active state
            if button.is_active:
                button.base_color = self.active_bg_color
                button.hover_color = (self.active_bg_color[0]+20, self.active_bg_color[1]+20, self.active_bg_color[2]+20)
            else:
                button.base_color = (60, 70, 100)
                button.hover_color = (80, 90, 130)
            button.draw(screen)
        
        # Draw game selection buttons (only for gameplay tab)
        if self.current_tab == 0:
            for button in self.game_buttons:
                # 如果按钮有键盘悬停状态，绘制高亮效果
                if button.keyboard_hovered:
                    highlight_rect = button.rect.inflate(8, 8)
                    highlight_surface = pygame.Surface((highlight_rect.width, highlight_rect.height), pygame.SRCALPHA)
                    pygame.draw.rect(highlight_surface, self.keyboard_selection_color, 
                                   (0, 0, highlight_rect.width, highlight_rect.height), 
                                   border_radius=button.corner_radius + 4)
                    screen.blit(highlight_surface, highlight_rect)
                    pygame.draw.rect(screen, self.keyboard_border_color, highlight_rect, 2, 
                                   border_radius=button.corner_radius + 4)
                
                # Update button color based on active state
                if button.is_active:
                    button.base_color = self.active_bg_color
                    button.hover_color = (self.active_bg_color[0]+20, self.active_bg_color[1]+20, self.active_bg_color[2]+20)
                else:
                    button.base_color = (50, 60, 90)
                    button.hover_color = (70, 80, 120)
                button.draw(screen)
        
        # Draw control section buttons (only for controls tab)
        if self.current_tab == 1:
            for button in self.control_sections:
                # 如果按钮有键盘悬停状态，绘制高亮效果
                if button.keyboard_hovered:
                    highlight_rect = button.rect.inflate(8, 8)
                    highlight_surface = pygame.Surface((highlight_rect.width, highlight_rect.height), pygame.SRCALPHA)
                    pygame.draw.rect(highlight_surface, self.keyboard_selection_color, 
                                   (0, 0, highlight_rect.width, highlight_rect.height), 
                                   border_radius=button.corner_radius + 4)
                    screen.blit(highlight_surface, highlight_rect)
                    pygame.draw.rect(screen, self.keyboard_border_color, highlight_rect, 2, 
                                   border_radius=button.corner_radius + 4)
                
                # Update button color based on active state
                if button.is_active:
                    button.base_color = self.active_bg_color
                    button.hover_color = (self.active_bg_color[0]+20, self.active_bg_color[1]+20, self.active_bg_color[2]+20)
                else:
                    button.base_color = (50, 60, 90)
                    button.hover_color = (70, 80, 120)
                button.draw(screen)
        
        # Draw close button
        if self.close_button.keyboard_hovered:
            highlight_rect = self.close_button.rect.inflate(8, 8)
            highlight_surface = pygame.Surface((highlight_rect.width, highlight_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(highlight_surface, self.keyboard_selection_color, 
                           (0, 0, highlight_rect.width, highlight_rect.height), 
                           border_radius=self.close_button.corner_radius + 4)
            screen.blit(highlight_surface, highlight_rect)
            pygame.draw.rect(screen, self.keyboard_border_color, highlight_rect, 2, 
                           border_radius=self.close_button.corner_radius + 4)
        
        self.close_button.draw(screen)
        
        # Draw scroll panel
        self.scroll_panel.draw(screen)
        
        # Draw instructions footer
        footer = self.font_manager.small.render(
            "Use mouse wheel to scroll • Click buttons to navigate • ESC to close",
            True, (150, 170, 190)
        )
        screen.blit(footer, (self.x + self.width//2 - footer.get_width()//2, 
                            self.y + self.height - 30))
        
        # 绘制键盘导航提示
        if self.keyboard_selected_index >= 0:
            nav_text = self.font_manager.small.render(
                "↑/↓: Navigate between sections • ←/→: Select items • ENTER: Activate",
                True, (180, 220, 255)
            )
            screen.blit(nav_text, (self.x + 20, self.y + self.height - 60))
    
    def _is_inside_dialog(self, pos):
        """Check if a position is inside the dialog"""
        return (self.x <= pos[0] <= self.x + self.width and 
                self.y <= pos[1] <= self.y + self.height)