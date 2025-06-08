from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class LogsConfig:
    logs_folder_path: Path
    log_level: str