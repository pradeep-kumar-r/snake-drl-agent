from time import sleep
from typing import Optional, Dict, Any
import tkinter as tk
import io
import gym
from gym import spaces
import numpy as np
from PIL import Image
from src.game.game import Game
from src.game.ui import UI
from src.config import ConfigManager


class SnakeEnv(gym.Env):
    """
    A Gym environment for the Snake game.
    """
    def __init__(self, app_config: ConfigManager):
        super().__init__()
        self.game_config = app_config.get_game_config()
        self.data_config = app_config.get_data_config()
        self.ui_config = app_config.get_ui_config()
        self.model_config = app_config.get_model_config()
        self.training_config = app_config.get_training_config()

        self.game = Game(game_config=self.game_config,
                         data_config=self.data_config)
        
        self.episodes_count: int = 0
        
        self.headless: bool = not self.episodes_count % self.game_config["EPISODES_PER_RENDER"] == 0
        self.ui: Optional[UI] = None
        self.root: Optional[tk.Tk] = None
        self.off_screen_root: Optional[tk.Tk] = None
        self.off_screen_ui: Optional[UI] = None
        
        # Action space: 0:STILL, 1:RIGHT, 2:DOWN, 3:LEFT, 4:UP
        self.action_space = spaces.Discrete(self.model_config["NUM_ACTIONS"])
        
        self.image_size: int = self.model_config["IMAGE_INPUT_SIZE"]
        
        # Observation space: RGB screenshot of the game
        self.observation_space = spaces.Box(
            low=0, 
            high=255, 
            shape=(self.image_size, self.image_size, 3),
            dtype=np.uint8
        )

    def _get_obs(self):
        self.off_screen_root = tk.Tk()
        self.off_screen_ui = UI(
                master=self.off_screen_root,
                ui_config=self.ui_config,
                snake=self.game.snake,
                food=self.game.current_food
            )
        self.off_screen_ui.off_screen_render()
        canvas = self.off_screen_ui.canvas
        # canvas.update_idletasks()
        ps_data = canvas.postscript(colormode='color')
        img = Image.open(io.BytesIO(ps_data.encode('utf-8')))
        img = img.resize((self.image_size, self.image_size), Image.Resampling.LANCZOS)
        self.off_screen_root.destroy()
        self.off_screen_root = None
        self.off_screen_ui = None
        return np.array(img.convert('RGB'))

    def _get_info(self):
        return self.game.get_state()

    def reset(self, 
              seed: Optional[int] = None, 
              options: Optional[Dict[str, Any]] = None):
        super().reset(seed=seed)
        self.episodes_count += 1
        self.game.reset()
        # self.game = Game(game_config=self.game_config,
        #                  data_config=self.data_config)
        observation = self._get_obs()
        info = self._get_info()
        return observation, info

    def step(self, action):
        prev_score = self.game.score
        
        _, terminated, _, _, _, _, _, _ = self.game.step(action)

        # Update rewards accumulated
        reward = 0
        if action == 0:
            reward += self.training_config["REWARDS"]["NOTHING"]
            
        if terminated:
            reward += self.training_config["REWARDS"]["COLLIDE"]
        else:
            reward += self.training_config["REWARDS"]["MOVE"]
            
        if self.game.score > prev_score:
            reward += self.game.score - prev_score
        
        observation = self._get_obs()
        info = self._get_info()
        truncated = False
        return observation, reward, terminated, truncated, info

    def render(self):
        if self.episodes_count % self.game_config["EPISODES_PER_RENDER"] == 0:
            sleep(self.game_config["SLEEP_PER_TIMESTEP"])
            self._display_ui()

    def close(self):
        self._cleanup_ui()
        
    def _display_ui(self):
        if not self.root:
            self.root = tk.Tk()
            self.root.deiconify()
            self.ui = UI(
                master=self.root,
                ui_config=self.ui_config,
                snake=self.game.snake,
                food=self.game.current_food,
                score=getattr(self.game, 'score', 0),
                high_score=getattr(self.game, 'high_score', 0)
            ) 
        self.ui.full_render()
    
    def _cleanup_ui(self):
        if self.root:
            self.root.destroy()
            self.root = None
        self.ui = None
        
