from abc import ABC, abstractmethod
from typing import List, Tuple, Optional
import random
from src.config import config


class Food(ABC):
    def __init__(self, board_dim: int):
        self.board_dim: int = board_dim
        self.position: Optional[Tuple[int, int]] = None
    
    @abstractmethod
    def place_food(self, snake_body: List[Tuple[int, int]]):
        pass

    @abstractmethod
    def is_eaten(self, snake_head: Tuple[int, int]):
        pass

    @abstractmethod
    def update(self):
        pass


class SimpleFood(Food):
    def __init__(self, 
                 board_dim: int=config.get_game_config().BOARD_DIM):
        super().__init__(board_dim)
        self.remaining_steps = 0
        
    def place_food(self, snake_body: List[Tuple[int, int]]):
        while True:
            pos = (random.randint(-1*self.board_dim//2, self.board_dim//2), random.randint(-1*self.board_dim//2, self.board_dim//2))
            if pos not in snake_body:
                self.position = pos
                break

    def is_eaten(self, snake_head: Tuple[int, int]):
        return snake_head == self.position

    def update(self):
        pass


class SuperFood(Food):
    def __init__(self, 
                 board_dim: int=config.get_game_config().BOARD_DIM,
                 lifetime: int=config.get_training_config().FOOD.SUPERFOOD_LIFETIME):
        super().__init__(board_dim)
        self.lifetime = lifetime
        self.remaining_steps = 0
        self.active = False

    def place_food(self, snake_body: List[Tuple[int, int]]):
        while True:
            pos = (random.randint(-1*self.board_dim//2, self.board_dim//2), random.randint(-1*self.board_dim//2, self.board_dim//2))
            if pos not in snake_body:
                self.position = pos
                self.active = True
                self.remaining_steps = self.lifetime
                break
        self.active = False

    def is_eaten(self, snake_head: Tuple[int, int]):
        return self.active and snake_head == self.position

    def update(self):
        if self.active:
            self.remaining_steps -= 1
            if self.remaining_steps <= 0:
                self.active = False