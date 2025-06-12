import tkinter as tk
from tkinter import font as tkFont
import os
from src.game.game import Game
from src.game.direction import Direction
from src.game.food import SuperFood
from src.config import config


class GameUI:
    def __init__(self, master, configuration=config):
        self.master = master
        self.config = configuration
        self.game_config = self.config.get_game_config()
        self.board_width = self.board_height = self.game_config.BOARD_DIM

        self.master.title("Snake Game")

        # Title Label
        self.title_label = tk.Label(master, text="Snake Game", font=("Arial", 16, "bold"))
        self.title_label.pack(pady=10)

        # Game Canvas
        self.canvas = tk.Canvas(master, width=self.board_width, height=self.board_height, bg="white", bd=0, highlightthickness=0)
        self.canvas.pack()

        self.game = Game(self.config)
        self.high_score = self._load_high_score()

        # Score Labels
        self.score_frame = tk.Frame(master)
        self.score_frame.pack(pady=10)

        self.current_score_label = tk.Label(self.score_frame, text=f"Current Score: {self.game.score}", font=("Arial", 12))
        self.current_score_label.pack(side=tk.LEFT, padx=20)

        self.high_score_label = tk.Label(self.score_frame, text=f"Previous High Score: {self.high_score}", font=("Arial", 12))
        self.high_score_label.pack(side=tk.LEFT, padx=20)

        # Legend
        self.legend_label = tk.Label(master, 
                                     text="Legend: Snake Head: > < v ^ (Bold) | Snake Body: * | Simple Food: O | Super Food: X", 
                                     font=("Arial", 10))
        self.legend_label.pack(pady=10)

        self.master.bind("<Left>", lambda event: self._handle_keypress(Direction.LEFT))
        self.master.bind("<Right>", lambda event: self._handle_keypress(Direction.RIGHT))
        self.master.bind("<Up>", lambda event: self._handle_keypress(Direction.UP))
        self.master.bind("<Down>", lambda event: self._handle_keypress(Direction.DOWN))

        self._draw_board()
        self._update_game()

    def _load_high_score(self):
        high_score_file = self.config.data_config.GAME_DATA_FOLDER.joinpath("high_score.txt")
        if os.path.exists(high_score_file):
            try:
                with open(high_score_file, "r", encoding="utf-8") as f:
                    return int(f.read())
            except ValueError:
                return 0
        return 0

    def _save_high_score(self):
        high_score_file = self.config.data_config.GAME_DATA_FOLDER.joinpath("high_score.txt")
        with open(high_score_file, "w", encoding="utf-8") as f:
            f.write(str(self.high_score))

    def _draw_board(self):
        self.canvas.delete("all")
        # Draw boundary (dashed lines)
        for x in range(0, self.board_width):
            self.canvas.create_line(x, 0, x, self.board_height, fill="gray", dash=(2, 2))
        for y in range(0, self.board_height):
            self.canvas.create_line(0, y, self.board_width, y, fill="gray", dash=(2, 2))

    def _draw_snake(self):
        head = self.game.snake.get_head()
        head_x, head_y = head.x, head.y
        
        direction_symbols = {
            Direction.UP: "^",
            Direction.DOWN: "v",
            Direction.LEFT: "<",
            Direction.RIGHT: ">"
        }
        head_symbol = direction_symbols.get(self.game.snake.direction, ">") # Default to > if direction is somehow None
        
        # Draw head
        self.canvas.create_text(head_x + 1 / 2, 
                                head_y + 1 / 2, 
                                text=head_symbol, 
                                font=tkFont.Font(family="Arial", size=6, weight="bold"), 
                                fill="black", tags="snake")

        # Draw body
        for segment in self.game.snake.get_body()[1:]:
            seg_x, seg_y = segment.x, segment.y
            self.canvas.create_text(seg_x + 1 / 2, 
                                    seg_y + 1 / 2, 
                                    text="*", 
                                    font=tkFont.Font(family="Arial", size=4), 
                                    fill="green", tags="snake")

    def _draw_food(self):
        if self.game.is_food_active and self.game.food:
            food_item = self.game.food
            food_x, food_y = food_item.position[0], food_item.position[1]
            symbol = "O"
            color = "red"
            if isinstance(food_item, SuperFood):
                symbol = "X"
                color = "purple"
            
            self.canvas.create_text(food_x + 1 / 2, 
                                    food_y + 1 / 2, 
                                    text=symbol, 
                                    font=tkFont.Font(family="Arial", size=6), 
                                    fill=color, tags="food")

    def _update_score_display(self):
        self.current_score_label.config(text=f"Score: {self.game.score}")

    def _handle_keypress(self, new_direction: Direction):
        # Prevent immediate 180-degree turns
        current_direction = self.game.snake.direction
        if (new_direction == Direction.UP and current_direction == Direction.DOWN) or \
           (new_direction == Direction.DOWN and current_direction == Direction.UP) or \
           (new_direction == Direction.LEFT and current_direction == Direction.RIGHT) or \
           (new_direction == Direction.RIGHT and current_direction == Direction.LEFT):
            return
        self.game.snake.set_direction(new_direction)

    def _update_game(self):
        if not self.game.is_game_over():
            self.game.step() # Pass no action, game handles current direction
            self._draw_board()
            self._draw_snake()
            self._draw_food()
            self._update_score_display()
            self._update_game()
        else:
            self._game_over_screen()

    def _game_over_screen(self):
        self.canvas.create_text(self.board_width / 2, self.board_height / 2 - 30,
                                text="GAME OVER", font=("Arial", 24, "bold"), fill="red")
        self.canvas.create_text(self.board_width / 2, self.board_height / 2 + 10,
                                text=f"Final Score: {self.game.score}", font=("Arial", 16), fill="black")
        self.canvas.create_text(self.board_width / 2, self.board_height / 2 + 10,
                                text=f"RESTARTING...", font=("Arial", 16), fill="black")
        self._restart_game()
        # restart_button = tk.Button(self.master, text="Restart", command=self._restart_game, font=("Arial", 12))
        # self.canvas.create_window(self.board_width / 2, self.board_height / 2 + 60, window=restart_button)

    def _restart_game(self):
        self.game.reset()
        self.high_score = self._load_high_score() # Re-load in case it was updated elsewhere or for consistency
        self._update_score_display()
        # Clear game over messages and button if they are canvas items
        self.canvas.delete("game_over_text") # Add tags to game over text if needed
        self.canvas.delete("restart_button_window") # Add tags to button window if needed
        
        # Re-bind keys if they were unbound or if master was destroyed/recreated
        self.master.bind("<Left>", lambda event: self._handle_keypress(Direction.LEFT))
        self.master.bind("<Right>", lambda event: self._handle_keypress(Direction.RIGHT))
        self.master.bind("<Up>", lambda event: self._handle_keypress(Direction.UP))
        self.master.bind("<Down>", lambda event: self._handle_keypress(Direction.DOWN))

        self._update_game() # Start the game loop again

if __name__ == '__main__':
    root = tk.Tk()
    app = GameUI(master=root)
    root.mainloop()