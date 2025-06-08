from abc import ABC, abstractmethod
import random

class Food(ABC):
    """
    Abstract base class for food items in the snake game.
    """
    def __init__(self, board_width, board_height):
        self.board_width = board_width
        self.board_height = board_height
        self.position = None
    
    @abstractmethod
    def place(self, snake_body):
        """Place food at a valid location not occupied by the snake."""
        pass

    @abstractmethod
    def is_eaten(self, snake_head):
        """Check if the food is eaten by the snake."""
        pass

    @abstractmethod
    def update(self):
        """Update food state (for timed/big food)."""
        pass

    @abstractmethod
    def get_positions(self):
        """Return list of occupied positions (for big food)."""
        pass


class SimpleFood(Food):
    def __init__(self, board_width, board_height):
        super().__init__(board_width, board_height)
        self.place([])

    def place(self, snake_body):
        while True:
            pos = (random.randint(0, self.board_width - 1), random.randint(0, self.board_height - 1))
            if pos not in snake_body:
                self.position = pos
                break

    def is_eaten(self, snake_head):
        return snake_head == self.position

    def update(self):
        pass

    def get_positions(self):
        return [self.position]


class SuperFood(Food):
    def __init__(self, board_width, board_height, size=1, lifetime=20):
        super().__init__(board_width, board_height)
        self.size = size
        self.lifetime = lifetime
        self.remaining_steps = 0
        self.active = False
        self.positions = []

    def place(self, snake_body):
        tries = 0
        while tries < 100:
            x = random.randint(0, self.board_width - self.size)
            y = random.randint(0, self.board_height - self.size)
            positions = [(x + dx, y + dy) for dx in range(self.size) for dy in range(self.size)]
            if all(pos not in snake_body for pos in positions):
                self.positions = positions
                self.position = (x, y)
                self.remaining_steps = self.lifetime
                self.active = True
                return
            tries += 1
        self.active = False
        self.positions = []

    def is_eaten(self, snake_head):
        return self.active and snake_head in self.positions

    def update(self):
        if self.active:
            self.remaining_steps -= 1
            if self.remaining_steps <= 0:
                self.active = False
                self.positions = []

    def get_positions(self):
        return self.positions if self.active else []