"""
Main entry point for ICG Games - Fixed to work with existing menus.py
"""

import pygame
import sys
import os
import gc
import time

# Add src to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

print("🚀 Starting ICG Games...")

def register_games():
    """Register all available games with deferred registration"""
    try:
        from core.game_registry import game_registry
        
        # Use deferred registration to avoid circular imports
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
            from games.split_cards.game import SplitCardsGame
            game_registry.register_game(
                game_id="split_cards",
                game_class=SplitCardsGame,
                name="Split Cards Game",
                description="Strategic card splitting and taking game",
                min_players=1,
                max_players=2
            )
            print("✅ Split Cards game registered successfully")
        except ImportError as e:
            print(f"❌ Could not import SplitCardsGame: {e}")

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

def check_font_support(font_manager):
    """检查字体支持情况"""
    test_chars = ['\n', '\t', '→', '←', '↑', '↓']
    unsupported = []
    
    for font_name, font in [('small', font_manager.small), 
                           ('medium', font_manager.medium),
                           ('large', font_manager.large)]:
        for char in test_chars:
            # 尝试渲染字符
            try:
                text_surface = font.render(char, True, (255, 255, 255))
                width, height = text_surface.get_size()
                if width == 0 and height == 0:
                    unsupported.append((font_name, char))
            except:
                unsupported.append((font_name, char))
    
    if unsupported:
        print(f"Warning: These characters are not supported: {unsupported}")
        print("Suggestions: Avoid using unsupported characters or change the font.")
    else:
        print("Font support check passed.")

def main():
    """Main entry point - Fixed to use existing menus.py structure"""
    try:
        # Import splash screen from ui module
        from ui.splash_screen import PygameSplash
        
        # Create and run startup animation
        splash = PygameSplash()
        animation_completed = splash.run_animation()
        
        if not animation_completed:
            print("Startup animation interrupted by user")
            pygame.quit()
            return
        
        # Close startup window
        splash.close()
        
        # Note: Pygame is still running, no need to reinitialize
        
        # Initialize performance monitoring
        perf_monitoring_available = initialize_performance_monitoring()
        
        # Register games
        if not register_games():
            print("Failed to register games. Exiting.")
            pygame.quit()
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
        print("Starting main menu...")
        
        # 初始化音乐 - 在导入 music_manager 之前先初始化 mixer
        pygame.mixer.init()
        
        # 正确导入 music_manager（根据你的目录结构）
        try:
            # 从 utils 模块导入 music_manager
            from utils.music_manager import music_manager
            print("✅ Music manager imported successfully")
            
            # 从配置加载音乐设置并播放音乐
            if music_manager.is_music_enabled() and music_manager.get_current_music_index() >= 0:
                # 播放当前选中的音乐
                music_manager.play_music(music_manager.get_current_music_index())
                print(f"🎵 Playing music: {music_manager.get_current_music_index()}")
            else:
                print("⚠️ Music is disabled or no music selected")
                
        except ImportError as e:
            print(f"❌ Could not import music_manager: {e}")
            print("Please make sure utils/music_manager.py exists.")
            # 创建一个简单的模拟对象以避免错误
            class DummyMusicManager:
                def is_music_enabled(self):
                    return False
                def get_current_music_index(self):
                    return -1
                def play_music(self, index):
                    return False
            music_manager = DummyMusicManager()
        
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