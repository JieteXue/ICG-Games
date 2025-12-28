"""
Help Dialog Component - Simplified version with full keyboard navigation
Displays game help and control guides
"""

import pygame
from .scrollables import ScrollablePanel
from .buttons import GameButton
from utils.constants import *
from utils.game_help_content import get_game_help, get_controls_help

class HelpDialog:
    """Help dialog with full keyboard navigation support"""
    
    def __init__(self, screen_width, screen_height, font_manager):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font_manager = font_manager
        self.visible = False

        # Dialog size
        self.width = min(950, screen_width - 50)
        self.height = min(750, screen_height - 50)
        self.x = (screen_width - self.width) // 2
        self.y = (screen_height - self.height) // 2

        # Scroll panel
        self.scroll_panel = ScrollablePanel(
            self.x + 40,
            self.y + 180,
            self.width - 80,
            self.height - 250,
            font_manager
        )
        
        # Navigation state
        self.current_tab = 0  # 0: Gameplay, 1: Controls
        self.selected_game = "take_coins"
        
        # Keyboard navigation
        self.keyboard_selection = {
            'level': 0,      # 0: tabs, 1: content, 2: close
            'index': 0       # index within current level
        }
        
        # Button groups
        self.tab_buttons = []
        self.game_buttons = []
        self.control_buttons = []
        self.close_button = None
        
        # Create UI
        self._create_ui()
        
        # Load initial content
        self._load_content()
    
    def _create_ui(self):
        """Create all UI elements"""
        # Tab buttons
        tab_names = ["Gameplay", "Controls"]
        tab_width = 160
        tab_height = 45
        tab_start_x = self.x + (self.width - (len(tab_names) * tab_width + (len(tab_names)-1) * 20)) // 2
        
        for i, name in enumerate(tab_names):
            x = tab_start_x + i * (tab_width + 20)
            y = self.y + 70
            
            button = GameButton(
                x, y, tab_width, tab_height,
                name, self.font_manager,
                tooltip=f"Switch to {name} tab"
            )
            button.tab_index = i
            button.is_active = (i == self.current_tab)
            button.keyboard_hovered = False
            self.tab_buttons.append(button)
        
        # Game selection buttons
        game_data = [
            ("take_coins", "Take Coins"),
            ("split_cards", "Split Cards"),
            ("card_nim", "Card Nim"),
            ("dawson_kayles", "Laser Defense"),
            ("subtract_factor", "Subtract Factor")
        ]
        
        game_button_width = 150
        game_button_height = 40
        game_start_x = self.x + (self.width - (len(game_data) * game_button_width + (len(game_data)-1) * 15)) // 2
        game_y = self.y + 130
        
        for i, (game_id, game_name) in enumerate(game_data):
            x = game_start_x + i * (game_button_width + 15)
            
            button = GameButton(
                x, game_y, game_button_width, game_button_height,
                game_name, self.font_manager.small,
                tooltip=f"Show help for {game_name}"
            )
            button.game_id = game_id
            button.is_active = (game_id == self.selected_game)
            button.keyboard_hovered = False
            self.game_buttons.append(button)
        
        # Control section buttons
        control_data = [
            ("keyboard", "Keyboard"),
            ("mouse", "Mouse"),
            ("game_specific", "Game Specific")
        ]
        
        control_button_width = 150
        control_button_height = 40
        control_start_x = self.x + (self.width - (len(control_data) * control_button_width + (len(control_data)-1) * 15)) // 2
        control_y = self.y + 130
        
        for i, (section_id, section_name) in enumerate(control_data):
            x = control_start_x + i * (control_button_width + 15)
            
            button = GameButton(
                x, control_y, control_button_width, control_button_height,
                section_name, self.font_manager.small,
                tooltip=f"Show {section_name.lower()} controls"
            )
            button.section_id = section_id
            button.is_active = (i == 0)
            button.keyboard_hovered = False
            self.control_buttons.append(button)
        
        # Close button
        close_size = 45
        self.close_button = GameButton(
            self.x + self.width - close_size - 25,
            self.y + 25,
            close_size, close_size,
            "", self.font_manager,
            icon='close',
            tooltip="Close help (ESC)"
        )
        self.close_button.keyboard_hovered = False
    
    def show(self):
        """Show the dialog and enable keyboard repeat"""
        self.visible = True
        self._reset_keyboard_selection()
        
        # Enable key repeat for continuous movement
        pygame.key.set_repeat(300, 100)  # 300ms initial delay, 100ms repeat
    
    def hide(self):
        """Hide the dialog and disable keyboard repeat"""
        self.visible = False
        
        # Disable key repeat when dialog is hidden
        pygame.key.set_repeat(0)
    
    def toggle(self):
        """Toggle visibility"""
        if self.visible:
            self.hide()
        else:
            self.show()
    
    def _reset_keyboard_selection(self):
        """Reset keyboard selection to default state"""
        self.keyboard_selection = {'level': 0, 'index': 0}
        self._update_button_states()
    
    def _update_button_states(self):
        """Update all button states based on keyboard selection"""
        # Reset all buttons
        for button in self.tab_buttons:
            button.keyboard_hovered = False
        
        for button in self.game_buttons:
            button.keyboard_hovered = False
        
        for button in self.control_buttons:
            button.keyboard_hovered = False
        
        self.close_button.keyboard_hovered = False
        
        # Set keyboard hover for selected button
        level = self.keyboard_selection['level']
        index = self.keyboard_selection['index']
        
        if level == 0:  # Tab buttons
            if 0 <= index < len(self.tab_buttons):
                self.tab_buttons[index].keyboard_hovered = True
        
        elif level == 1:  # Content buttons
            if self.current_tab == 0:  # Gameplay
                if 0 <= index < len(self.game_buttons):
                    self.game_buttons[index].keyboard_hovered = True
            else:  # Controls
                if 0 <= index < len(self.control_buttons):
                    self.control_buttons[index].keyboard_hovered = True
        
        elif level == 2:  # Close button
            self.close_button.keyboard_hovered = True
    
    def _get_current_button_group(self):
        """Get the current active button group based on level and tab"""
        level = self.keyboard_selection['level']
        
        if level == 0:
            return self.tab_buttons
        elif level == 1:
            if self.current_tab == 0:
                return self.game_buttons
            else:
                return self.control_buttons
        elif level == 2:
            return [self.close_button]
        
        return []
    
    def _navigate_up_down(self, direction):
        """Navigate up (-1) or down (+1) between levels"""
        current_level = self.keyboard_selection['level']
        new_level = current_level + direction
        
        # Wrap around: 0 -> 1 -> 2 -> 0
        if new_level < 0:
            new_level = 2
        elif new_level > 2:
            new_level = 0
        
        self.keyboard_selection['level'] = new_level
        self.keyboard_selection['index'] = 0  # Reset index when changing levels
        self._update_button_states()
        return True
    
    def _navigate_left_right(self, direction):
        level = self.keyboard_selection['level']
        index = self.keyboard_selection['index']
        buttons = self._get_current_button_group()

        if not buttons:
            return False

        new_index = index + direction

        if new_index < 0:
            new_index = len(buttons) - 1
        elif new_index >= len(buttons):
            new_index = 0

        self.keyboard_selection['index'] = new_index
        self._update_button_states()

        # Activate new selection
        if level == 0:  # Tab按钮
            button = self.tab_buttons[new_index]
            if button.tab_index != self.current_tab:
                self.current_tab = button.tab_index
                for btn in self.tab_buttons:
                    btn.is_active = (btn == button)
                self._load_content()

        elif level == 1:  # 内容按钮
            if self.current_tab == 0:  # Gameplay
                button = self.game_buttons[new_index]
                if button.game_id != self.selected_game:
                    self.selected_game = button.game_id
                    for btn in self.game_buttons:
                        btn.is_active = (btn == button)
                    self._load_content()
            else:  # Controls
                button = self.control_buttons[new_index]
                for btn in self.control_buttons:
                    btn.is_active = (btn == button)
                self._load_content()

        return True
    
    def _activate_current_selection(self):
        """Activate the currently selected item"""
        level = self.keyboard_selection['level']
        index = self.keyboard_selection['index']
        
        if level == 0:  # Tab button
            if 0 <= index < len(self.tab_buttons):
                button = self.tab_buttons[index]
                # Update active states
                for btn in self.tab_buttons:
                    btn.is_active = (btn == button)
                self.current_tab = button.tab_index
                self._load_content()
                return True
        
        elif level == 1:  # Content button
            if self.current_tab == 0:  # Gameplay
                if 0 <= index < len(self.game_buttons):
                    button = self.game_buttons[index]
                    # Update active states
                    for btn in self.game_buttons:
                        btn.is_active = (btn == button)
                    self.selected_game = button.game_id
                    self._load_content()
                    return True
            else:  # Controls
                if 0 <= index < len(self.control_buttons):
                    button = self.control_buttons[index]
                    # Update active states
                    for btn in self.control_buttons:
                        btn.is_active = (btn == button)
                    self._load_content()
                    return True
        
        elif level == 2:  # Close button
            self.hide()
            return True
        
        return False
    
    def _load_content(self):
        """Load content based on current selection"""
        self.scroll_panel.clear_content()
        
        if self.current_tab == 0:  # Gameplay
            help_data = get_game_help(self.selected_game, "gameplay")
            if help_data:
                self.scroll_panel.add_line(
                    help_data["title"], 
                    (220, 220, 255), 
                    'large',
                    centered=True
                )
                self.scroll_panel.add_spacing(20)
                
                for line in help_data["content"]:
                    if line == "":
                        self.scroll_panel.add_spacing(10)
                    else:
                        color = (200, 200, 220) if line.startswith("•") else (180, 200, 255)
                        font_size = 'small' if line.startswith("•") else 'medium'
                        self.scroll_panel.add_line(line, color, font_size)
        
        else:  # Controls
            active_section = None
            for btn in self.control_buttons:
                if btn.is_active:
                    active_section = btn.section_id
                    break
            
            if active_section:
                content = get_controls_help(active_section)
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
                
                for line in content:
                    if line == "":
                        self.scroll_panel.add_spacing(10)
                    else:
                        color = (200, 200, 220) if line.startswith("•") else (180, 200, 255)
                        font_size = 'small' if line.startswith("•") else 'medium'
                        self.scroll_panel.add_line(line, color, font_size)
    
    def handle_event(self, event):
        """Handle events for the dialog"""
        if not self.visible:
            return False
        
        mouse_pos = pygame.mouse.get_pos()
        
        # Update hover states for mouse
        for button in self.tab_buttons:
            button.update_hover(mouse_pos)
        
        for button in self.game_buttons:
            button.update_hover(mouse_pos)
        
        for button in self.control_buttons:
            button.update_hover(mouse_pos)
        
        self.close_button.update_hover(mouse_pos)
        
        # Mouse click handling
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Click resets keyboard selection
            self.keyboard_selection = {'level': -1, 'index': 0}
            self._update_button_states()
            
            # Check close button
            if self.close_button.is_clicked(event):
                self.hide()
                return True
            
            # Check tab buttons
            for i, button in enumerate(self.tab_buttons):
                if button.is_clicked(event):
                    for btn in self.tab_buttons:
                        btn.is_active = (btn == button)
                    self.current_tab = button.tab_index
                    self._load_content()
                    return True
            
            # Check game buttons
            if self.current_tab == 0:
                for i, button in enumerate(self.game_buttons):
                    if button.is_clicked(event):
                        for btn in self.game_buttons:
                            btn.is_active = (btn == button)
                        self.selected_game = button.game_id
                        self._load_content()
                        return True
            
            # Check control buttons
            if self.current_tab == 1:
                for i, button in enumerate(self.control_buttons):
                    if button.is_clicked(event):
                        for btn in self.control_buttons:
                            btn.is_active = (btn == button)
                        self._load_content()
                        return True
            
            # Scroll panel
            if self.scroll_panel.rect.collidepoint(mouse_pos):
                self.scroll_panel.handle_event(event)
                return True
        
        # Mouse wheel
        elif event.type == pygame.MOUSEWHEEL:
            if self.scroll_panel.rect.collidepoint(mouse_pos):
                self.scroll_panel.handle_event(event)
                return True
        
        # Keyboard handling (SIMPLE - just handle each key press)
        elif event.type == pygame.KEYDOWN:
            # Debug: print key info
            # print(f"Key pressed: {pygame.key.name(event.key)} (code: {event.key})")
            
            if event.key == pygame.K_ESCAPE:
                self.hide()
                return True
            elif event.key == pygame.K_h:
                self.hide()
                return True
            
            # Navigation keys - ALWAYS process these
            handled = False
            
            if event.key == pygame.K_UP:
                handled = self._navigate_up_down(-1)
            elif event.key == pygame.K_DOWN:
                handled = self._navigate_up_down(1)
            elif event.key == pygame.K_LEFT:
                handled = self._navigate_left_right(-1)
            elif event.key == pygame.K_RIGHT:
                handled = self._navigate_left_right(1)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                handled = self._activate_current_selection()
            elif event.key == pygame.K_TAB:
                # Toggle tab
                self.current_tab = 1 if self.current_tab == 0 else 0
                for i, btn in enumerate(self.tab_buttons):
                    btn.is_active = (i == self.current_tab)
                self._load_content()
                handled = True
            
            if handled:
                return True
        
        return False
    
    def draw(self, screen):
        """Draw the dialog"""
        if not self.visible:
            return
        
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # Dialog background
        pygame.draw.rect(screen, (30, 35, 50), 
                        (self.x, self.y, self.width, self.height), 
                        border_radius=15)
        pygame.draw.rect(screen, (60, 70, 100), 
                        (self.x, self.y, self.width, self.height), 
                        2, border_radius=15)
        
        # Title
        title = self.font_manager.large.render("Game Help & Guide", True, (220, 220, 255))
        screen.blit(title, (self.x + 20, self.y + 30))
        
        # Draw tab buttons with keyboard highlight
        for button in self.tab_buttons:
            if button.keyboard_hovered:
                # Draw keyboard selection highlight
                highlight_rect = button.rect.inflate(10, 10)
                highlight_surface = pygame.Surface((highlight_rect.width, highlight_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(highlight_surface, KEY_NAVIGATION_COLORS['selection_bg'], 
                               (0, 0, highlight_rect.width, highlight_rect.height), 
                               border_radius=button.corner_radius + 5)
                screen.blit(highlight_surface, highlight_rect)
                pygame.draw.rect(screen, KEY_NAVIGATION_COLORS['selection_border'], 
                               highlight_rect, 2, border_radius=button.corner_radius + 5)
            
            button.draw(screen)
        
        # Draw content buttons based on current tab
        if self.current_tab == 0:  # Gameplay
            for button in self.game_buttons:
                if button.keyboard_hovered:
                    highlight_rect = button.rect.inflate(8, 8)
                    highlight_surface = pygame.Surface((highlight_rect.width, highlight_rect.height), pygame.SRCALPHA)
                    pygame.draw.rect(highlight_surface, KEY_NAVIGATION_COLORS['selection_bg'], 
                                   (0, 0, highlight_rect.width, highlight_rect.height), 
                                   border_radius=button.corner_radius + 4)
                    screen.blit(highlight_surface, highlight_rect)
                    pygame.draw.rect(screen, KEY_NAVIGATION_COLORS['selection_border'], 
                                   highlight_rect, 2, border_radius=button.corner_radius + 4)
                
                button.draw(screen)
        else:  # Controls
            for button in self.control_buttons:
                if button.keyboard_hovered:
                    highlight_rect = button.rect.inflate(8, 8)
                    highlight_surface = pygame.Surface((highlight_rect.width, highlight_rect.height), pygame.SRCALPHA)
                    pygame.draw.rect(highlight_surface, KEY_NAVIGATION_COLORS['selection_bg'], 
                                   (0, 0, highlight_rect.width, highlight_rect.height), 
                                   border_radius=button.corner_radius + 4)
                    screen.blit(highlight_surface, highlight_rect)
                    pygame.draw.rect(screen, KEY_NAVIGATION_COLORS['selection_border'], 
                                   highlight_rect, 2, border_radius=button.corner_radius + 4)
                
                button.draw(screen)
        
        # Draw close button with keyboard highlight
        if self.close_button.keyboard_hovered:
            highlight_rect = self.close_button.rect.inflate(8, 8)
            highlight_surface = pygame.Surface((highlight_rect.width, highlight_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(highlight_surface, KEY_NAVIGATION_COLORS['selection_bg'], 
                           (0, 0, highlight_rect.width, highlight_rect.height), 
                           border_radius=self.close_button.corner_radius + 4)
            screen.blit(highlight_surface, highlight_rect)
            pygame.draw.rect(screen, KEY_NAVIGATION_COLORS['selection_border'], 
                           highlight_rect, 2, border_radius=self.close_button.corner_radius + 4)
        
        self.close_button.draw(screen)
        
        # Draw scroll panel
        self.scroll_panel.draw(screen)
        
        # Navigation instructions
        instructions = [
            "Keyboard Navigation:",
            "↑/↓: Move between sections",
            "←/→: Select items within section", 
            "ENTER/SPACE: Activate selection",
            "TAB: Switch tabs",
            "ESC: Close dialog"
        ]
        
        instruction_y = self.y + self.height - 120
        
        # for i, text in enumerate(instructions):
        #     color = (180, 220, 255) if i == 0 else (150, 180, 220)
        #     font = self.font_manager.medium if i == 0 else self.font_manager.small
        #     instruction_text = font.render(text, True, color)
        #     screen.blit(instruction_text, (self.x + 20, instruction_y + i * 25))
        
        # Current selection debug
        # debug_text = self.font_manager.small.render(
        #     f"Selected: Level={self.keyboard_selection['level']}, Index={self.keyboard_selection['index']}",
        #     True, (255, 200, 100)
        # )
        # screen.blit(debug_text, (self.x + 20, self.y + self.height - 40))
    
    def _is_inside_dialog(self, pos):
        """Check if position is inside dialog"""
        return (self.x <= pos[0] <= self.x + self.width and 
                self.y <= pos[1] <= self.y + self.height)