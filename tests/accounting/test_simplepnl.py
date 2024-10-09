import pytest
from endersgame.accounting.pnl import Pnl
from endersgame import EPSILON, DEFAULT_TRADE_BACKOFF

def test_initial_state():
    """Test if the initial state of the PnL class is correct."""
    pnl_tracker = Pnl(epsilon=0)
    assert pnl_tracker.current_ndx == 0, f"Expected current_ndx=0, got {pnl_tracker.current_ndx}"
    assert pnl_tracker.pending_decisions == [], f"Expected pending_decisions=[], got {pnl_tracker.pending_decisions}"
    assert pnl_tracker.pnl_data == [], f"Expected pnl_data=[], got {pnl_tracker.pnl_data}"


def test_tick_once_horizon_one():
    pnl_tracker = Pnl(epsilon=0)
    pnl_tracker.tick(x=1.0, horizon=1, decision=1)
    assert len(pnl_tracker.pending_decisions) == 1, f"Expected 1 pending decision, got {len(pnl_tracker.pending_decisions)}"


def test_tick_once():
    pnl_tracker = Pnl(epsilon=0)
    pnl_tracker.tick(x=1.0, horizon=7, decision=1)
    assert len(pnl_tracker.pending_decisions) == 1, f"Expected 1 pending decision, got {len(pnl_tracker.pending_decisions)}"

def test_tick_twice_with_backoff():
    pnl_tracker = Pnl(epsilon=0, backoff=10)
    pnl_tracker.tick(x=1.0, horizon=7, decision=1)
    pnl_tracker.tick(x=1.1, horizon=7, decision=1)  # Backoff prevents tracking
    assert len(pnl_tracker.pending_decisions) == 1, f"Expected 1 pending decision, got {len(pnl_tracker.pending_decisions)}"

def test_tick_twice_no_backoff():
    pnl_tracker = Pnl(epsilon=0, backoff=1)
    pnl_tracker.tick(x=1.0, horizon=7, decision=1)
    pnl_tracker.tick(x=1.1, horizon=7, decision=1)
    assert len(pnl_tracker.pending_decisions) == 2, f"Expected 2 pending decisions, got {len(pnl_tracker.pending_decisions)}"

def test_record_and_resolve_decision():
    """Test recording and resolving a single decision."""
    pnl_tracker = Pnl(epsilon=0)

    pnl_tracker.tick(x=100, horizon=100, decision=1)
    assert len(pnl_tracker.pending_decisions) == 1, f"Expected 1 pending decision, got {len(pnl_tracker.pending_decisions)}"

    pnl_tracker.current_ndx = 100
    pnl_tracker.tick(x=150, horizon=100, decision=0)  # No new decision
    assert len(pnl_tracker.pending_decisions) == 0, f"Expected 0 pending decisions after resolution, got {len(pnl_tracker.pending_decisions)}"
    assert len(pnl_tracker.pnl_data) == 1, f"Expected 1 PnL record, got {len(pnl_tracker.pnl_data)}"
    expected_pnl = 150 - 100 - pnl_tracker.epsilon
    actual_pnl = pnl_tracker.pnl_data[0]['pnl']
    assert actual_pnl == expected_pnl, f"Expected PnL={expected_pnl}, got {actual_pnl}"

