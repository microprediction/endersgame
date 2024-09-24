from endersgame.attackers.attackerwithsimplepnl import AttackerWithSimplePnL
from endersgame.rivertransformers.macd import MACD
from river import stats
import numpy as np
import math


class MacdAttacker(AttackerWithSimplePnL):
    """

        An attacker that makes decisions based on the MACD momentum indicator.
        No need to worry about accounting as the parent tick_and_predict() takes care of it.

    """

    def __init__(self, window_slow=26, window_fast=12, window_sign=9, decision_threshold=0.5, min_abstention=50,
                 fading_factor=0.01, warmup=500):
        """
        Parameters:
            - window_slow: int, default=26
                The number of periods for the slow EMA.
            - window_fast: int, default=12
                The number of periods for the fast EMA.
            - window_sign: int, default=9
                The number of periods for the signal EMA.
            - decision_threshold: float, default=2.5
                The threshold for making decisions based on the normalized MACD signal.
            - min_abstention: int, default=50
                Minimum steps between predictions to avoid overtrading.
            - fading_factor: float, default=0.01
                Fading factor for the exponentially weighted moving average (EWMA).
            - warmup: int
                How long to wait before making any predictions
        """
        super().__init__()
        self.macd = MACD(window_slow=window_slow, window_fast=window_fast, window_sign=window_sign)
        self.ewvar_macd_signal = stats.EWVar(fading_factor=fading_factor)
        self.decision_threshold = decision_threshold
        self.abstention_count = min_abstention
        self.min_abstention = min_abstention
        self.observation_count = 0
        self.warmup = warmup

    def tick(self, x: float, k: int = None) -> float:
        """
        Update the MACD and PnL tracking with each new observation.
        """

        # Update the MACD signal
        if not np.isnan(x):
            self.macd.learn_one(x=x)

            # Also update the running Var of the signal
            macd_signal = self.macd.transform_one()['macd_line']
            if not np.isnan(macd_signal):
                self.ewvar_macd_signal.update(macd_signal)


    def predict(self, k: int = None) -> float:
        """
            Predict based on the MACD signal and make decisions when momentum exceeds the threshold.
        """

        # Avoid making predictions too frequently
        if (self.abstention_count < self.min_abstention):
            self.abstention_count += 1
            return 0

        # Get standardized signal
        try:
            standardized_signal = math.sqrt(self.ewvar_macd_signal.get())
        except ArithmeticError:
            standardized_signal = 0

        decision = int(standardized_signal / self.decision_threshold)

        # If we're predicting directionally, reset the abstention count
        if abs(decision):
            self.abstention_count = 0
        return decision



if __name__ == '__main__':
    from endersgame.syntheticdata.momentumregimes import momentum_regimes
    xs = momentum_regimes(n=2000)
    attacker = MacdAttacker(window_slow=26, window_fast=12, window_sign=9, decision_threshold=2.5,
                            min_abstention=5, fading_factor=0.05, warmup=10)

    # Process each point and make decisions
    k=100  # Horizon
    for i, x in enumerate(xs):
        decision = attacker.tick_and_predict(x=x, k=k)
        print(f"Step {i + 1}: Price: {x:.2f}, Decision: {decision}")

    # Print the final PnL summary after all points
    summary = attacker.get_pnl_summary()
    from pprint import pprint
    pprint(summary)

