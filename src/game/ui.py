from typing import Dict, Any, Optional, Tuple, List
import pygame
import numpy as np
from src.game.food import Food, SuperFood
from src.game.snake import Snake
from src.game.colour import Colour


class UI:
    def __init__(self,
                 ui_config: Dict[str, Any],
                 snake: Snake,
                 episode: int,
                 food: Optional[Food] = None,
                 score: Optional[int] = 0,
                 high_score: Optional[int] = 0):
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
        
        self.window_width: int = self.board_width * self.cell_size
        self.window_height: int = self.board_height * self.cell_size + self.ui_config["EXTRA_WINDOW_HEIGHT"]
        
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
    
    def _draw_title(self, surface: pygame.Surface) -> Tuple[pygame.Surface, pygame.Rect]:
        center_y = self.ui_config['TITLE']['TOP_PADDING']
        title_text = self.font_title.render(
            f"{self.ui_config['TITLE']['TEXT']}: Episode {self.episode}",
            True,
            Colour[self.ui_config['TITLE']['COLOUR']].value,
        )
        title_rect = title_text.get_rect(
            center=(self.window_width // 2, center_y)
        )
        surface.blit(title_text, title_rect)
        return surface, title_rect
    
    def _draw_score_labels(self, surface: pygame.Surface) -> Tuple[pygame.Surface, pygame.Rect]:
        bottom_y = self.ui_config['SCORE']['BOTTOM_PADDING']
        score_text = self.font_score.render(
            f"Current Score: {self.score}\nHigh Score: {self.high_score}",
            True,
            Colour[self.ui_config["SCORE"]["COLOUR"]].value,
        )
        score_rect = score_text.get_rect(
            bottomleft=(0, bottom_y)
        )
        surface.blit(score_text, score_rect)
        return surface, score_rect
        
    def _draw_food_lifetime_label(self, surface: pygame.Surface) -> Tuple[pygame.Surface, pygame.Rect]:
        bottom_y = self.ui_config['SCORE']['BOTTOM_PADDING']
        lifetime_text = "-"
        if (self.food and 
            hasattr(self.food, 'remaining_steps') and 
            self.food.remaining_steps is not None):
            lifetime_text = str(self.food.remaining_steps)
        
        food_lifetime_text = self.font_score.render(
            f"Food Lifetime:\n{lifetime_text}",
            True,
            Colour[self.ui_config["FOOD_LABEL"]["COLOUR"]].value
        )
        food_lifetime_rect = food_lifetime_text.get_rect(
            bottomright=(self.window_width, bottom_y)
        )
        surface.blit(food_lifetime_text, food_lifetime_rect)
        return surface, food_lifetime_rect
    
    def _draw_board(self, 
                    surface: pygame.Surface, 
                    title_rect: pygame.Rect,
                    score_rect: pygame.Rect,
                    food_lifetime_rect: pygame.Rect) -> Tuple[pygame.Surface, pygame.Rect]:
        surface.fill(Colour[self.ui_config['BOARD']['FILL']].value)
        pad = self.ui_config['BOARD']['PADDING']
        board_topleft_x, board_topleft_y = (pad, 
                                            title_rect.bottom + pad
        )
        board_bottomright_x, board_bottomright_y = (self.window_width - pad, 
                                                    min(score_rect.bottom, food_lifetime_rect.bottom) - pad
        )
        
        # Draw bounding box
        board_rect = pygame.draw.rect(
            surface,
            Colour[self.ui_config['BOARD']['BORDER']['FILL']].value,
            (board_topleft_x, board_topleft_y, board_bottomright_x - board_topleft_x, board_bottomright_y - board_topleft_y),
            self.ui_config['BOARD']['BORDER']['THICKNESS']
        )
        
        # Draw grid lines
        
        for i in range(board_topleft_x + self.cell_size, board_bottomright_x + 1, self.cell_size):
            pygame.draw.line(
                surface,
                Colour[self.ui_config['BOARD']['GRID']['FILL']].value,
                (i, board_topleft_y),
                (i, board_bottomright_y),
                self.ui_config['BOARD']['GRID']['THICKNESS']
            )
        
        for i in range(board_topleft_y + self.cell_size, board_bottomright_y + 1, self.cell_size):
            pygame.draw.line(
                surface,
                Colour[self.ui_config['BOARD']['GRID']['FILL']].value,
                (board_topleft_x, i),
                (board_bottomright_x, i),
                self.ui_config['BOARD']['GRID']['THICKNESS']
            )
        return surface, board_rect
    
    def _draw_snake(self, 
                    surface: pygame.Surface, 
                    board_rect: pygame.Rect) -> Tuple[pygame.Surface, List[pygame.Rect]]:
        snake_pygame_objects: List[pygame.Rect] = []
        # Draw head
        head_x, head_y = self.snake.body[0]
        head_y1 = self.board_height - head_y
        head_top_y = board_rect.top + head_y1 * self.cell_size - self.ui_config["SNAKE"]["HEAD"]["STRETCH"]
        head_center_y = board_rect.top + head_y1 * self.cell_size + self.cell_size // 2
        head_bottom_y = board_rect.top + head_y1 * self.cell_size + self.cell_size + self.ui_config["SNAKE"]["HEAD"]["STRETCH"]
        head_left_x = board_rect.left + head_x * self.cell_size - self.ui_config["SNAKE"]["HEAD"]["STRETCH"]
        head_right_x = board_rect.left + head_x * self.cell_size + self.cell_size + self.ui_config["SNAKE"]["HEAD"]["STRETCH"]
        head_polygon = pygame.draw.polygon(
            surface,
            Colour[self.ui_config["SNAKE"]["HEAD"]["FILL"]].value,
            [
               (head_left_x, head_top_y),
               (head_left_x, head_bottom_y),
               (head_right_x, head_center_y)
            ]
        )
        snake_pygame_objects.append(head_polygon)
        
        # Draw body
        body_radius = self.cell_size * 2 // 3
        for x, y in self.snake.body[1:]:
            y1 = self.board_height - y
            body_center_x, body_center_y = (board_rect.left + x * self.cell_size + self.cell_size // 2, 
                                            board_rect.top + y1 * self.cell_size + self.cell_size // 2)
            body_circle = pygame.draw.circle(
                surface,
                Colour[self.ui_config["SNAKE"]["BODY"]["FILL"]].value,
                (body_center_x, body_center_y),
                body_radius
            )
            snake_pygame_objects.append(body_circle)
        return surface, snake_pygame_objects
    
    def _draw_food(self, 
                   surface: pygame.Surface, 
                   board_rect: pygame.Rect) -> Tuple[pygame.Surface, pygame.Rect]:
        if not self.food:
            return
        food_x, food_y = self.food.position
        food_y = self.board_height - food_y
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
        if new_snake:
            self._update_snake(new_snake)
        if new_food:
            self._update_food(new_food)
            
    def full_render(self, is_game_over: bool = False) -> None:
        if not self._is_initialized:
            self._initialize_display()
        else:
            blank_surface = pygame.Surface((self.window_width, self.window_height))
            blank_surface.fill(Colour[self.ui_config["BG_COLOUR"]].value)
            self.screen.blit(blank_surface, (0, 0))
     
        self.screen, self.title_rect = self._draw_title(self.screen)
        self.screen, self.food_lifetime_rect = self._draw_food_lifetime_label(self.screen)
        self.screen, self.score_rect = self._draw_score_labels(self.screen)
        self.screen, self.board_rect = self._draw_board(self.screen, 
                                                        title_rect=self.title_rect,
                                                        score_rect=self.score_rect,
                                                        food_lifetime_rect=self.food_lifetime_rect)
        self.screen, self.snake_rect = self._draw_snake(self.screen, board_rect=self.board_rect)
        if self.food:
            self.screen, self.food_rect = self._draw_food(self.screen, board_rect=self.board_rect)
        if is_game_over:
            self.screen, self.game_over_rect = self._game_over_screen(self.screen, board_rect=self.board_rect)
        pygame.display.flip()
    
    def headless_render(self, is_game_over: bool = False) -> Tuple[np.ndarray, Tuple[int, int]]:
        if not self._is_initialized:
            self._initialize_display()
        else:
            blank_surface = pygame.Surface((self.window_width, self.window_height))
            blank_surface.fill(Colour[self.ui_config["BG_COLOUR"]].value)
            self.headless_surface.blit(blank_surface, (0, 0))
     
        self.headless_surface, self.title_rect = self._draw_title(self.headless_surface)
        self.headless_surface, self.food_lifetime_rect = self._draw_food_lifetime_label(self.headless_surface)
        self.headless_surface, self.score_rect = self._draw_score_labels(self.headless_surface)
        self.headless_surface, self.board_rect = self._draw_board(self.headless_surface, 
                                                        title_rect=self.title_rect,
                                                        score_rect=self.score_rect,
                                                        food_lifetime_rect=self.food_lifetime_rect)
        self.headless_surface, self.snake_rect = self._draw_snake(self.headless_surface, board_rect=self.board_rect)
        if self.food:
            self.headless_surface, self.food_rect = self._draw_food(self.headless_surface, board_rect=self.board_rect)
        if is_game_over:
            self.headless_surface, self.game_over_rect = self._game_over_screen(self.headless_surface, board_rect=self.board_rect)
        pygame.display.flip()
        
        # Convert surface to numpy array
        rgb_array = pygame.surfarray.array3d(self.headless_surface)
        rgb_array = np.transpose(rgb_array, (1, 0, 2))
        
        return rgb_array, (self.window_width, self.window_height)
    
    def close(self):
        pygame.quit()
