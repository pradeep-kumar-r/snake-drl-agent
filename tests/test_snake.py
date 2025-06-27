"""
Unit tests for the Snake class.
"""
import unittest
from unittest.mock import patch

from src.game.snake import Snake
from src.game.direction import Direction

class TestSnake(unittest.TestCase):
    """Test cases for the Snake class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.board_dim = 20
        self.init_pos = (0, 0)
        self.init_length = 3
        self.init_direction = Direction.RIGHT
        self.snake = Snake(
            board_dim=self.board_dim,
            init_pos=self.init_pos,
            init_length=self.init_length,
            init_direction=self.init_direction
        )
    
    def test_initialization(self):
        """Test snake initialization."""
        self.assertEqual(len(self.snake), self.init_length)
        self.assertEqual(self.snake.get_head(), (self.init_pos[0], self.init_pos[1]))
        self.assertEqual(self.snake.get_direction(), self.init_direction)
        self.assertTrue(self.snake.alive)
    
    def test_movement(self):
        """Test snake movement."""
        initial_head = self.snake.get_head()
        self.snake.move()
        new_head = self.snake.get_head()
        # Should move right by default
        self.assertEqual(new_head, (initial_head[0] + 1, initial_head[1]))
    
    def test_direction_change(self):
        """Test changing snake direction."""
        # Change direction to down
        self.snake.set_direction(Direction.DOWN)
        self.snake.move()
        self.assertEqual(self.snake.get_head(), (0, 1))
        
        # Try to move back up (should be ignored as it's opposite direction)
        self.snake.set_direction(Direction.UP)
        self.snake.move()
        # Should still move down
        self.assertEqual(self.snake.get_head(), (0, 2))
    
    def test_growth(self):
        """Test snake growth when eating food."""
        initial_length = len(self.snake)
        self.snake.should_grow = True
        self.snake.move()
        self.assertEqual(len(self.snake), initial_length + 1)
        self.assertFalse(self.snake.should_grow)
    
    def test_wrap_around(self):
        """Test snake wrapping around the board edges."""
        boundary = self.board_dim // 2
        # Move to right edge
        for _ in range(boundary):
            self.snake.move()
        # Should wrap around to left edge
        self.snake.move()
        self.assertEqual(self.snake.get_head()[0], -boundary)
    
    def test_collision_detection(self):
        """Test collision detection with self."""
        # Create a snake that's about to collide with itself
        self.snake.body = [(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]
        self.assertTrue(self.snake.check_collision())
    
    def test_kill(self):
        """Test killing the snake."""
        self.snake.kill()
        self.assertFalse(self.snake.alive)
        initial_head = self.snake.get_head()
        self.snake.move()  # Shouldn't move when dead
        self.assertEqual(self.snake.get_head(), initial_head)
        
    def test_equality(self):
        """Test snake equality comparison."""
        snake1 = Snake(
            board_dim=self.board_dim,
            init_pos=self.init_pos,
            init_length=self.init_length,
            init_direction=self.init_direction
        )
        
        snake2 = Snake(
            board_dim=self.board_dim,
            init_pos=self.init_pos,
            init_length=self.init_length,
            init_direction=self.init_direction
        )
        
        snake3 = Snake(
            board_dim=self.board_dim,
            init_pos=(1, 1),  # Different position
            init_length=self.init_length,
            init_direction=self.init_direction
        )
        
        self.assertEqual(snake1, snake2)
        self.assertNotEqual(snake1, snake3)
        self.assertNotEqual(snake1, "not a snake object")

if __name__ == '__main__':
    unittest.main()
