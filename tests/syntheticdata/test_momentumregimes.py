
from midone.syntheticdata.momentumregimes import momentum_regimes
import numpy as np



def test_momentum_regimes_length():
    """Test that the generated sequence has the expected length."""
    n = 1000
    data = momentum_regimes(n=n)
    assert len(data) == n, f"Expected sequence of length {n}, but got {len(data)}"


def test_momentum_regimes_non_constant():
    """Test that the generated sequence is not constant and contains noise."""
    data = momentum_regimes(n=1000, noise_level=0.1)
    unique_values = len(np.unique(data))
    assert unique_values > 1, "Generated data is constant, but expected some variance."


def test_momentum_regimes_regime_changes():
    """Test that the generated sequence contains regime changes."""
    np.random.seed(42)  # Fix seed for reproducibility
    data = momentum_regimes(n=1000, regime_change_prob=0.1)

    # Check that we have both increasing and decreasing segments
    diffs = np.diff(data)
    num_positive_diffs = np.sum(diffs > 0)
    num_negative_diffs = np.sum(diffs < 0)

    assert num_positive_diffs > 0, "Expected some positive trends in the data."
    assert num_negative_diffs > 0, "Expected some negative trends in the data."


def test_momentum_regimes_bounce_and_momentum():
    """Test that both momentum and bounce behaviors are present in the data."""
    np.random.seed(42)
    data = momentum_regimes(n=1000, regime_change_prob=0.05, momentum_strength=1.0, bounce_strength=0.5)

    # Calculate consecutive differences in the data
    diffs = np.diff(data)

    # Check for presence of momentum regime (long stretches of positive or negative diffs)
    momentum_detected = np.any(np.abs(diffs) > 0.8)

    # Check for presence of bounce regime (mean-reverting behavior)
    bounce_detected = np.any(np.abs(diffs) < 0.2)

    assert momentum_detected, "Expected some momentum regime behavior (large trends)."
    assert bounce_detected, "Expected some bounce regime behavior (mean reversion)."
