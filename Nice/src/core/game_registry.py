"""
Game registry for managing all available games
"""

class GameRegistry:
    """Manages registration and retrieval of games"""
    
    def __init__(self):
        self._games = {}
    
    def register_game(self, game_id, game_class, name, description, min_players=1, max_players=2):
        """Register a new game"""
        self._games[game_id] = {
            'class': game_class,
            'name': name,
            'description': description,
            'min_players': min_players,
            'max_players': max_players
        }
    
    def get_game(self, game_id):
        """Get game class by ID"""
        return self._games.get(game_id)
    
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