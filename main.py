from ib_insync import *
from datetime import datetime, timedelta
import pandas as pd
import time
import logging

from monitoring.models import OptionPosition
from monitoring.monitor import OptionMonitor
from alerting.alerts import AlertEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("spx_monitor.log"),
        logging.StreamHandler()
    ]
)

# Inventory Setup
inventory = [
    OptionPosition('SPX', '20250419', 5100, 'C', 1, strategy='Bull Call Spread'),
    OptionPosition('SPX', '20250419', 5200, 'C', -1, strategy='Bull Call Spread'),
    OptionPosition('SPX', '20250419', 4900, 'P', 1, strategy='Protective Put'),
]
inventory_lookup = {pos.key(): pos for pos in inventory}

# Connect
ib = IB()
ib.connect('127.0.0.1', 7497, clientId=123)

# Setup SPX index
spx_index = Index('SPX', 'CBOE')
ib.qualifyContracts(spx_index)
spx_ticker = ib.reqMktData(spx_index, '', False, False)

# Get option chain
chains = ib.reqSecDefOptParams(spx_index.symbol, '', spx_index.secType, spx_index.conId)
chain = chains[0]

# Filter expirations (0-60 days)
today = datetime.now().date()
valid_expirations = [
    exp for exp in chain.expirations
    if 0 <= (datetime.strptime(exp, '%Y%m%d').date() - today).days <= 60
]

# Determine OTM strikes
ib.sleep(2)
underlying_price = spx_ticker.last or spx_ticker.close
otm_calls = [strike for strike in chain.strikes if strike > underlying_price]
otm_puts = [strike for strike in chain.strikes if strike < underlying_price]

# Prepare contracts
contracts = []
for exp in valid_expirations:
    for strike in otm_calls:
        contracts.append(Option('SPX', exp, strike, 'C', 'SMART'))
    for strike in otm_puts:
        contracts.append(Option('SPX', exp, strike, 'P', 'SMART'))
for pos in inventory:
    contracts.append(Option(pos.symbol, pos.expiry, pos.strike, pos.right, 'SMART'))

ib.qualifyContracts(*contracts)
tickers = ib.reqMktData(contracts, '', True, False)

# Initialize helpers
monitor = OptionMonitor()
alerter = AlertEngine(watched_strikes={5100, 5200, 5300})

# Logging loop
try:
    logging.info("Logging every 15s with alert triggers (CTRL+C to exit)...")
    while True:
        ib.sleep(1.5)
        underlying_price = spx_ticker.last or spx_ticker.close
        timestamp = datetime.now().isoformat()
        snapshot = []

        for ticker in tickers:
            contract = ticker.contract
            greeks = ticker.modelGreeks
            iv = greeks.impliedVol if greeks else None
            key = (contract.lastTradeDateOrContractMonth, contract.right, contract.strike)

            if iv:
                monitor.iv_history[key].append(iv)
                monitor.iv_history[key] = monitor.iv_history[key][-50:]

            iv_z = monitor.get_iv_zscore(monitor.iv_history[key], iv)

            position = inventory_lookup.get((contract.symbol, contract.lastTradeDateOrContractMonth, contract.strike, contract.right))
            strategy = position.strategy if position else None
            quantity = position.quantity if position else 0

            snapshot.append({
                'timestamp': timestamp,
                'expiration': contract.lastTradeDateOrContractMonth,
                'right': contract.right,
                'strike': contract.strike,
                'bid': ticker.bid,
                'ask': ticker.ask,
                'last': ticker.last,
                'delta': greeks.delta if greeks else None,
                'theta': greeks.theta if greeks else None,
                'iv': iv,
                'iv_zscore': iv_z,
                'quantity': quantity,
                'strategy': strategy
            })

            for alert in alerter.check_alerts(underlying_price, contract, greeks):
                logging.warning(alert)

        monitor.snapshot_log.extend(snapshot)
        logging.info(f"[{timestamp}] Logged {len(snapshot)} entries")
        time.sleep(15)

except KeyboardInterrupt:
    logging.info("Stopped by user.")

finally:
    ib.disconnect()
    df = pd.DataFrame(monitor.snapshot_log)
    df.to_csv("spx_monitoring_with_alerts.csv", index=False)
    logging.info("Saved logs to spx_monitoring_with_alerts.csv")