def test_multiple_decisions_over_time():
    """Test multiple decisions being made and resolved over time."""

    pnl_tracker = Pnl(epsilon=0, backoff=0)
    # Step 1: Initial state check
    assert pnl_tracker.current_ndx == 0, f"Expected current_ndx=0, got {pnl_tracker.current_ndx}"
    assert pnl_tracker.pending_decisions == [], f"Expected pending_decisions=[], got {pnl_tracker.pending_decisions}"
    assert pnl_tracker.pnl_data == [], f"Expected pnl_data=[], got {pnl_tracker.pnl_data}"


    # Step 2: Record first decision at step 0 (y = 100, decision = 1)
    pnl_tracker.tick(x=100, horizon=100, decision=1)
    assert len(pnl_tracker.pending_decisions) == 1, f"Expected 1 pending decision, got {len(pnl_tracker.pending_decisions)}"

    # Step 3: Move forward by 50 steps without resolving (y = 120, decision = 0)
    pnl_tracker.current_ndx = 50
    pnl_tracker.tick(x=120, horizon=50, decision=0)
    assert len(pnl_tracker.pending_decisions) == 1, f"Expected 1 pending decision, got {len(pnl_tracker.pending_decisions)}"

    # Step 4: Move forward another 50 steps and resolve first decision (y = 150)
    pnl_tracker.current_ndx = 100
    pnl_tracker.tick(x=150, horizon=100, decision=0)
    assert len(pnl_tracker.pending_decisions) == 0, f"Expected 0 pending decisions after resolution, got {len(pnl_tracker.pending_decisions)}"
    assert len(pnl_tracker.pnl_data) == 1, f"Expected 1 PnL record, got {len(pnl_tracker.pnl_data)}"
    expected_pnl = 150 - 100 - pnl_tracker.epsilon
    actual_pnl = pnl_tracker.pnl_data[0]['pnl']
    assert actual_pnl == expected_pnl, f"Expected PnL={expected_pnl}, got {actual_pnl}"

    # Step 5: Record second decision at step 100 (y = 150, decision = -1)
    pnl_tracker.tick(x=150, horizon=100, decision=-1)
    assert len(pnl_tracker.pending_decisions) == 1, f"Expected 1 pending decision, got {len(pnl_tracker.pending_decisions)}"

    # Step 6: Move forward 50 steps without resolving (y = 140)
    pnl_tracker.current_ndx = 150
    pnl_tracker.tick(x=140, horizon=50, decision=0)
    assert len(pnl_tracker.pending_decisions) == 1, f"Expected 1 pending decision, got {len(pnl_tracker.pending_decisions)}"

    # Step 7: Resolve second decision (y = 100)
    pnl_tracker.current_ndx = 201
    pnl_tracker.tick(x=130, horizon=100, decision=0)
    assert len(pnl_tracker.pending_decisions) == 0, f"Expected 0 pending decisions after resolution, got {len(pnl_tracker.pending_decisions)}"
    assert len(pnl_tracker.pnl_data) == 2, f"Expected 2 PnL records, got {len(pnl_tracker.pnl_data)}"

    expected_pnl_second = 150 - 130 - pnl_tracker.epsilon
    actual_pnl_second = pnl_tracker.pnl_data[1]['pnl']
    assert actual_pnl_second == expected_pnl_second, f"Expected second PnL={expected_pnl_second}, got {actual_pnl_second}"

def test_sequential_decisions_and_partial_resolution():
    """Test sequential decisions and resolving them one by one."""
    pnl_tracker = Pnl(epsilon=0, backoff=10)

    pnl_tracker.tick(x=100, horizon=100, decision=1)
    assert len(pnl_tracker.pending_decisions) == 1, f"Expected 1 pending decision, got {len(pnl_tracker.pending_decisions)}"

    pnl_tracker.current_ndx = 50
    pnl_tracker.tick(x=110, horizon=150, decision=-1)
    assert len(pnl_tracker.pending_decisions) == 2, f"Expected 2 pending decisions, got {len(pnl_tracker.pending_decisions)}"

    pnl_tracker.current_ndx = 100
    pnl_tracker.tick(x=150, horizon=50, decision=0)
    assert len(pnl_tracker.pending_decisions) == 1, f"Expected 1 pending decision after partial resolution, got {len(pnl_tracker.pending_decisions)}"
    assert len(pnl_tracker.pnl_data) == 1, f"Expected 1 PnL record, got {len(pnl_tracker.pnl_data)}"

    expected_pnl_first = 150 - 100 - pnl_tracker.epsilon
    actual_pnl_first = pnl_tracker.pnl_data[0]['pnl']
    assert actual_pnl_first == expected_pnl_first, f"Expected first PnL={expected_pnl_first}, got {actual_pnl_first}"

    pnl_tracker.current_ndx = 200
    pnl_tracker.tick(x=100, horizon=50, decision=0)
    assert len(pnl_tracker.pending_decisions) == 0, f"Expected 0 pending decisions after full resolution, got {len(pnl_tracker.pending_decisions)}"
    assert len(pnl_tracker.pnl_data) == 2, f"Expected 2 PnL records, got {len(pnl_tracker.pnl_data)}"

    expected_pnl_second = 110 - 100 - pnl_tracker.epsilon
    actual_pnl_second = pnl_tracker.pnl_data[1]['pnl']
    assert actual_pnl_second == expected_pnl_second, f"Expected second PnL={expected_pnl_second}, got {actual_pnl_second}"

