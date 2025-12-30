"""
Configuration manager for game settings and preferences
"""

import json
import os
from typing import Dict, Any, Optional,List
from dataclasses import dataclass, asdict,field

@dataclass
class GameConfig:
    """Configuration for a specific game"""
    game_id: str
    name: str
    description: str
    min_players: int = 1
    max_players: int = 2
    default_difficulty: int = 2  # Normal
    ai_delay_ms: int = 500  # Delay before AI moves
    positions_range: Dict[int, tuple] = None  # Difficulty -> (min, max) positions
    visual_settings: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.positions_range is None:
            self.positions_range = {
                1: (3, 5),   # Easy
                2: (4, 6),   # Normal
                3: (5, 7),   # Hard
                4: (6, 8)    # Insane
            }
        if self.visual_settings is None:
            self.visual_settings = {
                'card_width': 80,
                'card_height': 120,
                'animation_speed': 0.3,
                'highlight_color': (255, 215, 0)
            }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameConfig':
        """Create from dictionary"""
        return cls(**data)
    
@dataclass  
class UserPreferences:
    """User preferences and settings"""
    sound_volume: float = 0.7
    music_volume: float = 0.5
    show_hints: bool = True
    show_animations: bool = True
    theme: str = 'dark'  # 'dark' or 'light'
    language: str = 'en'
    autosave: bool = True
    winning_hints: bool = False  # 新增：Winning Hints开关，默认关闭
    music_enabled: bool = True  # 新增：背景音乐开关
    selected_music: int = 0  # 新增：当前选中的音乐索引
    unlocked_music: List[int] = field(default_factory=lambda: [0, 1, 2])  # 新增：已解锁的音乐列表
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserPreferences':
        return cls(**data)


class ConfigManager:
    """Manages all game configurations and user preferences"""
    
    def __init__(self, config_dir: str = "configs"):
        self.config_dir = config_dir
        os.makedirs(config_dir, exist_ok=True)
        
        self.game_configs: Dict[str, GameConfig] = {}
        self.user_prefs = UserPreferences()
        self.global_settings = {}
        
        self._load_all_configs()
    
    def _load_all_configs(self):
        """Load all configurations from files"""
        # Load user preferences
        prefs_file = os.path.join(self.config_dir, "preferences.json")
        if os.path.exists(prefs_file):
            try:
                with open(prefs_file, 'r') as f:
                    data = json.load(f)
                    self.user_prefs = UserPreferences.from_dict(data)
            except Exception as e:
                print(f"Error loading preferences: {e}")
        
        # Load game configurations
        games_config_file = os.path.join(self.config_dir, "games.json")
        if os.path.exists(games_config_file):
            try:
                with open(games_config_file, 'r') as f:
                    games_data = json.load(f)
                    for game_id, game_data in games_data.items():
                        self.game_configs[game_id] = GameConfig.from_dict(game_data)
            except Exception as e:
                print(f"Error loading game configs: {e}")
        
        # If no game configs loaded, create defaults
        if not self.game_configs:
            self._create_default_game_configs()
    
    def _create_default_game_configs(self):
        """Create default game configurations"""
        default_configs = {
            "take_coins": GameConfig(
                game_id="take_coins",
                name="Take Coins Game",
                description="Strategic coin manipulation game on a line",
                min_players=1,
                max_players=2,
                default_difficulty=2,
                ai_delay_ms=800,
                positions_range={
                    1: (6, 8),   # Easy
                    2: (8, 10),  # Normal
                    3: (10, 12), # Hard
                    4: (12, 14)  # Insane
                },
                visual_settings={
                    'coin_radius': 12,
                    'coin_spacing': 6,
                    'max_display_coins': 8
                }
            ),
            "card_nim": GameConfig(
                game_id="card_nim",
                name="Card Nim Game",
                description="Strategic card taking game using Nim theory",
                min_players=1,
                max_players=2,
                default_difficulty=2,
                ai_delay_ms=600,
                positions_range={
                    1: (3, 5),   # Easy
                    2: (4, 6),   # Normal
                    3: (5, 7),   # Hard
                    4: (6, 8)    # Insane
                }
            ),
            "subtract_factor": GameConfig(
                game_id="subtract_factor",
                name="Subtract Factor Game",
                description="Strategic number reduction using factor subtraction",
                min_players=1,
                max_players=2,
                default_difficulty=2,
                ai_delay_ms=700,
                positions_range={
                    1: (120, 200),  # Easy
                    2: (150, 250),  # Normal
                    3: (200, 350),  # Hard
                    4: (250, 500)   # Insane
                }
            ),
            "dawson_kayles": GameConfig(
                game_id="dawson_kayles",
                name="Laser Defense",
                description="Strategic tower connection game using Dawson-Kayles rules",
                min_players=1,
                max_players=2,
                default_difficulty=2,
                ai_delay_ms=900
            ),
            "split_cards": GameConfig(
                game_id="split_cards",
                name="Magic Cards Split",
                description="Strategic card splitting game with magical theme",
                min_players=1,
                max_players=2,
                default_difficulty=2,
                ai_delay_ms=750
            )
        }
        
        self.game_configs.update(default_configs)
        self.save_game_configs()
    
    def get_game_config(self, game_id: str) -> Optional[GameConfig]:
        """Get configuration for a specific game"""
        return self.game_configs.get(game_id)
    
    def update_game_config(self, game_id: str, config: GameConfig):
        """Update configuration for a game"""
        self.game_configs[game_id] = config
        self.save_game_configs()
    
    def get_user_preferences(self) -> UserPreferences:
        """Get user preferences"""
        return self.user_prefs
    
    def update_user_preferences(self, prefs: UserPreferences):
        """Update user preferences"""
        self.user_prefs = prefs
        self.save_user_preferences()
    
    def save_game_configs(self):
        """Save all game configurations to file"""
        try:
            games_data = {game_id: config.to_dict() 
                         for game_id, config in self.game_configs.items()}
            games_file = os.path.join(self.config_dir, "games.json")
            with open(games_file, 'w') as f:
                json.dump(games_data, f, indent=2)
        except Exception as e:
            print(f"Error saving game configs: {e}")
    
    def save_user_preferences(self):
        """Save user preferences to file"""
        try:
            prefs_file = os.path.join(self.config_dir, "preferences.json")
            with open(prefs_file, 'w') as f:
                json.dump(self.user_prefs.to_dict(), f, indent=2)
        except Exception as e:
            print(f"Error saving preferences: {e}")
    
    def get_difficulty_settings(self, game_id: str, difficulty: int) -> Dict[str, Any]:
        """Get settings for a specific game and difficulty"""
        config = self.get_game_config(game_id)
        if not config:
            return {}
        
        settings = {
            'positions_range': config.positions_range.get(difficulty, (4, 6)),
            'ai_delay_ms': config.ai_delay_ms,
            'visual_settings': config.visual_settings.copy()
        }
        
        # Add game-specific difficulty settings
        if game_id == "take_coins":
            settings['initial_coins_range'] = (1, 3)
            settings['max_attempts'] = 100
        elif game_id == "subtract_factor":
            settings['threshold_ratio'] = 0.3  # k/n ratio
            settings['min_k'] = 10
        
        return settings

# Global configuration manager instance
config_manager = ConfigManager()