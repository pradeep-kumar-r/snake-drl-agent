import tkinter as tk
from tkinter import Canvas
from src.config import config


class Board:
    def __init__(self,
                 board_width: int=config.get_game_config().BOARD_WIDTH,
                 board_height: int=config.get_game_config().BOARD_HEIGHT):
        self.root = tk.Tk()
        self.root.title("Snake Game")
        self.canvas = Canvas(self.root, 
                             width=board_width, 
                             height=board_height)
        self.canvas.pack()
        