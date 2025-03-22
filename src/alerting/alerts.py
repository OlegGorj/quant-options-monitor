from abc import ABC, abstractmethod

class AlertEngine(ABC):
    def __init__(self):
        self.alerts_triggered = set()

    def has_been_triggered(self, key):
        return key in self.alerts_triggered

    def mark_triggered(self, key):
        self.alerts_triggered.add(key)

    @abstractmethod
    def check(self, *args, **kwargs):
        pass


class AlertAssetEngine(AlertEngine):
    def __init__(self, low_threshold=4500, high_threshold=5500):
        self.low_threshold = low_threshold
        self.high_threshold = high_threshold
        self.alerts_triggered = set()

    def check(self, underlying_price):
        alerts = []
        if underlying_price < self.low_threshold and "under_below" not in self.alerts_triggered:
            self.alerts_triggered.add("under_below")
            alerts.append(f"⚠️ SPX dropped below {self.low_threshold}: {underlying_price}")

        if underlying_price > self.high_threshold and "under_above" not in self.alerts_triggered:
            self.alerts_triggered.add("under_above")
            alerts.append(f"⚠️ SPX spiked above {self.high_threshold}: {underlying_price}")
        return alerts


class AlertOptionEngine(AlertEngine):
    def __init__(self, delta_threshold=0.5, gamma_threshold=None, theta_threshold=None, watched_strikes=None):
        self.delta_threshold = delta_threshold
        self.gamma_threshold = gamma_threshold
        self.theta_threshold = theta_threshold
        self.watched_strikes = watched_strikes or set()
        self.alerts_triggered = set()

    def check(self, contract, greeks):
        alerts = []
        if contract.strike not in self.watched_strikes or not greeks:
            return alerts
        
        if greeks.delta is not None and greeks.delta > self.delta_threshold:
            key = (contract.lastTradeDateOrContractMonth, contract.right, contract.strike, 'delta')
            if not self.has_been_triggered(key):
                self.mark_triggered(key)
                alerts.append(f"⚠️ {contract.right} {contract.strike} delta crossed {self.delta_threshold}: {greeks.delta:.2f}")

        if self.gamma_threshold is not None and greeks.gamma is not None and greeks.gamma > self.gamma_threshold:
            key = (contract.lastTradeDateOrContractMonth, contract.right, contract.strike, 'gamma')
            if not self.has_been_triggered(key):
                self.mark_triggered(key)
                alerts.append(f"⚠️ {contract.right} {contract.strike} gamma crossed {self.gamma_threshold}: {greeks.gamma:.2f}")

        if self.theta_threshold is not None and greeks.theta is not None and greeks.theta < self.theta_threshold:
            key = (contract.lastTradeDateOrContractMonth, contract.right, contract.strike, 'theta')
            if not self.has_been_triggered(key):
                self.mark_triggered(key)
                alerts.append(f"⚠️ {contract.right} {contract.strike} theta dropped below {self.theta_threshold}: {greeks.theta:.2f}")
        return alerts
