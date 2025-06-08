from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DataConfig:
    data_path: Path