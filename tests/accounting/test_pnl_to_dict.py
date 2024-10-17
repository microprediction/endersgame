import pytest
from midone.accounting.pnl import Pnl

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

    # Additional checks for the structure of pending_decisions and pnl_data
    assert isinstance(state['pending_decisions'], list)
    for decision in state['pending_decisions']:
        assert isinstance(decision, dict)
        assert 'index' in decision
        assert 'x' in decision
        assert 'horizon' in decision
        assert 'decision' in decision

    assert isinstance(state['pnl_data'], list)
    for pnl_entry in state['pnl_data']:
        assert isinstance(pnl_entry, dict)
        assert 'decision_ndx' in pnl_entry
        assert 'resolution_ndx' in pnl_entry
        assert 'horizon' in pnl_entry
        assert 'decision' in pnl_entry
        assert 'y_decision' in pnl_entry
        assert 'y_resolution' in pnl_entry
        assert 'pnl' in pnl_entry

def test_pnl_from_dict():
    # Define the serialized state
    state = {
        'epsilon': 0.01,
        'backoff': 50,
        'current_ndx': 2,
        'last_attack_ndx': 1,
        'pending_decisions': [
            {'index': 1, 'x': 5.0, 'horizon': 10, 'decision': 1.0}
        ],
        'pnl_data': [
            {
                'decision_ndx': 1,
                'resolution_ndx': 2,
                'horizon': 10,
                'decision': 1.0,
                'y_decision': 5.0,
                'y_resolution': 6.0,
                'pnl': 0.99
            }
        ]
    }

    # Deserialize into PnL
    restored_pnl = Pnl.from_dict(state)

    # Assert the restored object matches the expected state
    assert restored_pnl.epsilon == 0.01
    assert restored_pnl.backoff == 50
    assert restored_pnl.current_ndx == 2
    assert restored_pnl.last_attack_ndx == 1
    assert restored_pnl.pending_decisions == [
        {'index': 1, 'x': 5.0, 'horizon': 10, 'decision': 1.0}
    ]
    assert restored_pnl.pnl_data == [
        {
            'decision_ndx': 1,
            'resolution_ndx': 2,
            'horizon': 10,
            'decision': 1.0,
            'y_decision': 5.0,
            'y_resolution': 6.0,
            'pnl': 0.99
        }
    ]

if __name__ == "__main__":
    pytest.main([__file__])
