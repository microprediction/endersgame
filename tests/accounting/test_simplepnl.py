import pytest
from endersgame.accounting.simplepnl import SimplePnL


def test_initial_state():
    """Test if the initial state of the SimplePnL class is correct."""
    pnl_tracker = SimplePnL()
    assert pnl_tracker.accounting["current_ndx"] == 0
    assert pnl_tracker.accounting["pending_decisions"] == []
    assert pnl_tracker.accounting["pnl_data"] == []


def test_record_and_resolve_decision():
    """Test recording and resolving a single decision."""
    pnl_tracker = SimplePnL()

    # Step 1: Record a decision at step 0 (y = 100, decision = 1)
    pnl_tracker.update_pnl(y=100, decision=1)
    assert len(pnl_tracker.accounting["pending_decisions"]) == 1

    # Step 2: Move forward 100 steps and resolve the decision (y = 150)
    pnl_tracker.accounting["current_ndx"] = 100
    pnl_tracker.update_pnl(y=150, decision=0)  # No new decision
    assert len(pnl_tracker.accounting["pending_decisions"]) == 0
    assert len(pnl_tracker.accounting["pnl_data"]) == 1
    assert pnl_tracker.accounting["pnl_data"][0][-1] == 50  # PnL = 150 - 100
