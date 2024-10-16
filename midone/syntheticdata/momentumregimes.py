import numpy as np


def momentum_regimes(n=1000, regime_change_prob=0.05, momentum_strength=0.5, bounce_strength=0.3, noise_level=0.1) -> [float]:
    """
    Generate a long sequence of data that sometimes bounces and sometimes exhibits momentum.

    The data alternates between two regimes:
      - Momentum regime: where the sequence trends in one direction (up or down).
      - Bounce regime: where the sequence mean-reverts or fluctuates around a central value.

    :param n: Number of data points to generate
    :param regime_change_prob: Probability of switching between regimes at each time step
    :param momentum_strength: Strength of the trend in the momentum regime
    :param bounce_strength: Strength of the mean reversion in the bounce regime
    :param noise_level: Random noise level added to the data
    :return: List of floats representing the generated data sequence
    """
    # Initialize the data sequence and the initial regime (0 = bounce, 1 = momentum)
    data = [0]  # Start with an initial value of 0
    current_regime = np.random.choice([0, 1])

    for _ in range(1, n):
        if np.random.rand() < regime_change_prob:
            # Switch between momentum and bounce regime
            current_regime = 1 - current_regime

        if current_regime == 0:  # Bounce regime (mean-reverting)
            # Generate a mean-reverting process around 0
            new_value = data[-1] + bounce_strength * (0 - data[-1]) + noise_level * np.random.randn()
        else:  # Momentum regime (trending)
            # Generate a trending process (momentum)
            direction = np.sign(np.random.randn())  # Randomly choose trend direction (up or down)
            new_value = data[-1] + direction * momentum_strength + noise_level * np.random.randn()

        data.append(new_value)

    return data
