from river import base, stats


class MACD(base.Transformer):
    """
    Moving Average Convergence Divergence (MACD) in the spirit of the river package.

    This class computes the MACD line and signal line in an online fashion
    using exponential weighted moving averages (EWMA). It can be used in a river pipeline
    for feature extraction and transformation.

    Parameters:
    - window_slow: int, default=26
        The number of periods for the slow EMA.
    - window_fast: int, default=12
        The number of periods for the fast EMA.
    - window_sign: int, default=9
        The number of periods for the signal EMA of the MACD line.

    """

    def __init__(self, window_slow=26, window_fast=12, window_sign=9):
        self.window_slow = window_slow
        self.window_fast = window_fast
        self.window_sign = window_sign

        # Using river's EWMA to track the slow and fast EMAs, and the signal line
        self.ema_slow = stats.EWMean(alpha=2 / (self.window_slow + 1))
        self.ema_fast = stats.EWMean(alpha=2 / (self.window_fast + 1))
        self.ema_signal = stats.EWMean(alpha=2 / (self.window_sign + 1))

        # To store the current MACD line and signal line
        self.macd_line = None
        self.signal_line = None

    def learn_one(self, x):
        """
        Update the MACD with the latest price (x).

        :param x: The new price observation
        :return: self
        """
        # Update slow and fast EMAs
        slow_ema_value = self.ema_slow.update(x)
        fast_ema_value = self.ema_fast.update(x)

        # Calculate the MACD line (difference between fast and slow EMAs)
        self.macd_line = fast_ema_value - slow_ema_value

        # Update the signal line (EMA of the MACD line)
        self.signal_line = self.ema_signal.update(self.macd_line)

        return self

    def transform_one(self, x=None):
        """
        Returns the current MACD line and signal line.

        :param x: Ignored, included for API consistency.
        :return: dict with the current MACD and signal line.
        """
        if self.macd_line is None or self.signal_line is None:
            return {'macd_line': float('nan'), 'signal_line': float('nan')}

        return {'macd_line': self.macd_line, 'signal_line': self.signal_line}

