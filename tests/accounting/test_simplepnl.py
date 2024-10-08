import pytest
from endersgame.accounting.pnl import Pnl

def test_initial_state():
    """Test if the initial state of the PnL class is correct."""
    pnl_tracker = Pnl(epsilon=0)
    assert pnl_tracker.current_ndx == 0
    assert pnl_tracker.pending_decisions == {}
    assert pnl_tracker.pnl_data == []

def test_horizon_one():
    """Test decision at horizon 1: simple lag."""
    pnl_tracker = Pnl(epsilon=0)
    pnl_tracker.tick(x=100, horizon=1, decision=1)
    assert len(pnl_tracker.pending_decisions) == 1
    assert len(pnl_tracker.pnl_data) == 0

    pnl_tracker.tick(x=110, horizon=1, decision=0)
    assert len(pnl_tracker.pending_decisions) == 0
    assert len(pnl_tracker.pnl_data) == 1
    assert pnl_tracker.pnl_data[0][-1] == 10  # PnL should be 110 - 100 = 10

def test_tick_once():
    pnl_tracker = Pnl(epsilon=0)
    pnl_tracker.tick(x=1.0, horizon=7, decision=1)
    assert len(pnl_tracker.pending_decisions) == 1
    assert len(pnl_tracker.pnl_data) == 0

def test_tick_twice_with_backoff():
    pnl_tracker = Pnl(epsilon=0, backoff=10)
    pnl_tracker.tick(x=1.0, horizon=7, decision=1)
    pnl_tracker.tick(x=1.1, horizon=7, decision=1)  # Backoff prevents tracking
    assert len(pnl_tracker.pending_decisions) == 1
    assert len(pnl_tracker.pnl_data) == 0

def test_tick_twice_no_backoff():
    pnl_tracker = Pnl(epsilon=0, backoff=1)
    pnl_tracker.tick(x=1.0, horizon=7, decision=1)
    pnl_tracker.tick(x=1.1, horizon=7, decision=1)
    assert len(pnl_tracker.pending_decisions) == 2
    assert len(pnl_tracker.pnl_data) == 0

def test_multiple_decisions_over_time():
    """Test multiple decisions being made and resolved over time."""
    pnl_tracker = Pnl(epsilon=0)

    # Step 1: Record first decision
    pnl_tracker.tick(x=100, horizon=3, decision=1)
    assert len(pnl_tracker.pending_decisions) == 1
    assert len(pnl_tracker.pnl_data) == 0

    # Step 2: Record second decision
    pnl_tracker.tick(x=110, horizon=4, decision=-1)
    assert len(pnl_tracker.pending_decisions) == 2
    assert len(pnl_tracker.pnl_data) == 0

    # Step 3: Resolve first decision
    pnl_tracker.tick(x=120, horizon=3, decision=0)
    pnl_tracker.tick(x=130, horizon=3, decision=0)
    assert len(pnl_tracker.pending_decisions) == 1
    assert len(pnl_tracker.pnl_data) == 1
    assert pnl_tracker.pnl_data[0][-1] == 30  # PnL should be 130 - 100 = 30

    # Step 4: Move forward without resolving second decision
    pnl_tracker.tick(x=140, horizon=3, decision=0)
    assert len(pnl_tracker.pending_decisions) == 1
    assert len(pnl_tracker.pnl_data) == 1

    # Step 5: Resolve second decision
    pnl_tracker.tick(x=150, horizon=3, decision=0)
    assert len(pnl_tracker.pending_decisions) == 0
    assert len(pnl_tracker.pnl_data) == 2
    assert pnl_tracker.pnl_data[1][-1] == -40  # PnL should be 110 - 150 = -40

def test_sequential_resolutions_with_no_decision():
    """Test resolving decisions with no new decision being made."""
    pnl_tracker = Pnl(epsilon=0)

    # Step 1: Record a decision
    pnl_tracker.tick(x=100, horizon=3, decision=1)
    assert len(pnl_tracker.pending_decisions) == 1
    assert len(pnl_tracker.pnl_data) == 0

    # Step 2: Move forward without new decisions
    pnl_tracker.tick(x=110, horizon=3, decision=0)
    pnl_tracker.tick(x=120, horizon=3, decision=0)
    assert len(pnl_tracker.pending_decisions) == 1
    assert len(pnl_tracker.pnl_data) == 0

    # Step 3: Resolve the decision
    pnl_tracker.tick(x=130, horizon=3, decision=0)
    assert len(pnl_tracker.pending_decisions) == 0
    assert len(pnl_tracker.pnl_data) == 1
    assert pnl_tracker.pnl_data[0][-1] == 30  # PnL should be 130 - 100 = 30

    # Step 4: Move forward with no pending decisions
    pnl_tracker.tick(x=140, horizon=3, decision=0)
    assert len(pnl_tracker.pending_decisions) == 0
    assert len(pnl_tracker.pnl_data) == 1

if __name__ == "__main__":
    pytest.main([__file__])
