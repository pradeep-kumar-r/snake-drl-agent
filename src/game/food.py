from abc import ABC, abstractmethod
from typing import List, Tuple, Optional
import random


class Food(ABC):
    def __init__(self, board_dim: int) -> None:
        self.board_dim: int = board_dim
        self.position: Optional[Tuple[int, int]] = None
        self.active: bool = False
    
    @abstractmethod
    def place_food(self, snake_body: List[Tuple[int, int]]) -> None:
        pass

    @abstractmethod
    def is_eaten(self, snake_head: Tuple[int, int]) -> bool:
        pass

    @abstractmethod
    def update(self) -> None:
        pass


class SimpleFood(Food):
    def __init__(self, board_dim: int):
        super().__init__(board_dim)
        self.remaining_steps = 0
        
    def place_food(self, snake_body: List[Tuple[int, int]]) -> None:
        while True:
            pos = (random.randint(0, self.board_dim-1), random.randint(0, self.board_dim-1))
            if pos not in snake_body:
                self.position = pos
                self.active = True
                break

    def is_eaten(self, snake_head: Tuple[int, int]) -> bool:
        return self.active and snake_head == self.position

    def update(self) -> None:
        pass
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SimpleFood):
            return False
        return self.position == other.position


class SuperFood(Food):
    def __init__(self, board_dim: int, lifetime: int):
        super().__init__(board_dim)
        self.lifetime = lifetime
        self.remaining_steps = 0
        self.active = False

    def place_food(self, snake_body: List[Tuple[int, int]]) -> None:
        while True:
            pos = (random.randint(0, self.board_dim-1), random.randint(0, self.board_dim-1))
            if pos not in snake_body:
                self.position = pos
                self.active = True
                self.remaining_steps = self.lifetime
                break

    def is_eaten(self, snake_head: Tuple[int, int]) -> bool:
        return self.active and snake_head == self.position

    def update(self) -> None:
        if self.active:
            self.remaining_steps -= 1
            if self.remaining_steps < 0:
                self.active = False
                
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SuperFood):
            return False
        return self.position == other.position