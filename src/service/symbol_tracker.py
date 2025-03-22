from ib_insync import Index, Stock, Option, Future

class SymbolTracker:
    """
    Usage:
    spy = SymbolTracker(ib, "SPY", sec_type="STK")
    price = spy.get_price()
    opt = spy.build_option("20250419", 450, "C")
    """
    def __init__(self, ib, symbol: str, exchange: str = 'SMART', sec_type: str = 'IND'):  # IND for index, STK for stock, ETF, FUT
        self.ib = ib
        self.symbol = symbol
        self.sec_type = sec_type.upper()

        if self.sec_type == 'IND':
            self.contract = Index(symbol, exchange)
        elif self.sec_type in ['STK', 'ETF']:
            self.contract = Stock(symbol, exchange, currency='USD')
        elif self.sec_type == 'FUT':
            # Simplified contract for futures; may need expansion
            self.contract = Future(symbol=symbol, exchange=exchange, currency='USD')
        else:
            raise ValueError(f"Unsupported security type: {self.sec_type}")

        self.ib.qualifyContracts(self.contract)
        self.ticker = self.ib.reqMktData(self.contract, '', False, False)

    def get_price(self):
        self.ib.sleep(1.5)
        return self.ticker.last or self.ticker.close

    def get_option_chain(self):
        chains = self.ib.reqSecDefOptParams(self.contract.symbol, '', self.contract.secType, self.contract.conId)
        return chains[0] if chains else None

    def build_option(self, expiry, strike, right):
        return Option(self.symbol, expiry, strike, right, 'SMART')
