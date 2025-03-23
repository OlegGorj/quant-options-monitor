from datetime import datetime
from ib_insync import Index, Stock, Option, Future, FuturesOption as FOP


class SymbolTracker:
    """
    A generic tracker for underlying instruments supporting indexes, equities, ETFs, futures, and their options (including FOPs).
    """

    def __init__(self, ib, symbol: str, exchange: str = 'SMART', sec_type: str = 'IND', continuous: bool = False):
        self.ib = ib
        self.symbol = symbol
        self.sec_type = sec_type.upper()
        self.contract = None

        if self.sec_type == 'IND':
            self.contract = Index(symbol, exchange)
        elif self.sec_type in ['STK', 'ETF']:
            self.contract = Stock(symbol, exchange, currency='USD')
        elif self.sec_type == 'FUT':
            self.contract = Future(symbol=symbol, exchange=exchange, currency='USD', continuous=continuous)
        else:
            raise ValueError(f"Unsupported security type: {self.sec_type}")

        self.ib.qualifyContracts(self.contract)
        self.ticker = self.ib.reqMktData(self.contract, '', False, False)

    def get_price(self):
        self.ib.sleep(1.5)
        return self.ticker.last or self.ticker.close

    def get_option_chain(self, right_filter=None, expiry_range=None):
        chains = self.ib.reqSecDefOptParams(
            self.contract.symbol, '', self.contract.secType, self.contract.conId)
        if not chains:
            return None

        chain = chains[0]

        if right_filter:
            chain.rights = [r for r in chain.rights if r in right_filter]

        if expiry_range:
            from datetime import datetime
            start_date, end_date = expiry_range
            chain.expirations = {
                exp for exp in chain.expirations
                if start_date <= datetime.strptime(exp, "%Y%m%d").date() <= end_date
            }

        return chain

    def build_option(self, expiry, strike, right):
        """
        Build an option contract for the given expiry, strike, and right.
        """
        if self.sec_type == 'FUT':
            return FOP(
                symbol=self.symbol,
                lastTradeDateOrContractMonth=expiry,
                strike=strike,
                right=right,
                exchange=self.contract.exchange,
                currency='USD',
                multiplier='50'
            )
        else:
            return Option(
                symbol=self.symbol,
                lastTradeDateOrContractMonth=expiry,
                strike=strike,
                right=right,
                exchange=self.contract.exchange,
                currency='USD'
            )
    
