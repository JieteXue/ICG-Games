"""
Game Help Content Configuration
Contains gameplay instructions and control guides for all games
"""

GAME_HELP_CONTENT = {
    # Gameplay Instructions
    "gameplay": {
        "take_coins": {
            "title": "Take Coins Game",
            "content": [
                "Game Objective:",
                "• Multiple coins are arranged in a line",
                "• Players take turns removing coins from either end",
                "• 1-3 coins can be removed per turn",
                "• Player who takes the last coin wins",
                "",
                "Game Rules:",
                "1. Game starts with N coins",
                "2. Players take turns removing coins",
                "3. Coins can only be removed from one end per turn",
                "4. Number of coins to remove: 1-3",
                "5. Player unable to make a move loses",
                "",
                "Strategy Tips:",
                "• Observe opponent's coin removal patterns",
                "• Try to keep coin count as a multiple of 4",
                "• Control game pace, don't rush to take coins"
            ]
        },
        "split_cards": {
            "title": "Magic Cards Split",
            "content": [
                "Game Objective:",
                "• Split a deck of cards into smaller piles",
                "• Player unable to make a legal split loses",
                "",
                "Game Rules:",
                "1. Start with a deck of cards (size N)",
                "2. Players take turns selecting a card to split",
                "3. Split must create two non-empty piles",
                "4. Two piles must have different sizes",
                "5. Player unable to make legal split loses",
                "",
                "Strategy Tips:",
                "• Analyze parity of card piles",
                "• Observe opponent's splitting strategy",
                "• Try to create symmetrical positions"
            ]
        },
        "card_nim": {
            "title": "Card Nim Game",
            "content": [
                "Game Objective:",
                "• Strategy game based on Nim theory",
                "• Players take turns removing cards from piles",
                "• Player who takes the last card wins",
                "",
                "Game Rules:",
                "1. Game starts with multiple piles of cards",
                "2. Each pile has different number of cards",
                "3. Players take turns removing cards",
                "4. Cards can only be removed from one pile per turn",
                "5. Must remove at least 1, at most all from a pile",
                "",
                "Strategy Tips:",
                "• Calculate XOR value of all piles",
                "• If XOR value is 0, you're in losing position",
                "• Force opponent into XOR=0 positions"
            ]
        },
        "dawson_kayles": {
            "title": "Laser Defense",
            "content": [
                "Game Objective:",
                "• Based on Dawson-Kayles rules",
                "• Connect or disconnect lasers in tower defense layout",
                "• Player unable to make legal move loses",
                "",
                "Game Rules:",
                "1. Multiple defense towers on the field",
                "2. Lasers may connect towers",
                "3. Players take turns choosing:",
                "   • Disconnect a laser connection",
                "   • Destroy a tower and all its connections",
                "4. Cannot choose isolated towers",
                "",
                "Strategy Tips:",
                "• Analyze graph symmetry",
                "• Prioritize disconnecting key connections",
                "• Create isolated towers to limit opponent's choices"
            ]
        },
        "subtract_factor": {
            "title": "Subtract Factor",
            "content": [
                "Game Objective:",
                "• Reduce number by subtracting its factors",
                "• Player who reduces number to 0 wins",
                "",
                "Game Rules:",
                "1. Game starts with initial number N",
                "2. Players take turns selecting a factor",
                "3. Factor must be less than current number",
                "4. Subtract factor from current number",
                "5. Result must be positive number",
                "6. Player unable to make legal move loses",
                "",
                "Strategy Tips:",
                "• Analyze number's prime factorization",
                "• Prioritize selecting prime factors",
                "• Avoid leaving favorable positions for opponent"
            ]
        }
    },
    
    # Control Guides
    "controls": {
        "keyboard": [
            "Keyboard Shortcuts:",
            "• ESC: Return/Exit",
            "• F1: Show game information",
            "• F2: Toggle performance display",
            "• F3: Toggle performance monitoring",
            "• H: Show help interface",
            "• Space: Confirm/Select",
            "• Arrow Keys: Navigate menus",
            "",
            "In-Game Controls:",
            "• WASD/Arrow Keys: Move selection",
            "• Enter/Space: Confirm action",
            "• R: Restart game",
            "• M: Return to main menu"
        ],
        "mouse": [
            "Mouse Controls:",
            "• Left Click: Select/Confirm",
            "• Mouse Wheel: Scroll content",
            "• Hover: Show tooltip",
            "",
            "Interface Controls:",
            "• Click buttons: Execute actions",
            "• Drag: Move elements (if supported)",
            "• Double-click: Quick confirm"
        ],
        "game_specific": [
            "Game-Specific Controls:",
            "• Take Coins: Click coins to select",
            "• Card Split: Drag cards to split",
            "• Laser Defense: Click towers or connections",
            "• Subtract Factor: Click factors to select",
            "",
            "General Visual Cues:",
            "• Green highlight: Available option",
            "• Red highlight: Unavailable option",
            "• Yellow highlight: Current selection"
        ]
    }
}

def get_game_help(game_id, help_type="gameplay"):
    """Get help content for specific game"""
    if help_type in GAME_HELP_CONTENT and game_id in GAME_HELP_CONTENT[help_type]:
        return GAME_HELP_CONTENT[help_type][game_id]
    return None

def get_controls_help(section="keyboard"):
    """Get control instructions"""
    if section in GAME_HELP_CONTENT["controls"]:
        return GAME_HELP_CONTENT["controls"][section]
    return []