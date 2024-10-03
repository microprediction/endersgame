from endersgame.accounting.pnl import Pnl

def test_pnl_to_dict():
    # Initialize and update PnL
    pnl = Pnl(epsilon=0.01, backoff=50)
    pnl.tick(5.0, horizon=10, decision=1.0)
    pnl.tick(6.0, horizon=10, decision=-1.0)

    # Serialize to dictionary
    state = pnl.to_dict()

    # Assert the serialized dictionary contains the correct state
    assert state == {
        'epsilon': 0.01,
        'backoff': 50,
        'current_ndx': pnl.current_ndx,
        'last_attack_ndx': pnl.last_attack_ndx,
        'pending_decisions': pnl.pending_decisions,
        'pnl_data': pnl.pnl_data
    }

def test_pnl_from_dict():
    # Define the serialized state
    state = {
        'epsilon': 0.01,
        'backoff': 50,
        'current_ndx': 2,
        'last_attack_ndx': 1,
        'pending_decisions': [(1, 5.0, 10, 1.0)],
        'pnl_data': [(1, 2, 10, 1.0, 5.0, 6.0, 0.99)]
    }

    # Deserialize into PnL
    restored_pnl = Pnl.from_dict(state)

    # Assert the restored object matches the expected state
    assert restored_pnl.epsilon == 0.01
    assert restored_pnl.backoff == 50
    assert restored_pnl.current_ndx == 2
    assert restored_pnl.last_attack_ndx == 1
    assert restored_pnl.pending_decisions == [(1, 5.0, 10, 1.0)]
    assert restored_pnl.pnl_data == [(1, 2, 10, 1.0, 5.0, 6.0, 0.99)]
