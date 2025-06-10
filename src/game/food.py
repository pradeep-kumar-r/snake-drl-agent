from abc import ABC, abstractmethod
from typing import List, Tuple, Optional
import random
from src.config import config


class Food(ABC):
    def __init__(self, board_width: int, board_height: int):
        self.board_width: int = board_width
        self.board_height: int = board_height
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
                 board_width: int=config.get_game_config().BOARD_WIDTH,
                 board_height: int=config.get_game_config().BOARD_HEIGHT):
        super().__init__(board_width, board_height)
        
    def place_food(self, snake_body: List[Tuple[int, int]]):
        while True:
            pos = (random.randint(0, self.board_width-1), random.randint(0, self.board_height-1))
            if pos not in snake_body:
                self.position = pos
                break

    def is_eaten(self, snake_head: Tuple[int, int]):
        return snake_head == self.position

    def update(self):
        pass


class SuperFood(Food):
    def __init__(self, 
                 board_width: int=config.get_game_config().BOARD_WIDTH,
                 board_height: int=config.get_game_config().BOARD_HEIGHT,
                 lifetime: int=config.get_training_config().FOOD.SUPERFOOD_LIFETIME):
        super().__init__(board_width, board_height)
        self.lifetime = lifetime
        self.remaining_steps = 0
        self.active = False

    def place_food(self, snake_body: List[Tuple[int, int]]):
        while True:
            pos = (random.randint(0, self.board_width-1), random.randint(0, self.board_height-1))
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