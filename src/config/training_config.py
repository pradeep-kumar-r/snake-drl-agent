from dataclasses import dataclass
from pathlib import Path
from .artefacts_config import ArtefactsConfig


@dataclass(frozen=True)
class TrainingConfig:
    num_epochs: int
    learning_rate: float
    batch_size: int
    artefacts_config: ArtefactsConfig