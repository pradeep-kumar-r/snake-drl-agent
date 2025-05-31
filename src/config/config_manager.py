from dataclasses import dataclass
from pathlib import Path
import os
from dotenv import load_dotenv
import yaml


@dataclass(frozen=True)
class DataDownloaderConfig:
    kaggle_dataset_path: Path
    data_folder_path: Path
    kaggle_user: str
    kaggle_key: str
    train_data_folder_path: Path
    val_data_folder_path: Path
    test_data_folder_path: Path
    train_split: float
    val_split: float


@dataclass(frozen=True)
class DataPipelineConfig:
    data_downloader_config: DataDownloaderConfig
    data_folder_path: Path
    images_path: Path
    batch_size: int
    dataset_path: Path
    train_data_folder_path: Path
    val_data_folder_path: Path
    test_data_folder_path: Path

    
@dataclass(frozen=True)
class ArtefactsConfig:
    artefacts_path: Path


@dataclass(frozen=True)
class ModelTrainingConfig:
    num_epochs: int
    learning_rate: float
    batch_size: int
    
    
@dataclass(frozen=True)
class TrainingPipelineConfig:
    model_training_config: ModelTrainingConfig
    artefacts_config: ArtefactsConfig
    train_dataset_path: Path
    val_dataset_path: Path
    test_dataset_path: Path
   

@dataclass(frozen=True)
class LogsConfig:
    logs_folder_path: Path

 

# Singleton config manager
class ConfigManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            load_dotenv()
            with open("config.yaml", "r") as file:
                cls.config_yaml = yaml.safe_load(file)
            cls._set_config()
        return cls._instance
    
    @classmethod
    def _set_config(cls):
        data_downloader_config = DataDownloaderConfig(
            kaggle_dataset_path=Path(cls.config_yaml['kaggle_dataset_path']),
            data_folder_path=Path(cls.config_yaml['data_folder_path']),
            kaggle_user=os.getenv("KAGGLE_USER"),
            kaggle_key=os.getenv("KAGGLE_KEY"),
            train_data_folder_path=Path(cls.config_yaml['train_data_folder_path']),
            val_data_folder_path=Path(cls.config_yaml['val_data_folder_path']),
            test_data_folder_path=Path(cls.config_yaml['test_data_folder_path']),
            train_split=cls.config_yaml['train_split'],
            val_split=cls.config_yaml['val_split']
        )
        data_pipeline_config = DataPipelineConfig(
            data_downloader_config=data_downloader_config,
            data_folder_path=Path(cls.config_yaml['data_folder_path']),
            images_path=Path(cls.config_yaml['images_folder_path']),
            batch_size=cls.config_yaml['batch_size'],
            dataset_path=Path(cls.config_yaml['dataset_path']),
            train_data_folder_path=Path(cls.config_yaml['train_data_folder_path']),
            val_data_folder_path=Path(cls.config_yaml['val_data_folder_path']),
            test_data_folder_path=Path(cls.config_yaml['test_data_folder_path'])
        )
        artefacts_config = ArtefactsConfig(
            artefacts_path=Path(cls.config_yaml['artefacts_folder_path'])
        )
        model_training_config = ModelTrainingConfig(
            num_epochs=cls.config_yaml['num_epochs'],
            learning_rate=cls.config_yaml['learning_rate'],
            batch_size=cls.config_yaml['batch_size']
        )
        training_pipeline_config = TrainingPipelineConfig(
            model_training_config=model_training_config,
            artefacts_config=artefacts_config,
            train_dataset_path=Path(cls.config_yaml['train_data_folder_path']) / "train_data.pt",
            val_dataset_path=Path(cls.config_yaml['val_data_folder_path']) / "val_data.pt",
            test_dataset_path=Path(cls.config_yaml['test_data_folder_path']) / "test_data.pt"
        )
        logs_config = LogsConfig(
            logs_folder_path=Path(cls.config_yaml['logs_folder_path'])
        )
        cls.config = Config(
            data_downloader_config=data_downloader_config,
            data_pipeline_config=data_pipeline_config,
            artefacts_config=artefacts_config,
            model_training_config=model_training_config,
            training_pipeline_config=training_pipeline_config,
            logs_config=logs_config
        )
    
    @classmethod
    def get_config(cls):
        return cls.config
    

# Testing configs
if __name__ == "__main__":
    config_manager = ConfigManager()
    print(config_manager.get_config())
    