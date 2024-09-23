from river import base, stats
import numpy as np


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
        """
        :param window_slow: The number of periods for the slow EMA.
        :param window_fast: The number of periods for the fast EMA.
        :param window_sign: The number of periods for the signal EMA of the MACD line.
        """
        self.window_slow = window_slow
        self.window_fast = window_fast
        self.window_sign = window_sign

        # Convert window sizes to fading factors
        fading_factor_slow = 2 / (self.window_slow + 1)
        fading_factor_fast = 2 / (self.window_fast + 1)
        fading_factor_sign = 2 / (self.window_sign + 1)

        # Using river's EWMA to track the slow and fast EMAs, and the signal line
        self.ema_slow = stats.EWMean(fading_factor=fading_factor_slow)
        self.ema_fast = stats.EWMean(fading_factor=fading_factor_fast)
        self.ema_signal = stats.EWMean(fading_factor=fading_factor_sign)

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

        # If either EMA is None, we cannot compute the MACD line yet
        if slow_ema_value is None or fast_ema_value is None:
            self.macd_line = None
        else:
            # Calculate the MACD line (difference between fast and slow EMAs)
            self.macd_line = fast_ema_value - slow_ema_value

        # Update the signal line (EMA of the MACD line)
        if (self.macd_line is not None) and (not np.isnan(self.macd_line)):
            self.signal_line = self.ema_signal.update(self.macd_line)
        else:
            self.signal_line = None

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

