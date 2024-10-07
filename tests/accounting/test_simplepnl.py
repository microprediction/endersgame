from endersgame.accounting.pnl import Pnl


def test_initial_state():
    """Test if the initial state of the PnL class is correct."""
    pnl_tracker = Pnl(epsilon=0)
    assert pnl_tracker.current_ndx == 0, f"Expected current_ndx=0, got {pnl_tracker.current_ndx}"
    assert pnl_tracker.pending_decisions == [], f"Expected pending_decisions=[], got {pnl_tracker.pending_decisions}"
    assert pnl_tracker.pnl_data == [], f"Expected pnl_data=[], got {pnl_tracker.pnl_data}"

def test_tick_once():
    pnl_tracker = Pnl(epsilon=0)
    pnl_tracker.tick(x=1.0, horizon=7, decision=1)
    assert(len(pnl_tracker.pending_decisions)==1)


def test_record_and_resolve_decision():
    """Test recording and resolving a single decision."""
    pnl_tracker = Pnl(epsilon=0)

    # Step 1: Record a decision at step 0 (y = 100, decision = 1)
    pnl_tracker.tick(x=100, horizon=100, decision=1)
    assert len(
        pnl_tracker.pending_decisions) == 1, f"Expected 1 pending decision, got {len(pnl_tracker.pending_decisions)}"

    # Step 2: Move forward 100 steps and resolve the decision (y = 150)
    pnl_tracker.current_ndx = 100
    pnl_tracker.tick(x=150, horizon=100, decision=0)  # No new decision
    assert len(
        pnl_tracker.pending_decisions) == 0, f"Expected 0 pending decisions after resolution, got {len(pnl_tracker.pending_decisions)}"
    assert len(pnl_tracker.pnl_data) == 1, f"Expected 1 PnL record, got {len(pnl_tracker.pnl_data)}"
    expected_pnl = 150 - 100 - pnl_tracker.epsilon  # PnL = y_resolution - y_decision - epsilon
    actual_pnl = pnl_tracker.pnl_data[0][-1]
    assert actual_pnl == expected_pnl, f"Expected PnL={expected_pnl}, got {actual_pnl}"


def test_multiple_decisions_over_time():
    """Test multiple decisions being made and resolved over time."""
    pnl_tracker = Pnl(epsilon=0)

    # Step 1: Initial state check
    assert pnl_tracker.current_ndx == 0, f"Expected current_ndx=0, got {pnl_tracker.current_ndx}"
    assert pnl_tracker.pending_decisions == [], f"Expected pending_decisions=[], got {pnl_tracker.pending_decisions}"
    assert pnl_tracker.pnl_data == [], f"Expected pnl_data=[], got {pnl_tracker.pnl_data}"

    # Step 2: Record first decision at step 0 (y = 100, decision = 1)
    pnl_tracker.tick(x=100, horizon=100, decision=1)
    assert len(
        pnl_tracker.pending_decisions) == 1, f"Expected 1 pending decision, got {len(pnl_tracker.pending_decisions)}"

    # Step 3: Move forward by 50 steps without resolving (y = 120, decision = 0)
    pnl_tracker.current_ndx = 50
    pnl_tracker.tick(x=120, horizon=50, decision=0)
    assert len(
        pnl_tracker.pending_decisions) == 1, f"Expected 1 pending decision, got {len(pnl_tracker.pending_decisions)}"

    # Step 4: Move forward another 50 steps and resolve first decision (y = 150)
    pnl_tracker.current_ndx = 100
    pnl_tracker.tick(x=150, horizon=100, decision=0)
    assert len(
        pnl_tracker.pending_decisions) == 0, f"Expected 0 pending decisions after resolution, got {len(pnl_tracker.pending_decisions)}"
    assert len(pnl_tracker.pnl_data) == 1, f"Expected 1 PnL record, got {len(pnl_tracker.pnl_data)}"
    expected_pnl = 150 - 100 - pnl_tracker.epsilon  # PnL = y_resolution - y_decision - epsilon
    actual_pnl = pnl_tracker.pnl_data[0][-1]
    assert actual_pnl == expected_pnl, f"Expected PnL={expected_pnl}, got {actual_pnl}"

    # Step 5: Record second decision at step 100 (y = 150, decision = -1)
    pnl_tracker.tick(x=150, horizon=100, decision=-1)
    assert len(
        pnl_tracker.pending_decisions) == 1, f"Expected 1 pending decision, got {len(pnl_tracker.pending_decisions)}"

    # Step 6: Move forward 50 steps without resolving (y = 140)
    pnl_tracker.current_ndx = 150
    pnl_tracker.tick(x=140, horizon=50, decision=0)
    assert len(
        pnl_tracker.pending_decisions) == 1, f"Expected 1 pending decision, got {len(pnl_tracker.pending_decisions)}"

    # Step 7: Resolve second decision (y = 100)
    pnl_tracker.current_ndx = 200
    pnl_tracker.tick(x=130, horizon=100, decision=0)
    assert len(
        pnl_tracker.pending_decisions) == 0, f"Expected 0 pending decisions after resolution, got {len(pnl_tracker.pending_decisions)}"
    assert len(pnl_tracker.pnl_data) == 2, f"Expected 2 PnL records, got {len(pnl_tracker.pnl_data)}"

    # Calculate expected PnL for the second decision
    # Decision 2: Short => PnL = y_decision - y_resolution - epsilon = 110 - 100 - 0 = 10
    expected_pnl_second = 150 - 130 - pnl_tracker.epsilon
    actual_pnl_second = pnl_tracker.pnl_data[1][-1]
    assert actual_pnl_second == expected_pnl_second, f"Expected second PnL={expected_pnl_second}, got {actual_pnl_second}"


