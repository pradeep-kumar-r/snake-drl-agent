from typing import Tuple
from .direction import Direction
from src.config import config


class Snake:
    def __init__(self, 
                 game_config = config.get_game_config):
        self.game_config = game_config
        self.board_dim: int = self.game_config.BOARD_DIM
        self.init_pos: Tuple[int, int] = self.game_config.SNAKE.SNAKE_INIT_POS
        self.init_length: int = self.game_config.SNAKE.SNAKE_INIT_LENGTH
        self.init_direction: Direction = self.game_config.SNAKE.SNAKE_INIT_DIRECTION
        x, y = self.init_pos
        self.body = [(x - i, y) for i in range(self.init_length)]
        self.direction = self.init_direction
        self.grow_pending = 0
        self.alive = True

    def set_direction(self, new_direction: Direction):
        if not Direction.is_opposite(self.direction, new_direction):
            self.direction = new_direction

    def move(self):
        left_wall_x = - 1 * self.board_dim//2
        right_wall_x = self.board_dim//2
        top_wall_y = self.board_dim//2
        bottom_wall_y = - 1 * self.board_dim//2
        if not self.alive:
            return
        head_x, head_y = self.body[0]
        dx, dy = self.direction.value
        new_head = (head_x + dx, head_y + dy)
        if new_head[0] < left_wall_x:
            new_head = (right_wall_x, new_head[1])
        elif new_head[0] > right_wall_x:
            new_head = (left_wall_x, new_head[1])
        elif new_head[1] < bottom_wall_y:
            new_head = (new_head[0], top_wall_y)
        elif new_head[1] > top_wall_y:
            new_head = (new_head[0], bottom_wall_y)
        self.body.insert(0, new_head)
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.body.pop()

    def grow(self, amount: int=1):
        self.grow_pending += amount

    def check_collision(self):
        head = self.body[0]
        return head in self.body[1:]

    def get_head(self):
        return self.body[0]

    def get_body(self):
        return self.body

    def get_direction(self):
        return self.direction

    def kill(self):
        self.alive = False
        