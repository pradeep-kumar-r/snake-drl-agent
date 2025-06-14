import gym
from gym import spaces
import numpy as np
from PIL import Image, ImageDraw
import torch
from src.game.game import Game
from src.game.food import SuperFood
from src.config import config as app_config


class SnakeEnv(gym.Env):
    metadata = {'render_modes': ['human', 'rgb_array'], 
                'render_fps': 10}

    def __init__(self, game_ui_instance=None, headless=True):
        super().__init__()
        self.config_module = app_config
        self.game_cfg = self.config_module.get_game_config()
        self.model_cfg = self.config_module.get_model_config()
        self.training_cfg = self.config_module.get_training_config()

        self.game = Game(configuration=self.config_module)
        self.game_ui = game_ui_instance # Optional GameUI for rendering
        self.headless = headless

        # Define image dimensions for the CNN input
        self.IMG_HEIGHT = self.game_cfg.UI.TARGET_IMG_HEIGHT # e.g., 40
        self.IMG_WIDTH = self.game_cfg.UI.TARGET_IMG_WIDTH   # e.g., 40

        # Action space: 0:STILL, 1:RIGHT, 2:DOWN, 3:LEFT, 4:UP
        self.action_space = spaces.Discrete(self.model_cfg.NUM_ACTIONS)

        # Observation space: a single channel (grayscale) image, normalized
        self.observation_space = spaces.Box(
            low=0, high=1, 
            shape=(1, self.IMG_HEIGHT, self.IMG_WIDTH), 
            dtype=np.float32
        )
        
        # For rendering rgb_array if needed
        self.window_width_px = self.game_cfg.GAME.WIDTH * self.game_cfg.UI.CELL_SIZE
        self.window_height_px = self.game_cfg.GAME.HEIGHT * self.game_cfg.UI.CELL_SIZE

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.game.reset()
        observation = self._get_processed_screen()
        info = self._get_info()
        if not self.headless and self.game_ui:
            self.render()
        return observation, info

    def step(self, action):
        reward, done, score = self.game.step(action)
        observation = self._get_processed_screen()
        info = self._get_info()
        info['score'] = score # Add current game score to info

        if not self.headless and self.game_ui:
            self.render()
            if done and hasattr(self.game_ui, '_game_over_screen'): # Show game over on UI if available
                self.game_ui._game_over_screen()

        return observation, reward, done, False, info # Gym API: obs, reward, terminated, truncated, info

    def _get_info(self):
        return {
            "snake_head_pos": self.game.snake.get_head().to_tuple(),
            "snake_length": len(self.game.snake.get_body()),
            "food_pos": self.game.food.position if self.game.is_food_active and self.game.food else None,
            "score": self.game.score
        }

    def _get_processed_screen(self):
        """Generates a 1xH_IMGxW_IMG normalized grayscale image of the game state."""
        # Create an image in memory
        # Dimensions are based on game grid, not pixels, for drawing simplicity
        # Then resize to target CNN input size
        grid_width = self.game_cfg.GAME.WIDTH
        grid_height = self.game_cfg.GAME.HEIGHT
        
        # Create a larger intermediate image to draw on, then scale down
        # This allows for clearer distinctions if cell_size is small
        # Let's use a scale factor, e.g., 10 pixels per grid cell for drawing
        draw_scale = 10 
        img_draw_width = grid_width * draw_scale
        img_draw_height = grid_height * draw_scale

        image = Image.new('L', (img_draw_width, img_draw_height), color='black') # Grayscale, black background
        draw = ImageDraw.Draw(image)

        # Define colors (0-255 for grayscale)
        SNAKE_COLOR = 255 # White
        FOOD_COLOR = 180  # Light Gray for simple food
        SUPER_FOOD_COLOR = 128 # Darker Gray for super food

        # Draw snake
        for segment in self.game.snake.get_body():
            x0, y0 = segment.x * draw_scale, segment.y * draw_scale
            x1, y1 = (segment.x + 1) * draw_scale, (segment.y + 1) * draw_scale
            draw.rectangle([x0, y0, x1, y1], fill=SNAKE_COLOR)

        # Draw food
        if self.game.is_food_active and self.game.food:
            food_item = self.game.food
            fx, fy = food_item.position[0] * draw_scale, food_item.position[1] * draw_scale
            fx1, fy1 = (food_item.position[0] + 1) * draw_scale, (food_item.position[1] + 1) * draw_scale
            food_c = SUPER_FOOD_COLOR if isinstance(food_item, SuperFood) else FOOD_COLOR
            draw.rectangle([fx, fy, fx1, fy1], fill=food_c)
        
        # Resize to target CNN dimensions (IMG_WIDTH, IMG_HEIGHT)
        image = image.resize((self.IMG_WIDTH, self.IMG_HEIGHT), Image.Resampling.LANCZOS)
        
        # Normalize to [0, 1]
        img_array = np.array(image, dtype=np.float32) / 255.0
        
        # Add channel dimension: (1, H, W)
        img_array = np.expand_dims(img_array, axis=0)
        return torch.from_numpy(img_array).float() # Return as a torch tensor

    def render(self, mode='human'):
        if self.headless:
            if mode == 'rgb_array':
                # Create an RGB image for gym's rgb_array mode (similar to _get_processed_screen but RGB)
                grid_width = self.game_cfg.GAME.WIDTH
                grid_height = self.game_cfg.GAME.HEIGHT
                draw_scale = 10 
                img_draw_width = grid_width * draw_scale
                img_draw_height = grid_height * draw_scale

                image = Image.new('RGB', (img_draw_width, img_draw_height), color='black')
                draw = ImageDraw.Draw(image)
                SNAKE_C_RGB = (0, 255, 0) # Green
                FOOD_C_RGB = (255, 0, 0) # Red
                SUPER_FOOD_C_RGB = (255, 0, 255) # Magenta

                for segment in self.game.snake.get_body():
                    x0, y0 = segment[0] * draw_scale, segment[1] * draw_scale
                    x1, y1 = (segment[0] + 1) * draw_scale, (segment[1] + 1) * draw_scale
                    draw.rectangle([x0, y0, x1, y1], fill=SNAKE_C_RGB)
                if self.game.is_food_active and self.game.food:
                    food_item = self.game.food
                    fx, fy = food_item.position[0] * draw_scale, food_item.position[1] * draw_scale
                    fx1, fy1 = (food_item.position[0] + 1) * draw_scale, (food_item.position[1] + 1) * draw_scale
                    food_c = SUPER_FOOD_C_RGB if isinstance(food_item, SuperFood) else FOOD_C_RGB
                    draw.rectangle([fx, fy, fx1, fy1], fill=food_c)
                
                # Resize to a viewable size if needed, or keep as is
                # For consistency with observation, let's resize to a multiple of IMG_WIDTH, IMG_HEIGHT
                # Or just return the raw draw_scale image
                # image = image.resize((self.window_width_px, self.window_height_px), Image.Resampling.NEAREST)
                return np.array(image)
            return None # No rendering in headless human mode

        if self.game_ui and mode == 'human':
            # This assumes GameUI has methods to update itself based on self.game
            # And that GameUI's internal loop is paused or managed externally
            self.game_ui._draw_board() 
            self.game_ui._draw_snake()
            self.game_ui._draw_food()
            self.game_ui._update_score_display()
            self.game_ui.master.update_idletasks()
            self.game_ui.master.update()
            return None
        elif mode == 'rgb_array': # Non-headless rgb_array
            # Similar to headless rgb_array logic
            grid_width = self.game_cfg.GAME.WIDTH
            grid_height = self.game_cfg.GAME.HEIGHT
            draw_scale = 10 
            img_draw_width = grid_width * draw_scale
            img_draw_height = grid_height * draw_scale
            image = Image.new('RGB', (img_draw_width, img_draw_height), color='black')
            draw = ImageDraw.Draw(image)
            SNAKE_C_RGB = (0, 255, 0) 
            FOOD_C_RGB = (255, 0, 0) 
            SUPER_FOOD_C_RGB = (255, 0, 255) 
            for segment in self.game.snake.get_body():
                x0, y0 = segment[0] * draw_scale, segment[1] * draw_scale
                x1, y1 = (segment[0] + 1) * draw_scale, (segment[1] + 1) * draw_scale
                draw.rectangle([x0, y0, x1, y1], fill=SNAKE_C_RGB)
            if self.game.is_food_active and self.game.food:
                food_item = self.game.food
                fx, fy = food_item.position[0] * draw_scale, food_item.position[1] * draw_scale
                fx1, fy1 = (food_item.position[0] + 1) * draw_scale, (food_item.position[1] + 1) * draw_scale
                food_c = SUPER_FOOD_C_RGB if isinstance(food_item, SuperFood) else FOOD_C_RGB
                draw.rectangle([fx, fy, fx1, fy1], fill=food_c)
            return np.array(image)

    def close(self):
        if self.game_ui and hasattr(self.game_ui.master, 'destroy'):
            self.game_ui.master.destroy()


# Example Usage (for testing the environment directly):
if __name__ == '__main__':
    # To test with UI (assuming GameUI is set up to be driven externally):
    # import tkinter as tk
    # from src.game.game_ui import GameUI
    # root = tk.Tk()
    # ui = GameUI(master=root, configuration=app_config)
    # env = SnakeEnv(game_ui_instance=ui, headless=False)

    # To test headless:
    env = SnakeEnv(headless=True)

    obs, info = env.reset()
    print("Initial observation shape:", obs.shape)
    print("Initial info:", info)

    for _ in range(100):
        action = env.action_space.sample()  # Sample random action
        obs, reward, terminated, truncated, info = env.step(action)
        print(f"Action: {action}, Reward: {reward}, Terminated: {terminated}, Truncated: {truncated}, Score: {info.get('score')}")
        # env.render() # Call this if not headless and UI is managed
        if terminated or truncated:
            print("Game Over. Final Score:", info.get('score'))
            obs, info = env.reset()
    env.close()
