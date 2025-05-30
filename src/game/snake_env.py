import gym
from gym import spaces
import numpy as np
from ..snake import SnakeGame

class SnakeEnvironment(gym.Env):
    def __init__(self):
        super(SnakeEnvironment, self).__init__()
        self.game = SnakeGame()
        self.action_space = spaces.Discrete(4)  # Up, Right, Down, Left
        self.observation_space = spaces.Box(low=0, high=1, shape=(self.game.grid_size, self.game.grid_size), dtype=np.float32)

    def reset(self):
        self.game.reset()
        return self._get_state()

    def step(self, action):
        reward, done = self.game.step(action)
        return self._get_state(), reward, done, {}

    def _get_state(self):
        # Create grid representation of the game
        grid = np.zeros((self.game.grid_size, self.game.grid_size), dtype=np.float32)
        for x, y in self.game.snake:
            grid[x, y] = 1  # Snake body
        food_x, food_y = self.game.food
        grid[food_x, food_y] = 2  # Food
        return grid

    def render(self, mode='human'):
        self.game.render()
