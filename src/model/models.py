from pydantic import BaseModel, RootModel

class OptionPosition(BaseModel):
    symbol: str
    expiry: str
    strike: float
    right: str
    quantity: int
    strategy: str = None

    def key(self):
        return (self.symbol, self.expiry, self.strike, self.right)


class Strategy(BaseModel):
    name: str
    options: list[OptionPosition]


class Portfolio(RootModel):
    root: dict[str, dict[str, Strategy]]

class OptionInventoryItem(BaseModel):
    symbol: str
    expiry: str
    strike: float
    right: str
    position: int
    cost_basis: float
    
class OptionInventory(RootModel):
    root: dict[str, list[OptionInventoryItem]]
