from pydantic import BaseModel

class OptionPosition(BaseModel):
    symbol: str
    expiry: str
    strike: float
    right: str
    quantity: int  # Positive for long, negative for short
    strategy: str = None

    def key(self):
        return (self.symbol, self.expiry, self.strike, self.right)

