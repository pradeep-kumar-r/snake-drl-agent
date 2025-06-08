from dataclasses import dataclass
from .data_config import DataConfig
from .training_config import TrainingConfig
from .logs_config import LogsConfig
from .model_config import ModelConfig
from .game_config import GameConfig


@dataclass(frozen=True)
class Config:
    data_config: DataConfig
    training_config: TrainingConfig
    logs_config: LogsConfig
    model_config: ModelConfig
    game_config: GameConfig