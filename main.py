from ib_insync import *
from datetime import datetime, timedelta
import pandas as pd
import time
import logging
import yaml

from src.model.models import OptionPosition, Portfolio
from src.monitoring.monitor import OptionMonitor
from src.alerting.alerts import AlertAssetEngine, AlertOptionEngine
from src.config.config import AlertConfig
from src.loader.inventory_loader import InventoryLoader
from src.client.ib_client import IBClient
from src.service.symbol_tracker import SymbolTracker

# Configure logging
logging.basicConfig(
    level=getattr(logging, AlertConfig().logging_level.upper(), logging.INFO),
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("monitor.log"),
        logging.StreamHandler()
    ]
)

# Initialize helpers
monitor = OptionMonitor()
config = AlertConfig()
asset_alert_engine = AlertAssetEngine(low_threshold=config.low_threshold, high_threshold=config.high_threshold)
option_alert_engine = AlertOptionEngine(
    delta_threshold=config.delta_threshold,
    gamma_threshold=config.gamma_threshold,
    theta_threshold=config.theta_threshold,
    watched_strikes=config.watched_strikes
)

# Load inventory from config-specified file
portfolio = Portfolio(**yaml.safe_load(open(config.inventory_file)))
print(f'>> loaded portfolio: {type(portfolio)}/{portfolio}')

for instrument in portfolio.root:
    print(f'>>> loaded instrument: {instrument}')

for strategies in portfolio.root.values():
    print(f'>>> loaded strategies: {type(strategies)}/{strategies}')
    for strategy in strategies.strategies:
        print(f'>>>> loaded strategy: {type(strategy)}/{strategy}')
        for option in strategy.options:
            print(f'>>>>> loaded option: {type(option)}/{option}')

inventory = InventoryLoader().load(portfolio)
print(f'>> loaded inventory: {type(inventory)}/{inventory}')

# Connect
ib_client = IBClient()
ib = ib_client.connect()

tsla_contract = Stock('TSLA', 'SMART', 'USD')
tsla_data = ib.reqMktData(tsla_contract)
print(f'>> TSLA data: {tsla_data}')

# Setup SPX index
# spx = SymbolTracker(ib, 'SPX')
# underlying_price = spx.get_price()
# print(f'Underlying price: {underlying_price}')
# chain = spx.get_option_chain()
# print(f'Option chain: {chain}')


# Filter expirations (0-60 days)
# today = datetime.now().date()
# valid_expirations = [
#     exp for exp in chain.expirations
#     if 0 <= (datetime.strptime(exp, '%Y%m%d').date() - today).days <= 60
# ]

# Determine OTM strikes
# ib.sleep(2)
# underlying_price = spx_ticker.last or spx_ticker.close
# otm_calls = [strike for strike in chain.strikes if strike > underlying_price]
# otm_puts = [strike for strike in chain.strikes if strike < underlying_price]

# Prepare contracts
# contracts = []
# for exp in valid_expirations:
#     for strike in otm_calls:
#         contracts.append(Option('SPX', exp, strike, 'C', 'SMART'))
#     for strike in otm_puts:
#         contracts.append(Option('SPX', exp, strike, 'P', 'SMART'))
# for pos in inventory:
#     contracts.append(Option(pos.symbol, pos.expiry, pos.strike, pos.right, 'SMART'))

# ib.qualifyContracts(*contracts)
# tickers = ib.reqMktData(contracts, '', True, False)


# Logging loop
# try:
#     logging.info(f"Logging every {config.polling_interval}s with alert triggers (CTRL+C to exit)...")
#     while True:
#         ib.sleep(1.5)
#         underlying_price = spx_ticker.last or spx_ticker.close
#         timestamp = datetime.now().isoformat()
#         snapshot = []

#         for ticker in tickers:
#             contract = ticker.contract
#             greeks = ticker.modelGreeks
#             iv = greeks.impliedVol if greeks else None
#             key = (contract.lastTradeDateOrContractMonth, contract.right, contract.strike)

#             if iv:
#                 monitor.iv_history[key].append(iv)
#                 monitor.iv_history[key] = monitor.iv_history[key][-50:]

#             iv_z = monitor.get_iv_zscore(monitor.iv_history[key], iv)

#             position = inventory_lookup.get((contract.symbol, contract.lastTradeDateOrContractMonth, contract.strike, contract.right))
#             strategy = position.strategy if position else None
#             quantity = position.quantity if position else 0

#             snapshot.append({
#                 'timestamp': timestamp,
#                 'expiration': contract.lastTradeDateOrContractMonth,
#                 'right': contract.right,
#                 'strike': contract.strike,
#                 'bid': ticker.bid,
#                 'ask': ticker.ask,
#                 'last': ticker.last,
#                 'delta': greeks.delta if greeks else None,
#                 'theta': greeks.theta if greeks else None,
#                 'iv': iv,
#                 'iv_zscore': iv_z,
#                 'quantity': quantity,
#                 'strategy': strategy
#             })

#             for alert in asset_alert_engine.check(underlying_price) + option_alert_engine.check(contract, greeks):
#                 logging.warning(alert)

#         monitor.snapshot_log.extend(snapshot)
#         logging.info(f"[{timestamp}] Logged {len(snapshot)} entries")
#         time.sleep(config.polling_interval)

# except KeyboardInterrupt:
#     logging.info("Stopped by user.")

# finally:
#     ib.disconnect()
#     # df = pd.DataFrame(monitor.snapshot_log)
#     # df.to_csv("spx_monitoring_with_alerts.csv", index=False)
#     logging.info("Saved logs to spx_monitoring_with_alerts.csv")

