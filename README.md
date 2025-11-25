
# Combinatorial Game Collection - Pygame Interface

A comprehensive graphical interface for multiple combinatorial mathematical games using Pygame, featuring human vs AI gameplay with strategic decision making.

## 🎮 Games Collection

### 1. Take Coins (取硬币游戏)
- **Description**: A mathematical game where players take coins from piles. The player who takes the last coin wins.
- **Rules**: Players alternate taking 1 to 3 coins from a single pile. Strategic play involves forcing the opponent into losing positions.
- **Mathematical Basis**: Based on modular arithmetic and winning positions.

### 2. Take and Split Cards (取卡分堆游戏)
- **Description**: A card game variant where players can take cards and optionally split remaining piles.
- **Rules**: Players can take cards from a pile and may split the remaining cards into two new piles.
- **Strategy**: Involves understanding heap nim-values and combinatorial game theory.

### 3. Cards Nim (卡牌尼姆游戏)
- **Description**: A Nim game variant played with cards instead of traditional objects.
- **Rules**: Multiple piles of cards, players take any number of cards from a single pile.
- **Mathematical Basis**: Classic Nim game using binary digital sum (nim-sum) strategy.

### 4. Dawson's Kayles (道森凯尔斯游戏)
- **Description**: A mathematical removal game based on bowling pins alignment.
- **Rules**: Players remove adjacent cards/pins, with constraints on which can be removed together.
- **Strategy**: Uses Sprague-Grundy theorem and impartial game theory.

### 5. Subtract Factor (因数减法游戏)
- **Description**: A mathematical number game where players subtract factors from a number, aiming to avoid being forced below a threshold.
- **Rules**: 
  - Start with an integer n and threshold k (1 ≤ k < n)
  - On each turn: subtract a proper divisor d of the current number m (1 ≤ d < m)
  - If the result (m - d) is less than k: the current player loses
  - Otherwise: continue with the new number
- **Mathematical Basis**: Based on number theory (divisors) and combinatorial game theory with dynamic programming for winning positions.
- **Strategy**: Identify winning positions by analyzing divisor patterns and forcing opponents into losing positions below the threshold.
- **Key Insight**: The game combines elements of factorization with subtraction games, creating complex strategic patterns based on number properties.

## 🏗️ Project Structure

