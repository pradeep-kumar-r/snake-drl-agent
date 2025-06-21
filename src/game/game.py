import random
from time import sleep
from uuid import uuid4
from datetime import datetime
import tkinter as tk
from typing import Optional, Literal, Tuple, Dict, Any
from src.game.direction import Direction
from src.game.snake import Snake
from src.game.food import Food, SimpleFood, SuperFood
from src.game.ui import UI


class Game:
    def __init__(self, 
                 game_config: Optional[Dict[str, Any]],
                 data_config: Optional[Dict[str, Any]],
                 ui_config: Optional[Dict[str, Any]] = None,
                 headless: bool = False):
        self.game_config = game_config
        self.data_config = data_config
        self.ui_config = ui_config
        self.snake: Optional[Snake] = None
        self.is_food_active: bool = False
        self.current_food: Optional[Food] = None
        self.steps_elapsed: int = 0
        self.food_count: int = 0
        self.score: int = 0
        self.is_game_over: bool = False
        self.end_state: Optional[Dict[str, int]] = None
        self.headless = headless
        self.ui = None
        self.root = None
        if not self.headless:
            self.root = tk.Tk()
            self.root.withdraw()
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
        
        # Read high score, default to 0 if the file doesn't exist
        try:
            with open(self.data_config.HIGH_SCORE_FILE, "r", encoding="utf-8") as f:
                self.high_score = int(f.read())
        except FileNotFoundError:
            self.high_score = 0
        
        # Display UI (headless scenario handled implicitly)
        self.display_ui()
        
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
        
        # Step 5: Sleep for the defined duration & display UI
        sleep(self.game_config.SLEEP_PER_TIMESTEP)
        self.display_ui()
        
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
                "game_id": uuid4(),
                "updated_at": datetime.now(),
                "steps_elapsed": self.steps_elapsed, 
                "food_count": self.food_count,
                "score": self.score,
            }
        self._record_score()
    
    def _record_score(self):
        if not self.is_game_over:
            return
        
        with open(self.data_config.SCORES_FILE, "a", encoding="utf-8") as f:
            f.write(f"{self.end_state}\n")
        
        if self.score > self.high_score:
            with open(self.data_config.HIGH_SCORE_FILE, "w", encoding="utf-8") as f:
                f.write(str(self.score))
                    
    def _init_or_update_ui(self):
        """Initialize or update the UI with current game state."""
        if self.headless or not self.root:
            return
            
        if not self.ui:
            # Create new UI if it doesn't exist
            self.root.deiconify()  # Show the window
            self.ui = UI(
                master=self.root,
                snake=self.snake,
                food=self.current_food,
                score=self.score,
                high_score=self.high_score,
                ui_config=self.ui_config,
                is_game_over=self.is_game_over
            )
        else:
            # Update existing UI
            self.ui.snake = self.snake
            self.ui.food = self.current_food
            self.ui.score = self.score
            self.ui.is_game_over = self.is_game_over
            
            # Redraw the UI
            self.ui.draw_board()
            self.ui.draw_snake()
            if self.ui.food:
                self.ui.draw_food()
            if self.ui.is_game_over:
                self.ui.game_over_screen()
                
            # Update the window
            self.root.update_idletasks()
            self.root.update()
    
    def display_ui(self):
        """Display or update the game UI."""
        if self.headless or not self.root:
            return
        self._init_or_update_ui()
    
    def cleanup(self):
        if self.root:
            self.root.destroy()
            self.root = None
        self.ui = None