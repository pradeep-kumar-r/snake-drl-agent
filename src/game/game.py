import random
from typing import Optional, Literal, Tuple
from src.game.direction import Direction
from src.game.snake import Snake
from src.game.food import Food, SimpleFood, SuperFood
from src.config import config


class Game:
    def __init__(self, configuration=config):
        self.config = configuration
        self.game_config = configuration.get_game_config()
        self.snake: Optional[Snake] = None
        self.food: Optional[Food] = None
        self.steps_elapsed: int = 0
        self.food_count: int = 0
        self.score: int = 0
        self.game_over: bool = False
        self.is_food_active: bool = False
        self.reset()

    def reset(self):
        self.snake = Snake(game_config=self.game_config)
        self.food: Optional[Food] = None
        self.steps_elapsed: int = 0
        self.food_count: int = 0
        self.score: int = 0
        self.game_over: bool = False
        self.is_food_active: bool = False
        
    def generate_food(self):
        if self.is_food_active:
            return
        if random.random() <= self.game_config.FOOD.SUPERFOOD_PROBABILITY:
            self.food = SuperFood()
        else:
            self.food = SimpleFood()
        snake_body = self.snake.get_body()
        self.food.place_food(snake_body)
        self.is_food_active = True
        
    def _is_food_eaten(self):
        if not self.is_food_active:
            return False
        return self.food.is_eaten(self.snake.get_head())
    
    def is_game_over(self):
        return self.game_over
    
    def step(self, action: Literal[0, 1, 2, 3, 4]) -> Tuple[float, bool, int, int]:
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
        training_rewards = self.config.get_training_config().REWARDS
        current_reward = training_rewards.MOVE

        action_to_direction_map = {
            1: Direction.RIGHT,
            2: Direction.DOWN,
            3: Direction.LEFT,
            4: Direction.UP,
        }

        if action in action_to_direction_map:
            new_direction = action_to_direction_map[action]
            if not Direction.is_opposite(new_direction, self.snake.direction):
                self.snake.set_direction(new_direction)
        else:
            current_reward += training_rewards.NOTHING
        
        self.snake.move()

        # Check if food is active - update food, if not generate food
        if self.is_food_active:
            if not self.food.update():
                self.is_food_active = False
                
        if not self.is_food_active:
            self.generate_food()
        
        # Check if the food is eaten after the snake moves
        if self._is_food_eaten():
            self.food_count += 1
            if isinstance(self.food, SimpleFood):
                current_reward += training_rewards.EAT_FOOD
                self.score += self.game_config.SCORE.EAT_FOOD
            else: 
                super_food_value = self.food.remaining_steps if hasattr(self.food, 'remaining_steps') else 1
                current_reward += training_rewards.XPLIER_EAT_SUPERFOOD * super_food_value
                self.score += self.game_config.SCORE.XPLIER_EAT_SUPERFOOD * super_food_value
            
            self.is_food_active = False 
            self.generate_food()
        
        # Check for collision
        if self.snake.check_collision():
            self.game_over = True
            current_reward += training_rewards.GAME_OVER_REWARD
            self.record_score()

        self.steps_elapsed += 1
        return current_reward, self.game_over, self.score, self.steps_elapsed
        
    def record_score(self):
        if self.is_game_over:
            score_file = self.config.data_config.GAME_DATA_FOLDER.joinpath("scores.txt")
            with open(score_file, "a", encoding="utf-8") as f:
                f.write(str(self.score) + "\n")
            
            high_score_file = self.config.data_config.GAME_DATA_FOLDER.joinpath("high_score.txt")
            with open(high_score_file, "r", encoding="utf-8") as f:
                high_score = int(f.read())
            
            if self.score > high_score:
                with open(high_score_file, "w", encoding="utf-8") as f:
                    f.write(str(self.score))