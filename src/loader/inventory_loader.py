import json
from pathlib import Path
from typing import Optional, Set
import yaml

from src.model.models import OptionPosition, Portfolio

class InventoryLoader:
    @staticmethod
    def load(portfolio: Portfolio) -> list[OptionPosition]:
        inventory = []
        for strategies in portfolio.root.values():
            for strategy in strategies.strategies:
                for option in strategy.options:
                    inventory.append(option)
        return inventory

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