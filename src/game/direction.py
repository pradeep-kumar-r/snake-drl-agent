from enum import Enum


class Direction(Enum):
    UP = (0, -1)  # Move up (decrease y)
    DOWN = (0, 1)  # Move down (increase y)
    LEFT = (-1, 0)  # Move left (decrease x)
    RIGHT = (1, 0)  # Move right (increase x)

    @staticmethod
    def is_opposite(dir1, dir2):
        return (dir1.value[0] == -dir2.value[0] and dir1.value[1] == -dir2.value[1])
    
    @staticmethod
    def get_opposite(dir1):
        return Direction((dir1.value[0] * -1, dir1.value[1] * -1))
    