def test_sequential_decisions_and_partial_resolution():
    """Test sequential decisions and resolving them one by one."""
    pnl_tracker = Pnl(epsilon=0)
    pnl_tracker.backoff = 10  # Adjust backoff if necessary

    # Step 1: Record first decision
    pnl_tracker.tick(x=100, horizon=100, decision=1)  # Decision 1: Long
    assert len(
        pnl_tracker.pending_decisions) == 1, f"Expected 1 pending decision, got {len(pnl_tracker.pending_decisions)}"

    # Step 2: Record second decision with a larger horizon
    pnl_tracker.current_ndx = 50
    pnl_tracker.tick(x=110, horizon=150, decision=-1)  # Decision 2: Short (larger horizon)
    assert len(
        pnl_tracker.pending_decisions) == 2, f"Expected 2 pending decisions, got {len(pnl_tracker.pending_decisions)}"

    # Step 3: Resolve only the first decision (y = 150)
    pnl_tracker.current_ndx = 100
    pnl_tracker.tick(x=150, horizon=50, decision=0)
    assert len(
        pnl_tracker.pending_decisions) == 1, f"Expected 1 pending decision after partial resolution, got {len(pnl_tracker.pending_decisions)}"
    assert len(pnl_tracker.pnl_data) == 1, f"Expected 1 PnL record, got {len(pnl_tracker.pnl_data)}"

    # Calculate expected PnL for the first decision
    # Decision 1: Long => PnL = y_resolution - y_decision - epsilon = 150 - 100 - 0 = 50
    expected_pnl_first = 150 - 100 - pnl_tracker.epsilon
    actual_pnl_first = pnl_tracker.pnl_data[0][-1]
    assert actual_pnl_first == expected_pnl_first, f"Expected first PnL={expected_pnl_first}, got {actual_pnl_first}"

    # Step 4: Resolve the second decision (y = 100)
    pnl_tracker.current_ndx = 200
    pnl_tracker.tick(x=100, horizon=50, decision=0)
    assert len(
        pnl_tracker.pending_decisions) == 0, f"Expected 0 pending decisions after full resolution, got {len(pnl_tracker.pending_decisions)}"
    assert len(pnl_tracker.pnl_data) == 2, f"Expected 2 PnL records, got {len(pnl_tracker.pnl_data)}"

    # Calculate expected PnL for the second decision
    # Decision 2: Short => PnL = y_decision - y_resolution - epsilon = 110 - 100 - 0 = 10
    expected_pnl_second = 110 - 100 - pnl_tracker.epsilon
    actual_pnl_second = pnl_tracker.pnl_data[1][-1]
    assert actual_pnl_second == expected_pnl_second, f"Expected second PnL={expected_pnl_second}, got {actual_pnl_second}"


def test_sequential_resolutions_with_no_decision():
    """Test resolving decisions with no new decision being made."""
    pnl_tracker = Pnl(epsilon=0)
    pnl_tracker.backoff = 10  # Adjust backoff if necessary

    # Step 1: Record a decision (y = 100, decision = 1)
    pnl_tracker.tick(x=100, horizon=100, decision=1)
    assert len(
        pnl_tracker.pending_decisions) == 1, f"Expected 1 pending decision, got {len(pnl_tracker.pending_decisions)}"

    # Step 2: Move forward and resolve the decision (y = 150)
    pnl_tracker.current_ndx = 100
    pnl_tracker.tick(x=150, horizon=100, decision=0)  # No new decision
    assert len(
        pnl_tracker.pending_decisions) == 0, f"Expected 0 pending decisions after resolution, got {len(pnl_tracker.pending_decisions)}"
    assert len(pnl_tracker.pnl_data) == 1, f"Expected 1 PnL record, got {len(pnl_tracker.pnl_data)}"
    expected_pnl = 150 - 100 - pnl_tracker.epsilon  # PnL = y_resolution - y_decision - epsilon
    actual_pnl = pnl_tracker.pnl_data[0][-1]
    assert actual_pnl == expected_pnl, f"Expected PnL={expected_pnl}, got {actual_pnl}"

    # Step 3: Move forward with no decision (y = 160)
    pnl_tracker.current_ndx = 150
    pnl_tracker.tick(x=160, horizon=50, decision=0)  # No new decision
    assert len(
        pnl_tracker.pending_decisions) == 0, f"Expected 0 pending decisions, got {len(pnl_tracker.pending_decisions)}"
    assert len(pnl_tracker.pnl_data) == 1, f"Expected 1 PnL record, got {len(pnl_tracker.pnl_data)}"



# Running all tests using pytest
if __name__ == "__main__":
    import pytest
    pytest.main([__file__])

