from dataclasses import dataclass
from pathlib import Path
from .artefacts_config import ArtefactsConfig
from .model_training_config import ModelTrainingConfig
from .logs_config import LogsConfig


@dataclass(frozen=True)
class Config:
    artefacts_config: ArtefactsConfig
    model_training_config: ModelTrainingConfig
    logs_config: LogsConfig