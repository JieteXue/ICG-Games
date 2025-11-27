# This file makes the pygame directory a Python package

def start_card_game(self):
    """Start the card taking game"""
    try:
        # Import from Modules.pygame package
        from Modules.pygame import game3
        
        pygame.quit()  # Close main menu
        
        # Start the card game
        card_game = game3.CardGame()
        card_game.run()
        
        # After card game ends, restart main menu
        self.__init__()  # Reinitialize main menu
        self.run()
        
    except Exception as e:
        print(f"Error starting card game: {e}")
        import traceback
        traceback.print_exc()
        # Fallback: restart main menu
        self.__init__()
        self.run()