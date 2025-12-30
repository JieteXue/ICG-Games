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
                "• Strategy game based on coin placement and removal",
                "• Players take turns placing a coin while removing adjacent coins",
                "• Player who makes the last valid move wins",
                "",
                "Game Rules:",
                "• Game starts with several coins placed at each of the positions arranged in a row.",
                "• On each turn, a player places one coin in a position and removes one coin from each adjacent position",
                "• The move cannot be performed if the position is at the edge or adjacent positions have no coins",
                "• Players alternate turns until one player cannot move, and the last player to move wins",
                "",
                "Strategy Tips:",
                "• Try to turn the situation into multiple independent subgames",
                "• Use symmetry: try to mirror your opponent’s moves to maintain control",
                "• Avoid leaving isolated coins near edges, as they become dead positions"
            ]
        },
        "split_cards": {
            "title": "Magic Cards Split",
            "content": [
                "Game Objective:",
                "• Strategy game combining pile splitting and card removal",
                "• Players take turns either splitting a pile or taking cards from a pile",
                "• Player who takes the last card wins",
                "",
                "Game Rules:",
                "• Game starts with one pile of cards",
                "• Players take turns choosing:",
                "•   Split any pile into two non-empty piles",
                "•   Take 1 to 9 cards from any pile",
                "• Players alternate turns until no cards remain",
                "• The player who takes the last card wins",
                "",
                "Strategy Tips:",
                "• Prefer direct removal when total cards are low",
                "• Be cautious when a pile’s count is near a multiple of 10",
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
                "• Game starts with multiple piles of cards",
                "• Each pile has different number of cards",
                "• Players take turns removing cards",
                "• Cards can only be removed from one pile per turn",
                "• Must remove at least 1, at most all from a pile",
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
                "• Strategy game of connecting adjacent positions",
                "• Players take turns drawing a line between two adjacent unconnected positions",
                "• Player who makes the last connection wins",
                "",
                "Game Rules:",
                "• Game starts with a row of empty positions",
                "• On each turn, a player connects two adjacent positions that are not yet connected",
                "• Once connected, those positions become “connected” and cannot be used again",
                "• New connections cannot cross existing ones",
                "• Players alternate turns until no more connections can be made",
                "• The last player to connect wins",
                "",
                "Strategy Tips:",
                "• Start from the center to divide the board into symmetric halves",
            ]
        },
        "subtract_factor": {
            "title": "Subtract Factor",
            "content": [
                "Game Objective:",
                "• Reduce number by subtracting its factors",
                "• Player who reduces number to the arithmetic square root of N (rounded up) wins",
                "",
                "Game Rules:",
                "• Game starts with initial number N",
                "• Players take turns selecting a factor of current number",
                "• Subtract factor from current number",
                "• Result must be larger than the arithmetic square root of N (rounded up)",
                "• Player unable to make legal move loses",
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
            "• F2: Toggle performance display",
            "• H: Show help interface",
            "• Space: Confirm/Select",
            "• Arrow Keys: Navigate menus",
            "",
            "In-Game Controls:",
            "• ESC: Activate Sidebar",
            "• Enter/Space: Confirm action",
            "• R: Restart game",
            "• H: Return to main menu",
            "• I: Game Information",
            "• S: Check settings"
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
            "• Split cards:Click card to select, choose to take cards or split plie, then confirm move",
            "• Card Nim: Click card to select, enter numbers to confirm",
            "• Dawson Kayles: Click towers or connections or enter numbers to confirm directly",
            "• Subtract Factor: Click factors to select",
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