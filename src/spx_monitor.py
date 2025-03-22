from ib_insync import *
from datetime import datetime, timedelta
import pandas as pd
import time
from collections import defaultdict
import statistics

# === ALERT CONFIGURATION ===
LOW_THRESHOLD = 4500      # Alert if SPX < 4500
HIGH_THRESHOLD = 5500     # Alert if SPX > 5500
DELTA_ALERT_THRESHOLD = 0.5  # Alert if delta exceeds this value
WATCHED_STRIKES = {5100, 5200, 5300}  # example: strike prices to monitor for delta alerts

# Connect
ib = IB()
ib.connect('127.0.0.1', 7497, clientId=123)

# Define SPX index
spx_index = Index('SPX', 'CBOE')
ib.qualifyContracts(spx_index)

# SPX market data
spx_ticker = ib.reqMktData(spx_index, '', False, False)

# Get option chain
chains = ib.reqSecDefOptParams(spx_index.symbol, '', spx_index.secType, spx_index.conId)
chain = chains[0]

# Expiration filter (0–60 days)
today = datetime.now().date()
valid_expirations = [
    exp for exp in chain.expirations
    if 0 <= (datetime.strptime(exp, '%Y%m%d').date() - today).days <= 60
]

# OTM only
strikes = chain.strikes
ib.sleep(2)  # allow SPX price to come in
underlying_price = spx_ticker.last or spx_ticker.close
otm_calls = [strike for strike in strikes if strike > underlying_price]
otm_puts = [strike for strike in strikes if strike < underlying_price]

# Contracts
contracts = []
for exp in valid_expirations:
    for strike in otm_calls:
        contracts.append(Option('SPX', exp, strike, 'C', 'SMART'))
    for strike in otm_puts:
        contracts.append(Option('SPX', exp, strike, 'P', 'SMART'))

ib.qualifyContracts(*contracts)
tickers = ib.reqMktData(contracts, '', True, False)

# Store logs
snapshot_log = []
iv_history = defaultdict(list)
alerts_triggered = set()

def get_iv_zscore(history, current_iv):
    if len(history) < 5 or current_iv is None:
        return None
    mean = statistics.mean(history)
    stdev = statistics.stdev(history)
    if stdev == 0:
        return 0
    return round((current_iv - mean) / stdev, 2)

# === ALERT CHECK ===
def check_alerts(underlying_price, contract, greeks):
    alerts = []

    # Underlying alerts
    if underlying_price < LOW_THRESHOLD and "under_below" not in alerts_triggered:
        alerts_triggered.add("under_below")
        alerts.append(f"⚠️ SPX dropped below {LOW_THRESHOLD}: {underlying_price}")

    if underlying_price > HIGH_THRESHOLD and "under_above" not in alerts_triggered:
        alerts_triggered.add("under_above")
        alerts.append(f"⚠️ SPX spiked above {HIGH_THRESHOLD}: {underlying_price}")

    # Delta alerts for selected strikes
    if contract.strike in WATCHED_STRIKES and greeks and greeks.delta is not None:
        if greeks.delta > DELTA_ALERT_THRESHOLD:
            key = (contract.lastTradeDateOrContractMonth, contract.right, contract.strike, 'delta')
            if key not in alerts_triggered:
                alerts_triggered.add(key)
                alerts.append(f"⚠️ {contract.right} {contract.strike} delta crossed {DELTA_ALERT_THRESHOLD}: {greeks.delta:.2f}")

    return alerts

# === Logging Loop ===
try:
    print("Logging every 15s with alert triggers (CTRL+C to exit)...")
    while True:
        ib.sleep(1.5)  # allow SPX to update
        underlying_price = spx_ticker.last or spx_ticker.close
        timestamp = datetime.now().isoformat()
        snapshot = []

        for ticker in tickers:
            contract = ticker.contract
            greeks = ticker.modelGreeks

            iv = greeks.impliedVol if greeks else None
            key = (contract.lastTradeDateOrContractMonth, contract.right, contract.strike)

            if iv:
                iv_history[key].append(iv)
                iv_history[key] = iv_history[key][-50:]

            iv_z = get_iv_zscore(iv_history[key], iv)

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
                'iv_zscore': iv_z
            })

            # 🔔 Check and print alerts
            for alert in check_alerts(underlying_price, contract, greeks):
                print(alert)

        snapshot_log.extend(snapshot)
        print(f"[{timestamp}] Logged {len(snapshot)} entries")
        time.sleep(15)

except KeyboardInterrupt:
    print("Stopped by user.")

finally:
    ib.disconnect()
    df = pd.DataFrame(snapshot_log)
    df.to_csv("spx_monitoring_with_alerts.csv", index=False)
    print("Saved logs to spx_monitoring_with_alerts.csv")

