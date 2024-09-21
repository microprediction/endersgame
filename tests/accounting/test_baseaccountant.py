import pytest
from endersgame.accounting.baseaccountant import BaseAccountant



@pytest.fixture
def accountant():
    """Fixture to initialize a new instance of BaseAccountant."""
    return BaseAccountant()


def test_initial_state(accountant):
    """Test if the initial state of the accountant is correctly initialized."""
    assert accountant.accounting["current_observation_ndx"] == 0
    assert accountant.accounting["last_attack_ndx"] is None
    assert accountant.accounting["pending_decisions"] == []
    assert accountant.accounting["pnl_data"] == []


def test_record_decision_with_large_gap(accountant):
    """Test recording a decision when there's more than a 100-step gap."""
    accountant.record_decision(current_ndx=0, decision=1)
    assert accountant.accounting["last_attack_ndx"] == 0
    assert accountant.accounting["pending_decisions"] == [(0, 1)]

    # Simulate a decision after 150 steps (more than 100)
    accountant.record_decision(current_ndx=150, decision=-1)
    assert accountant.accounting["last_attack_ndx"] == 150
    assert accountant.accounting["pending_decisions"] == [(0, 1), (150, -1)]


def test_record_decision_with_small_gap(accountant):
    """Test recording a decision when there's less than a 100-step gap."""
    accountant.record_decision(current_ndx=0, decision=1)
    assert accountant.accounting["last_attack_ndx"] == 0
    assert accountant.accounting["pending_decisions"] == [(0, 1)]

    # Simulate a decision after 50 steps (less than 100, should be ignored)
    accountant.record_decision(current_ndx=50, decision=-1)
    assert accountant.accounting["last_attack_ndx"] == 0  # No update
    assert accountant.accounting["pending_decisions"] == [(0, 1)]  # No new decision added


def test_resolve_decisions(accountant):
    """Test resolving a pending decision."""
    # Record a decision at step 0
    accountant.record_decision(current_ndx=0, decision=1)

    # Move forward 100 steps and resolve the decision with a value of 150
    accountant.resolve_decisions(current_ndx=100, y_current=50)
    assert len(accountant.accounting["pnl_data"]) == 1
    resolved_decision = accountant.accounting["pnl_data"][0]

    assert resolved_decision["decision_time"] == 0
    assert resolved_decision["resolution_time"] == 100
    assert resolved_decision["decision"] == 1
    assert resolved_decision["pnl"] == 50  # current_ndx - y_current = 100 - 50


def test_resolve_multiple_decisions(accountant):
    """Test resolving multiple decisions."""
    # Record multiple decisions at different times
    accountant.record_decision(current_ndx=0, decision=1)
    accountant.record_decision(current_ndx=150, decision=-1)

    # Move forward and resolve both decisions
    accountant.resolve_decisions(current_ndx=100, y_current=50)  # First decision should be resolved
    accountant.resolve_decisions(current_ndx=250, y_current=300)  # Second decision should be resolved

    assert len(accountant.accounting["pnl_data"]) == 2
    assert accountant.accounting["pnl_data"][0]["decision_time"] == 0
    assert accountant.accounting["pnl_data"][1]["decision_time"] == 150
    assert accountant.accounting["pnl_data"][0]["pnl"] == 50  # First decision PnL
    assert accountant.accounting["pnl_data"][1]["pnl"] == 50  # Second decision PnL


def test_summary(accountant):
    """Test getting a summary of the PnL."""
    accountant.record_decision(current_ndx=0, decision=1)
    accountant.resolve_decisions(current_ndx=100, y_current=50)
    accountant.record_decision(current_ndx=150, decision=-1)
    accountant.resolve_decisions(current_ndx=250, y_current=300)

    summary = accountant.get_pnl_summary()
    assert summary["current_observation_ndx"] == 2
    assert summary["num_resolved_decisions"] == 2
    assert summary["total_profit"] == 100  # 50 from the first and 50 from the second


def test_reset(accountant):
    """Test resetting the accountant state."""
    accountant.record_decision(current_ndx=0, decision=1)
    accountant.resolve_decisions(current_ndx=100, y_current=50)

    accountant.reset_pnl()

    assert accountant.accounting["current_observation_ndx"] == 0
    assert accountant.accounting["last_attack_ndx"] is None
    assert accountant.accounting["pending_decisions"] == []
    assert accountant.accounting["pnl_data"] == []
