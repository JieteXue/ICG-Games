"""
Main entry point for ICG Games
"""

import pygame
import sys
import os

# 添加src到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
sys.path.insert(0, src_path)

print("🚀 Starting ICG Games...")

try:
    from ui.menus import MainMenu
    from core.game_registry import game_registry
    print("✅ Successfully imported core modules")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def register_games():
    """注册所有可用游戏"""
    try:
         # Installation and registry of Take Coins game
        from games.take_coins.game import TakeCoinsGame
        game_registry.register_game(
            game_id="take_coins",
            game_class=TakeCoinsGame,
            name="Take Coins Game",
            description="Strategic coin manipulation game on a line",
            min_players=1,
            max_players=2
        )
        print("✅ Take Coins game registered successfully")

        # Installation and registry of Split Cards game
        from games.split_cards.game import SplitCardsGame
        game_registry.register_game(
            game_id="split_cards",
            game_class=SplitCardsGame,
            name="Magic Cards Split",
            description="Strategic card splitting game with magical theme",
            min_players=1,
            max_players=2
        )
        print("✅ Split Cards game registered successfully")

        # Installation and registry of Card Nim game
        from games.card_nim.game import CardNimGame
        game_registry.register_game(
            game_id="card_nim",
            game_class=CardNimGame,
            name="Card Nim Game",
            description="Strategic card taking game using Nim theory",
            min_players=1,
            max_players=2
        )
        print("✅ Card Nim game registered successfully")
        
         # Installation and registry of Dawson-Kayles game
        from games.dawson_kayles.game import DawsonKaylesGame
        game_registry.register_game(
            game_id="dawson_kayles",
            game_class=DawsonKaylesGame,
            name="Laser Connection",
            description="Strategic tower connection game using Dawson-Kayles rules",
            min_players=1,
            max_players=2
        )
        print("✅ Dawson-Kayles game registered successfully")

        # Installation and registry of Subtract Factor game
        from games.subtract_factor.game import SubtractFactorGame
        game_registry.register_game(
            game_id="subtract_factor",
            game_class=SubtractFactorGame,
            name="Subtract Factor", 
            description="Strategic number reduction using factor subtraction",
            min_players=1,
            max_players=2
        )
        print("✅ Subtract Factor game registered successfully")

        return True
        
        
    except ImportError as e:
        print(f"❌ Error registering games: {e}")
        return False

def main():
    """主入口点"""
    try:
        # 注册游戏
        if not register_games():
            print("Failed to register games. Exiting.")
            return
        
        # 显示可用游戏
        available_games = game_registry.get_available_games()
        print(f"📋 Available games: {len(available_games)}")
        for game in available_games:
            print(f"  - {game['name']}: {game['description']}")
        
        # 启动主菜单
        print("🎮 Starting main menu...")
        menu = MainMenu()
        menu.run()
        
    except Exception as e:
        print(f"💥 Error starting application: {e}")
        import traceback
        traceback.print_exc()
        pygame.quit()
        sys.exit(1)

if __name__ == "__main__":
    main()