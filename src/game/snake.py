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
        self.growth_pending: bool = False
        self.alive: bool = True
        self._set_body()
    
    def _set_body(self) -> None:
        opposite_dir = Direction.get_opposite(self.init_direction)
        dx, dy = opposite_dir.value
        self.body: List[Tuple[int, int]] = [(self.init_pos[0] + dx * i, 
                                             self.init_pos[1] + dy * i) for i in range(self.init_length)]
        
    def set_direction(self, new_direction: Direction) -> None:
        if not Direction.is_opposite(self.direction, new_direction):
            self.direction = new_direction

    def move(self) -> None:
        if not self.alive:
            return
        head = self.body[0]
        new_head = add_tuples(head, self.direction.value)
        # Handle wrapping around the edges with pygame coordinates (0,0 at top-left)
        if new_head[0] < 0:
            new_head = (self.board_dim - 1, new_head[1])
        elif new_head[0] >= self.board_dim:
            new_head = (0, new_head[1])
        elif new_head[1] < 0:
            new_head = (new_head[0], self.board_dim - 1)
        elif new_head[1] >= self.board_dim:
            new_head = (new_head[0], 0)
        self.body.insert(0, new_head)
        if self.growth_pending:
            self.growth_pending = False
        else:
            self.body.pop()

    def check_collision(self) -> bool:
        head = self.body[0]
        return head in self.body[1:]

    def __len__(self):
        return len(self.body)
    
    def get_head(self) -> Tuple[int, int]:
        return self.body[0]

    def get_body(self) -> List[Tuple[int, int]]:
        return self.body

    def get_direction(self) -> Direction:
        return self.direction

    def kill(self) -> None:
        self.alive = False
        
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Snake):
            return False
        return all([self.body == other.body, 
                    self.direction == other.direction])
        