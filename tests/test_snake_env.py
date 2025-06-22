"""
Unit tests for the SnakeEnv class.
"""
import unittest
from unittest.mock import MagicMock, patch, ANY
import numpy as np
import gym
from src.game.snake_env import SnakeEnv
from src.config import ConfigManager

class TestSnakeEnv(unittest.TestCase):
    """Test cases for the SnakeEnv class."""
    
    @classmethod
    def setUpClass(cls):
        """Set up class fixtures before any tests are run."""
        cls.config = ConfigManager()
    
    def setUp(self):
        """Set up test fixtures."""
        self.env = SnakeEnv(app_config=self.config)
    
    def test_initialization(self):
        """Test environment initialization."""
        self.assertIsInstance(self.env, gym.Env)
        self.assertEqual(self.env.episodes_count, 0)
        self.assertIsNone(self.env.ui)
        self.assertIsNone(self.env.root)
        self.assertIsNone(self.env.off_screen_root)
        self.assertIsNone(self.env.off_screen_ui)
    
    def test_reset(self):
        """Test environment reset."""
        obs, info = self.env.reset()
        self.assertEqual(self.env.episodes_count, 1)
        self.assertIsInstance(obs, np.ndarray)
        self.assertIsInstance(info, dict)
        self.assertIn('score', info)
        self.assertEqual(info['score'], 0)
    
    @patch('src.game.snake_env.Image.open')
    @patch('src.game.snake_env.io.BytesIO')
    @patch('src.game.ui.UI')
    @patch('tkinter.Tk')
    def test_get_obs(self, mock_tk, mock_ui, mock_bytes_io, mock_image_open):
        """Test observation generation."""
        # Mock the image conversion process
        mock_img = MagicMock()
        mock_img.convert.return_value = MagicMock()
        mock_img.resize.return_value = mock_img
        mock_image_open.return_value = mock_img
        
        # Call _get_obs
        obs = self.env._get_obs()
        
        # Verify the observation is a numpy array with correct shape
        self.assertIsInstance(obs, np.ndarray)
        self.assertEqual(obs.shape, (self.env.image_size, self.env.image_size, 3))
        
        # Verify the UI and Tkinter objects were created and cleaned up
        mock_tk.assert_called_once()
        mock_ui.assert_called_once_with(
            master=ANY,
            ui_config=self.config.get_ui_config(),
            snake=self.env.game.snake,
            food=self.env.game.current_food
        )
    
    def test_step(self):
        """Test taking a step in the environment."""
        # Reset the environment first
        self.env.reset()
        
        # Take a step (action 1 = RIGHT)
        obs, reward, done, truncated, info = self.env.step(1)
        
        # Verify the return values
        self.assertIsInstance(obs, np.ndarray)
        self.assertIsInstance(reward, float)
        self.assertIsInstance(done, bool)
        self.assertIsInstance(truncated, bool)
        self.assertIsInstance(info, dict)
        
        # The snake should have moved right
        self.assertEqual(self.env.game.snake.get_direction().name, 'RIGHT')
    
    @patch('time.sleep')
    @patch('src.game.snake_env.SnakeEnv._display_ui')
    def test_render(self, mock_display_ui, mock_sleep):
        """Test environment rendering."""
        # Set episodes_count to a multiple of EPISODES_PER_RENDER
        self.env.episodes_count = self.env.game_config["EPISODES_PER_RENDER"]
        
        # Call render
        self.env.render()
        
        # Verify _display_ui was called
        mock_display_ui.assert_called_once()
        mock_sleep.assert_called_once_with(self.env.game_config["SLEEP_PER_TIMESTEP"])
    
    @patch('src.game.snake_env.SnakeEnv._cleanup_ui')
    def test_close(self, mock_cleanup_ui):
        """Test environment cleanup."""
        self.env.close()
        mock_cleanup_ui.assert_called_once()

if __name__ == '__main__':
    unittest.main()
