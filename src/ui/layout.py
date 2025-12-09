"""
Universal UI Layout Manager
"""

class UILayout:
    """Manages layout of UI elements"""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.layouts = self._create_default_layouts()
    
    def _create_default_layouts(self):
        """Create default layout configurations"""
        return {
            'header': {
                'height': 180,
                'title_y': 20,
                'info_y': 80,
                'player_info_x': 20,
                'player_info_y': 140
            },
            'game_area': {
                'top': 200,
                'height': 250,
                'margin': 50
            },
            'control_panel': {
                'top': 470,
                'height': 150,
                'width': 400
            },
            'footer': {
                'top': 600,
                'height': 100
            },
            'navigation': {
                'button_size': 50,
                'spacing': 10,
                'margin': 20
            }
        }
    
    def center_x(self, element_width):
        """Calculate center X position"""
        return (self.screen_width - element_width) // 2
    
    def center_y(self, element_height):
        """Calculate center Y position"""
        return (self.screen_height - element_height) // 2
    
    def create_grid_layout(self, cell_width, cell_height, columns, rows, spacing=20):
        """Create grid layout positions"""
        grid_width = columns * cell_width + (columns - 1) * spacing
        grid_height = rows * cell_height + (rows - 1) * spacing
        start_x = self.center_x(grid_width)
        start_y = self.center_y(grid_height)
        
        positions = []
        for row in range(rows):
            for col in range(columns):
                x = start_x + col * (cell_width + spacing)
                y = start_y + row * (cell_height + spacing)
                positions.append((x, y, cell_width, cell_height))
        
        return positions
    
    def get_header_position(self, element_type='title'):
        """Get position for header elements"""
        layout = self.layouts['header']
        if element_type == 'title':
            return (self.center_x(0), layout['title_y'])
        elif element_type == 'info':
            return (layout['player_info_x'], layout['info_y'])
        elif element_type == 'player_info':
            return (self.screen_width - 200, layout['player_info_y'])
        return (0, 0)
    
    def get_game_area_position(self, index=0, total_items=1, item_width=80, spacing=20):
        """Get position for game area elements"""
        layout = self.layouts['game_area']
        total_width = total_items * item_width + (total_items - 1) * spacing
        start_x = self.center_x(total_width)
        y = layout['top'] + (layout['height'] // 2)
        
        x = start_x + index * (item_width + spacing)
        return (x, y)