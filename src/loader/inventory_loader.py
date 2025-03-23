import json
from pathlib import Path
from typing import Optional, Set
import yaml

from src.model.models import OptionPosition, Portfolio

class InventoryLoader:
    @staticmethod
    def load(path: str) -> list[OptionPosition]:
        ext = Path(path).suffix.lower()
        with open(path) as f:
            if ext == '.json':
                raw = json.load(f)
            elif ext in ['.yml', '.yaml']:
                raw = yaml.safe_load(f)
            else:
                raise ValueError(f"Unsupported inventory file type: {ext}")
        return [OptionPosition(**item) for item in raw]



    logging_level: str = 'INFO'
    polling_interval: int = 15
    inventory_file: str = 'inventory.json'
    low_threshold: float = 4500
    high_threshold: float = 5500
    delta_threshold: float = 0.5
    gamma_threshold: Optional[float] = None
    theta_threshold: Optional[float] = None
    watched_strikes: Set[int] = {5100, 5200, 5300}

    class Config:
        env_file = ".env"