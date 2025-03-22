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

    def get_option_chain(self, right_filter=None, expiry_range=None):
        chains = self.ib.reqSecDefOptParams(
            self.contract.symbol, '', self.contract.secType, self.contract.conId)
        if not chains:
            return None

        chain = chains[0]

        if right_filter:
            chain.rights = [r for r in chain.rights if r in right_filter]

        if expiry_range:
            start_date, end_date = expiry_range
            chain.expirations = {
                exp for exp in chain.expirations
                if start_date <= datetime.strptime(exp, "%Y%m%d").date() <= end_date
            }

        return chain

    def build_option(self, expiry, strike, right):
        return Option(self.symbol, expiry, strike, right, 'SMART')

