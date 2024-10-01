import pytest
import numpy as np
from endersgame.attackers.calibratedattacker import CalibratedAttacker

# Mock attacker class with moving average signal
class MockAttacker:
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


@pytest.fixture
def setup_attacker():
    """
    Fixture to set up the CalibratedAttacker with a MockAttacker.
    """
    attacker = MockAttacker(window=5)
    calibrated_attacker = CalibratedAttacker(attacker=attacker, epsilon=0.005, fading_factor=0.01)
    return calibrated_attacker


def test_initialization(setup_attacker):
    """
    Test that the CalibratedAttacker initializes correctly.
    """
    calibrated_attacker = setup_attacker
    assert calibrated_attacker.attacker is not None, "Attacker should be initialized"
    assert isinstance(calibrated_attacker.attacker, MockAttacker), "Attacker should be an instance of MockAttacker"


def test_tick_and_predict_valid_decisions(setup_attacker):
    """
    Test that the tick_and_predict method returns valid decisions.
    """
    calibrated_attacker = setup_attacker
    price_changes = np.random.randn(10)  # Simulated price changes (random walk)

    for price_change in price_changes:
        decision = calibrated_attacker.tick_and_predict(x=price_change, horizon=1)
        assert decision in [-1, 0, 1], "Decision should be -1, 0, or 1"


def test_empirical_attacker_on_sequence(setup_attacker):
    """
    Test the behavior of the empirical attacker on a known sequence of price changes.
    """
    calibrated_attacker = setup_attacker
    price_changes = [0.1, -0.2, 0.3, -0.4, 0.5, -0.1, 0.2, -0.3, 0.4, -0.5]

    decisions = []
    for price_change in price_changes:
        decision = calibrated_attacker.tick_and_predict(x=price_change, horizon=1)
        decisions.append(decision)

    # Ensure that decisions are in the expected range and length
    assert len(decisions) == len(price_changes), "There should be a decision for each price change"
    assert all(d in [-1, 0, 1] for d in decisions), "All decisions should be -1, 0, or 1"


if __name__ == "__main__":
    pytest.main()
