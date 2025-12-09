"""
Configuration Manager
"""

import json
import os
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class GameConfig:
    """Game configuration class"""
    name: str
    description: str
    min_players: int = 1
    max_players: int = 2
    difficulty_levels: Dict = None
    ui_settings: Dict = None
    
    def __post_init__(self):
        if self.difficulty_levels is None:
            self.difficulty_levels = {
                1: {"name": "Easy", "description": "For beginners"},
                2: {"name": "Normal", "description": "Standard difficulty"},
                3: {"name": "Hard", "description": "Challenging"},
                4: {"name": "Insane", "description": "Expert difficulty"}
            }
        if self.ui_settings is None:
            self.ui_settings = {
                "button_size": (80, 40),
                "scroll_speed": 1,
                "animation_speed": 0.5
            }

class ConfigManager:
    """Configuration manager"""
    
    def __init__(self, config_dir="configs"):
        self.config_dir = config_dir
        self.games_config = {}
        self.load_all_configs()
    
    def load_all_configs(self):
        """Load all game configurations"""
        default_configs = {
            "card_nim": GameConfig(
                name="Card Nim",
                description="Strategic card taking game using Nim theory"
            ),
            "take_coins": GameConfig(
                name="Take Coins",
                description="Strategic coin manipulation game on a line"
            ),
            "subtract_factor": GameConfig(
                name="Subtract Factor",
                description="Strategic number reduction using factor subtraction"
            ),
            "dawson_kayles": GameConfig(
                name="Laser Defense",
                description="Strategic tower connection game using Dawson-Kayles rules"
            ),
            "split_cards": GameConfig(
                name="Magic Cards Split",
                description="Strategic card splitting game with magical theme"
            )
        }
        
        # Try to load from files
        try:
            if os.path.exists(self.config_dir):
                for config_file in os.listdir(self.config_dir):
                    if config_file.endswith('.json'):
                        game_id = config_file[:-5]  # Remove .json extension
                        with open(os.path.join(self.config_dir, config_file), 'r') as f:
                            config_data = json.load(f)
                            self.games_config[game_id] = GameConfig(**config_data)
        except Exception as e:
            print(f"Error loading configs: {e}")
            self.games_config = default_configs
    
    def get_game_config(self, game_id):
        """Get game configuration"""
        return self.games_config.get(game_id)
    
    def save_game_config(self, game_id, config):
        """Save game configuration"""
        os.makedirs(self.config_dir, exist_ok=True)
        config_file = os.path.join(self.config_dir, f"{game_id}.json")
        with open(config_file, 'w') as f:
            json.dump(config.__dict__, f, indent=2)