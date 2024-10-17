# demo_standardization_animation.py

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from midone.accounting.stdsignalpnl import StdSignalPnl
import math
import numpy as np


def generate_ornstein_uhlenbeck(length, theta=0.15, mu=0.0, sigma=2.0, x0=0.0, seed=None):
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
        ou[t] = ou[t - 1] + theta * (mu - ou[t - 1]) * dt + sigma * math.sqrt(dt) * np.random.normal()
    return ou


def main():
    # Configuration
    decay = 0.9  # Decay factor for EWMean and EWVar
    fading_factor = 1-decay
    num_points = 200  # Number of data points (made longer)
    k = 5  # Prediction horizon for PnL calculations
    seed = 42  # Seed for reproducibility

    # Initialize SignalPnl with default thresholds and specified decay
    pnl = StdSignalPnl(fading_factor=fading_factor)

    # Generate stochastic signals using an Ornstein-Uhlenbeck process
    # Adjust mu and sigma as needed for desired behavior
    signals = generate_ornstein_uhlenbeck(length=num_points, theta=0.15, mu=0.0, sigma=2.0, x0=0.0, seed=seed)

    # Simulated x values (e.g., time steps or asset prices)
    x_values = [i for i in range(1, num_points + 1)]  # Data points from 1 to num_points

    # Lists to store standardized signals
    standardized_signals = []

    # Lists to store indices where thresholds are exceeded
    positive_exceeds = []
    negative_exceeds = []

    # Define thresholds for highlighting
    positive_threshold = 1.0  # Z > 1.0
    negative_threshold = -1.0  # Z < -1.0

    # Initialize plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(18, 10))
    plt.subplots_adjust(hspace=0.4)

    # Plot elements for Original Signal
    line_original, = ax1.plot([], [], label='Original Signal (OU Process)', color='blue')
    ax1.set_xlim(0, num_points + 1)
    ax1.set_ylim(min(signals) - 5, max(signals) + 5)
    ax1.set_title('Stochastic Original Signal (Ornstein-Uhlenbeck Process)')
    ax1.set_xlabel('Data Point')
    ax1.set_ylabel('Signal Value')
    ax1.legend()
    ax1.grid(True)

    # Plot elements for Standardized Signal
    line_standardized, = ax2.plot([], [], label='Standardized Signal (Z-Score)', color='red', linewidth=1.5)
    scat_positive = ax2.scatter([], [], color='green', label='Z > 1.0', marker='^', s=100)
    scat_negative = ax2.scatter([], [], color='purple', label='Z < -1.0', marker='v', s=100)
    ax2.set_xlim(0, num_points + 1)
    ax2.set_ylim(-3, 3)
    ax2.set_title('Standardized Signal with Threshold Highlights (Z > 1 and Z < -1)')
    ax2.set_xlabel('Data Point')
    ax2.set_ylabel('Standardized Signal (Z-Score)')
    ax2.legend(loc='upper right')
    ax2.grid(True)

    # Initialize lines and scatter plots
    def init():
        line_original.set_data([], [])
        line_standardized.set_data([], [])
        # Use np.empty with shape (0, 2) to initialize scatter plots correctly
        scat_positive.set_offsets(np.empty((0, 2)))
        scat_negative.set_offsets(np.empty((0, 2)))
        return line_original, line_standardized, scat_positive, scat_negative

    # Update function for animation
    def update(frame):
        # Ensure frame index is within the range
        if frame >= num_points:
            return line_original, line_standardized, scat_positive, scat_negative

        x = x_values[frame]
        signal = signals[frame]
        pnl.tick(x, horizon=k, signal=signal)
        standardized_signal = pnl.current_standardized_signal
        standardized_signals.append(standardized_signal)

        # Update Original Signal
        line_original.set_data(x_values[:frame + 1], signals[:frame + 1])

        # Update Standardized Signal
        line_standardized.set_data(x_values[:frame + 1], standardized_signals)

        # Check for threshold exceedances and record indices
        if standardized_signal > positive_threshold:
            positive_exceeds.append(frame)
        if standardized_signal < negative_threshold:
            negative_exceeds.append(frame)

        # Update scatter points
        # Convert to 2D array if there are exceedances, else keep empty
        if positive_exceeds:
            pos_coords = np.array([[x_values[i], standardized_signals[i]] for i in positive_exceeds])
            scat_positive.set_offsets(pos_coords)
        else:
            scat_positive.set_offsets(np.empty((0, 2)))

        if negative_exceeds:
            neg_coords = np.array([[x_values[i], standardized_signals[i]] for i in negative_exceeds])
            scat_negative.set_offsets(neg_coords)
        else:
            scat_negative.set_offsets(np.empty((0, 2)))

        return line_original, line_standardized, scat_positive, scat_negative

    # Create animation
    ani = animation.FuncAnimation(
        fig, update, frames=num_points, init_func=init,
        blit=True, interval=50, repeat=False
    )

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
