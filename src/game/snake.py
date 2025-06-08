from .direction import Direction


class Snake:
    def __init__(self, init_pos=(5, 5), init_length=3, init_direction=Direction.RIGHT):
        self.init_pos = init_pos
        self.init_length = init_length
        self.init_direction = init_direction
        self.reset()

    def reset(self):
        x, y = self.init_pos
        self.body = [(x - i, y) for i in range(self.init_length)]
        self.direction = self.init_direction
        self.grow_pending = 0
        self.alive = True

    def set_direction(self, new_direction):
        # Prevent direct reversal
        if not Direction.opposite(self.direction, new_direction):
            self.direction = new_direction

    def move(self):
        if not self.alive:
            return
        head_x, head_y = self.body[0]
        dx, dy = self.direction.value
        new_head = (head_x + dx, head_y + dy)
        self.body.insert(0, new_head)
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.body.pop()

    def grow(self, amount=1):
        self.grow_pending += amount

    def check_self_collision(self):
        head = self.body[0]
        return head in self.body[1:]

    def check_wall_collision(self, width, height):
        head_x, head_y = self.body[0]
        return not (0 <= head_x < width and 0 <= head_y < height)

    def get_head(self):
        return self.body[0]

    def get_body(self):
        return self.body

    def get_direction(self):
        return self.direction

    def kill(self):
        self.alive = False
        