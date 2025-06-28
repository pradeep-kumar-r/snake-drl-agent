"""
Unit tests for the SnakeEnv class.
"""
import unittest
from unittest.mock import MagicMock, patch
import numpy as np
import gym
from src.game.env import SnakeEnv
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
    
    def test_reset(self):
        """Test environment reset."""
        obs, info = self.env.reset()
        self.assertEqual(self.env.episodes_count, 1)
        self.assertIsInstance(obs, np.ndarray)
        self.assertIsInstance(info, dict)
        self.assertIn('score', info)
        self.assertEqual(info['score'], 0)
    
    def test_get_obs(self):
        """Test observation generation."""
        # Reset to initialize the game
        self.env.reset()
        
        # Call _get_obs
        obs = self.env._get_obs()
        
        # Verify the observation is a numpy array with correct shape
        self.assertIsInstance(obs, np.ndarray)
        self.assertEqual(obs.shape, (self.env.model_config["IMAGE_INPUT_SIZE"][0], 
                                    self.env.model_config["IMAGE_INPUT_SIZE"][1], 
                                    3))
    
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
    
    def test_render(self):
        """Test environment rendering."""
        # Create a mock for the sleep function
        with patch('src.game.env.sleep') as mock_sleep:
            # Force the condition to be true by setting episodes_count
            # to be divisible by EPISODES_PER_RENDER
            self.env.episodes_count = self.env.game_config["EPISODES_PER_RENDER"]
            
            # Call render
            self.env.render()
            
            # Verify sleep was called
            mock_sleep.assert_called_once_with(self.env.game_config["SLEEP_PER_TIMESTEP"])
    
    def test_cleanup_ui(self):
        """Test environment cleanup."""
        # Create a UI first
        self.env.reset()
        self.assertIsNotNone(self.env.ui)
        
        # Clean up
        self.env.cleanup_ui()
        self.assertIsNone(self.env.ui)
        
    def test_update_ui_components(self):
        """Test updating UI components."""
        # Create a UI first
        self.env.reset()
        
        # Mock the UI's update_components method
        self.env.ui.update_components = MagicMock()
        
        # Call the method
        self.env._update_ui_components()
        
        # Verify the UI's update_components was called
        self.env.ui.update_components.assert_called_once()

if __name__ == '__main__':
    unittest.main()
