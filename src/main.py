"""
Main entry point for ICG Games - Fixed to work with existing menus.py
"""

import pygame
import sys
import os
import gc

# Add src to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

print("🚀 Starting ICG Games...")

def register_games():
    """Register all available games with deferred registration"""
    try:
        from core.game_registry import game_registry
        
        # 使用延迟注册，避免循环导入
        game_registry.register_game_deferred(
            game_id="take_coins",
            game_class_path="games.take_coins.game.TakeCoinsGame",
            name="Take Coins Game",
            description="Strategic coin manipulation game on a line",
            min_players=1,
            max_players=2
        )
        print("✅ Take Coins game deferred registration")

        game_registry.register_game_deferred(
            game_id="split_cards",
            game_class_path="games.split_cards.game.SplitCardsGame",
            name="Magic Cards Split",
            description="Strategic card splitting game with magical theme",
            min_players=1,
            max_players=2
        )
        print("✅ Split Cards game deferred registration")

        game_registry.register_game_deferred(
            game_id="card_nim",
            game_class_path="games.card_nim.game.CardNimGame",
            name="Card Nim Game",
            description="Strategic card taking game using Nim theory",
            min_players=1,
            max_players=2
        )
        print("✅ Card Nim game deferred registration")
        
        game_registry.register_game_deferred(
            game_id="dawson_kayles",
            game_class_path="games.dawson_kayles.game.DawsonKaylesGame",
            name="Laser Connection",
            description="Strategic tower connection game using Dawson-Kayles rules",
            min_players=1,
            max_players=2
        )
        print("✅ Dawson-Kayles game deferred registration")

        game_registry.register_game_deferred(
            game_id="subtract_factor",
            game_class_path="games.subtract_factor.game.SubtractFactorGame",
            name="Subtract Factor", 
            description="Strategic number reduction using factor subtraction",
            min_players=1,
            max_players=2
        )
        print("✅ Subtract Factor game deferred registration")

        try:
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
        except ImportError as e:
            print(f"❌ Could not import TakeCoinsGame: {e}")
        
        try:
            from games.card_nim.game import CardNimGame
            game_registry.register_game(
                game_id="card_nim",
                game_class=CardNimGame,
                name="Card Nim Game",
                description="Strategic card taking game using Nim theory",
                min_players=1,
                max_players=2
            )
            print("✅ Card Nim game preloaded successfully")
        except ImportError as e:
            print(f"❌ Could not import CardNimGame: {e}")
        
        try:
            from games.subtract_factor.game import SubtractFactorGame
            game_registry.register_game(
                game_id="subtract_factor",
                game_class=SubtractFactorGame,
                name="Subtract Factor Game", 
                description="Strategic number reduction using factor subtraction",
                min_players=1,
                max_players=2
            )
            print("✅ Subtract Factor game registered successfully")
        except ImportError as e:
            print(f"❌ Could not import SubtractFactorGame: {e}")

        try:
            from games.dawson_kayles.game import DawsonKaylesGame
            game_registry.register_game(
                game_id="dawson_kayles",
                game_class=DawsonKaylesGame,
                name="Laser Defense",
                description="Strategic tower connection game using Dawson-Kayles rules",
                min_players=1,
                max_players=2
            )
            print("✅ Dawson-Kayles game registered successfully")
        except ImportError as e:
            print(f"❌ Could not import DawsonKaylesGame: {e}")

        try:
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
        except ImportError as e:
            print(f"❌ Could not import SplitCardsGame: {e}")

        return True 
    except Exception as e:
        print(f"❌ Error registering games: {e}")
        import traceback
        traceback.print_exc()
        return False

def initialize_performance_monitoring():
    """Initialize performance monitoring systems"""
    try:
        from utils.performance_monitor import performance_monitor
        from utils.optimization_tools import (
            memory_optimizer, 
            render_optimizer, 
            asset_optimizer,
            optimize_game_performance
        )
        from utils.error_handler import error_reporter
        
        # Enable performance monitoring
        performance_monitor.enabled = True
        
        # Enable memory optimization
        memory_optimizer.enabled = True
        
        print("✅ Performance monitoring initialized")
        return True
    except ImportError as e:
        print(f"⚠️ Performance modules not available: {e}")
        return False

def main():
    """Main entry point - Fixed to use existing menus.py structure"""
    try:
        # Initialize Pygame
        pygame.init()
        
        # Initialize performance monitoring
        perf_monitoring_available = initialize_performance_monitoring()
        
        # Register games
        if not register_games():
            print("Failed to register games. Exiting.")
            return
        
        # Import MainMenu after pygame is initialized
        try:
            from ui.menus import MainMenu
        except ImportError as e:
            print(f"❌ Could not import MainMenu: {e}")
            print("Please make sure ui/menus.py exists and is correctly formatted.")
            pygame.quit()
            sys.exit(1)
        
        # Show available games
        try:
            from core.game_registry import game_registry
            available_games = game_registry.get_available_games()
            print(f"📋 Available games: {len(available_games)}")
            for game in available_games:
                print(f"  - {game['name']}: {game['description']}")
        except:
            print("⚠️ Could not display available games")
        
        # Start main menu
        print("🎮 Starting main menu...")
        menu = MainMenu()
        
        # Run the menu (uses its own run() method)
        menu.run()
        
        print("👋 Goodbye!")
        
    except Exception as e:
        print(f"💥 Critical error starting application: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit()
        sys.exit(0)

if __name__ == "__main__":
    main()