import gym
from gym import spaces
import numpy as np
import tkinter as tk
import io
from PIL import Image
from src.game.game import Game
from src.game.ui import UI
from src.config import ConfigManager


class SnakeEnv(gym.Env):
    """
    A Gym environment for the Snake game.
    """
    metadata = {'render_modes': ['human'], 
                'render_fps': 10}

    def __init__(self, 
                 app_config: ConfigManager,
                 headless: bool = True):
        super().__init__()
        self.game_config = app_config.get_game_config()
        self.data_config = app_config.get_data_config()
        self.ui_config = app_config.get_ui_config()
        self.model_config = app_config.get_model_config()

        self.game = Game(game_config=self.game_config,
                           data_config=self.data_config,
                           ui_config=self.ui_config,
                           headless=headless)
        
        # Action space: 0:STILL, 1:RIGHT, 2:DOWN, 3:LEFT, 4:UP
        self.action_space = spaces.Discrete(self.model_config.NUM_ACTIONS)
        
        # Calculate the expected dimensions of the game window
        self.window_height = self.game_config.BOARD_DIM + 150  # Adding extra space for UI elements
        self.window_width = self.game_config.BOARD_DIM
        
        # Define the target dimensions for the observation space
        self.target_height = self.model_config.INPUT_HEIGHT
        self.target_width = self.model_config.INPUT_WIDTH
        
        # Observation space: RGB screenshot of the game
        self.observation_space = spaces.Box(
            low=0, 
            high=255, 
            shape=(self.target_height, self.target_width, 3),  # Height, Width, RGB channels
            dtype=np.uint8
        )
        
        self.episodes_count: int = 0

    def _get_obs(self):
        """Render the game state to an off-screen canvas and convert to an RGB array."""
        # Create an off-screen canvas with the same dimensions as the game board
        off_screen_root = tk.Tk()
        off_screen_root.withdraw()  # Hide the window
        
        # Calculate canvas size based on board dimensions and UI elements
        canvas_width = self.game_config.BOARD_DIM
        canvas_height = self.game_config.BOARD_DIM
        
        # Create a canvas to draw on
        canvas = tk.Canvas(off_screen_root, 
                           width=canvas_width, 
                           height=canvas_height, 
                           bg='black')
        
        # Create a UI instance for rendering
        off_screen_ui = UI(
            master=off_screen_root,
            snake=self.game.snake,
            food=self.game.current_food,
            score=self.game.score,
            high_score=getattr(self.game, 'high_score', 0),
            ui_config=self.ui_config,
            is_game_over=self.game.is_game_over
        )
        
        # Draw the game state to the canvas
        off_screen_ui.draw_board()
        off_screen_ui.draw_snake()
        if self.game.is_food_active and self.game.current_food:
            off_screen_ui.draw_food()
        if self.game.is_game_over:
            off_screen_ui.game_over_screen()
        
        # Update the canvas
        canvas.update()
        
        # Convert the canvas to a PhotoImage
        canvas.update_idletasks()
        
        # Create a PIL Image from the canvas
        # First, we need to postscript the canvas to a file
        ps_data = canvas.postscript(colormode='color')
        img = Image.open(io.BytesIO(ps_data.encode('utf-8')))
        
        # Resize to target dimensions
        img = img.resize((self.target_width, self.target_height), Image.Resampling.LANCZOS)
        
        # Convert to RGB mode if not already
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Convert to numpy array
        observation = np.array(img)
        
        # Clean up
        off_screen_root.destroy()
        
        return observation

    def _get_info(self):
        return {
            "score": self.game.score,
            "steps_elapsed": self.game.steps_elapsed,
            "food_count": self.game.food_count,
        }

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.game.reset()
        observation = self._get_obs()
        info = self._get_info()
        return observation, info

    def step(self, action):
        prev_score = self.game.score
        
        (steps_elapsed, 
         is_game_over, 
         score,
         snake_body,
         snake_direction,
         is_food_active,
         food_position,
         food_remaining_steps) = self.game.step(action)

        terminated = is_game_over
        
        # Define reward structure
        if terminated:
            reward = -10  # Penalty for losing
        elif self.game.score > prev_score:
            reward = 10   # Reward for eating food
        else:
            reward = -0.1 # Small penalty for each step to encourage efficiency

        observation = self._get_obs()
        info = self._get_info()
        
        # The environment is not truncated
        truncated = False

        return observation, reward, terminated, truncated, info

    def render(self, mode='human'):
        if mode == 'human':
            self.game.display_ui()

    def close(self):
        self.game.cleanup()
