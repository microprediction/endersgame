# tests/attackers/test_attackerwithpnl.py

import pytest
from midone.attackers.attackerwithpnl import AttackerWithPnl
from midone.accounting.pnl import Pnl
from midone.attackers.baseattacker import BaseAttacker
from midone import EPSILON, DEFAULT_TRADE_BACKOFF

class ConcreteAttackerWithPnl(AttackerWithPnl):
    def __init__(self, epsilon: float = EPSILON, backoff: int = DEFAULT_TRADE_BACKOFF):
        super().__init__(epsilon=epsilon, backoff=backoff)

    def tick(self, x):
        # Simple implementation for testing
        pass

    def predict(self, horizon: int = 100) -> float:
        # Simple implementation for testing
        return 0.0

@pytest.fixture
def attacker_instance():
    """
    Fixture to create an instance of ConcreteAttackerWithPnl for testing.
    """
    return ConcreteAttackerWithPnl(epsilon=0.1, backoff=50)

def test_attackerwithpnl_initialization(attacker_instance):
    """
    Test the initialization of AttackerWithPnl.
    """
    assert isinstance(attacker_instance.pnl, Pnl)
    assert attacker_instance.pnl.epsilon == 0.1
    assert attacker_instance.pnl.backoff == 50

def test_attackerwithpnl_to_dict(attacker_instance):
    """
    Test that the to_dict method correctly serializes the AttackerWithPnl instance.
    """
    state = attacker_instance.to_dict()

    assert 'pnl' in state
    pnl_state = state['pnl']
    assert isinstance(pnl_state, dict)
    assert pnl_state['epsilon'] == 0.1
    assert pnl_state['backoff'] == 50
    assert pnl_state['current_ndx'] == 0
    assert pnl_state['pending_decisions'] == []
    assert pnl_state['pnl_data'] == []

def test_attackerwithpnl_from_dict():
    """
    Test that the from_dict class method correctly deserializes the AttackerWithPnl instance.
    """
    state = {
        'pnl': {
            'epsilon': 0.2,
            'backoff': 100,
            'current_ndx': 5,
            'last_attack_ndx': 3,
            'pending_decisions': [
                {'index': 0, 'x': 100.0, 'horizon': 100, 'decision': 1.0}
            ],
            'pnl_data': [
                {
                    'decision_ndx': 5,
                    'resolution_ndx': 10,
                    'horizon': 100,
                    'decision': 1.0,
                    'y_decision': 100.0,
                    'y_resolution': 150.0,
                    'pnl': 50.0
                }
            ]
        }
    }

    attacker = ConcreteAttackerWithPnl.from_dict(state)

    assert attacker.pnl.epsilon == 0.2
    assert attacker.pnl.backoff == 100
    assert attacker.pnl.current_ndx == 5
    assert attacker.pnl.pending_decisions == [
        {'index': 0, 'x': 100.0, 'horizon': 100, 'decision': 1.0}
    ]
    assert attacker.pnl.pnl_data == [
        {
            'decision_ndx': 5,
            'resolution_ndx': 10,
            'horizon': 100,
            'decision': 1.0,
            'y_decision': 100.0,
            'y_resolution': 150.0,
            'pnl': 50.0
        }
    ]

def test_attackerwithpnl_serialization_round_trip():
    """
    Test that serializing and then deserializing an AttackerWithPnl instance preserves its state.
    """
    attacker = ConcreteAttackerWithPnl(epsilon=0.3, backoff=75)
    attacker.pnl.tick(x=100.0, horizon=100, decision=1.0)
    attacker.pnl.tick(x=150.0, horizon=100, decision=0.0)  # Resolves the previous decision

    state = attacker.to_dict()
    restored_attacker = AttackerWithPnl.from_dict(state)

    assert restored_attacker.pnl.epsilon == attacker.pnl.epsilon
    assert restored_attacker.pnl.backoff == attacker.pnl.backoff
    assert restored_attacker.pnl.current_ndx == attacker.pnl.current_ndx
    assert restored_attacker.pnl.pending_decisions == attacker.pnl.pending_decisions
    assert restored_attacker.pnl.pnl_data == attacker.pnl.pnl_data

def test_attackerwithpnl_from_dict_with_missing_pnl():
    """
    Test that from_dict handles missing 'pnl' key gracefully by initializing a default Pnl.
    """
    state = {}
    attacker = AttackerWithPnl.from_dict(state)

    assert attacker.pnl.epsilon == EPSILON
    assert attacker.pnl.backoff == DEFAULT_TRADE_BACKOFF
    assert attacker.pnl.current_ndx == 0
    assert attacker.pnl.pending_decisions == []
    assert attacker.pnl.pnl_data == []

def test_attackerwithpnl_from_dict_with_partial_pnl():
    """
    Test that from_dict handles partially missing pnl data.
    """
    state = {
        'pnl': {
            'epsilon': 0.25,
            'backoff': 80,
            'pending_decisions': [
                {'index': 1, 'x': 200.0, 'horizon': 100, 'decision': -1.0}
            ],
        }
    }

    attacker = AttackerWithPnl.from_dict(state)

    assert attacker.pnl.epsilon == 0.25
    assert attacker.pnl.backoff == 80
    assert attacker.pnl.current_ndx == 0  # Default value
    assert attacker.pnl.pending_decisions == [
        {'index': 1, 'x': 200.0, 'horizon': 100, 'decision': -1.0}
    ]
    assert attacker.pnl.pnl_data == []  # Default value

def test_attackerwithpnl_from_dict_with_malformed_pnl():
    """
    Test that from_dict raises an error or handles malformed pnl data.
    """
    state = {
        'pnl': 'this should be a dict'
    }

    with pytest.raises(AttributeError):
        AttackerWithPnl.from_dict(state)

if __name__ == "__main__":
    pytest.main([__file__])
