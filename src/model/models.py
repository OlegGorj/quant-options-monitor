from pydantic import BaseModel, RootModel


class OptionPosition(BaseModel):
    symbol: str
    expiry: str
    strike: float
    right: str
    quantity: int
    strategy: str

class Strategy(BaseModel):
    name: str
    options: list[OptionPosition]

class Strategies(BaseModel):
    strategies: list[Strategy]

class Portfolio(RootModel):
    root: dict[str, Strategies]

