from pathlib import Path
import yaml


class ConfigManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            with open("config.yaml", "r", encoding="utf-8") as file:
                cls.config = yaml.safe_load(file)
                cls._set_config()
        return cls._instance

    @classmethod
    def _set_config(cls):
        cls.data_config = cls.config["DATA_CONFIG"]
        cls.data_config["DATA_FOLDER_PATH"] = Path(cls.data_config["DATA_FOLDER_PATH"])
        
        cls.training_config = cls.config["TRAINING_CONFIG"]
        
        cls.logs_config = cls.config["LOGS_CONFIG"]
        cls.logs_config["LOGS_FOLDER_PATH"] = Path(cls.logs_config["LOGS_FOLDER_PATH"])
        
        cls.model_config = cls.config["MODEL_CONFIG"]
        cls.model_config["MODELS_FOLDER_PATH"] = Path(cls.model_config["MODELS_FOLDER_PATH"])
        
        cls.game_config = cls.config["GAME_CONFIG"]
    
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

config = ConfigManager()

# Testing configs
if __name__ == "__main__":
    print(config.get_data_config())
    