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
        # 添加调试信息
        print("🔍 Checking Python path...")
        import sys
        print(f"Python path: {sys.path}")
        
        # 检查模块是否存在
        print("🔍 Checking if modules exist...")
        try:
            from games.dawson_kayles import game
            print("✅ games.dawson_kayles.game module found")
        except ImportError as e:
            print(f"❌ Cannot import games.dawson_kayles.game: {e}")
        
        # 检查具体类是否存在
        try:
            from games.dawson_kayles.game import DawsonKaylesGame
            print("✅ DawsonKaylesGame class found")
        except ImportError as e:
            print(f"❌ Cannot import DawsonKaylesGame: {e}")
            import traceback
            traceback.print_exc()
        # 导入并注册Card Nim游戏
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
        
        # 导入并注册Subtract Factor游戏
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
        
        # Installment and registry of Dawson-Kayles game
        from games.dawson_kayles.game import DawsonKaylesGame
        game_registry.register_game(
            game_id="dawson_kayles",
            game_class=DawsonKaylesGame,
            name="Laser Defense - Dawson-Kayles",
            description="Strategic tower connection game using Dawson-Kayles rules",
            min_players=1,
            max_players=2
        )
        print("✅ Dawson-Kayles game registered successfully")
        
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