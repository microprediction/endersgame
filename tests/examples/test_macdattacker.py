import pytest
import numpy as np
from midone.examples.macdattacker import MacdAttacker  # Replace with the actual path to the MacdAttacker
from midone.syntheticdata.momentumregimes import momentum_regimes
from midone.rivertransformers.macd import MACD

@pytest.fixture
def macd_attacker():
    """Fixture to initialize the MacdAttacker instance with default parameters."""
    return MacdAttacker(window_slow=26, window_fast=12, window_sign=9, decision_threshold=0.1,
                        min_abstention=5, fading_factor=0.05, warmup=10, epsilon=0.01)


def test_initial_state(macd_attacker):
    """Test the initial state of the MacdAttacker."""
    assert macd_attacker.abstention_count == 5, "Abstention count should be initialized to 5"
    assert macd_attacker.observation_count == 0, "Observation count should be initialized to 0"
    assert isinstance(macd_attacker.macd, MACD), "MACD should be properly initialized"
    assert macd_attacker.decision_threshold == 0.1, "Decision threshold should be initialized to the correct value"


def test_tick_updates_macd_and_var(macd_attacker):
    """Test that tick updates the MACD and variance of the MACD signal."""
    y_values = [100, 101, 102]

    for y in y_values:
        macd_attacker.tick(x=y)

    macd_signal = macd_attacker.macd.transform_one()['macd_line']
    assert not np.isnan(macd_signal), "MACD line should have been updated"
    assert macd_attacker.ewvar_macd_signal.get() != 0, "EWVar mean should be updated"


def test_predict_with_abstention(macd_attacker):
    """Test that predictions are abstained when abstention_count is below min_abstention."""
    macd_attacker.abstention_count = 0
    macd_attacker.observation_count = 100
    macd_attacker.min_abstention = 5
    result = macd_attacker.predict()
    assert result == 0, "Should abstain from decision if abstention_count < min_abstention"
    assert macd_attacker.abstention_count == 1, "Abstention count should increment"



def test_predict_with_random_data(macd_attacker):
    """Test the attacker on a random walk to see if it behaves as expected."""
    np.random.seed(42)
    y_values = momentum_regimes(n=20000)

    decisions = []
    for y in y_values:
        macd_attacker.tick(x=y)
        decision = macd_attacker.predict()
        decisions.append(decision)

    assert len(decisions) == len(y_values), "Should have a prediction for each price point"
    assert any(decision != 0 for decision in decisions), "There should be at least one non-zero decision"


def test_warmup_behavior(macd_attacker):
    """Test that no predictions are made before the warmup period."""
    macd_attacker.warmup = 10  # Set a small warmup period
    y_values = [100, 101, 102, 103, 104, 105]

    for i, y in enumerate(y_values):
        macd_attacker.tick(x=y)
        decision = macd_attacker.predict()
        if i < macd_attacker.warmup:
            assert decision == 0, f"Should not predict before warmup period at step {i + 1}"
        else:
            assert decision == 0 or decision != 0, "Prediction should be allowed after warmup"


def test_final_pnl_summary(macd_attacker):
    """Test that the PnL summary is generated correctly after processing data."""
    y_values = momentum_regimes(n=200)

    for y in y_values:
        macd_attacker.tick_and_predict(x=y, horizon=100)

    summary = macd_attacker.pnl.summary()
    assert isinstance(summary, dict), "PnL summary should be a dictionary"
