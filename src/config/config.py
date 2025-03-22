import json
from pathlib import Path
from pydantic import BaseSettings
from typing import Set, Optional

class AlertConfig(BaseSettings):
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
