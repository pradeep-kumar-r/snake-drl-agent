from typing import Dict, Any, Optional, Tuple, List
import pygame
import numpy as np
from src.game.snake import Snake
from src.game.food import Food, SuperFood
from src.game.colour import Colour
from src.utils.logger import logger


class UI:
    def __init__(self,
                 ui_config: Dict[str, Any],
                 snake: Snake,
                 episode: int,
                 food: Optional[Food] = None,
                 score: Optional[int] = 0,
                 high_score: Optional[int] = 0):
        logger.debug(f"Initializing UI for episode {episode}")
        pygame.init()
        self.ui_config = ui_config
        self.board_width: int = self.ui_config["BOARD_DIM"]
        self.board_height: int = self.ui_config["BOARD_DIM"]
        self.cell_size: int = self.ui_config["CELL_SIZE_IN_PIXELS"]
        self.snake: Snake = snake
        self.episode: int = episode
        self.food: Optional[Food] = food
        self.score: int = score
        self.high_score: int = high_score
        
        # Calculate window dimensions to accommodate UI elements
        self.extra_height = self.ui_config["EXTRA_WINDOW_HEIGHT"]
        self.padding = self.ui_config['BOARD']['PADDING']
        
        # Calculate board dimensions
        self.board_pixel_width = self.board_width * self.cell_size
        self.board_pixel_height = self.board_height * self.cell_size
        
        # Calculate window dimensions
        self.window_width = self.board_pixel_width + 2 * self.padding
        self.window_height = self.board_pixel_height + self.extra_height
        
        self.screen: Optional[pygame.Surface] = None
        self.font_title: Optional[pygame.font.Font] = None
        self.font_score: Optional[pygame.font.Font] = None
        self.title_rect: Optional[pygame.Rect] = None
        self.score_rect: Optional[pygame.Rect] = None
        self.food_lifetime_rect: Optional[pygame.Rect] = None
        self.board_rect: Optional[pygame.Rect] = None
        self.snake_rect: Optional[pygame.Rect] = None
        self.food_rect: Optional[pygame.Rect] = None
        self.game_over_rect: Optional[pygame.Rect] = None
        self.font_game_over: Optional[pygame.font.Font] = None
        self._is_initialized: bool = False
        self.headless_surface: Optional[pygame.Surface] = None
    
    def _initialize_fonts(self) -> None:
        self.font_title = pygame.font.SysFont(
            self.ui_config["TITLE"]["FONT"]["NAME"], 
            self.ui_config["TITLE"]["FONT"]["SIZE"]
        )
        self.font_score = pygame.font.SysFont(
            self.ui_config["SCORE"]["FONT"]["NAME"], 
            self.ui_config["SCORE"]["FONT"]["SIZE"]
        )
        self.font_game_over = pygame.font.SysFont(
            self.ui_config["GAME_OVER_LABEL"]["FONT"]["NAME"], 
            self.ui_config["GAME_OVER_LABEL"]["FONT"]["SIZE"]
        )
    
    def _initialize_display(self) -> None:
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption(self.ui_config["TITLE"]["TEXT"])
        self._initialize_fonts()
        self.headless_surface = pygame.Surface((self.window_width, self.window_height))
        self._is_initialized = True
        logger.debug(f"Display initialized with dimensions: {self.window_width}x{self.window_height}")
    
    def _draw_title(self, surface: pygame.Surface) -> Tuple[pygame.Surface, pygame.Rect]:
        # Create a title section with a border
        title_height = self.ui_config['TITLE']['TOP_PADDING'] * 2
        title_section = pygame.Rect(0, 0, self.window_width, title_height)
        
        # Draw title section background
        pygame.draw.rect(
            surface,
            Colour[self.ui_config['BG_COLOUR']].value,
            title_section
        )
        
        # Draw border around title section
        pygame.draw.rect(
            surface,
            Colour[self.ui_config['BOARD']['BORDER']['FILL']].value,
            title_section,
            self.ui_config['BOARD']['BORDER']['THICKNESS'] // 2
        )
        
        # Render title text
        title_text = self.font_title.render(
            f"{self.ui_config['TITLE']['TEXT']}: Episode {self.episode}",
            True,
            Colour[self.ui_config['TITLE']['COLOUR']].value,
        )
        
        # Position title text in the center of the title section
        title_rect = title_text.get_rect(
            center=(self.window_width // 2, title_section.height // 2)
        )
        
        surface.blit(title_text, title_rect)
        return surface, title_section
    
    def __draw_scores_food_lifetime_labels(self, surface: pygame.Surface) -> Tuple[pygame.Surface, pygame.Rect]:
        # Create a score section below the title
        score_section = pygame.Rect(
            0, 
            self.ui_config['TITLE']['TOP_PADDING'] * 2, 
            self.window_width, 
            self.ui_config['SCORE']['SECTION_HEIGHT']
        )
        
        # Draw score section background
        pygame.draw.rect(
            surface,
            Colour[self.ui_config['BG_COLOUR']].value,
            score_section
        )
        
        # Draw border around score section
        pygame.draw.rect(
            surface,
            Colour[self.ui_config['BOARD']['BORDER']['FILL']].value,
            score_section,
            self.ui_config['BOARD']['BORDER']['THICKNESS'] // 2
        )
        
        # Render score and high score texts
        score_text = self.font_score.render(
            f"Current Score: {self.score}",
            True,
            Colour[self.ui_config["SCORE"]["COLOUR"]].value,
        )
        high_score_text = self.font_score.render(
            f"High Score: {self.high_score}",
            True,
            Colour[self.ui_config["SCORE"]["COLOUR"]].value,
        )
        
        # Determine the food lifetime text
        lifetime_text = "-"
        if (self.food and 
            hasattr(self.food, 'remaining_steps') and 
            self.food.remaining_steps is not None):
            lifetime_text = f"Food Lifetime: {self.food.remaining_steps}"
        elif (self.food and 
              isinstance(self.food, SuperFood)):
            lifetime_text = "Super Food!"
        else:
            lifetime_text = "Food: Normal"
            
        # Render food lifetime text
        food_lifetime_text = self.font_score.render(
            lifetime_text,
            True,
            Colour[self.ui_config["FOOD_LABEL"]["COLOUR"]].value
        )
        
        # Position score text on the left side of the score section
        score_rect = score_text.get_rect(
            center=(self.window_width // 6, score_section.centery)
        )
        
        # Position food lifetime text in the center of the score section
        food_lifetime_rect = food_lifetime_text.get_rect(
            center=(self.window_width // 2, score_section.centery)
        )
        
        # Position high score text on the right side of the score section
        high_score_rect = high_score_text.get_rect(
            center=(self.window_width * 5 // 6, score_section.centery)
        )
        
        # Render all texts to the surface
        surface.blit(score_text, score_rect)
        surface.blit(food_lifetime_text, food_lifetime_rect)
        surface.blit(high_score_text, high_score_rect)
        
        return surface, score_section
    
    def _draw_board(self, 
                    surface: pygame.Surface, 
                    score_rect: pygame.Rect) -> Tuple[pygame.Surface, pygame.Rect]:
        # Calculate board position below the score section
        pad = self.ui_config['BOARD']['PADDING']
        
        # Board starts after the score section
        board_topleft_x = pad
        board_topleft_y = score_rect.bottom + pad
        
        # Board dimensions are fixed based on cell size and board dimensions
        board_width = self.board_width * self.cell_size
        board_height = self.board_height * self.cell_size
        
        board_bottomright_x = board_topleft_x + board_width
        board_bottomright_y = board_topleft_y + board_height
        
        # Create board rectangle
        board_rect = pygame.Rect(
            board_topleft_x, 
            board_topleft_y, 
            board_width, 
            board_height
        )
        
        # Draw board background
        pygame.draw.rect(
            surface,
            Colour[self.ui_config['BOARD']['FILL']].value,
            board_rect
        )
        
        # Draw thick border around the board
        pygame.draw.rect(
            surface,
            Colour[self.ui_config['BOARD']['BORDER']['FILL']].value,
            board_rect,
            self.ui_config['BOARD']['BORDER']['THICKNESS']
        )
        
        # Draw grid lines
        for i in range(1, self.board_width):
            x_pos = board_topleft_x + i * self.cell_size
            pygame.draw.line(
                surface,
                Colour[self.ui_config['BOARD']['GRID']['FILL']].value,
                (x_pos, board_topleft_y),
                (x_pos, board_bottomright_y),
                self.ui_config['BOARD']['GRID']['THICKNESS']
            )
        
        for i in range(1, self.board_height):
            y_pos = board_topleft_y + i * self.cell_size
            pygame.draw.line(
                surface,
                Colour[self.ui_config['BOARD']['GRID']['FILL']].value,
                (board_topleft_x, y_pos),
                (board_bottomright_x, y_pos),
                self.ui_config['BOARD']['GRID']['THICKNESS']
            )
        return surface, board_rect
    
    def _draw_snake(self, 
                    surface: pygame.Surface, 
                    board_rect: pygame.Rect) -> Tuple[pygame.Surface, List[pygame.Rect]]:
        snake_pygame_objects: List[pygame.Rect] = []
        # Draw head
        head_x, head_y = self.snake.body[0]
        head_y = (self.board_height - 1) - head_y
        head_top_y = board_rect.top + head_y * self.cell_size - self.ui_config["SNAKE"]["HEAD"]["STRETCH"]
        head_bottom_y = board_rect.top + head_y * self.cell_size + self.cell_size + self.ui_config["SNAKE"]["HEAD"]["STRETCH"]
        head_left_x = board_rect.left + head_x * self.cell_size - self.ui_config["SNAKE"]["HEAD"]["STRETCH"]
        head_right_x = board_rect.left + head_x * self.cell_size + self.cell_size + self.ui_config["SNAKE"]["HEAD"]["STRETCH"]
        
        head_rect = pygame.draw.rect(
            surface,
            Colour[self.ui_config["SNAKE"]["HEAD"]["FILL"]].value,
            (head_left_x, head_top_y, head_right_x - head_left_x, head_bottom_y - head_top_y)
        )
        snake_pygame_objects.append(head_rect)
        
        # Draw body
        body_radius = self.cell_size // 2
        for x, y in self.snake.body[1:]:
            y = (self.board_height - 1) - y
            body_center_x, body_center_y = (board_rect.left + x * self.cell_size + self.cell_size // 2, 
                                            board_rect.top + y * self.cell_size + self.cell_size // 2)
            body_circle = pygame.draw.circle(
                surface,
                Colour[self.ui_config["SNAKE"]["BODY"]["FILL"]].value,
                (body_center_x, body_center_y),
                body_radius + self.ui_config["SNAKE"]["BODY"]["STRETCH"]
            )
            snake_pygame_objects.append(body_circle)
        return surface, snake_pygame_objects
    
    def _draw_food(self, 
                   surface: pygame.Surface, 
                   board_rect: pygame.Rect) -> Tuple[pygame.Surface, pygame.Rect]:
        if not self.food:
            return
        food_x, food_y = self.food.position
        food_y = (self.board_height - 1) - food_y 
        food_center_x, food_center_y = (board_rect.left + food_x * self.cell_size + self.cell_size // 2, 
                                        board_rect.top + food_y * self.cell_size + self.cell_size // 2)
        is_super_food = isinstance(self.food, SuperFood)
        fill_color = Colour[self.ui_config["FOOD"]["SUPER"]["FILL"]].value if is_super_food else Colour[self.ui_config["FOOD"]["SIMPLE"]["FILL"]].value
        symbol = self.ui_config["FOOD"]["SUPER"]["SYMBOL"] if is_super_food else self.ui_config["FOOD"]["SIMPLE"]["SYMBOL"]
        font_name = self.ui_config["FOOD"]["SUPER"]["FONT"]["NAME"] if is_super_food else self.ui_config["FOOD"]["SIMPLE"]["FONT"]["NAME"]
        font_size = self.ui_config["FOOD"]["SUPER"]["FONT"]["SIZE"] if is_super_food else self.ui_config["FOOD"]["SIMPLE"]["FONT"]["SIZE"]
        font_color = Colour[self.ui_config["FOOD"]["SUPER"]["FONT"]["COLOUR"]].value if is_super_food else Colour[self.ui_config["FOOD"]["SIMPLE"]["FONT"]["COLOUR"]].value
        
        pygame.draw.circle(
            surface,
            fill_color,
            (food_center_x, food_center_y),
            self.cell_size // 2 - 2
        )
        
        food_text = pygame.font.SysFont(
            font_name,
            font_size
        ).render(symbol, True, font_color)
        
        food_rect = food_text.get_rect(
            center=(food_center_x, food_center_y)
        )
        surface.blit(food_text, food_rect)
        return surface, food_rect
    
    def _game_over_screen(self, 
                          surface: pygame.Surface,
                          board_rect: pygame.Rect) -> Tuple[pygame.Surface, pygame.Rect]:
        overlay = pygame.Surface((self.window_width, self.window_height))
        overlay.set_alpha(180)
        overlay.fill(Colour[self.ui_config["GAME_OVER_LABEL"]["FILL"]["COLOUR"]].value)
        surface.blit(overlay, (0, 0))
        
        game_over_text = self.font_game_over.render(
            f"{self.ui_config['GAME_OVER_LABEL']['TEXT']}\nFinal Score: {self.score}",
            True,
            Colour[self.ui_config['GAME_OVER_LABEL']['FONT']['COLOUR']].value
        )
        game_over_rect = game_over_text.get_rect(
            center=board_rect.center
        )
        surface.blit(game_over_text, game_over_rect)
        return surface, game_over_rect
    
    def _update_score(self, new_score: int) -> None:
        if self.score != new_score:
            self.score = new_score
    
    def _update_snake(self, new_snake: Snake) -> None:
        if self.snake != new_snake:
            self.snake = new_snake
    
    def _update_food(self, new_food: Food) -> None:
        if self.food != new_food:
            self.food = new_food
            
    def update_components(self,
                          new_score: Optional[int],
                          new_snake: Optional[Snake],
                          new_food: Optional[Food]
                          ) -> None:
        if new_score:
            self._update_score(new_score)
            logger.debug(f"Updated score to {new_score}")
        if new_snake:
            self._update_snake(new_snake)
            logger.debug("Updated snake position")
        if new_food:
            self._update_food(new_food)
            logger.debug(f"Updated food position to {new_food.position}")
            
    def full_render(self, is_game_over: bool = False) -> None:
        if not self._is_initialized:
            self._initialize_display()
        
        self.screen.fill(Colour[self.ui_config["BG_COLOUR"]].value)
        self.screen, self.title_rect = self._draw_title(self.screen)
        self.screen, self.score_rect = self.__draw_scores_food_lifetime_labels(self.screen)
        self.screen, self.board_rect = self._draw_board(self.screen, 
                                                      score_rect=self.score_rect)
        
        self.screen, self.snake_rect = self._draw_snake(self.screen, board_rect=self.board_rect)
        if self.food:
            self.screen, self.food_rect = self._draw_food(self.screen, board_rect=self.board_rect)
        if is_game_over:
            self.screen, self.game_over_rect = self._game_over_screen(self.screen, board_rect=self.board_rect)
        pygame.display.flip()
    
    def headless_render(self, is_game_over: bool = False) -> Tuple[np.ndarray, np.ndarray]:
        if not self._is_initialized:
            self._initialize_display()
        
        self.headless_surface.fill(Colour[self.ui_config["BG_COLOUR"]].value)
        self.headless_surface, self.title_rect = self._draw_title(self.headless_surface)
        self.headless_surface, self.score_rect = self.__draw_scores_food_lifetime_labels(self.headless_surface)
        self.headless_surface, self.board_rect = self._draw_board(self.headless_surface, 
                                                      score_rect=self.score_rect)
        self.headless_surface, self.snake_rect = self._draw_snake(self.headless_surface, board_rect=self.board_rect)
        if self.food:
            self.headless_surface, self.food_rect = self._draw_food(self.headless_surface, board_rect=self.board_rect)
        
        if is_game_over:
            self.headless_surface, self.game_over_rect = self._game_over_screen(self.headless_surface, board_rect=self.board_rect)
        pygame.display.flip()
        
        window_rgb_array = pygame.surfarray.array3d(self.headless_surface)
        board_rgb_array = window_rgb_array[
            self.board_rect.left:self.board_rect.right, 
            self.board_rect.top:self.board_rect.bottom, 
            : 
        ]
        window_rgb_array = np.transpose(window_rgb_array, (2, 1, 0))
        board_rgb_array = np.transpose(board_rgb_array, (2, 1, 0))
        return window_rgb_array, board_rgb_array
    
    def close(self):
        logger.debug("Closing pygame UI resources")
        pygame.quit()
