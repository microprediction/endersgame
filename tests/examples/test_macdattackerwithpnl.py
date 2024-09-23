import pytest
import numpy as np
from endersgame.rivertransformers.macd import MACD  # Replace with the actual path to your MACD class


@pytest.fixture
def macd():
    """Fixture to initialize the MACD instance with default parameters."""
    return MACD(window_slow=26, window_fast=12, window_sign=9)


def test_initial_state(macd):
    """Test that MACD returns NaN for both lines before learning any data."""
    result = macd.transform_one()
    assert np.isnan(result['macd_line']), "MACD line should be NaN initially"
    assert np.isnan(result['signal_line']), "Signal line should be NaN initially"


def test_learning_single_point(macd):
    """Test that learning a single data point updates the EMA values but still returns NaN for MACD and signal lines."""
    macd.learn_one(100)
    result = macd.transform_one()

    assert np.isnan(result['macd_line']), "MACD line should still be NaN after a single point"
    assert np.isnan(result['signal_line']), "Signal line should still be NaN after a single point"


def test_macd_with_random_walk(macd):
    """Test MACD on a simple random walk and ensure it produces valid values."""
    np.random.seed(42)
    random_walk = np.cumsum(np.random.randn(100))

    for price in random_walk:
        macd.learn_one(price)
        result = macd.transform_one()

        assert isinstance(result['macd_line'], float), "MACD line should be a float"
        assert isinstance(result['signal_line'], float), "Signal line should be a float"


def test_macd_transform_without_learn(macd):
    """Test transform_one without learning anything to ensure it still handles the case."""
    result = macd.transform_one()

    assert np.isnan(result['macd_line']), "MACD line should be NaN when no data has been learned"
    assert np.isnan(result['signal_line']), "Signal line should be NaN when no data has been learned"


