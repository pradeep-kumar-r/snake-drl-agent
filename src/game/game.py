import random
from time import sleep
import tkinter as tk
from typing import Optional, Literal, Tuple, Dict
from src.game.direction import Direction
from src.game.snake import Snake
from src.game.food import Food, SimpleFood, SuperFood
from src.game.ui import UI
from src.config import config


class Game:
    def __init__(self, 
                 game_config=config.get_game_config(),
                 headless=False):
        self.game_config = game_config
        self.snake: Optional[Snake] = None
        self.is_food_active: bool = False
        self.current_food: Optional[Food] = None
        self.steps_elapsed: int = 0
        self.food_count: int = 0
        self.score: int = 0
        self.is_game_over: bool = False
        self.end_state: Optional[Dict[str, int]] = None
        self.headless = headless
        self.reset()

    def reset(self) -> None:
        self.snake = Snake(board_dim=self.game_config.BOARD_DIM,
                           init_pos=self.game_config.SNAKE.INIT_POS,
                           init_length=self.game_config.SNAKE.INIT_LENGTH,
                           init_direction=self.game_config.SNAKE.INIT_DIRECTION)
        self._generate_or_update_food()
        self.is_food_active: bool = False
        self.current_food: Optional[Food] = None
        self.steps_elapsed: int = 0
        self.food_count: int = 0
        self.score: int = 0
        self.is_game_over: bool = False
        
    def _is_food_eaten(self) -> bool:
        if not self.is_food_active:
            return False
        return self.current_food.is_eaten(self.snake.get_head())
    
    def _generate_or_update_food(self) -> None:
        # Start generating food only after the first 3 steps in a new game
        if self.steps_elapsed < 3:
            return
        
        if not self.current_food.active or not self.is_food_active:
            if random.random() <= self.game_config.FOOD.SUPERFOOD_PROBABILITY and self.food_count > 0:
                self.current_food = SuperFood(board_dim=self.game_config.BOARD_DIM,
                                    lifetime=self.game_config.FOOD.SUPERFOOD_LIFETIME)
            else:
                self.current_food = SimpleFood(board_dim=self.game_config.BOARD_DIM)
            self.current_food.place_food(self.snake.get_body())
            self.is_food_active = True        
        else:
            self.current_food.update()
        
    def _update_score(self) -> None:
        if not self.is_food_active:
            return
        if isinstance(self.current_food, SimpleFood):
            self.score += self.game_config.SCORE.EAT_FOOD
        else: 
            self.score += self.game_config.SCORE.XPLIER_EAT_SUPERFOOD*(1+self.current_food.remaining_steps)    
    
    def step(self, action: Literal[0, 1, 2, 3, 4]=0) -> Tuple[float, bool, int, int]:
        """
        Actions:
            0: STILL (do nothing)
            1: RIGHT
            2: DOWN
            3: LEFT
            4: UP
        Returns:
            tuple: (reward, game_over, score, steps_elapsed)
        """
        
        self.steps_elapsed += 1
        
        # Step 1: Generate/update food if no food is active
        self._generate_or_update_food()
        
        # Step 2: Update snake direction and move it
        action_to_direction_map = {
            1: Direction.RIGHT,
            2: Direction.DOWN,
            3: Direction.LEFT,
            4: Direction.UP,
        }

        if action in action_to_direction_map:
            new_direction = action_to_direction_map[action]
            self.snake.set_direction(new_direction)

        self.snake.move()

        # Step 3: Check if food is eaten after snake moves, if so grow snake, update food count & score
        if self._is_food_eaten():
            self.food_count += 1
            self._update_score()
            self.snake.should_grow = True
                
        # Step 4: Check for collision
        if self.snake.check_collision():
            self.is_game_over = True
            self.snake.kill()
            self._record_end_state()
        
        return (self.steps_elapsed, 
                self.is_game_over, 
                self.score,
                self.snake.get_body(),
                self.snake.get_direction(),
                self.is_food_active,
                self.current_food.position if self.is_food_active else None,
                self.current_food.remaining_steps if self.is_food_active and isinstance(self.current_food, SuperFood) else None)
        
    def _record_end_state(self):
        if self.is_game_over:
            self.end_state = {
                "steps_elapsed": self.steps_elapsed, 
                "food_count": self.food_count,
                "score": self.score,
            }
    
    def record_score(self):
        ...
        # if self.is_game_over:
        #     score_file = self.config.data_config.GAME_DATA_FOLDER.joinpath("scores.txt")
        #     with open(score_file, "a", encoding="utf-8") as f:
        #         f.write(str(self.score) + "\n")
            
        #     high_score_file = self.config.data_config.GAME_DATA_FOLDER.joinpath("high_score.txt")
        #     with open(high_score_file, "r", encoding="utf-8") as f:
        #         high_score = int(f.read())
            
        #     if self.score > high_score:
        #         with open(high_score_file, "w", encoding="utf-8") as f:
        #             f.write(str(self.score))
                    
    def display_ui(self):
        ...
        # root = tk.Tk()
        # app = UI(master=root,
        #         snake=Snake(board_dim=11,
        #                     init_pos=(5, 5),
        #                     init_length=3,
        #                     init_direction=Direction.RIGHT),
        #         food=Food(position=(6, 6)),
        #         score=10,
        #         high_score=10,
        #         ui_config=config.get_ui_config(),
        #         is_game_over=False)
        # root.mainloop()