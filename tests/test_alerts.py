import pytest
from alerting.alerts import AlertAssetEngine, AlertOptionEngine

class DummyContract:
    def __init__(self, strike, right, expiry):
        self.strike = strike
        self.right = right
        self.lastTradeDateOrContractMonth = expiry

class DummyGreeks:
    def __init__(self, delta):
        self.delta = delta

def test_asset_alert_below():
    engine = AlertAssetEngine(low_threshold=4500, high_threshold=5500)
    alerts = engine.check(4400)
    assert any("dropped below" in a for a in alerts)

def test_asset_alert_above():
    engine = AlertAssetEngine(low_threshold=4500, high_threshold=5500)
    alerts = engine.check(5600)
    assert any("spiked above" in a for a in alerts)

def test_option_delta_alert():
    contract = DummyContract(5100, 'C', '20250419')
    greeks = DummyGreeks(0.6)
    engine = AlertOptionEngine(delta_threshold=0.5, watched_strikes={5100})
    alerts = engine.check(contract, greeks)
    assert any("delta crossed" in a for a in alerts)

    