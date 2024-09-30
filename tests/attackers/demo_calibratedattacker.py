import numpy as np
import matplotlib.pyplot as plt
from endersgame.attackers.calibratedattacker import CalibratedAttacker

# A demonstration of how to create a calibrated attacker
# This shows the decisions ("signal") made by a "raw" attacker,
# and also the decisions made by its empirical counterpart.


class MyUncalibratedAttacker:
    """
    A mock attacker that generates real-valued signals based on the
    rate of change in the price (i.e., using a moving average approach).
    """
    def __init__(self, window=5):
        self.window = window
        self.prices = []

    def tick_and_predict(self, x):
        # Add the new price change to the list
        self.prices.append(x)
        if len(self.prices) > self.window:
            self.prices.pop(0)

        # Signal is based on the moving average of price changes
        if len(self.prices) == self.window:
            return np.mean(self.prices)
        else:
            return 0.0  # No signal if there isn't enough data


if __name__=='__main__':

    # Simulation parameters
    np.random.seed(42)  # For reproducibility
    n_ticks = 100       # Number of ticks to simulate
    price_changes = np.random.randn(n_ticks)  # Simulated price changes (random walk)

    # Initialize the mock attacker and the calibrated attacker
    uncalibrated_attacker = MyUncalibratedAttacker(window=5)
    calibrated_attacker = CalibratedAttacker(attacker=uncalibrated_attacker, epsilon=0.005, fading_factor=0.01)

    # Arrays to store the signals and decisions
    mock_signals = []
    empirical_decisions = []

    # Run the simulation
    for i, price_change in enumerate(price_changes):
        mock_signal = uncalibrated_attacker.tick_and_predict(x=price_change)
        empirical_decision = calibrated_attacker.tick_and_predict(x=price_change, k=1)

        mock_signals.append(mock_signal)
        empirical_decisions.append(empirical_decision)

    # Plotting the results
    plt.figure(figsize=(12, 6))

    # Plot mock signals (raw signals)
    plt.subplot(2, 1, 1)
    plt.plot(mock_signals, label='Mock Attacker Signals (Real-Valued)', color='blue')
    plt.title('Mock Attacker Signals')
    plt.xlabel('Tick')
    plt.ylabel('Signal Value')
    plt.legend()

    # Plot empirical decisions (discrete decisions)
    plt.subplot(2, 1, 2)
    plt.plot(empirical_decisions, label='Empirical Attacker Decisions', color='green')
    plt.title('Empirical Attacker Decisions')
    plt.xlabel('Tick')
    plt.ylabel('Decision (-1, 0, 1)')
    plt.legend()

    plt.tight_layout()
    plt.show()
