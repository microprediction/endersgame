from collections import defaultdict

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
    """Test a single decision with horizon=1.
    Decision ticked at idx=0
    Anchor the decision at idx=1 (the start value for the trade)
    Resolve the decision at idx=2 (the end value for the trade)
    """

    pnl_tracker = Pnl()
    pnl_tracker.tick(x=0., horizon=1, decision=1)
    assert len(pnl_tracker.pending_decisions) == 1, f"Expected 1 pending decision, got {len(pnl_tracker.pending_decisions)}"
    assert len(pnl_tracker.pnl_data) == 0, f"Expected 0 PnL records, got {len(pnl_tracker.pnl_data)}"

    pnl_tracker.tick(x=10.0)
    assert len(pnl_tracker.pending_decisions) == 1, f"Expected 1 pending decision, got {len(pnl_tracker.pending_decisions)}"
    assert len(pnl_tracker.pnl_data) == 0, f"Expected 0 PnL records, got {len(pnl_tracker.pnl_data)}"

    pnl_tracker.tick(x=50.0)
    assert len(pnl_tracker.pending_decisions) == 0, f"Expected 1 pending decision, got {len(pnl_tracker.pending_decisions)}"
    assert len(pnl_tracker.pnl_data) == 1, f"Expected 1 PnL record, got {len(pnl_tracker.pnl_data)}"
    expected_pnl = 50 - 10 - pnl_tracker.epsilon
    actual_pnl = pnl_tracker.pnl_data[0]['pnl']
    assert actual_pnl == expected_pnl, f"Expected PnL={expected_pnl}, got {actual_pnl}"


def test_tick_once():
    # value is index ^ 2
    horizon = 7
    pnl_tracker = Pnl()
    pnl_tracker.tick(x=0.0, horizon=horizon, decision=1)
    assert len(pnl_tracker.pending_decisions) == 1, f"Expected 1 pending decision, got {len(pnl_tracker.pending_decisions)}"
    # need "blank" horizon steps to resolve the decision
    for x in range(horizon):
        pnl_tracker.tick(x=float(1+x)**2)
        assert len(pnl_tracker.pending_decisions) == 1, f"Expected 0 pending decisions after resolution, got {len(pnl_tracker.pending_decisions)}"
    # tick the "resolution" step
    pnl_tracker.tick(x=float(1+horizon)**2)
    assert len(pnl_tracker.pending_decisions) == 0, f"Expected 0 pending decisions after resolution, got {len(pnl_tracker.pending_decisions)}"
    assert len(pnl_tracker.pnl_data) == 1, f"Expected 1 PnL record, got {len(pnl_tracker.pnl_data)}"
    expected_pnl = (1+horizon)**2 - 1.0 - pnl_tracker.epsilon
    actual_pnl = pnl_tracker.pnl_data[0]['pnl']
    assert actual_pnl == expected_pnl, f"Expected PnL={expected_pnl}, got {actual_pnl}"


def test_tick_twice_with_backoff():
    pnl_tracker = Pnl(backoff=10)
    pnl_tracker.tick(x=1.0, horizon=7, decision=1)
    pnl_tracker.tick(x=1.1, horizon=7, decision=1)  # Backoff prevents tracking
    assert len(pnl_tracker.pending_decisions) == 1, f"Expected 1 pending decision, got {len(pnl_tracker.pending_decisions)}"

def test_tick_twice_no_backoff():
    pnl_tracker = Pnl(backoff=1)
    pnl_tracker.tick(x=1.0, horizon=7, decision=1)
    pnl_tracker.tick(x=1.1, horizon=7, decision=1)
    assert len(pnl_tracker.pending_decisions) == 2, f"Expected 2 pending decisions, got {len(pnl_tracker.pending_decisions)}"

def test_multiple_decisions_over_time():
    """Test multiple decisions being made and resolved over time."""
    pnl_tracker = Pnl(backoff=0)
    decision_ndx = {0: (1, 5), 5: (-1, 10), 10: (1, 7), 15: (-1, 3)}
    end_ndx = 15+3+1 # max decision_ndx + horizon + 1
    expected_pnl = {}
    for ndx, (decision, horizon) in decision_ndx.items():
        expected_pnl[ndx + horizon + 1] = decision*(float(ndx + horizon + 1)**2 - float(ndx + 1)**2) - pnl_tracker.epsilon
    for ndx in range(end_ndx+1):
        x = float(ndx)**2
        if ndx in decision_ndx:
            decision, horizon = decision_ndx[ndx]
            pnl_tracker.tick(x=x, horizon=horizon, decision=decision)
        else:
            pnl_tracker.tick(x=x)
        if ndx in expected_pnl:
            # get the latest one
            pnl_data = pnl_tracker.pnl_data[-1]
            assert pnl_data['pnl'] == expected_pnl[ndx], f"Expected PnL={expected_pnl[ndx]}, got {pnl_data['pnl']}"
            del expected_pnl[ndx]
    assert expected_pnl == {}, f"Expected all PnL records to be resolved, got {len(expected_pnl)} unresolved"



def test_periodic_decisions():
    horizon = 10
    pnl_tracker = Pnl(epsilon=0, backoff=0)

    # Do some very timple bookkeeping to ensure that the pending decisions are being tracked correctly
    def run_test(decision_period, num_steps):
        pnl_tracker.reset_pnl()
        decision_times = defaultdict(int)
        for i in range(num_steps):
            decision = 1 if i % decision_period == 0 else 0
            pnl_tracker.tick(x=i, horizon=horizon, decision=decision)
            if i in decision_times:
                # cleanup:
                del decision_times[i]

            if decision  != 0:
                decision_times[i+horizon+1] += 1 # +1 because we need 1 to anchor

            expected_pending = sum(v for v in decision_times.values())
            actual_pending = len(pnl_tracker.pending_decisions)
            assert actual_pending == expected_pending, \
                f"Step {i}: Expected {expected_pending} pending decision(s), got {actual_pending}"

    # Test cases
    run_test(decision_period=5, num_steps=30)  # Period smaller than horizon
    run_test(decision_period=10, num_steps=30) # Period equal to horizon
    run_test(decision_period=15, num_steps=45) # Period larger than horizon



def test_periodic_decisions_with_backoff():
    horizon = 10
    backoff = 3
    pnl_tracker = Pnl(epsilon=0, backoff=backoff)

    def run_test(decision_period, num_steps):
        pnl_tracker.reset_pnl()
        decision_times = defaultdict(int)
        last_decision_time = -float('inf')
        for i in range(num_steps):
            decision = 1 if i % decision_period == 0 and i - last_decision_time >= backoff else 0
            pnl_tracker.tick(x=i, horizon=horizon, decision=decision)

            if i in decision_times:
                del decision_times[i]

            if decision != 0:
                decision_times[i+horizon+1] += 1 # +1 because we need 1 to anchor
                last_decision_time = i

            expected_pending = sum(v for v in decision_times.values())
            actual_pending = len(pnl_tracker.pending_decisions)
            assert actual_pending == expected_pending, \
                f"Step {i}: Expected {expected_pending} pending decision(s), got {actual_pending}"

            print(f"Period: {decision_period}, Step: {i}, Pending: {actual_pending}")

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
