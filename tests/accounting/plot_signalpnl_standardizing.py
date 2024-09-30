
# demo_standardization_stochastic.py

import matplotlib.pyplot as plt
from endersgame.accounting.signalpnl import SignalPnl
import math
import numpy as np

def generate_ornstein_uhlenbeck(length, theta=0.15, mu=0.0, sigma=1.0, x0=0.0, seed=None):
    """
    Generates an Ornstein-Uhlenbeck process.

    Parameters:
    - length (int): Number of data points.
    - theta (float): Speed of mean reversion.
    - mu (float): Long-term mean.
    - sigma (float): Volatility parameter.
    - x0 (float): Initial value.
    - seed (int or None): Seed for reproducibility.

    Returns:
    - np.ndarray: Array containing the OU process.
    """
    if seed is not None:
        np.random.seed(seed)
    ou = np.zeros(length)
    ou[0] = x0
    for t in range(1, length):
        dt = 1.0
        ou[t] = ou[ t -1] + theta * (mu - ou[ t -1]) * dt + sigma * math.sqrt(dt) * np.random.normal()
    return ou

def main():
    # Configuration
    decay = 0.9  # Decay factor for EWMean and EWVar
    num_points = 200  # Number of data points (made longer)
    k = 5  # Prediction horizon for PnL calculations
    seed = 42  # Seed for reproducibility

    # Initialize SignalPnl with default thresholds and specified decay
    pnl = SignalPnl(decay=decay)

    # Generate stochastic signals using an Ornstein-Uhlenbeck process
    # Adjust mu and sigma as needed for desired behavior
    signals = generate_ornstein_uhlenbeck(length=num_points, theta=0.15, mu=0.0, sigma=2.0, x0=0.0, seed=seed)

    # Simulated x values (e.g., asset prices or other relevant data)
    x_values = [100 + i for i in range(num_points)]  # Simple incremental x for demonstration

    # Lists to store standardized signals
    standardized_signals = []

    # Define thresholds for highlighting
    positive_threshold = 1.0  # Changed from 2.0 to 1.0
    negative_threshold = -1.0  # Changed from -2.0 to -1.0

    # Process each signal through the SignalPnl class
    for x, signal in zip(x_values, signals):
        pnl.tick(x, k=k, signal=signal)
        standardized_signals.append(pnl.current_standardized_signal)

    # Identify points where standardized signal exceeds thresholds
    positive_exceeds = [i for i, z in enumerate(standardized_signals) if z > positive_threshold]
    negative_exceeds = [i for i, z in enumerate(standardized_signals) if z < negative_threshold]

    # Plotting the original and standardized signals
    plt.figure(figsize=(18, 10))

    # Plot Original Signal
    plt.subplot(2, 1, 1)
    plt.plot(x_values, signals, label='Original Signal (OU Process)', color='blue')
    plt.title('Stochastic Original Signal (Ornstein-Uhlenbeck Process)')
    plt.xlabel('Data Point')
    plt.ylabel('Signal Value')
    plt.legend()
    plt.grid(True)

    # Plot Standardized Signal
    plt.subplot(2, 1, 2)
    plt.plot(x_values, standardized_signals, label='Standardized Signal (Z-Score)', color='red', linewidth=1.5)

    # Highlight points exceeding positive threshold
    if positive_exceeds:
        plt.scatter(
            [x_values[i] for i in positive_exceeds],
            [standardized_signals[i] for i in positive_exceeds],
            color='green', label=f'Z > {positive_threshold}', zorder=5, marker='^', s=100
        )

    # Highlight points exceeding negative threshold
    if negative_exceeds:
        plt.scatter(
            [x_values[i] for i in negative_exceeds],
            [standardized_signals[i] for i in negative_exceeds],
            color='purple', label=f'Z < {negative_threshold}', zorder=5, marker='v', s=100
        )

    # Plot threshold lines
    plt.axhline(y=positive_threshold, color='green', linestyle='--', linewidth=1, label='Positive Threshold (Z=1)')
    plt.axhline(y=negative_threshold, color='purple', linestyle='--', linewidth=1, label='Negative Threshold (Z=-1)')

    plt.title('Standardized Signal with Threshold Highlights (Z > 1 and Z < -1)')
    plt.xlabel('Data Point')
    plt.ylabel('Standardized Signal (Z-Score)')
    plt.legend(loc='upper right')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
