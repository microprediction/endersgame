# endersgame/attackers/testattacker.py

from typing import Dict, Any
import pytest
from endersgame.attackers.baseattacker import BaseAttacker
from endersgame.gameconfig import HORIZON

class TestAttacker(BaseAttacker):
    """
    A simple concrete subclass of BaseAttacker for testing purposes.
    """

    def __init__(self, parameter: float = 0.0):
        super().__init__()
        self.parameter = parameter

    def tick(self, x: float):
        """
        Simple implementation that increments the parameter.
        """
        self.parameter += x

    def predict(self, horizon: int = HORIZON) -> float:
        """
        Simple predict implementation based on the parameter.
        """
        if self.parameter > 10:
            return 1.0  # Up
        elif self.parameter < -10:
            return -1.0  # Down
        else:
            return 0.0  # Neither

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize the TestAttacker's state.
        """
        state = super().to_dict()
        state.update({
            'parameter': self.parameter
        })
        return state

    @classmethod
    def from_dict(cls, state: Dict[str, Any]) -> 'TestAttacker':
        """
        Deserialize a dictionary to create a TestAttacker instance.
        """
        # Create a new instance without invoking __init__
        attacker = super().from_dict(state)
        # Manually set the 'parameter' attribute
        attacker.parameter = state.get('parameter', 0.0)
        return attacker



# endersgame/tests/attackers/test_baseattacker.py


def test_testattacker_instantiation():
    """
    Test that the TestAttacker can be instantiated correctly.
    """
    attacker = TestAttacker(parameter=5.0)
    assert isinstance(attacker, TestAttacker)
    assert attacker.parameter == 5.0

def test_testattacker_tick():
    """
    Test the tick method of TestAttacker.
    """
    attacker = TestAttacker(parameter=5.0)
    attacker.tick(3.0)
    assert attacker.parameter == 8.0

    attacker.tick(-20.0)
    assert attacker.parameter == -12.0

def test_testattacker_predict():
    """
    Test the predict method of TestAttacker.
    """
    attacker = TestAttacker(parameter=0.0)
    assert attacker.predict() == 0.0

    attacker.parameter = 15.0
    assert attacker.predict() == 1.0

    attacker.parameter = -15.0
    assert attacker.predict() == -1.0

def test_testattacker_tick_and_predict():
    """
    Test the tick_and_predict method of TestAttacker.
    """
    attacker = TestAttacker(parameter=0.0)
    decision = attacker.tick_and_predict(x=12.0)
    assert attacker.parameter == 12.0
    assert decision == 1.0

    decision = attacker.tick_and_predict(x=-25.0)
    assert attacker.parameter == -13.0
    assert decision == -1.0

    decision = attacker.tick_and_predict(x=5.0)
    assert attacker.parameter == -8.0
    assert decision == 0.0

def test_testattacker_to_dict():
    """
    Test the serialization (to_dict) of TestAttacker.
    """
    attacker = TestAttacker(parameter=7.5)
    state = attacker.to_dict()
    expected_state = {
        'parameter': 7.5
    }
    assert state == expected_state

def test_testattacker_from_dict():
    """
    Test the deserialization (from_dict) of TestAttacker.
    """
    state = {
        'parameter': -10.0
    }
    attacker = TestAttacker.from_dict(state)
    assert isinstance(attacker, TestAttacker)
    assert attacker.parameter == -10.0

def test_testattacker_full_serialization_cycle():
    """
    Test the full serialization and deserialization cycle of TestAttacker.
    """
    attacker = TestAttacker(parameter=3.5)
    attacker.tick(2.5)  # parameter should now be 6.0
    attacker.tick(-10.0)  # parameter should now be -4.0

    state = attacker.to_dict()
    expected_state = {
        'parameter': -4.0
    }
    assert state == expected_state

    new_attacker = TestAttacker.from_dict(state)
    assert isinstance(new_attacker, TestAttacker)
    assert new_attacker.parameter == -4.0
