"""
Unit tests for the UI class.
"""
import unittest
from unittest.mock import MagicMock, patch, call
import tkinter as tk
from src.game.ui import UI
from src.game.snake import Snake
from src.game.food import SimpleFood
from src.game.direction import Direction

class TestUI(unittest.TestCase):
    """Test cases for the UI class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock master
        self.master = MagicMock(spec=tk.Tk)
        
        # Mock UI configuration
        self.ui_config = {
            "BOARD_DIM": 20,
            "TITLE": {
                "TEXT": "Snake Game",
                "FONT": {"NAME": "Arial", "SIZE": 20, "STYLE": "bold"},
                "PADDING": 10
            },
            "CANVAS": {
                "BG": "black",
                "BD": 0,
                "HIGHLIGHTTHICKNESS": 0
            },
            "SCORE": {
                "FONT": {"NAME": "Arial", "SIZE": 12, "STYLE": "normal"},
                "SIDE": "left",
                "PADDING": 20
            },
            "LEGEND": {
                "FONT": {"NAME": "Arial", "SIZE": 10, "STYLE": "normal"},
                "PADDING": 5
            },
            "FOOD": {
                "SIMPLE": {
                    "FILL": "red",
                    "FONT": {"NAME": "Arial", "SIZE": 10}
                },
                "SUPER": {
                    "FILL": "yellow",
                    "FONT": {"NAME": "Arial", "SIZE": 10}
                }
            },
            "SNAKE": {
                "FILL": "green"
            },
            "GAME_OVER": {
                "TEXT": "Game Over!",
                "FILL": "red",
                "FONT": {"NAME": "Arial", "SIZE": 30, "STYLE": "bold"}
            }
        }
        
        # Create a mock snake
        self.snake = Snake(
            board_dim=20,
            init_pos=(0, 0),
            init_length=3,
            init_direction=Direction.RIGHT
        )
        
        # Create a mock food
        self.food = SimpleFood(board_dim=20)
        self.food.position = (5, 5)
        self.food.active = True
        
        # Initialize UI
        self.ui = UI(
            master=self.master,
            ui_config=self.ui_config,
            snake=self.snake,
            food=self.food,
            score=0,
            high_score=100
        )
    
    def test_initialization(self):
        """Test UI initialization."""
        self.assertEqual(self.ui.board_width, self.ui_config["BOARD_DIM"])
        self.assertEqual(self.ui.board_height, self.ui_config["BOARD_DIM"])
        self.assertEqual(self.ui.snake, self.snake)
        self.assertEqual(self.ui.food, self.food)
        self.assertEqual(self.ui.score, 0)
        self.assertEqual(self.ui.high_score, 100)
    
    @patch('tkinter.Label')
    def test_draw_title(self, mock_label):
        """Test drawing the title."""
        self.ui._draw_title()
        
        # Check if title label was created with correct parameters
        mock_label.assert_called_once()
        args, kwargs = mock_label.call_args
        self.assertEqual(kwargs["text"], self.ui_config["TITLE"]["TEXT"])
        self.assertEqual(kwargs["font"][0], self.ui_config["TITLE"]["FONT"]["NAME"])
        self.assertEqual(kwargs["font"][1], self.ui_config["TITLE"]["FONT"]["SIZE"])
        self.assertEqual(kwargs["font"][2], self.ui_config["TITLE"]["FONT"]["STYLE"])
    
    @patch('tkinter.Canvas')
    def test_draw_game_canvas(self, mock_canvas):
        """Test drawing the game canvas."""
        self.ui._draw_game_canvas()
        
        # Check if canvas was created with correct parameters
        mock_canvas.assert_called_once_with(
            self.master,
            width=self.ui_config["BOARD_DIM"],
            height=self.ui_config["BOARD_DIM"],
            bg=self.ui_config["CANVAS"]["BG"],
            bd=self.ui_config["CANVAS"]["BD"],
            highlightthickness=self.ui_config["CANVAS"]["HIGHLIGHTTHICKNESS"]
        )
    
    @patch('tkinter.Frame')
    @patch('tkinter.Label')
    def test_draw_score_labels(self, mock_label, mock_frame):
        """Test drawing score labels."""
        # Mock the frame and label
        mock_frame_instance = MagicMock()
        mock_frame.return_value = mock_frame_instance
        
        mock_label_instance = MagicMock()
        mock_label.return_value = mock_label_instance
        
        self.ui._draw_score_labels()
        
        # Check if frame was created
        mock_frame.assert_called_once()
        
        # Check if labels were created with correct parameters
        self.assertEqual(mock_label.call_count, 2)  # Current score and high score
        
        # Check current score label
        args, kwargs = mock_label.call_args_list[0]
        self.assertIn("Score: 0", kwargs["text"])
        self.assertEqual(kwargs["font"][0], self.ui_config["SCORE"]["FONT"]["NAME"])
        self.assertEqual(kwargs["font"][1], self.ui_config["SCORE"]["FONT"]["SIZE"])
        
        # Check pack was called on the frame
        mock_frame_instance.pack.assert_called_once_with(pady=self.ui_config["SCORE"]["PADDING"])
    
    @patch('tkinter.Canvas.create_rectangle')
    def test_draw_board(self, mock_create_rect):
        """Test drawing the game board."""
        # Mock the canvas
        self.ui.canvas = MagicMock()
        
        # Call the method
        self.ui._draw_board()
        
        # Check if canvas was cleared and board was drawn
        self.ui.canvas.delete.assert_called_once_with("all")
        
        # The exact number of rectangles depends on the implementation
        # Just check that create_rectangle was called
        self.ui.canvas.create_rectangle.assert_called()
    
    @patch('tkinter.Canvas.create_rectangle')
    def test_draw_snake(self, mock_create_rect):
        """Test drawing the snake."""
        # Mock the canvas
        self.ui.canvas = MagicMock()
        
        # Call the method
        self.ui._draw_snake()
        
        # Should create rectangles for each segment of the snake
        # For a snake of length 3, we expect 3 rectangles
        self.assertEqual(self.ui.canvas.create_rectangle.call_count, 3)
    
    @patch('tkinter.Canvas.create_text')
    def test_draw_food(self, mock_create_text):
        """Test drawing the food."""
        # Mock the canvas
        self.ui.canvas = MagicMock()
        
        # Call the method
        self.ui._draw_food()
        
        # Should create text for the food
        mock_create_text.assert_called_once()
        
        # Check if food lifetime label was updated
        self.assertIn("Food Lifetime:", self.ui.food_lifetime_label.cget("text"))
    
    @patch('tkinter.Canvas.create_text')
    def test_game_over_screen(self, mock_create_text):
        """Test drawing the game over screen."""
        # Mock the canvas
        self.ui.canvas = MagicMock()
        
        # Call the method
        self.ui._game_over_screen()
        
        # Should create text for game over message and final score
        self.assertEqual(mock_create_text.call_count, 2)
        
        # Check if game over text was created
        args, kwargs = mock_create_text.call_args_list[0]
        self.assertEqual(kwargs["text"], self.ui_config["GAME_OVER"]["TEXT"])
        self.assertEqual(kwargs["fill"], self.ui_config["GAME_OVER"]["FILL"])
        
        # Check if score text was created
        args, kwargs = mock_create_text.call_args_list[1]
        self.assertIn("Final Score:", kwargs["text"])
    
    @patch('src.game.ui.UI._draw_title')
    @patch('src.game.ui.UI._draw_game_canvas')
    @patch('src.game.ui.UI._draw_score_labels')
    @patch('src.game.ui.UI._draw_legend')
    @patch('src.game.ui.UI._draw_food_lifetime_label')
    def test_full_render(self, mock_draw_food_lifetime, mock_draw_legend, 
                        mock_draw_scores, mock_draw_canvas, mock_draw_title):
        """Test the full render method."""
        # First call should initialize everything
        self.ui.full_render()
        
        # Check that all draw methods were called
        mock_draw_title.assert_called_once()
        mock_draw_canvas.assert_called_once()
        mock_draw_scores.assert_called_once()
        mock_draw_legend.assert_called_once()
        mock_draw_food_lifetime.assert_called_once()
        
        # Second call should not reinitialize
        self.ui.full_render()
        self.assertEqual(mock_draw_title.call_count, 1)  # Still only called once

if __name__ == '__main__':
    unittest.main()
