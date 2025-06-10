from enum import Enum


class Direction(Enum):
    UP = (0, 1)
    DOWN = (0, -1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

    @staticmethod
    def is_opposite(dir1, dir2):
        return (dir1.value[0] == -dir2.value[0] and dir1.value[1] == -dir2.value[1])