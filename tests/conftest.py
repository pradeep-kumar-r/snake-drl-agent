"""
Pytest configuration and fixtures for testing.
"""
import pytest
from unittest.mock import MagicMock, patch
import numpy as np
import torch

# Add any common fixtures here that should be available across all test files

@pytest.fixture
def mock_config():
    """Fixture that provides a mock ConfigManager."""
    config = MagicMock()
    
    # Mock game config
    game_config = {
        "BOARD_DIM": 20,
        "SNAKE": {
            "SNAKE_INIT_POS": (0, 0),
            "SNAKE_INIT_LENGTH": 3,
            "SNAKE_INIT_DIRECTION": "RIGHT"
        },
        "FOOD": {
            "SUPERFOOD_PROBABILITY": 0.1,
            "SUPERFOOD_LIFETIME": 10
        },
        "SCORE": {
            "EAT_FOOD": 10,
            "XPLIER_EAT_SUPERFOOD": 2
        },
        "EPISODES_PER_RENDER": 10,
        "SLEEP_PER_TIMESTEP": 0.1
    }
    
    # Mock data config
    data_config = {
        "HIGH_SCORE_FILE_PATH": "high_score.txt",
        "SCORES_FILE_PATH": "scores.txt"
    }
    
    # Mock UI config
    ui_config = {
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
    
    # Mock model config
    model_config = {
        "NUM_ACTIONS": 5,
        "LEARNING_RATE": 0.001,
        "IMAGE_INPUT_SIZE": 84
    }
    
    # Mock training config
    training_config = {
        "BATCH_SIZE": 4,
        "GAMMA": 0.99,
        "EPSILON_START": 1.0,
        "EPSILON_END": 0.01,
        "EPSILON_DECAY": 10000,
        "TARGET_UPDATE": 10,
        "REPLAY_MEMORY_SIZE": 10000,
        "REWARDS": {
            "NOTHING": -0.1,
            "MOVE": -0.1,
            "COLLIDE": -10.0
        }
    }
    
    # Set up mock methods
    config.get_game_config.return_value = game_config
    config.get_data_config.return_value = data_config
    config.get_ui_config.return_value = ui_config
    config.get_model_config.return_value = model_config
    config.get_training_config.return_value = training_config
    
    return config

@pytest.fixture
def mock_snake():
    """Fixture that provides a mock Snake instance."""
    snake = MagicMock()
    snake.get_head.return_value = (0, 0)
    snake.get_body.return_value = [(0, 0), (1, 0), (2, 0)]
    snake.get_direction.return_value = "RIGHT"
    snake.__len__.return_value = 3
    snake.alive = True
    snake.should_grow = False
    return snake

@pytest.fixture
def mock_food():
    """Fixture that provides a mock Food instance."""
    food = MagicMock()
    food.position = (5, 5)
    food.active = True
    food.remaining_steps = 10
    food.is_eaten.return_value = False
    return food

@pytest.fixture
def mock_ui():
    """Fixture that provides a mock UI instance."""
    ui = MagicMock()
    return ui

@pytest.fixture
def mock_env(mock_config):
    """Fixture that provides a mock SnakeEnv instance."""
    with patch('src.game.snake_env.Game'), \
         patch('src.game.snake_env.UI'):
        from src.game.snake_env import SnakeEnv
        env = SnakeEnv(mock_config)
        env.game = MagicMock()
        env.game.snake = mock_snake()
        env.game.current_food = mock_food()
        env.game.score = 0
        env.game.high_score = 100
        env.game.is_game_over = False
        return env

@pytest.fixture
def sample_state():
    """Fixture that provides a sample game state."""
    return np.random.rand(84, 84, 3).astype(np.uint8)

@pytest.fixture(autouse=True)
def mock_tkinter():
    """Mock Tkinter to avoid creating actual windows during tests."""
    with patch('tkinter.Tk'), \
         patch('tkinter.Canvas'), \
         patch('tkinter.Label'), \
         patch('tkinter.Frame'):
        yield
