import random
from uuid import uuid4
from datetime import datetime
from typing import Optional, Literal, Tuple, Dict, Any
from pathlib import Path
from src.game.direction import Direction
from src.game.snake import Snake
from src.game.food import Food, SimpleFood, SuperFood


class Game:
    def __init__(self, 
                 game_config: Optional[Dict[str, Any]],
                 data_config: Optional[Dict[str, Any]]):
        self.game_config = game_config
        self.data_config = data_config
        self.snake: Optional[Snake] = None
        self.is_food_active: bool = False
        self.current_food: Optional[Food] = None
        self.steps_elapsed: int = 0
        self.food_count: int = 0
        self.score: int = 0
        self.high_score: int = 0
        self.is_game_over: bool = False
        self.state: Optional[Dict[str, int]] = None
        self.reset()

    def reset(self) -> None:
        self.snake = Snake(board_dim=self.game_config["BOARD_DIM"],
                           init_pos=self.game_config["SNAKE"]["SNAKE_INIT_POS"],
                           init_length=self.game_config["SNAKE"]["SNAKE_INIT_LENGTH"],
                           init_direction=Direction[self.game_config["SNAKE"]["SNAKE_INIT_DIRECTION"]])
        self._generate_or_update_food()
        self.is_food_active: bool = False
        self.current_food: Optional[Food] = None
        self.steps_elapsed: int = 0
        self.food_count: int = 0
        self.score: int = 0
        self.is_game_over: bool = False
        
        # Read high score, default to 0 if the file doesn't exist
        try:
            with open(self.data_config["HIGH_SCORE_FILE_PATH"], "r", encoding="utf-8") as f:
                self.high_score = int(f.read())
        except (ValueError, FileNotFoundError):
            self.high_score = 0
        
    def _is_food_eaten(self) -> bool:
        if not self.is_food_active:
            return False
        return self.current_food.is_eaten(self.snake.get_head())
    
    def _generate_or_update_food(self) -> None:
        # Start generating food only after the first 3 steps in a new game
        if self.steps_elapsed < 3:
            return
        
        if not hasattr(self.current_food, 'active') or not self.is_food_active:
            if random.random() <= self.game_config["FOOD"]["SUPERFOOD_PROBABILITY"] and self.food_count > 0:
                self.current_food = SuperFood(board_dim=self.game_config["BOARD_DIM"],
                                    lifetime=self.game_config["FOOD"]["SUPERFOOD_LIFETIME"])
            else:
                self.current_food = SimpleFood(board_dim=self.game_config["BOARD_DIM"])
            self.current_food.place_food(self.snake.get_body())
            self.is_food_active = True
        else:
            self.current_food.update()
        
    def _update_score(self) -> None:
        if not self.is_food_active:
            return
        if isinstance(self.current_food, SimpleFood):
            self.score += self.game_config["SCORE"]["EAT_FOOD"]
        else: 
            self.score += self.game_config["SCORE"]["XPLIER_EAT_SUPERFOOD"]*(1+self.current_food.remaining_steps)    
    
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
            self.snake.growth_pending = True
            self.current_food.active = False
            self.is_food_active = False
                
        # Step 4: Check for end states (collision or if the snake has eaten all foods)
        if self.snake.check_collision() or len(self.snake) >= self.game_config["BOARD_DIM"] ** 2:
            self.is_game_over = True
            self.snake.kill()
            self._record_state()
        
        return (self.steps_elapsed, 
                self.is_game_over, 
                self.score,
                self.snake.get_body(),
                self.snake.get_direction(),
                self.is_food_active,
                self.current_food.position if self.is_food_active else None,
                self.current_food.remaining_steps if self.is_food_active and isinstance(self.current_food, SuperFood) else None)
        
    def _record_state(self):
        self.state = {
            "game_id": str(uuid4()),
            "updated_at": datetime.now(),
            "steps_elapsed": self.steps_elapsed, 
            "food_count": self.food_count,
            "score": self.score,
        }
        self._record_score()
    
    def get_state(self):
        return {
            "game_id": str(uuid4()),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "steps_elapsed": self.steps_elapsed, 
            "food_count": self.food_count,
            "score": self.score,
            "is_game_over": self.is_game_over,
        }
    
    def _record_score(self):
        scores_path = Path(self.data_config["SCORES_FILE_PATH"])
        scores_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(scores_path, "a", encoding="utf-8") as f:
            f.write(f"{self.state}\n")
        
        high_score_path = Path(self.data_config["HIGH_SCORE_FILE_PATH"])
        high_score_path.parent.mkdir(parents=True, exist_ok=True)
        
        if self.score > self.high_score:
            with open(high_score_path, "w", encoding="utf-8") as f:
                f.write(str(self.score))