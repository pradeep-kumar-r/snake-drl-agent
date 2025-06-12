import random
from typing import Optional
from src.game.direction import Direction
from src.game.snake import Snake
from src.game.food import Food, SimpleFood, SuperFood
from src.config import config


class Game:
    def __init__(self, configuration=config):
        self.config = configuration
        self.game_config = configuration.get_game_config()
        # Initialize attributes to default values before reset
        self.snake: Optional[Snake] = None # Will be set in reset
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
    
    def step(self, action: int):
        """
        Processes a single step of the game based on the given action.
        Actions:
            0: STILL (continue in current direction)
            1: RIGHT
            2: DOWN
            3: LEFT
            4: UP
        Returns:
            tuple: (reward, game_over, score)
        """
        training_rewards = self.config.get_training_config().REWARDS
        current_reward = training_rewards.ALIVE_REWARD  # Start with reward/penalty for surviving a step

        # Define action mapping to Direction enum
        # Order: RIGHT, DOWN, LEFT, UP (corresponds to actions 1, 2, 3, 4)
        # Action 0 (STILL) means no change in direction
        action_to_direction_map = {
            1: Direction.RIGHT,
            2: Direction.DOWN,
            3: Direction.LEFT,
            4: Direction.UP,
        }

        if action in action_to_direction_map:
            new_direction = action_to_direction_map[action]
            # Prevent immediate 180-degree turns if it's a valid new direction
            if not Direction.is_opposite(new_direction, self.snake.direction):
                self.snake.set_direction(new_direction)
        # If action is 0 (STILL) or an invalid turn, snake continues in its current direction
        
        self.snake.move()

        # Check if food is active - update food, if not generate food
        if self.is_food_active:
            if not self.food.update(): # update returns False if food expired
                self.is_food_active = False # Mark as inactive so new food is generated
                # Optional: Add a small penalty for letting superfood expire if desired
        
        if not self.is_food_active:
            self.generate_food()
        
        # Check if the food is eaten after the snake moves
        if self._is_food_eaten():
            self.food_count += 1
            if isinstance(self.food, SimpleFood):
                food_reward = training_rewards.EAT_FOOD
                self.score += self.game_config.SCORE.EAT_FOOD
            else: # SuperFood
                # Ensure remaining_steps is available and positive for SuperFood
                super_food_value = self.food.remaining_steps if hasattr(self.food, 'remaining_steps') else 1
                food_reward = training_rewards.XPLIER_EAT_SUPERFOOD * super_food_value
                self.score += self.game_config.SCORE.XPLIER_EAT_SUPERFOOD * super_food_value
            
            current_reward += food_reward
            self.is_food_active = False # Mark as eaten so new food is generated
            self.generate_food() # Generate new food immediately
        
        # Check for collision
        if self.snake.check_collision():
            self.game_over = True
            current_reward += training_rewards.GAME_OVER_REWARD
            self.record_score() # Record score on game over

        self.steps_elapsed += 1
        return current_reward, self.game_over, self.score
        
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