from collections import defaultdict
import statistics

class OptionMonitor:
    def __init__(self):
        self.snapshot_log = []
        self.iv_history = defaultdict(list)

    def get_iv_zscore(self, history, current_iv):
        if len(history) < 5 or current_iv is None:
            return None
        mean = statistics.mean(history)
        stdev = statistics.stdev(history)
        if stdev == 0:
            return 0
        return round((current_iv - mean) / stdev, 2)
    
    def get_iv_percentile(self, history, current_iv):
        if len(history) < 5 or current_iv is None:
            return None
        return round(sum(iv < current_iv for iv in history) / len(history), 2)
    
    def get_iv_rank(self, history, current_iv):
        if len(history) < 5 or current_iv is None:
            return None
        return round(sum(iv < current_iv for iv in history) / len(history), 2)
    
    