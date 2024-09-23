
import pytest
import numpy as np
from endersgame.rivertransformers.macd import MACD  # Replace with the actual module path for the MACD class


@pytest.fixture
def macd():
    """Fixture to initialize the MACD instance with default parameters."""
    return MACD(window_slow=26, window_fast=12, window_sign=9)


def test_initial_state(macd):
    """Test that the MACD and signal line return NaN before any data is learned."""
    result = macd.transform_one()
    assert np.isnan(result['macd_line']), "MACD line should be NaN initially"
    assert np.isnan(result['signal_line']), "Signal line should be NaN initially"


def test_learning_single_point(macd):
    """Test that learning a single data point does not update the MACD or signal line."""
    macd.learn_one(100)
    result = macd.transform_one()
    assert result['macd_line']==0, "MACD line should be zero after learning a single point"
    assert result['signal_line']==0, "Signal line should be NaN after learning a single point"



def test_macd_with_random_walk(macd):
    """Test MACD on a random walk and ensure it produces valid values."""
    np.random.seed(42)
    random_walk = np.cumsum(np.random.randn(100))

    for price in random_walk:
        macd.learn_one(price)
        result = macd.transform_one()

        assert isinstance(result['macd_line'], float), "MACD line should return a float"
        assert isinstance(result['signal_line'], float), "Signal line should return a float"

