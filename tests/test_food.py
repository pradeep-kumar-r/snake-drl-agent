"""
Unit tests for the Food classes.
"""
import unittest
from unittest.mock import patch
import random
from typing import List, Tuple

from src.game.food import SimpleFood, SuperFood

class TestFood(unittest.TestCase):
    """Test cases for the Food classes."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.board_dim = 20
        self.simple_food = SimpleFood(board_dim=self.board_dim)
        self.super_food = SuperFood(board_dim=self.board_dim, lifetime=10)
    
    def test_simple_food_initialization(self):
        """Test SimpleFood initialization."""
        self.assertFalse(self.simple_food.active)
        self.assertIsNone(self.simple_food.position)
        self.assertEqual(self.simple_food.remaining_steps, 0)
    
    @patch('random.randint', side_effect=[5, 5])  # Mock random position
    def test_simple_food_placement(self, mock_randint):
        """Test placing simple food on the board."""
        snake_body = [(0, 0), (1, 0), (1, 1)]
        self.simple_food.place_food(snake_body)
        self.assertTrue(self.simple_food.active)
        self.assertEqual(self.simple_food.position, (5, 5))
    
    def test_simple_food_eaten(self):
        """Test simple food eaten detection."""
        self.simple_food.position = (5, 5)
        self.simple_food.active = True
        self.assertTrue(self.simple_food.is_eaten((5, 5)))
        self.assertFalse(self.simple_food.is_eaten((0, 0)))
    
    def test_simple_food_update(self):
        """Test simple food update method."""
        # Simple food's update method should do nothing
        self.simple_food.position = (5, 5)
        self.simple_food.active = True
        self.simple_food.update()
        self.assertEqual(self.simple_food.position, (5, 5))
        self.assertTrue(self.simple_food.active)
    
    def test_simple_food_equality(self):
        """Test SimpleFood equality comparison."""
        food1 = SimpleFood(board_dim=self.board_dim)
        food1.position = (5, 5)
        
        food2 = SimpleFood(board_dim=self.board_dim)
        food2.position = (5, 5)
        
        food3 = SimpleFood(board_dim=self.board_dim)
        food3.position = (6, 6)
        
        self.assertEqual(food1, food2)
        self.assertNotEqual(food1, food3)
        self.assertNotEqual(food1, "not a food object")
    
    def test_super_food_initialization(self):
        """Test SuperFood initialization."""
        self.assertFalse(self.super_food.active)
        self.assertIsNone(self.super_food.position)
        self.assertEqual(self.super_food.lifetime, 10)
        self.assertEqual(self.super_food.remaining_steps, 0)
    
    @patch('random.randint', side_effect=[5, 5])  # Mock random position
    def test_super_food_placement(self, mock_randint):
        """Test placing super food on the board."""
        snake_body = [(0, 0), (1, 0), (1, 1)]
        self.super_food.place_food(snake_body)
        self.assertTrue(self.super_food.active)
        self.assertEqual(self.super_food.position, (5, 5))
        self.assertEqual(self.super_food.remaining_steps, 10)
    
    def test_super_food_update(self):
        """Test super food lifetime update."""
        self.super_food.active = True
        self.super_food.remaining_steps = 3
        
        self.super_food.update()
        self.assertEqual(self.super_food.remaining_steps, 2)
        self.assertTrue(self.super_food.active)
        
        self.super_food.update()
        self.assertEqual(self.super_food.remaining_steps, 1)
        self.assertTrue(self.super_food.active)
        
        self.super_food.update()
        self.assertEqual(self.super_food.remaining_steps, 0)
        self.assertTrue(self.super_food.active)
        
        self.super_food.update()
        self.assertEqual(self.super_food.remaining_steps, -1)
        self.assertFalse(self.super_food.active)
    
    def test_super_food_eaten(self):
        """Test super food eaten detection."""
        self.super_food.position = (5, 5)
        self.super_food.active = True
        self.assertTrue(self.super_food.is_eaten((5, 5)))
        self.assertFalse(self.super_food.is_eaten((0, 0)))
        
        # Test when food is not active
        self.super_food.active = False
        self.assertFalse(self.super_food.is_eaten((5, 5)))
    
    def test_super_food_equality(self):
        """Test SuperFood equality comparison."""
        food1 = SuperFood(board_dim=self.board_dim, lifetime=10)
        food1.position = (5, 5)
        
        food2 = SuperFood(board_dim=self.board_dim, lifetime=10)
        food2.position = (5, 5)
        
        food3 = SuperFood(board_dim=self.board_dim, lifetime=10)
        food3.position = (6, 6)
        
        self.assertEqual(food1, food2)
        self.assertNotEqual(food1, food3)
        self.assertNotEqual(food1, "not a food object")
        self.assertNotEqual(food1, self.simple_food)

if __name__ == '__main__':
    unittest.main()
