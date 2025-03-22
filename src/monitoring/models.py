from pydantic import BaseModel

class OptionPosition(BaseModel):
    """A class representing an option position in a trading portfolio.
    This class stores essential information about an options contract position,
    including the underlying symbol, expiration date, strike price, option type,
    position size and trading strategy.
    Attributes:
        symbol (str): The ticker symbol of the underlying asset
        expiry (str): The expiration date of the option
        strike (float): The strike price of the option
        right (str): The option type ('C' for call, 'P' for put)
        quantity (int): Number of contracts, positive for long positions, 
                       negative for short positions
        strategy (str, optional): The trading strategy this position belongs to
    Methods:
        key(): Returns a tuple of (symbol, expiry, strike, right) that uniquely
              identifies this option contract
    """
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


class Portfolio(BaseModel):
    __root__: dict[str, dict[str, Strategy]]

