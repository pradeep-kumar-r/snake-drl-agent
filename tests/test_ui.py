#!/usr/bin/env python3
"""
Test script for the Pygame UI implementation.
"""
import sys
import time
import unittest
from unittest.mock import MagicMock, patch
import pygame
import numpy as np
from src.config import ConfigManager
from src.game.game import Game
from src.game.snake import Snake
from src.game.food import SimpleFood
from src.game.direction import Direction
from src.game.ui import UI
from src.game.colour import Colour

class TestUI(unittest.TestCase):
    """Test cases for the UI class."""
    
    def setUp(self):
        """Set up test fixtures."""
        pygame.init()
        self.config_manager = ConfigManager()
        self.ui_config = self.config_manager.get_ui_config()
        self.game_config = self.config_manager.get_game_config()
        
        # Create a snake for testing
        self.snake = Snake(
            board_dim=self.game_config["BOARD_DIM"],
            init_pos=self.game_config["SNAKE"]["SNAKE_INIT_POS"],
            init_length=self.game_config["SNAKE"]["SNAKE_INIT_LENGTH"],
            init_direction=Direction[self.game_config["SNAKE"]["SNAKE_INIT_DIRECTION"]]
        )
        
        # Create food for testing
        self.food = SimpleFood(board_dim=self.game_config["BOARD_DIM"])
        self.food.position = (5, 5)
        self.food.active = True
        
        # Create UI
        self.ui = UI(
            ui_config=self.ui_config,
            snake=self.snake,
            episode=1,
            food=self.food,
            score=0,
            high_score=0
        )
    
    def tearDown(self):
        """Clean up after tests."""
        if hasattr(self, 'ui') and self.ui:
            self.ui.close()
    
    def test_initialization(self):
        """Test UI initialization."""
        self.assertEqual(self.ui.board_width, self.ui_config["BOARD_DIM"])
        self.assertEqual(self.ui.board_height, self.ui_config["BOARD_DIM"])
        self.assertEqual(self.ui.cell_size, self.ui_config["CELL_SIZE_IN_PIXELS"])
        self.assertEqual(self.ui.snake, self.snake)
        self.assertEqual(self.ui.food, self.food)
        self.assertEqual(self.ui.score, 0)
        self.assertEqual(self.ui.high_score, 0)
        self.assertEqual(self.ui.episode, 1)
    
    def test_update_components(self):
        """Test updating UI components."""
        new_snake = Snake(
            board_dim=self.game_config["BOARD_DIM"],
            init_pos=(15, 10),  # Different position
            init_length=self.game_config["SNAKE"]["SNAKE_INIT_LENGTH"],
            init_direction=Direction[self.game_config["SNAKE"]["SNAKE_INIT_DIRECTION"]]
        )
        
        new_food = SimpleFood(board_dim=self.game_config["BOARD_DIM"])
        new_food.position = (10, 10)
        new_food.active = True
        
        new_score = 100
        
        self.ui.update_components(
            new_score=new_score,
            new_snake=new_snake,
            new_food=new_food
        )
        
        self.assertEqual(self.ui.score, new_score)
        self.assertEqual(self.ui.snake, new_snake)
        self.assertEqual(self.ui.food, new_food)
    
    def test_headless_render(self):
        """Test headless rendering."""
        window_rgb_array, board_rgb_array = self.ui.headless_render()
        
        self.assertIsInstance(window_rgb_array, np.ndarray)
        self.assertIsInstance(board_rgb_array, np.ndarray)
        self.assertEqual(window_rgb_array.shape, (3, self.ui.window_height, self.ui.window_width))
        self.assertEqual(board_rgb_array.shape, (3, self.ui.board_pixel_height, self.ui.board_pixel_width))
    
    @patch('pygame.display.flip')
    def test_full_render(self, mock_flip):
        """Test full rendering."""
        self.ui.full_render()
        mock_flip.assert_called_once()


def main():
    """Run a simple test of the Pygame UI."""
    # Initialize configuration
    config_manager = ConfigManager()
    game_config = config_manager.get_game_config()
    ui_config = config_manager.get_ui_config()
    data_config = config_manager.get_data_config()
    
    # Initialize game
    game = Game(game_config=game_config, data_config=data_config)
    
    # Initialize UI
    ui = UI(
        ui_config=ui_config,
        snake=game.snake,
        episode=1,
        food=game.current_food,
        score=0,
        high_score=0
    )
    
    # Main game loop
    running = True
    clock = pygame.time.Clock()
    
    while running:
        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_RIGHT:
                    game.step(1)  # RIGHT
                elif event.key == pygame.K_DOWN:
                    game.step(2)  # DOWN
                elif event.key == pygame.K_LEFT:
                    game.step(3)  # LEFT
                elif event.key == pygame.K_UP:
                    game.step(4)  # UP
        
        # Update UI
        ui.update_components(
            new_score=game.score,
            new_snake=game.snake,
            new_food=game.current_food
        )
        
        # Render
        ui.full_render(is_game_over=game.is_game_over)
        
        # Cap the frame rate
        clock.tick(5)  # 5 FPS for visibility
    
    # Clean up
    ui.close()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
