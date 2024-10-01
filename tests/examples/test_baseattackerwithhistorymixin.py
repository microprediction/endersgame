import pytest
import numpy as np
from endersgame.attackers.baseattackerwithhistorymixin import ExampleHistoricalAttacker  # Import your actual class


@pytest.fixture
def attacker():
    return ExampleHistoricalAttacker(max_history_len=10)


@pytest.fixture
def long_time_series():
    # Create a long enough time series (e.g., random walk)
    num_points = 5000
    return np.cumsum(np.random.randn(num_points))


def test_no_crash_on_empty_history():
    """Test that the class doesn't crash when history is too short to compute predictions."""
    attacker = ExampleHistoricalAttacker()
    assert attacker.predict() == 0, "Predict should return 0 when there is not enough history"
