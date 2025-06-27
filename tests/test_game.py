"""
Unit tests for the game module.
"""
import unittest
from unittest.mock import MagicMock, patch
import numpy as np
from src.game.game import Game
from src.game.snake import Snake
from src.game.food import SimpleFood, SuperFood
from src.game.direction import Direction

class TestGame(unittest.TestCase):
    """Test cases for the Game class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.game_config = {
            "BOARD_DIM": 20,
            "SNAKE": {
                "SNAKE_INIT_POS": (0, 0),
                "SNAKE_INIT_LENGTH": 3,
                "SNAKE_INIT_DIRECTION": Direction.RIGHT
            },
            "FOOD": {
                "SUPERFOOD_PROBABILITY": 0.1,
                "SUPERFOOD_LIFETIME": 10
            },
            "SCORE": {
                "EAT_FOOD": 10,
                "XPLIER_EAT_SUPERFOOD": 2
            }
        }
        self.data_config = {
            "HIGH_SCORE_FILE_PATH": "high_score.txt",
            "SCORES_FILE_PATH": "scores.txt"
        }
        self.game = Game(game_config=self.game_config, data_config=self.data_config)
    
    def test_initialization(self):
        """Test game initialization."""
        self.assertIsInstance(self.game.snake, Snake)
        self.assertEqual(len(self.game.snake), 3)
        self.assertEqual(self.game.score, 0)
        self.assertFalse(self.game.is_game_over)
    
    def test_reset(self):
        """Test game reset functionality."""
        # Modify some attributes
        self.game.score = 100
        self.game.is_game_over = True
        self.game.steps_elapsed = 50
        
        # Reset the game
        self.game.reset()
        
        # Check if reset worked
        self.assertEqual(self.game.score, 0)
        self.assertFalse(self.game.is_game_over)
        self.assertEqual(self.game.steps_elapsed, 0)
        self.assertEqual(len(self.game.snake), 3)
    
    @patch('random.random', return_value=0.05)  # Will trigger superfood
    def test_generate_superfood(self, mock_random):
        """Test superfood generation."""
        self.game.food_count = 1  # Need at least one food to generate superfood
        self.game._generate_or_update_food()
        self.assertIsNotNone(self.game.current_food)
        self.assertTrue(hasattr(self.game.current_food, 'remaining_steps'))
    
    def test_step_movement(self):
        """Test snake movement in a step."""
        initial_head = self.game.snake.get_head()
        # Step returns multiple values, but we don't need them for this test
        self.game.step(1)  # Move right
        new_head = self.game.snake.get_head()
        self.assertEqual(new_head, (initial_head[0] + 1, initial_head[1]))
    
    def test_step_return_values(self):
        """Test the return values of the step method."""
        # Reset game to ensure clean state
        self.game.reset()
        
        # Take a step and check return values
        steps_elapsed, terminated, score, snake_body, direction, is_food_active, food_pos, remaining_steps = self.game.step(1)
        
        self.assertIsInstance(steps_elapsed, int)
        self.assertIsInstance(terminated, bool)
        self.assertIsInstance(score, int)
        self.assertIsInstance(snake_body, list)
        self.assertIsInstance(direction, Direction)
        self.assertIsInstance(is_food_active, bool)
    
    def test_food_eating(self):
        """Test food eating and score update."""
        # Place food in front of the snake
        food_pos = (3, 0)
        self.game.current_food = SimpleFood(board_dim=20)
        self.game.current_food.position = food_pos
        self.game.current_food.active = True
        
        # Move snake to food
        for _ in range(3):
            self.game.step(1)  # Move right
        
        # Check if food was eaten and score updated
        self.assertNotEqual(self.game.current_food.position, food_pos)
        self.assertEqual(self.game.score, self.game_config["SCORE"]["EAT_FOOD"])
    
    def test_collision_detection(self):
        """Test collision detection."""
        # Make the snake collide with itself
        self.game.snake.body = [(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]
        self.game.step(0)  # No movement, but will check collision
        self.assertTrue(self.game.is_game_over)
        
    def test_get_state(self):
        """Test getting the game state."""
        state = self.game.get_state()
        self.assertIsInstance(state, dict)
        self.assertIn('score', state)
        self.assertIn('high_score', state)
        self.assertIn('steps_elapsed', state)
        self.assertIn('is_game_over', state)

if __name__ == '__main__':
    unittest.main()