def test_sequential_resolutions_with_no_decision():
    """Test resolving decisions with no new decision being made."""
    pnl_tracker = Pnl(epsilon=0, backoff=10)

    pnl_tracker.tick(x=100, horizon=100, decision=1)
    assert len(pnl_tracker.pending_decisions) == 1, f"Expected 1 pending decision, got {len(pnl_tracker.pending_decisions)}"

    pnl_tracker.current_ndx = 100
    pnl_tracker.tick(x=150, horizon=100, decision=0)
    assert len(pnl_tracker.pending_decisions) == 0, f"Expected 0 pending decisions after resolution, got {len(pnl_tracker.pending_decisions)}"
    assert len(pnl_tracker.pnl_data) == 1, f"Expected 1 PnL record, got {len(pnl_tracker.pnl_data)}"
    expected_pnl = 150 - 100 - pnl_tracker.epsilon
    actual_pnl = pnl_tracker.pnl_data[0]['pnl']
    assert actual_pnl == expected_pnl, f"Expected PnL={expected_pnl}, got {actual_pnl}"

    pnl_tracker.current_ndx = 150
    pnl_tracker.tick(x=160, horizon=50, decision=0)
    assert len(pnl_tracker.pending_decisions) == 0, f"Expected 0 pending decisions, got {len(pnl_tracker.pending_decisions)}"
    assert len(pnl_tracker.pnl_data) == 1, f"Expected 1 PnL record, got {len(pnl_tracker.pnl_data)}"

def test_pnl_to_dict_no_backoff():
    pnl_tracker = Pnl(epsilon=0.01, backoff=0)
    pnl_tracker.tick(x=100, horizon=100, decision=1)
    pnl_tracker.tick(x=150, horizon=100, decision=-1)

    state = pnl_tracker.to_dict()

    assert state['epsilon'] == 0.01
    assert state['backoff'] == 0
    assert state['current_ndx'] == 2
    assert len(state['pending_decisions']) == 2
    assert state['pnl_data'] == []

def test_pnl_to_dict_with_backoff():
    pnl_tracker = Pnl(epsilon=0.01, backoff=10)
    pnl_tracker.tick(x=100, horizon=100, decision=1)
    pnl_tracker.tick(x=150, horizon=100, decision=-1)

    state = pnl_tracker.to_dict()

    assert state['epsilon'] == 0.01
    assert state['backoff'] == 10
    assert state['current_ndx'] == 2
    assert len(state['pending_decisions']) == 1
    assert state['pnl_data'] == []

def test_pnl_from_dict():
    state = {
        'epsilon': 0.01,
        'backoff': 50,
        'current_ndx': 2,
        'last_attack_ndx': 1,
        'pending_decisions': [
            {'index': 0, 'x': 100.0, 'horizon': 100, 'decision': 1.0},
            {'index': 1, 'x': 150.0, 'horizon': 100, 'decision': -1.0}
        ],
        'pnl_data': []
    }

    pnl_tracker = Pnl.from_dict(state)

    assert pnl_tracker.epsilon == 0.01
    assert pnl_tracker.backoff == 50
    assert pnl_tracker.current_ndx == 2
    assert pnl_tracker.last_attack_ndx == 1
    assert len(pnl_tracker.pending_decisions) == 2
    assert pnl_tracker.pnl_data == []

def test_pnl_reset():
    pnl_tracker = Pnl(epsilon=0.01, backoff=50)
    pnl_tracker.tick(x=100, horizon=100, decision=1)
    pnl_tracker.tick(x=150, horizon=100, decision=-1)

    pnl_tracker.reset_pnl()

    assert pnl_tracker.current_ndx == 0
    assert pnl_tracker.last_attack_ndx is None
    assert pnl_tracker.pending_decisions == []
    assert pnl_tracker.pnl_data == []

if __name__ == "__main__":
    pytest.main([__file__])
