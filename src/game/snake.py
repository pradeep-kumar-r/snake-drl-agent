from typing import Tuple
from .direction import Direction
from src.config import config


class Snake:
    def __init__(self, 
                 init_pos: Tuple[int, int] = config.get_game_config().snake_init_pos,
                 init_length: int = config.get_game_config().snake_init_length,
                 init_direction: Direction = config.get_game_config().snake_init_direction):
        self.init_pos: Tuple[int, int] = init_pos
        self.init_length: int = init_length
        self.init_direction: Direction = init_direction
        self.reset()

    def reset(self):
        x, y = self.init_pos
        self.body = [(x - i, y) for i in range(self.init_length)]
        self.direction = self.init_direction
        self.grow_pending = 0
        self.alive = True

    def set_direction(self, new_direction: Direction):
        if not Direction.is_opposite(self.direction, new_direction):
            self.direction = new_direction

    def move(self, 
             board_width: int=config.get_game_config().board_width,
             board_height: int=config.get_game_config().board_height):
        left_wall_x = - 1 * board_width//2
        right_wall_x = board_width//2
        top_wall_y = board_height//2
        bottom_wall_y = - 1 * board_height//2
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
        