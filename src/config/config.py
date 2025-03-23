from pathlib import Path
from typing import Optional, Set
import yaml
from pydantic_settings import BaseSettings
from pydantic import field_validator, BaseModel


class AlertConfig(BaseModel):
    logging_level: str = 'INFO'
    polling_interval: int = 15
    inventory_file: str = 'inventory.yaml'
    low_threshold: float = 4500
    high_threshold: float = 5500
    delta_threshold: float = 0.5
    gamma_threshold: Optional[float] = None
    theta_threshold: Optional[float] = None
    watched_strikes: Set[int] = {5100, 5200, 5300}

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

    @field_validator('watched_strikes', mode='before')
    def parse_watched_strikes(cls, v):
        if isinstance(v, str):
            return {int(x.strip()) for x in v.split(',')}
        return v

