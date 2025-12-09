"""
Game registry for managing all available games
"""

class GameRegistry:
    """Manages registration and retrieval of games"""
    
    def __init__(self):
        self._games = {}
        self._pending_registrations = []  # 存储延迟注册的游戏
    
    def register_game_deferred(self, game_id, game_class_path, name, description, min_players=1, max_players=2):
        """延迟注册游戏，避免循环导入"""
        self._pending_registrations.append({
            'game_id': game_id,
            'game_class_path': game_class_path,
            'name': name,
            'description': description,
            'min_players': min_players,
            'max_players': max_players
        })
    
    def register_game(self, game_id, game_class, name, description, min_players=1, max_players=2):
        """Register a new game (立即注册)"""
        self._games[game_id] = {
            'class': game_class,
            'name': name,
            'description': description,
            'min_players': min_players,
            'max_players': max_players
        }
    
    def get_game(self, game_id):
        """Get game class by ID - 支持延迟加载"""
        if game_id in self._games:
            return self._games[game_id]
        
        # 检查是否有延迟注册的游戏
        for reg in self._pending_registrations:
            if reg['game_id'] == game_id:
                # 延迟加载游戏类
                try:
                    module_path, class_name = reg['game_class_path'].rsplit('.', 1)
                    module = __import__(module_path, fromlist=[class_name])
                    game_class = getattr(module, class_name)
                    
                    # 移动到正式注册
                    self.register_game(game_id, game_class, reg['name'], 
                                     reg['description'], reg['min_players'], reg['max_players'])
                    
                    # 从待注册列表中移除
                    self._pending_registrations = [r for r in self._pending_registrations if r['game_id'] != game_id]
                    
                    return self._games[game_id]
                except Exception as e:
                    print(f"Error loading game class {reg['game_class_path']}: {e}")
                    return None
        
        return None
    
    def get_all_games(self):
        """Get all registered games"""
        return self._games
    
    def get_available_games(self):
        """Get list of available games for display"""
        return [
            {
                'id': game_id,
                'name': info['name'],
                'description': info['description'],
                'min_players': info['min_players'],
                'max_players': info['max_players']
            }
            for game_id, info in self._games.items()
        ]

# Global game registry instance
game_registry = GameRegistry()