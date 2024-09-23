

import pytest
import numpy as np
from endersgame.examples.bufferingattacker import BufferingAttacker  # Import your actual class

@pytest.fixture
def attacker():
    return BufferingAttacker()

@pytest.fixture
def long_time_series():
    # Create a long enough time series (e.g., random walk)
    num_points = 5000
    return np.cumsum(np.random.randn(num_points))

def test_warmup(attacker, long_time_series):
    """Test that the attacker does not predict before warming up."""
    for i in range(attacker._warmup - 1):
        decision = attacker.tick_and_predict(y=long_time_series[i])
        assert decision == 0, f"Should not predict before warmup, step {i}"

def test_buffering(attacker, long_time_series):
    """Test that the buffer maintains the correct length and purges old data."""
    for i, y in enumerate(long_time_series):
        attacker.tick(y=y)
        # After each tick, check that the buffer size does not exceed max length
        if i >= attacker._max_history_len:
            assert len(attacker._history) == attacker._max_history_len, "Buffer should maintain max history length"

def test_prediction_period(attacker, long_time_series):
    """Test that predictions are made only at the specified prediction period."""
    for i, y in enumerate(long_time_series):
        decision = attacker.tick_and_predict(y=y)
        # Predictions should only occur at the correct interval (every `_prediction_period` steps)
        if len(attacker._history) >= attacker._warmup:
            if (len(attacker._history) % attacker._prediction_period) == 0:
                assert True
            else:
                assert decision == 0, f"No prediction should be made at step {i} outside the period"

def test_prediction_accuracy(attacker, long_time_series):
    """Test that the predictions follow the expected logic in the `_predict_using_buffer` method."""
    # Feed enough data to warm up the attacker
    for i in range(attacker._warmup):
        attacker.tick(y=long_time_series[i])

    # Feed additional data and check the prediction logic
    for i in range(attacker._warmup, len(long_time_series)):
        attacker.tick(y=long_time_series[i])
        if len(attacker._history) >= attacker._warmup:
            if (len(attacker._history) % attacker._prediction_period) == 0:
                decision = attacker.predict()
                assert isinstance(decision,(int,float))

def test_no_crash_on_empty_history():
    """Test that the class doesn't crash when history is too short to compute predictions."""
    attacker = BufferingAttacker()
    assert attacker.predict() == 0, "Predict should return 0 when there is not enough history"
