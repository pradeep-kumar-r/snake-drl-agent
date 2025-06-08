from pathlib import Path
from dotenv import load_dotenv
import yaml
from .config import Config
from .data_config import DataConfig
from .training_config import TrainingConfig
from .logs_config import LogsConfig
from .model_config import ModelConfig
from .game_config import GameConfig


class ConfigManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            load_dotenv()
            with open("config.yaml", "r", encoding="utf-8") as file:
                cls.config_yaml = yaml.safe_load(file)
            cls._set_config()
        return cls._instance
    
    @classmethod
    def _set_config(cls):
        cls.config = Config(
            # data_config=DataConfig(
            #     data_path=Path(cls.config_yaml["DATA_CONFIG"]["DATA_PATH"])
            #     ),
            data_config=None,
            training_config=None,
            logs_config=None,
            model_config=None,
            game_config=None
        )
    
    @classmethod
    def get_config(cls):
        return cls.config
    

# Testing configs
if __name__ == "__main__":
    config_manager = ConfigManager()
    print(config_manager.get_config())
    