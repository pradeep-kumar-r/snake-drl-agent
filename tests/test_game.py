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
                "SNAKE_INIT_POS": (10, 10),
                "SNAKE_INIT_LENGTH": 3,
                "SNAKE_INIT_DIRECTION": "RIGHT"
            },
            "FOOD": {
                "SUPERFOOD_PROBABILITY": 0.1,
                "SUPERFOOD_LIFETIME": 10
            },
            "SCORE": {
                "EAT_FOOD": 10.0,
                "XPLIER_EAT_SUPERFOOD": 2.0
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
    
    @patch('random.random', return_value=0.05)
    def test_generate_superfood(self, mock_random):
        """Test superfood generation."""
        # Set up conditions for superfood generation
        self.game.food_count = 1
        self.game.is_food_active = False  # Fixed: use game.is_food_active, not self.is_food_active
        self.game.steps_elapsed = 5  # Ensure steps_elapsed >= 3 for food generation
        
        # Generate food
        self.game._generate_or_update_food()
        
        # Verify superfood was generated
        self.assertIsNotNone(self.game.current_food)
        self.assertIsInstance(self.game.current_food, SuperFood)
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
        print(f"Snake head: {snake_body[0]}")
    
    def test_food_eating(self):
        """Test food eating and score update."""
        # Get the snake's current head position
        head_pos = self.game.snake.get_head()
        
        # Place food one step to the right of the snake's head
        food_pos = (head_pos[0] + 1, head_pos[1])
        self.game.current_food = SimpleFood(board_dim=self.game_config["BOARD_DIM"])
        self.game.current_food.position = food_pos
        self.game.current_food.active = True
        self.game.is_food_active = True  # This is crucial - need to set both flags
        
        # Move snake to food (one step right)
        self.game.step(1)  # Move right
        
        # Check if food was eaten and score updated
        self.assertEqual(self.game.score, self.game_config["SCORE"]["EAT_FOOD"])
    
    def test_collision_detection(self):
        """Test collision detection."""
        # Create a snake body where the head will collide with the body after moving
        # Initial body: [(5,5), (6,5), (7,5), (8,5)]
        # After moving left: [(4,5), (5,5), (6,5), (7,5)] - head at (4,5) doesn't collide
        # After another left: [(3,5), (4,5), (5,5), (6,5)] - still no collision
        # After turning down: [(3,6), (3,5), (4,5), (5,5)] - no collision
        # After turning right: [(4,6), (3,6), (3,5), (4,5)] - no collision
        # After another right: [(5,6), (4,6), (3,6), (3,5)] - no collision
        # After another right: [(6,6), (5,6), (4,6), (3,6)] - no collision
        # After turning up: [(6,5), (6,6), (5,6), (4,6)] - head at (6,5) will be in body
        
        # Set up the snake with a body that will cause collision after specific movements
        self.game.snake.body = [(5, 5), (6, 5), (7, 5), (8, 5)]
        
        # Move left twice
        self.game.step(3)  # LEFT
        self.game.step(3)  # LEFT
        
        # Move down
        self.game.step(2)  # DOWN
        
        # Move right three times
        self.game.step(1)  # RIGHT
        self.game.step(1)  # RIGHT
        self.game.step(1)  # RIGHT
        
        # Move up - this should cause collision
        self.game.step(4)  # UP
        
        # Verify game is over due to collision
        self.assertTrue(self.game.is_game_over)
        
    def test_get_state(self):
        """Test getting the game state."""
        state = self.game.get_state()
        self.assertIsInstance(state, dict)
        self.assertIn('game_id', state)
        self.assertIn('updated_at', state)
        self.assertIn('steps_elapsed', state)
        self.assertIn('food_count', state)
        self.assertIn('score', state)
        self.assertIn('is_game_over', state)

if __name__ == '__main__':
    unittest.main()
