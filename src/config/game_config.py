from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class GameConfig:
    game_width: int
    game_height: int
    snake_init_pos: tuple
    snake_init_length: int
    snake_init_direction: Literal["UP", "DOWN", "LEFT", "RIGHT"]