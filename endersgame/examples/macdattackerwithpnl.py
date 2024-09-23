from endersgame.attackers.attackerwithsimplepnl import AttackerWithSimplePnL
from endersgame.rivertransformers.macd import MACD
from river import stats
import numpy as np
import matplotlib.pyplot as plt
import math


class MacdAttacker(AttackerWithSimplePnL):
    """

        An attacker that makes decisions based on the MACD momentum indicator.
        No need to worry about accounting as the parent tick_and_predict() takes care of it.

    """

    def __init__(self, window_slow=26, window_fast=12, window_sign=9, decision_threshold=2.5, min_abstention=50,
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
        self.abstention_count = 0
        self.min_abstention = min_abstention
        self.observation_count = 0
        self.warmup = warmup

    def tick(self, y: float, k: int = None) -> float:
        """
        Update the MACD and PnL tracking with each new observation.
        """

        # Update the MACD signal
        self.macd.learn_one(x=y)

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
    # Parameters for the time series
    num_points = 5000  # Long series
    regime_change_prob = 0.01  # Probability of switching between regimes
    momentum_strength = 0.5  # Strength of trends in momentum regimes
    bounce_strength = 0.3  # Strength of reversions in bounce regimes
    noise_level = 0.2  # Random noise level

    # Initialize time series
    y_values = np.zeros(num_points)

    # Set the initial regime (0 = bounce, 1 = momentum)
    current_regime = np.random.choice([0, 1])

    for i in range(1, num_points):
        # Random chance to switch regime
        if np.random.rand() < regime_change_prob:
            current_regime = 1 - current_regime  # Switch between bounce and momentum

        if current_regime == 0:  # Bounce regime
            # Bounce around a mean (mean-reverting behavior)
            y_values[i] = y_values[i - 1] + bounce_strength * (
                        np.random.randn() - y_values[i - 1]) + noise_level * np.random.randn()
        else:  # Momentum regime
            # Trending behavior (momentum)
            direction = np.sign(np.random.randn())  # Randomly trend up or down
            y_values[i] = y_values[i - 1] + direction * momentum_strength + noise_level * np.random.randn()

    # Instantiate the MACD attacker with a specific fading factor
    attacker = MacdAttacker(window_slow=26, window_fast=12, window_sign=9, decision_threshold=2.5,
                            min_abstention=50, fading_factor=0.05)

    # Process each point and make decisions
    for i, y in enumerate(y_values):
        decision = attacker.tick(y=y)
        print(f"Step {i + 1}: Price: {y:.2f}, Decision: {decision}")

    # Plot the time series
    plt.figure(figsize=(12, 6))
    plt.plot(y_values, label="Simulated Price Series")
    plt.title("Simulated Time Series (Alternating Between Momentum and Bounce Regimes)")
    plt.xlabel("Time")
    plt.ylabel("Price")
    plt.legend()
    plt.show()

    # Print the final PnL summary after all points
    summary = attacker.get_pnl_summary()
    from pprint import pprint
    pprint(summary)

