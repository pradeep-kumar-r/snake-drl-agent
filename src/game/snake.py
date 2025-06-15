from typing import Tuple, List
from src.game.direction import Direction
from src.utils.utils import add_tuples


class Snake:
    def __init__(self, 
                 board_dim: int,
                 init_pos: Tuple[int, int],
                 init_length: int,
                 init_direction: Direction):
        self.board_dim = board_dim
        self.init_pos = init_pos
        self.init_length = init_length
        self.direction = self.init_direction = init_direction
        self.should_grow: bool = False
        self.alive: bool = True
        x, y = self.init_pos
        self.body: List[Tuple[int, int]] = [(x - i, y) for i in range(self.init_length)]
        
    def set_direction(self, new_direction: Direction) -> None:
        # Check for 180 degree turns and modify direction
        if not Direction.is_opposite(self.direction, new_direction):
            self.direction = new_direction

    def move(self) -> None:
        boundary = self.board_dim//2
        left_bound_x = bottom_bound_y = -1*boundary
        right_bound_x = top_bound_y = boundary
        if not self.alive:
            return
        head = self.body[0]
        new_head = add_tuples(head, self.direction.value)
        if new_head[0] < left_bound_x:
            new_head = (right_bound_x, new_head[1])
        elif new_head[0] > right_bound_x:
            new_head = (left_bound_x, new_head[1])
        elif new_head[1] < bottom_bound_y:
            new_head = (new_head[0], top_bound_y)
        elif new_head[1] > top_bound_y:
            new_head = (new_head[0], bottom_bound_y)
        self.body.insert(0, new_head)
        if self.should_grow:
            self.should_grow = False
        else:
            self.body.pop()

    def check_collision(self) -> bool:
        head = self.body[0]
        return head in self.body[1:]

    def get_head(self) -> Tuple[int, int]:
        return self.body[0]

    def get_body(self) -> List[Tuple[int, int]]:
        return self.body

    def get_direction(self) -> Direction:
        return self.direction

    def kill(self) -> None:
        self.alive = False
        