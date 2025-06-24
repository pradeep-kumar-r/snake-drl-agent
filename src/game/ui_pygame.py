from typing import Dict, Any, Optional, List
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
        self.font_legend: Optional[pygame.font.Font] = None
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
        self.font_legend = pygame.font.SysFont(
            self.ui_config["LEGEND"]["FONT"]["NAME"], 
            self.ui_config["LEGEND"]["FONT"]["SIZE"]
        )
        self.font_game_over = pygame.font.SysFont(
            self.ui_config["GAME_OVER"]["FONT"]["NAME"], 
            self.ui_config["GAME_OVER"]["FONT"]["SIZE"]
        )
    
    def _initialize_display(self) -> None:
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption(self.ui_config["TITLE"]["TEXT"])
        self._initialize_fonts()
        self.headless_surface = pygame.Surface((self.window_width, self.window_height))
        self._is_initialized = True
    
    def _draw_title(self, 
                    surface: pygame.Surface, 
                    center_y: Optional[int] = None) -> pygame.Rect:
        if center_y is None:
            center_y = self.ui_config['TITLE']['TOP_PADDING']
        title_text = self.font_title.render(
            f"{self.ui_config['TITLE']['TEXT']}: Episode {self.episode}",
            True,
            Colour(self.ui_config['TITLE']['COLOUR']).value,
        )
        title_rect = title_text.get_rect(
            center=(self.window_width // 2, center_y)
        )
        surface.blit(title_text, title_rect)
        
        return title_rect
    
    def _draw_score_labels(self, 
                           surface: pygame.Surface,
                           bottom_y: Optional[int] = None,
                           ) -> pygame.Rect:
        if bottom_y is None:
            bottom_y = self.ui_config['SCORE']['BOTTOM_PADDING']
        score_text = self.font_score.render(
            f"Current Score: {self.score}\nHigh Score: {self.high_score}",
            True,
            Colour(self.ui_config["SCORE"]["COLOUR"]).value,
        )
        score_rect = score_text.get_rect(
            bottomcenter=(self.window_width // 4, bottom_y)
        )
        surface.blit(score_text, score_rect)
        
        return score_rect
        
    def _draw_food_lifetime_label(self, 
                                  surface: pygame.Surface,
                                  bottom_y: Optional[int] = None,
                                  ) -> pygame.Rect:
        if bottom_y is None:
            bottom_y = self.ui_config['SCORE']['BOTTOM_PADDING']
        lifetime_text = "-"
        if (self.food and 
            hasattr(self.food, 'remaining_steps') and 
            self.food.remaining_steps is not None):
            lifetime_text = str(self.food.remaining_steps)
        
        food_lifetime_text = self.font_score.render(
            f"Food Lifetime:\n{lifetime_text}",
            True,
            Colour(self.ui_config["FOOD_LABEL"]["COLOUR"]).value
        )
        food_lifetime_rect = food_lifetime_text.get_rect(
            bottomcenter=(self.window_width * 3 // 4, bottom_y)
        )
        surface.blit(food_lifetime_text, food_lifetime_rect)
        
        return food_lifetime_rect
    
    def _draw_board(self, 
                    surface: pygame.Surface, 
                    title_rect: Optional[pygame.Rect] = None,
                    score_rect: Optional[pygame.Rect] = None,
                    food_lifetime_rect: Optional[pygame.Rect] = None) -> pygame.Rect:
        surface.fill(Colour('black').value)
        pad = self.ui_config['BOARD']['PADDING']
        board_topleft_x, board_topleft_y = (pad, 
                                            title_rect.bottom + pad if title_rect else pad
        )
        board_bottomright_x, board_bottomright_y = (self.window_width - pad, 
                                                    min(score_rect.bottom, food_lifetime_rect.bottom) - pad
        )
        
        # Draw bounding box
        board_rect = pygame.draw.rect(
            surface,
            Colour('white').value,
            (board_topleft_x, board_topleft_y, board_bottomright_x - board_topleft_x, board_bottomright_y - board_topleft_y),
            3
        )
        
        # Draw grid lines
        
        for i in range(board_topleft_x + self.cell_size, board_bottomright_x + 1, self.cell_size):
            pygame.draw.line(
                surface,
                Colour('light_grey').value,
                (i, board_topleft_y),
                (i, board_bottomright_y),
                1
            )
        
        for i in range(board_topleft_y + self.cell_size, board_bottomright_y + 1, self.cell_size):
            pygame.draw.line(
                surface,
                Colour('light_grey').value,
                (board_topleft_x, i),
                (board_bottomright_x, i),
                1
            )
            
        return board_rect
    
    def _draw_snake(self, 
                    surface: pygame.Surface, 
                    board_rect: pygame.Rect) -> List[pygame.Rect]:
        snake_pygame_objects: List[pygame.Rect] = []
        # Draw head
        head_x, head_y = self.snake.body[0]
        head_y1 = self.board_height - head_y
        head_top_y = board_rect.top + head_y1 * self.cell_size
        head_center_y = board_rect.top + head_y1 * self.cell_size + self.cell_size // 2
        head_bottom_y = board_rect.top + head_y1 * self.cell_size + self.cell_size
        head_left_x = board_rect.left + head_x * self.cell_size
        head_right_x = board_rect.left + head_x * self.cell_size + self.cell_size
        head_polygon = pygame.draw.polygon(
            surface,
            Colour(self.ui_config["SNAKE"]["HEAD"]["FILL"]).value,
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
                Colour(self.ui_config["SNAKE"]["BODY"]["FILL"]).value,
                (body_center_x, body_center_y),
                body_radius
            )
            snake_pygame_objects.append(body_circle)
        
        return snake_pygame_objects
    
    def _draw_food(self, 
                   surface: pygame.Surface, 
                   board_rect: pygame.Rect) -> pygame.Rect:
        if not self.food:
            return
        food_x, food_y = self.food.position
        food_y = self.board_height - food_y
        food_center_x, food_center_y = (board_rect.left + food_x * self.cell_size + self.cell_size // 2, 
                                        board_rect.top + food_y * self.cell_size + self.cell_size // 2)
        is_super_food = isinstance(self.food, SuperFood)
        fill_color = Colour(self.ui_config["FOOD"]["SUPER"]["FILL"]).value if is_super_food else Colour(self.ui_config["FOOD"]["SIMPLE"]["FILL"]).value
        symbol = self.ui_config["FOOD"]["SUPER"]["SYMBOL"] if is_super_food else self.ui_config["FOOD"]["SIMPLE"]["SYMBOL"]
        font_name = self.ui_config["FOOD"]["SUPER"]["FONT"]["NAME"] if is_super_food else self.ui_config["FOOD"]["SIMPLE"]["FONT"]["NAME"]
        font_size = self.ui_config["FOOD"]["SUPER"]["FONT"]["SIZE"] if is_super_food else self.ui_config["FOOD"]["SIMPLE"]["FONT"]["SIZE"]
        font_color = Colour(self.ui_config["FOOD"]["SUPER"]["FONT"]["COLOUR"]).value if is_super_food else Colour(self.ui_config["FOOD"]["SIMPLE"]["FONT"]["COLOUR"]).value
        
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
        
        return food_rect
    
    def _game_over_screen(self, 
                          surface: pygame.Surface,
                          board_rect: pygame.Rect) -> pygame.Rect:
        overlay = pygame.Surface((self.window_width, self.window_height))
        overlay.set_alpha(180)
        overlay.fill(Colour(self.ui_config["GAME_OVER_LABEL"]["FILL"]["COLOUR"]).value)
        surface.blit(overlay, (0, 0))
        
        game_over_text = self.font_game_over.render(
            f"{self.ui_config['GAME_OVER_LABEL']['TEXT']}\nFinal Score: {self.score}",
            True,
            Colour(self.ui_config['GAME_OVER_LABEL']['FONT']['COLOUR']).value
        )
        game_over_rect = game_over_text.get_rect(
            center=board_rect.center
        )
        surface.blit(game_over_text, game_over_rect)
        
        return game_over_rect
    
    def _update_scores(self, new_score: int) -> pygame.Rect:
        # This is handled directly in the env class directly
        if self.score == new_score:
            return
        self.score = new_score
        return self._draw_score_labels(self.screen)
    
    def _update_snake(self):
        # This is handled directly in the env class directly
        pass
    
    def _update_food(self):
        # This is handled directly in the env class directly
        pass
    
    def _update_food_lifetime(self):
        # This is handled directly in the env class directly
        pass
    
    def full_render(self, is_game_over=False) -> None:
        if not self._is_initialized:
            self._initialize_display()
        
        title_rect = self._draw_title(self.screen)
        food_lifetime_rect = self._draw_food_lifetime_label(self.screen)
        score_rect = self._draw_score_labels(self.screen)
        board_rect = self._draw_board(self.screen, 
                                      title_rect=title_rect,
                                      score_rect=score_rect,
                                      food_lifetime_rect=food_lifetime_rect
                                      )
        snake_rect = self._draw_snake(self.screen, board_rect=board_rect)
        
        if self.food:
            food_rect = self._draw_food(self.screen, board_rect=board_rect)
        
        if is_game_over:
            game_over_rect = self._game_over_screen(self.screen, board_rect=board_rect)
        
        pygame.display.flip()
    
    def headless_render(self, is_game_over=False) -> np.ndarray:
        if not self._is_initialized:
            self._initialize_display()
        
        if self.headless_surface is None:
            self.headless_surface = pygame.Surface((self.window_width, self.window_height))
        
        title_rect = self._draw_title(self.headless_surface)
        food_lifetime_rect = self._draw_food_lifetime_label(self.headless_surface)
        score_rect = self._draw_score_labels(self.headless_surface)
        board_rect = self._draw_board(self.headless_surface, 
                                      title_rect=title_rect,
                                      score_rect=score_rect,
                                      food_lifetime_rect=food_lifetime_rect
                                      )
        snake_rect = self._draw_snake(self.headless_surface, board_rect=board_rect)
        
        if self.food:
            food_rect = self._draw_food(self.headless_surface, board_rect=board_rect)
        
        if is_game_over:
            game_over_rect = self._game_over_screen(self.headless_surface, board_rect=board_rect)
        
        # Convert surface to numpy array
        rgb_array = pygame.surfarray.array3d(self.headless_surface)
        rgb_array = np.transpose(rgb_array, (1, 0, 2))
        
        return rgb_array
    
    def close(self):
        """Clean up Pygame resources."""
        pygame.quit()
