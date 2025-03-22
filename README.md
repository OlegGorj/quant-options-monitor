# quant-options-monitor
Quantitative monitoring tool

## Description
The repository contains a tool to monitor options data. The tool is designed to be used by quantitative analysts to monitor options data and to generate alerts when certain conditions are met.
This is experimantal project and is not intended to be used in production.


## Running the application locally

Setup virtual environment:
```bash
python3 -m venv environment ; source environment/bin/activate
```

Install dependencies:
```bash
pip3 install -r requirements.txt
```

# How to use this project

## `IBClient` class

Connecting to TWS or IB Gateway with IBClient
```python
from service.ib_client import IBClient

# Step 1: Instantiate the client
ib_client = IBClient()
# Step 2: Connect to TWS or Gateway using environment variables
ib = ib_client.connect()

# Step 3: Now use `ib` just like a normal ib_insync client
print("Connected to IBKR:", ib.isConnected())
```

Required Environment Variables

```bash
IB_HOST=127.0.0.1
IB_PORT=7497
IB_CLIENT_ID=42
IB_TIMEOUT=10
IB_RETRIES=5
IB_RETRY_DELAY=2
```

### How It Works

- `IBClient.__init__()` reads environment variables and stores them.
- `IBClient.connect()` establishes a connection to TWS or `IB` Gateway and returns a live `IB` instance.
- This IB instance is fully compatible with all `ib_insync` functionality, such as:
    - Submitting orders
    - Requesting market data
    - Requesting option chains
    - Managing portfolio positions
- Reconnect logic: configurable number of retries (IB_RETRIES) and delay (IB_RETRY_DELAY).
- Timeout control: via IB_TIMEOUT.


## `SymbolTracker` class

The `SymbolTracker` class is used to track the options data for a given symbol. The class is initialized with the symbol name and the options data is updated using the `update` method.

`SymbolTracker` has been enhanced to support:
- Continuous futures via a continuous=True flag.
- Futures options (FOPs) via dynamic creation based on sec_type == 'FUT'.
- Maintains compatibility with index, equity, and ETF symbols.

Usage examples:
```python
from symbol_tracker import SymbolTracker

# Continuous futures
es = SymbolTracker(ib, "ES", sec_type="FUT", exchange="GLOBEX", continuous=True)

# FOP contract from future
fop = es.build_option("20240419", 4200, "C")
```

### Track SPX Index and Fetch Option Chain

- Tracks the SPX index on the CBOE.
- Fetches current market price.
- Retrieves the full option chain (calls and puts, all expirations).

```python
spx = SymbolTracker(ib, symbol="SPX", sec_type="IND", exchange="CBOE")
price = spx.get_price()
chain = spx.get_option_chain()
```

### Track SPY ETF with Expiration and Call Filter

- Tracks SPY, an ETF.
- Retrieves only call options expiring in the next 30 days.

```python
spy = SymbolTracker(ib, symbol="SPY", sec_type="ETF", exchange="SMART")
price = spy.get_price()

from datetime import date, timedelta
today = date.today()
chain = spy.get_option_chain(
    right_filter={"C"},  # Only call options
    expiry_range=(today, today + timedelta(days=30))  # Next 30 days
)
```

### Track ES Futures (E-Mini S&P 500) and Build FOP Option

Tracks the continuous ES futures contract on GLOBEX.
Builds and qualifies a put option on the future (a FOP).

```python
es = SymbolTracker(ib, symbol="ES", sec_type="FUT", exchange="GLOBEX", continuous=True)
price = es.get_price()

# Build a futures option (FOP) manually
fop = es.build_option(expiry="20240419", strike=4500, right="P")
ib.qualifyContracts(fop)
```

### Track AAPL Stock and Access Full Chain

Tracks Apple stock.
Gets current price and complete option chain.

```python
aapl = SymbolTracker(ib, symbol="AAPL", sec_type="STK", exchange="SMART")
price = aapl.get_price()
chain = aapl.get_option_chain()
```

### Filter FOP Chain by Puts and Near-Term Expiration

Tracks natural gas futures (non-continuous).
Filters for put options expiring within 10 days.

```python
from datetime import date, timedelta
today = date.today()

ng = SymbolTracker(ib, symbol="NG", sec_type="FUT", exchange="NYMEX", continuous=False)
price = ng.get_price()
chain = ng.get_option_chain(
    right_filter={"P"},
    expiry_range=(today, today + timedelta(days=10))
)
```


