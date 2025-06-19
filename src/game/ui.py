import tkinter as tk
from tkinter import font as tkFont
from typing import Dict, Any, Optional

from sympy import root
from src.game.food import Food, SuperFood
from src.game.snake import Snake


class UI:
    def __init__(self, 
                 master, 
                 snake: Snake,
                 food: Optional[Food],
                 score: int,
                 high_score: Optional[int],
                 ui_config: Dict[str, Any],
                 is_game_over: bool=False):
        self.master = master
        self.ui_config = ui_config
        self.board_width = self.board_height = self.ui_config.BOARD_DIM
        self.snake = snake
        self.food = food
        self.score = score
        self.high_score = high_score
        self.is_game_over = is_game_over

        self.master.title(self.ui_config.TITLE.TEXT)

        # Title Label
        self.title_label = tk.Label(self.master, 
                                    text=self.ui_config.TITLE.TEXT, 
                                    font=(self.ui_config.TITLE.FONT.NAME, 
                                          self.ui_config.TITLE.FONT.SIZE, 
                                          self.ui_config.TITLE.FONT.STYLE))
        self.title_label.pack(pady=self.ui_config.TITLE.PADDING)

        # Game Canvas
        self.canvas = tk.Canvas(self.master, 
                                width=self.board_width, 
                                height=self.board_height, 
                                bg=self.ui_config.CANVAS.BG, 
                                bd=self.ui_config.CANVAS.BD, 
                                highlightthickness=self.ui_config.CANVAS.HIGHLIGHTTHICKNESS)
        self.canvas.pack()

        # Score Labels
        self.score_frame = tk.Frame(self.master)
        self.score_frame.pack(pady=self.ui_config.SCORE.PADDING)

        self.current_score_label = tk.Label(self.score_frame, 
                                            text=f"Current Score: {self.score}", 
                                            font=(self.ui_config.SCORE.FONT.NAME, 
                                                  self.ui_config.SCORE.FONT.SIZE, 
                                                  self.ui_config.SCORE.FONT.STYLE))
        self.current_score_label.pack(side=self.ui_config.SCORE.SIDE, 
                                      padx=self.ui_config.SCORE.PADDING)

        self.high_score_label = tk.Label(self.score_frame, 
                                         text=f"Previous High Score: {self.high_score}", 
                                         font=(self.ui_config.SCORE.FONT.NAME, 
                                               self.ui_config.SCORE.FONT.SIZE, 
                                               self.ui_config.SCORE.FONT.STYLE))
        self.high_score_label.pack(side=self.ui_config.SCORE.SIDE, 
                                   padx=self.ui_config.SCORE.PADDING)

        # Legend
        self.legend_label = tk.Label(master, 
                                     text="Legend: \nSnake: ***> | Simple Food: O | Super Food: X", 
                                     font=(self.ui_config.LEGEND.FONT.NAME, 
                                           self.ui_config.LEGEND.FONT.SIZE,
                                           self.ui_config.LEGEND.FONT.STYLE))
        self.legend_label.pack(pady=self.ui_config.LEGEND.PADDING)

        # self.master.bind("<Left>", lambda event: self._handle_keypress(Direction.LEFT))
        # self.master.bind("<Right>", lambda event: self._handle_keypress(Direction.RIGHT))
        # self.master.bind("<Up>", lambda event: self._handle_keypress(Direction.UP))
        # self.master.bind("<Down>", lambda event: self._handle_keypress(Direction.DOWN))

        self._draw_board()
        self._draw_snake()
        if self.food:
            self._draw_food()
        if self.is_game_over:
            self._game_over_screen()

    def _draw_board(self):
        self.canvas.delete("all")
        for x in range(0, self.board_width):
            self.canvas.create_line(x,
                                    0,
                                    x,
                                    self.board_height,
                                    fill=self.ui_config.BOARD.FILL,
                                    dash=self.ui_config.BOARD.DASH)
        for y in range(0, self.board_height):
            self.canvas.create_line(0, 
                                    y,
                                    self.board_width, 
                                    y, 
                                    fill=self.ui_config.BOARD.FILL,
                                    dash=self.ui_config.BOARD.DASH)

    def _draw_snake(self):
        head = self.snake.get_head()
        head_x, head_y = head.x, head.y
        self.canvas.create_text(head_x + 1/2,
                                head_y + 1/2,
                                text=self.ui_config.SNAKE.HEAD.SYMBOL.get(self.snake.direction, ">"),
                                font=tkFont.Font(family=self.ui_config.SNAKE.HEAD.FONT.NAME, 
                                                 size=self.ui_config.SNAKE.HEAD.FONT.SIZE, 
                                                 weight=self.ui_config.SNAKE.HEAD.FONT.STYLE),
                                fill=self.ui_config.SNAKE.HEAD.FILL,
                                tags="snake")

        for segment in self.snake.get_body()[1:]:
            seg_x, seg_y = segment.x, segment.y
            self.canvas.create_text(seg_x + 1/2,
                                    seg_y + 1/2,
                                    text=self.ui_config.SNAKE.BODY.SYMBOL,
                                    font=tkFont.Font(family=self.ui_config.SNAKE.BODY.FONT.NAME, 
                                                     size=self.ui_config.SNAKE.BODY.FONT.SIZE),
                                    fill=self.ui_config.SNAKE.BODY.FILL,
                                    tags="snake")

    def _draw_food(self):
        symbol = self.ui_config.FOOD.SUPER.SYMBOL if isinstance(self.food, SuperFood) else self.ui_config.FOOD.SIMPLE.SYMBOL
        color = self.ui_config.FOOD.SUPER.FILL if isinstance(self.food, SuperFood) else self.ui_config.FOOD.SIMPLE.FILL
        font_family = self.ui_config.FOOD.SUPER.FONT.NAME if isinstance(self.food, SuperFood) else self.ui_config.FOOD.SIMPLE.FONT.NAME
        font_size = self.ui_config.FOOD.SUPER.FONT.SIZE if isinstance(self.food, SuperFood) else self.ui_config.FOOD.SIMPLE.FONT.SIZE
        food_x, food_y = self.food.position[0], self.food.position[1]
        self.canvas.create_text(food_x + 1/2,
                                food_y + 1/2,
                                text=symbol,
                                font=tkFont.Font(family=font_family, size=font_size),
                                fill=color,
                                tags="food")

    def _game_over_screen(self):
        self.canvas.create_text(self.board_width/2, 
                                self.board_height/2 - 30,
                                text=self.ui_config.GAME_OVER.TEXT, 
                                font=(self.ui_config.GAME_OVER.FONT.NAME, 
                                      self.ui_config.GAME_OVER.FONT.SIZE, 
                                      self.ui_config.GAME_OVER.FONT.STYLE), 
                                fill=self.ui_config.GAME_OVER.FILL)
        self.canvas.create_text(self.board_width/2, 
                                self.board_height/2 + 10,
                                text=f"Final Score: {self.score}",
                                font=(self.ui_config.GAME_OVER.FONT.NAME, 
                                      self.ui_config.GAME_OVER.FONT.SIZE, 
                                      self.ui_config.GAME_OVER.FONT.STYLE), 
                                fill=self.ui_config.GAME_OVER.FILL)
        
if __name__ == "__main__":
    master = tk.Tk.master(root)
    tk.mainloop()