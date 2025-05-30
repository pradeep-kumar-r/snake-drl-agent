import random
import numpy as np
from enum import Enum
import gym
from gym import spaces
from typing import Any, Tuple, List
from turtle import Screen, Turtle


class Direction(Enum):
    UP = (-1, 0)
    RIGHT = (0, 1)
    DOWN = (1, 0)
    LEFT = (0, -1)

class SnakeGame:
    
    def __init__(self, grid_size: int = 20) -> None:
        self.grid_size: int = max(10, grid_size)
        self.snake: List[Tuple[int]] = []
        self.direction: Tuple[int] = None
        self.reset()
        
    def reset(self) -> None:
        start_xcor = self.grid_size // 2
        start_ycor = self.grid_size // 2 - 3
        self.snake = [(start_xcor, start_ycor), 
                      (start_xcor, start_ycor + 1), 
                      (start_xcor, start_ycor + 2)]
        self.direction = 