from pathlib import Path
import yaml
import numpy as np
from src.game.direction import Direction


class ConfigManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            with open("config.yml", "r", encoding="utf-8") as file:
                cls.config = yaml.safe_load(file)
                cls._set_config()
        return cls._instance

    @classmethod
    def _set_config(cls):
        cls.game_config = cls.config["GAME_CONFIG"]
        cls.data_config = cls.config["DATA_CONFIG"]
        cls.training_config = cls.config["TRAINING_CONFIG"]
        cls.logs_config = cls.config["LOGS_CONFIG"]
        cls.model_config = cls.config["MODEL_CONFIG"]
        cls.ui_config = cls.config["UI_CONFIG"]
        
        cls.data_config["DATA_FOLDER_PATH"] = Path(cls.data_config["DATA_FOLDER_PATH"])
        cls.data_config["GAME_DATA_FOLDER_PATH"] = Path(cls.data_config["GAME_DATA_FOLDER_PATH"])
        cls.data_config["MODEL_DATA_FOLDER_PATH"] = Path(cls.data_config["MODEL_DATA_FOLDER_PATH"])
        cls.data_config["SCORES_FILE_PATH"] = Path(cls.data_config["SCORES_FILE_PATH"])
        cls.data_config["HIGH_SCORE_FILE_PATH"] = Path(cls.data_config["HIGH_SCORE_FILE_PATH"])
        
        cls.logs_config["LOGS_FOLDER_PATH"] = Path(cls.logs_config["LOGS_FOLDER_PATH"])
        
        cls.model_config["MODELS_FOLDER_PATH"] = Path(cls.model_config["MODELS_FOLDER_PATH"])
        cls.model_config["IMAGE_INPUT_SIZE"] = (cls.game_config["BOARD_DIM"] * cls.ui_config["CELL_SIZE_IN_PIXELS"] + cls.ui_config["EXTRA_WINDOW_HEIGHT"],
                                                cls.game_config["BOARD_DIM"] * cls.ui_config["CELL_SIZE_IN_PIXELS"])
        
        cls.ui_config["BOARD_DIM"] = cls.game_config["BOARD_DIM"]
        
        cls.game_config["SNAKE"]["SNAKE_INIT_POS"] = tuple(cls.game_config["SNAKE"]["SNAKE_INIT_POS"])
        
        board_size_in_pix = cls.ui_config["BOARD_DIM"] * cls.ui_config["CELL_SIZE_IN_PIXELS"]
        cls.model_config["IMAGE_INPUT_SIZE"] = (board_size_in_pix, board_size_in_pix)
    
    @classmethod
    def get_data_config(cls):
        return cls.data_config
    
    @classmethod
    def get_training_config(cls):
        return cls.training_config
    
    @classmethod
    def get_logs_config(cls):
        return cls.logs_config
    
    @classmethod
    def get_model_config(cls):
        return cls.model_config
    
    @classmethod
    def get_game_config(cls):
        return cls.game_config
    
    @classmethod
    def get_ui_config(cls):
        return cls.ui_config

config = ConfigManager()


# Testing configs
if __name__ == "__main__":
    game_config = config.get_game_config()
    print(game_config)
    print(game_config["SNAKE"]["SNAKE_INIT_POS"])
    