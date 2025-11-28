"""
Test cases for ICG Games
"""

import unittest
import sys
import os

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, '..', 'src')
sys.path.insert(0, src_path)

from src.games.card_nim.logic import CardNimLogic, AutoPlayer

class TestCardNimLogic(unittest.TestCase):
    """Test cases for Card Nim game logic"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.logic = CardNimLogic()
    
    def test_initialization(self):
        """Test game initialization"""
        self.logic.initialize_game("PVE", 2)
        self.assertIsNotNone(self.logic.positions)
        self.assertGreater(len(self.logic.positions), 0)
        self.assertEqual(self.logic.current_player, "Player 1")
        self.assertFalse(self.logic.game_over)
    
    def test_nim_sum_calculation(self):
        """Test nim-sum calculation"""
        # Test case: positions [3, 4, 5]
        # 3 ^ 4 ^ 5 = 0b11 ^ 0b100 ^ 0b101 = 0b010 = 2
        self.logic.positions = [3, 4, 5]
        self.assertEqual(self.logic.calculate_nim_sum(), 2)
        
        # Test case: positions [1, 1, 1]
        # 1 ^ 1 ^ 1 = 1
        self.logic.positions = [1, 1, 1]
        self.assertEqual(self.logic.calculate_nim_sum(), 1)
    
    def test_judge_win(self):
        """Test winning position judgment"""
        # Winning position (nim-sum != 0)
        self.logic.positions = [3, 4, 5]
        self.assertTrue(self.logic.judge_win())
        
        # Losing position (nim-sum == 0)
        self.logic.positions = [1, 2, 3]  # 1 ^ 2 ^ 3 = 0
        self.assertFalse(self.logic.judge_win())
    
    def test_make_move(self):
        """Test making a valid move"""
        self.logic.positions = [3, 4, 5]
        self.logic.selected_position_index = 0
        self.logic.selected_count = 2
        
        result = self.logic.make_move(0, 2)
        self.assertTrue(result)
        self.assertEqual(self.logic.positions[0], 1)
    
    def test_invalid_move(self):
        """Test making an invalid move"""
        self.logic.positions = [3, 4, 5]
        
        # Invalid position index
        result = self.logic.make_move(5, 1)
        self.assertFalse(result)
        
        # Invalid card count
        result = self.logic.make_move(0, 5)  # Trying to take 5 from position with 3
        self.assertFalse(result)
    
    def test_game_over(self):
        """Test game over condition"""
        self.logic.positions = [1]  # Only one card left
        self.logic.make_move(0, 1)  # Take the last card
        
        self.assertTrue(self.logic.game_over)
        self.assertEqual(self.logic.winner, "Player 1")

class TestAutoPlayer(unittest.TestCase):
    """Test cases for AI player"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.positions = [3, 4, 5]
        self.ai = AutoPlayer(self.positions)
    
    def test_nim_sum_calculation(self):
        """Test AI nim-sum calculation"""
        nim_sum = self.ai.calculate_nim_sum([3, 4, 5])
        self.assertEqual(nim_sum, 2)
    
    def test_find_winning_move(self):
        """Test finding winning moves"""
        # Test case where winning move exists
        self.ai.positions = [3, 4, 5]  # nim-sum = 2
        move = self.ai.find_winning_move()
        self.assertIsNotNone(move)
        position_idx, count = move
        self.assertIn(position_idx, [0, 1, 2])
        self.assertGreater(count, 0)
        self.assertLessEqual(count, self.ai.positions[position_idx])
        
        # Test case where no winning move (losing position)
        self.ai.positions = [1, 2, 3]  # nim-sum = 0
        move = self.ai.find_winning_move()
        self.assertIsNone(move)
    
    def test_move_instruction(self):
        """Test AI move generation"""
        # Test with different difficulties
        for difficulty in [1, 2, 3, 4]:
            move = self.ai.move_instruction(difficulty)
            self.assertIsNotNone(move)
            position_idx, count = move
            self.assertIn(position_idx, range(len(self.positions)))
            self.assertGreater(count, 0)
            self.assertLessEqual(count, self.positions[position_idx])

if __name__ == '__main__':
    unittest.main()