```
Combinatorial-Games/
├── 🔧 Game_class.py                 # Core game engine class
├── 🚀 main.py                       # Main Pygame launcher  
├── 📋 requirements.txt              # Python dependencies list
├── 📜 LICENSE                       # MIT License file
├── 📄 ChangeLog.md                  # Change log file
├── 📚 README.md                     # Project documentation
└── 🎯 games/                        # Game implementation modules
    ├── game1_Take_Coins.py
    ├── game2_Take_and_Split_Cards.py
    ├── game3_Nim.py
    ├── game4_Dawson_Kayles.py
    ├── game5_Subtract_Factor.py
    └── pygame/
        ├──
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.7 or higher
- Pip package manager

### Step-by-Step Installation

1. **Clone or Download the Project**
   ```bash
   # If using git
   git clone <repository-url>
   cd Combinatorial-Games
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
  
   ```
   *Or manually install:*
   ```bash
   pip install pygame
   # If use python3: pip3 install pygame
   ```
  Make sure pygame has the same root as python
  
3. **Verify Project Structure**
   Ensure all files are in the correct locations as shown in the project structure above.

4. **Run the Game**
   ```bash
   python main.py
   ```

## 🎯 Features

### Core Gameplay
- **Human vs AI Competition**: Play against computer opponents
- **Multiple Difficulty Levels**: 
  - Easy (Level 1): AI makes occasional optimal moves
  - Normal (Level 2): Balanced strategy
  - Hard (Level 3): Mostly optimal play
  - Insane (Level 4): Perfect mathematical play
- **Real-time Game Analysis**: Display current game state (winning/losing positions)

### User Interface
- **Visual Card Representation**: Intuitive card stack visualization
- **Dual Control Schemes**: 
  - Mouse: Point-and-click interface
  - Keyboard: Quick navigation with arrow keys
- **Game State Tracking**: Current player turn, move history, game status
- **Responsive Design**: Adapts to different screen sizes

### Technical Features
- **Modular Architecture**: Easy to add new games
- **Mathematical Integration**: Built-in game theory algorithms
- **Error Handling**: Robust error recovery and user feedback
- **Save/Load Ready**: Architecture supports game state persistence

## 🕹️ How to Play

### Starting a Game
1. Run `python main.py`
2. Select your desired game from the menu
3. Choose difficulty level (1-4)
4. Begin playing!

### Controls

#### Mouse Controls
- **Left Click**: Select card piles/positions
- **Button Clicks**: Adjust numbers and confirm moves
- **Hover Effects**: Visual feedback on interactive elements

#### Keyboard Controls
- **Arrow Keys**:
  - ↑/↓: Increase/decrease number of cards to take
  - ←/→: Navigate between different card piles
- **Enter/Return**: Confirm your move
- **ESC**: Close game (or use window close button)

### Game Flow
1. **Player Turn**: 
   - Select a card pile
   - Choose how many cards to take
   - Confirm your move
2. **AI Turn**: 
   - Watch AI make its strategic move
   - Analyze the AI's strategy
3. **Continue** alternating turns until game completion
4. **Victory**: The player who makes the last legal move wins!

## 🧠 Mathematical Background

All games in this collection are based on combinatorial game theory principles:

### Key Concepts
- **Impartial Games**: Same moves available to both players
- **Normal Play**: Last move wins convention
- **Nim-Heap Equivalents**: Games reducible to Nim positions
- **Grundy Numbers**: Mathematical values for game positions
- **Winning Strategies**: Algorithmic approaches to perfect play

### Educational Value
- Learn mathematical game theory through interactive play
- Understand concepts like Sprague-Grundy theorem
- Develop strategic thinking and pattern recognition
- Explore computational complexity in games

## 🔧 Technical Details

### Game Class Architecture
The `Game_class.py` provides a unified interface for all games:
- **Initialization**: Game setup and configuration
- **Move Generation**: Legal move enumeration
- **State Evaluation**: Position analysis and winning determination
- **AI Strategy**: Difficulty-based decision making

### Pygame Implementation
- **Rendering**: Efficient card and UI element drawing
- **Event Handling**: Comprehensive input management
- **Animation**: Smooth transitions and visual feedback
- **Performance**: Optimized for real-time gameplay

## 🎯 Strategy Tips

### General Principles
1. **Learn the Patterns**: Each game has characteristic winning positions
2. **Think Ahead**: Consider multiple moves in advance
3. **Force Opponent Mistakes**: Create positions where all moves lead to losing outcomes
4. **Practice**: Start with easier difficulties to understand game mechanics

### Game-Specific Advice
- **Take Coins**: Learn modulo arithmetic patterns
- **Nim Variants**: Master the concept of nim-sum
- **Splitting Games**: Understand heap division consequences
- **Removal Games**: Recognize symmetric and mirror strategies

## 🐛 Troubleshooting

### Common Issues

**Game won't start:**
- Ensure Python 3.7+ is installed
- Verify pygame is properly installed: `python -m pygame.version`
- Check all game files are in the correct directories

**Import errors:**
- Confirm `Game_class.py` is in the parent directory
- Verify the `games/` folder contains all game modules
- Check Python path and working directory

**Display issues:**
- Update graphics drivers
- Try running in windowed mode if fullscreen has issues
- Check display resolution compatibility

### Getting Help
1. Check the error messages in the console
2. Verify file locations match the project structure
3. Ensure all dependencies are installed
4. Consult the mathematical game rules for understanding gameplay

## 📚 Extending the Collection

### Adding New Games
1. Create a new game module in the `games/` directory
2. Implement the required functions:
   - `initial_setting()`
   - `judge_win()`
   - `judge_move_global()`
   - `acted_list()`
3. Update the main menu in `main.py`
4. Test thoroughly with various game states

### Customization Options
- Modify difficulty curves
- Add new visual themes
- Implement additional game variants
- Create tutorial modes

## 👥 Contributing

We welcome contributions to:
- Add new combinatorial games
- Improve AI algorithms
- Enhance user interface
- Fix bugs and optimize performance
- Translate to other languages


## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏆 Acknowledgments

- Based on classical combinatorial game theory
- Inspired by mathematical puzzle collections
- Built with Pygame community resources

---

**Enjoy exploring the fascinating world of mathematical games! 🎲**
