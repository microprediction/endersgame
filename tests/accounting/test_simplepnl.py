from endersgame.accounting.simplepnl import SimplePnL


def test_initial_state():
    """Test if the initial state of the SimplePnL class is correct."""
    pnl_tracker = SimplePnL()
    assert pnl_tracker.simplepnl["current_ndx"] == 0
    assert pnl_tracker.simplepnl["pending_decisions"] == []
    assert pnl_tracker.simplepnl["pnl_data"] == []


def test_record_and_resolve_decision():
    """Test recording and resolving a single decision."""
    pnl_tracker = SimplePnL()

    # Step 1: Record a decision at step 0 (y = 100, decision = 1)
    pnl_tracker.tick_pnl(x=100, k=100, decision=1)
    assert len(pnl_tracker.simplepnl["pending_decisions"]) == 1

    # Step 2: Move forward 100 steps and resolve the decision (y = 150)
    pnl_tracker.simplepnl["current_ndx"] = 100
    pnl_tracker.tick_pnl(x=150, k=100, decision=0)  # No new decision
    assert len(pnl_tracker.simplepnl["pending_decisions"]) == 0
    assert len(pnl_tracker.simplepnl["pnl_data"]) == 1
    assert pnl_tracker.simplepnl["pnl_data"][0][-1] == 50  # PnL = 150 - 100



def test_multiple_decisions_over_time():
    """Test multiple decisions being made and resolved over time."""
    pnl_tracker = SimplePnL()

    # Step 1: Initial state check
    assert pnl_tracker.simplepnl["current_ndx"] == 0
    assert pnl_tracker.simplepnl["pending_decisions"] == []
    assert pnl_tracker.simplepnl["pnl_data"] == []

    # Step 2: Record first decision at step 0 (y = 100, decision = 1)
    pnl_tracker.tick_pnl(x=100, k=100, decision=1)
    assert len(pnl_tracker.simplepnl["pending_decisions"]) == 1

    # Step 3: Move forward by 50 steps without resolving (y = 120, decision = 0)
    pnl_tracker.simplepnl["current_ndx"] = 50
    pnl_tracker.tick_pnl(x=120, k=50, decision=0)
    assert len(pnl_tracker.simplepnl["pending_decisions"]) == 1  # Still pending

    # Step 4: Move forward another 50 steps and resolve first decision (y = 150)
    pnl_tracker.simplepnl["current_ndx"] = 100
    pnl_tracker.tick_pnl(x=150, k=100, decision=0)
    assert len(pnl_tracker.simplepnl["pending_decisions"]) == 0  # First decision resolved
    assert len(pnl_tracker.simplepnl["pnl_data"]) == 1
    assert pnl_tracker.simplepnl["pnl_data"][0][-1] == 50  # PnL = 150 - 100

    # Step 5: Record second decision at step 100 (y = 150, decision = -1)
    pnl_tracker.tick_pnl(x=150, k=100, decision=-1)
    assert len(pnl_tracker.simplepnl["pending_decisions"]) == 1

    # Step 6: Move forward 50 steps without resolving (y = 140)
    pnl_tracker.simplepnl["current_ndx"] = 150
    pnl_tracker.tick_pnl(x=140, k=50, decision=0)
    assert len(pnl_tracker.simplepnl["pending_decisions"]) == 1  # Still pending

    # Step 7: Resolve second decision (y = 100)
    pnl_tracker.simplepnl["current_ndx"] = 200
    pnl_tracker.tick_pnl(x=100, k=100, decision=0)
    assert len(pnl_tracker.simplepnl["pending_decisions"]) == 0  # Second decision resolved
    assert len(pnl_tracker.simplepnl["pnl_data"]) == 2
    assert pnl_tracker.simplepnl["pnl_data"][1][-1] == 50  # PnL = 150 - 100 (short)


def test_sequential_decisions_and_partial_resolution():
    """Test sequential decisions and resolving them one by one."""
    pnl_tracker = SimplePnL()
    pnl_tracker.simplepnl['backoff'] = 10

    # Step 1: Record first decision
    pnl_tracker.tick_pnl(x=100, k=100, decision=1)  # Decision 1: Long
    assert len(pnl_tracker.simplepnl["pending_decisions"]) == 1

    # Step 2: Record second decision with a larger horizon
    pnl_tracker.simplepnl["current_ndx"] = 50
    pnl_tracker.tick_pnl(x=110, k=150, decision=-1)  # Decision 2: Short (larger horizon)
    assert len(pnl_tracker.simplepnl["pending_decisions"]) == 2

    # Step 3: Resolve only the first decision (y = 150)
    pnl_tracker.simplepnl["current_ndx"] = 100
    pnl_tracker.tick_pnl(x=150, k=50, decision=0)
    assert len(pnl_tracker.simplepnl["pending_decisions"]) == 1  # One decision remains

    # Step 4: Resolve the second decision (y = 100)
    pnl_tracker.simplepnl["current_ndx"] = 200
    pnl_tracker.tick_pnl(x=100, k=50, decision=0)
    assert len(pnl_tracker.simplepnl["pending_decisions"]) == 0  # All decisions resolved


def test_sequential_resolutions_with_no_decision():
    """Test resolving decisions with no new decision being made."""
    pnl_tracker = SimplePnL()
    pnl_tracker.simplepnl['backoff'] = 10

    # Step 1: Record a decision (y = 100, decision = 1)
    pnl_tracker.tick_pnl(x=100, k=100, decision=1)
    assert len(pnl_tracker.simplepnl["pending_decisions"]) == 1

    # Step 2: Move forward and resolve the decision (y = 150)
    pnl_tracker.simplepnl["current_ndx"] = 100
    pnl_tracker.tick_pnl(x=150, k=100, decision=0)  # No new decision
    assert len(pnl_tracker.simplepnl["pending_decisions"]) == 0  # Decision resolved
    assert len(pnl_tracker.simplepnl["pnl_data"]) == 1
    assert pnl_tracker.simplepnl["pnl_data"][0][-1] == 50  # PnL = 150 - 100

    # Step 3: Move forward with no decision (y = 160)
    pnl_tracker.simplepnl["current_ndx"] = 150
    pnl_tracker.tick_pnl(x=160, k=50, decision=0)  # No new decision
    assert len(pnl_tracker.simplepnl["pending_decisions"]) == 0  # No decisions pending
    assert len(pnl_tracker.simplepnl["pnl_data"]) == 1  # No additional PnL
