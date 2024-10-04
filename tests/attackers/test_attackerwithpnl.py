
# endersgame/attackers/attackerwithpnl.py

# tests/attackers/test_attackerwithpnl.py

import pytest
from endersgame.attackers.attackerwithpnl import AttackerWithPnl
from endersgame.accounting.pnl import Pnl
from endersgame.attackers.baseattacker import BaseAttacker
from endersgame import EPSILON


class ConcreteAttackerWithPnl(AttackerWithPnl):

    def __init__(self, epsilon: float = EPSILON):
        super().__init__(epsilon=epsilon)

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
    return ConcreteAttackerWithPnl(epsilon=0.1)


def test_attackerwithpnl_to_dict(attacker_instance):
    """
    Test that the to_dict method correctly serializes the AttackerWithPnl instance.
    """
    # Simulate some ticks and predictions
    # Since tick and predict are simple pass and return 0, pnl remains default
    state = attacker_instance.to_dict()

    # Check that 'pnl' key exists
    assert 'pnl' in state

    # Verify pnl serialization
    pnl_state = state['pnl']
    assert isinstance(pnl_state, dict)
    assert pnl_state['epsilon'] == 0.1
    assert pnl_state['current_ndx'] == 0
    assert pnl_state['pending_decisions'] == []
    assert pnl_state['pnl_data'] == []

def test_attackerwithpnl_from_dict():
    """
    Test that the from_dict class method correctly deserializes the AttackerWithPnl instance.
    """
    # Create a sample state dictionary
    state = {
        'pnl': {
            'epsilon': 0.2,
            'backoff': 100,
            'current_ndx': 5,
            'last_attack_ndx': 3,
            'pending_decisions': [{'x': 100.0, 'horizon': 100, 'decision': 1.0, 'ndx': 0}],
            'pnl_data': [{'ndx': 5, 'pnl': 50.0}]
        }
    }

    # Deserialize to create a new instance using the concrete subclass
    attacker = ConcreteAttackerWithPnl.from_dict(state)

    # Verify the pnl attributes
    assert attacker.pnl.epsilon == 0.2
    assert attacker.pnl.current_ndx == 5
    assert attacker.pnl.pending_decisions == [{'x': 100.0, 'horizon': 100, 'decision': 1.0, 'ndx': 0}]
    assert attacker.pnl.pnl_data == [{'ndx': 5, 'pnl': 50.0}]


def test_attackerwithpnl_serialization_round_trip():
    """
    Test that serializing and then deserializing an AttackerWithPnl instance preserves its state.
    """
    # Create an instance and simulate some state changes
    attacker = ConcreteAttackerWithPnl(epsilon=0.3)
    attacker.pnl.tick(x=100.0, horizon=100, decision=1.0)
    attacker.pnl.tick(x=150.0, horizon=100, decision=0.0)  # Resolves the previous decision

    # Serialize to dict
    state = attacker.to_dict()

    # Deserialize to create a new instance
    restored_attacker = AttackerWithPnl.from_dict(state)

    # Verify that the restored attacker's pnl matches the original
    assert restored_attacker.pnl.epsilon == attacker.pnl.epsilon
    assert restored_attacker.pnl.current_ndx == attacker.pnl.current_ndx
    assert restored_attacker.pnl.pending_decisions == attacker.pnl.pending_decisions
    assert restored_attacker.pnl.pnl_data == attacker.pnl.pnl_data


def test_attackerwithpnl_from_dict_with_missing_pnl():
    """
    Test that from_dict handles missing 'pnl' key gracefully by initializing a default Pnl.
    """
    # Create a state dictionary without 'pnl'
    state = {}

    # Deserialize to create a new instance
    attacker = AttackerWithPnl.from_dict(state)

    # Verify that Pnl is initialized with default epsilon
    assert attacker.pnl.epsilon == EPSILON
    assert attacker.pnl.current_ndx == 0
    assert attacker.pnl.pending_decisions == []
    assert attacker.pnl.pnl_data == []


def test_attackerwithpnl_from_dict_with_partial_pnl():
    """
    Test that from_dict handles partially missing pnl data.
    """
    # Create a state dictionary with partial pnl data
    state = {
        'pnl': {
            'epsilon': 0.25,
            # 'current_ndx' is missing
            'pending_decisions': [{'x': 200.0, 'horizon': 100, 'decision': -1.0, 'ndx': 1}],
            # 'pnl_data' is missing
        }
    }

    # Deserialize to create a new instance
    attacker = AttackerWithPnl.from_dict(state)

    # Verify the pnl attributes
    assert attacker.pnl.epsilon == 0.25
    assert attacker.pnl.current_ndx == 0  # Default value
    assert attacker.pnl.pending_decisions == [{'x': 200.0, 'horizon': 100, 'decision': -1.0, 'ndx': 1}]
    assert attacker.pnl.pnl_data == []  # Default value


def test_attackerwithpnl_from_dict_with_malformed_pnl():
    """
    Test that from_dict raises an error or handles malformed pnl data.
    """
    # Create a state dictionary with malformed pnl data
    state = {
        'pnl': 'this should be a dict'
    }

    # Attempt to deserialize and expect an error
    with pytest.raises(AttributeError):
        AttackerWithPnl.from_dict(state)

