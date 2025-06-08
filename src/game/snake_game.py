import tkinter as tk
import random

class SnakeGame:
    """Snake game implementation using a grid-based system.

    This class implements a classic snake game where the player controls a snake
    that moves around a grid, eating food and growing longer. The game ends if
    the snake collides with itself or the grid boundaries.

    Attributes:
        grid_size (int): The size of the square grid (default: 20)
        cell_size (int): The size of each cell in pixels (default: 20)
        snake (list): List of (x, y) tuples representing snake body segments
        direction (tuple): Current direction of snake movement as (dx, dy)
        food (tuple): (x, y) coordinates of the current food position
        game_over (bool): Flag indicating if the game has ended

    Methods:
        reset(): Resets the game to initial state
        generate_food(): Creates new food at random position
        step(action): Updates game state based on given action
        render(): Placeholder for game visualization

    Actions:
        0: Move Up    (-1, 0)
        1: Move Right (0, 1)
        2: Move Down  (1, 0)
        3: Move Left  (0, -1)

    Rewards:
        +10: Food eaten
        -10: Collision detected
        0: Normal movement
    """
    def __init__(self, grid_size=20, cell_size=20):
        self.grid_size: int = grid_size
        self.cell_size: int = cell_size
        self.direction: any = None
        self.reset()

    def reset(self):
        self.snake = [(5, 5), (5, 4), (5, 3)]
        self.direction = (0, 1)  # Initial direction: right
        self.food = self.generate_food()
        self.game_over = False

    def generate_food(self):
        while True:
            food = (random.randint(0, self.grid_size - 1), random.randint(0, self.grid_size - 1))
            if food not in self.snake:
                return food

    def step(self, action):
        # Actions: 0 = Up, 1 = Right, 2 = Down, 3 = Left
        directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        self.direction = directions[action]
        head = (self.snake[0][0] + self.direction[0], self.snake[0][1] + self.direction[1])

        # Check for collisions
        if (head in self.snake) or head[0] < 0 or head[1] < 0 or head[0] >= self.grid_size or head[1] >= self.grid_size:
            self.game_over = True
            return -10, self.game_over

        self.snake.insert(0, head)

        # Check if food eaten
        if head == self.food:
            self.food = self.generate_food()
            return 10, self.game_over
        else:
            self.snake.pop()  # Move forward
            return 0, self.game_over

    def render(self):
        # Visualization placeholder (Tkinter or GUI rendering logic)
        pass
