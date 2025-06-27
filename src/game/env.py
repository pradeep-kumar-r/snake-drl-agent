from time import sleep
from typing import Optional, Dict, Any, Tuple
import gym
from gym import spaces
import numpy as np
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
        
        # Action space: 0:STILL, 1:RIGHT, 2:DOWN, 3:LEFT, 4:UP
        self.action_space = spaces.Discrete(self.model_config["NUM_ACTIONS"])
        
        self.image_dim: Tuple[int, int] = self.model_config["IMAGE_INPUT_SIZE"]
        
        # Observation space: RGB screenshot of the game
        self.observation_space = spaces.Box(
            low=0,
            high=255,
            shape=(self.model_config["IMAGE_INPUT_SIZE"][0],
                   self.model_config["IMAGE_INPUT_SIZE"][1],
                   3),
            dtype=np.uint8
        )

    def _update_ui_components(self) -> None:
        if self.ui:
            self.ui.update_components(
                new_snake=self.game.snake,
                new_food=self.game.current_food,
                new_score=self.game.score)
    
    def _get_obs(self) -> np.ndarray:
        # Headless rendering
        if self.ui is None:
            self.ui = UI(
                ui_config=self.ui_config,
                snake=self.game.snake,
                episode=self.episodes_count,
                food=self.game.current_food,
                score=self.game.score,
                high_score=self.game.high_score
            )
        else:
            self._update_ui_components()
        
        rgb_array, _ = self.ui.headless_render()
        return rgb_array

    def _get_info(self) -> Dict[str, Any]:
        return self.game.get_state()

    def reset(self, 
              seed: Optional[int] = None, 
              options: Optional[Dict[str, Any]] = None) -> Tuple[np.ndarray, Dict[str, Any]]:
        super().reset(seed=seed)
        self.episodes_count += 1
        self.game.reset()
        # self.game = Game(game_config=self.game_config,
        #                  data_config=self.data_config)
        observation = self._get_obs()
        self.cleanup_ui()
        self.ui = UI(
                ui_config=self.ui_config,
                snake=self.game.snake,
                episode=self.episodes_count,
                food=self.game.current_food,
                score=self.game.score,
                high_score=self.game.high_score
            )
        info = self._get_info()
        return observation, info

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, bool, Dict[str, Any]]:
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

    def render(self) -> None:
        if self.ui is None:
                self.ui = UI(
                    ui_config=self.ui_config,
                    snake=self.game.snake,
                    episode=self.episodes_count,
                    food=self.game.current_food,
                    score=self.game.score,
                    high_score=self.game.high_score
                )
        else:
            self._update_ui_components()
                
        if self.episodes_count % self.game_config["EPISODES_PER_RENDER"] == 0:
            sleep(self.game_config["SLEEP_PER_TIMESTEP"])
            self.ui.full_render()

    def cleanup_ui(self) -> None:
        if self.ui:
            self.ui.close()
            self.ui = None
        
