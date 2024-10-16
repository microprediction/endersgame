# tests/accounting/test_historymixin.py

import pytest
import json
from collections import deque
from midone.mixins.historymixin import HistoryMixin  # Adjust the import path as needed


class DummyClass(HistoryMixin):
    """
    A dummy class to inherit from HistoryMixin for testing purposes.
    """

    def __init__(self, max_history_len=200):
        super().__init__(max_history_len=max_history_len)


@pytest.fixture
def dummy_instance():
    """
    Fixture to create a DummyClass instance for testing.
    """
    return DummyClass()


def test_initialization_default(dummy_instance):
    """
    Test the default initialization of HistoryMixin.
    """
    assert dummy_instance.max_history_len == 200
    assert isinstance(dummy_instance.history, deque)
    assert dummy_instance.history.maxlen == 200
    assert len(dummy_instance.history) == 0


def test_initialization_custom():
    """
    Test custom initialization of HistoryMixin with a different max_history_len.
    """
    custom_len = 100
    instance = DummyClass(max_history_len=custom_len)
    assert instance.max_history_len == custom_len
    assert instance.history.maxlen == custom_len
    assert len(instance.history) == 0


def test_tick_history(dummy_instance):
    """
    Test adding elements to the history.
    """
    dummy_instance.tick_history(1.0)
    dummy_instance.tick_history(2.0)
    dummy_instance.tick_history(3.0)
    assert list(dummy_instance.history) == [1.0, 2.0, 3.0]


def test_tick_history_with_conversion(dummy_instance):
    """
    Test that non-float inputs are coerced to float.
    """
    dummy_instance.tick_history("4.5")  # String that can be converted to float
    dummy_instance.tick_history("invalid")  # String that cannot be converted to float
    dummy_instance.tick_history(None)  # NoneType
    assert list(dummy_instance.history) == [4.5, 0.0, 0.0]


def test_history_maxlen():
    """
    Test that the history does not exceed max_history_len.
    """
    max_len = 5
    instance = DummyClass(max_history_len=max_len)
    for i in range(10):
        instance.tick_history(float(i))
    assert len(instance.history) == max_len
    assert list(instance.history) == [5.0, 6.0, 7.0, 8.0, 9.0]


def test_get_recent_history(dummy_instance):
    """
    Test retrieving the most recent n history elements.
    """
    for i in range(5):
        dummy_instance.tick_history(float(i))
    recent = dummy_instance.get_recent_history(3)
    assert recent == [2.0, 3.0, 4.0]


def test_get_recent_history_more_than_available(dummy_instance):
    """
    Test retrieving more history elements than available.
    """
    for i in range(3):
        dummy_instance.tick_history(float(i))
    recent = dummy_instance.get_recent_history(5)
    assert recent == [0.0, 1.0, 2.0]


def test_len(dummy_instance):
    """
    Test the __len__ method.
    """
    assert len(dummy_instance) == 0
    dummy_instance.tick_history(1.0)
    dummy_instance.tick_history(2.0)
    assert len(dummy_instance) == 2


def test_is_history_full_false(dummy_instance):
    """
    Test is_history_full method when history is not full.
    """
    for i in range(3):
        dummy_instance.tick_history(float(i))
    assert not dummy_instance.is_history_full()


def test_is_history_full_true():
    """
    Test is_history_full method when history is full.
    """
    max_len = 4
    instance = DummyClass(max_history_len=max_len)
    for i in range(max_len):
        instance.tick_history(float(i))
    assert instance.is_history_full()


def test_to_dict(dummy_instance):
    """
    Test the to_dict method for correct serialization.
    """
    dummy_instance.tick_history(1.0)
    dummy_instance.tick_history(2.0)
    state = dummy_instance.to_dict()

    expected_state = {
        'max_history_len': 200,
        'history': [1.0, 2.0]
    }

    assert state == expected_state


def test_from_dict():
    """
    Test the from_dict method for correct deserialization.
    """
    state = {
        'max_history_len': 5,
        'history': [1.0, 2.0, 3.0]
    }
    instance = HistoryMixin.from_dict(state)

    assert instance.max_history_len == 5
    assert isinstance(instance.history, deque)
    assert instance.history.maxlen == 5
    assert list(instance.history) == [1.0, 2.0, 3.0]


def test_from_dict_with_non_float_history():
    """
    Test that from_dict handles non-float history entries by coercing them to float.
    """
    state = {
        'max_history_len': 3,
        'history': [1.0, "2.5", "invalid", None]
    }
    instance = HistoryMixin.from_dict(state)

    # "2.5" should be converted to 2.5, "invalid" and None should be converted to 0.0
    assert list(instance.history) == [2.5, 0.0, 0.0]


def test_round_trip_serialization(dummy_instance):
    """
    Test that serializing to dict and then deserializing back maintains state.
    """
    for i in range(3):
        dummy_instance.tick_history(float(i))
    state = dummy_instance.to_dict()

    # Serialize to JSON string
    json_string = json.dumps(state)

    # Deserialize back to dict
    state_from_json = json.loads(json_string)

    # Create a new instance from the deserialized dict
    restored_instance = HistoryMixin.from_dict(state_from_json)

    assert restored_instance.max_history_len == dummy_instance.max_history_len
    assert list(restored_instance.history) == list(dummy_instance.history)


def test_full_round_trip_serialization():
    """
    Comprehensive round-trip test: serialize, deserialize, modify, serialize again, and compare.
    """
    # Initialize instance with a smaller max_history_len for testing
    initial_state = {
        'max_history_len': 3,
        'history': [1.0, 2.0, 3.0]
    }

    # Serialize to JSON
    json_string = json.dumps(initial_state)

    # Deserialize from JSON
    state_from_json = json.loads(json_string)
    instance = HistoryMixin.from_dict(state_from_json)

    # Verify initial state
    assert instance.max_history_len == 3
    assert list(instance.history) == [1.0, 2.0, 3.0]

    # Modify the history
    instance.tick_history(4.0)
    instance.tick_history(5.0)

    # Serialize again
    new_state = instance.to_dict()
    expected_new_history = [3.0, 4.0, 5.0]
    assert new_state['history'] == expected_new_history
    assert new_state['max_history_len'] == 3

    # Ensure the history length is still max_history_len
    assert len(instance.history) == 3
    assert instance.is_history_full()


def test_empty_history_serialization():
    """
    Test serialization and deserialization when history is empty.
    """
    instance = DummyClass(max_history_len=10)
    state = instance.to_dict()

    expected_state = {
        'max_history_len': 10,
        'history': []
    }

    assert state == expected_state

    # Deserialize
    restored_instance = HistoryMixin.from_dict(state)
    assert restored_instance.max_history_len == 10
    assert len(restored_instance.history) == 0
    assert list(restored_instance.history) == []


def test_history_with_non_float_values():
    """
    Test that non-float values are handled correctly by coercing to float.
    """
    instance = DummyClass(max_history_len=5)
    instance.tick_history("4.5")  # String that can be converted to float
    instance.tick_history("invalid")  # String that cannot be converted to float
    instance.tick_history(None)  # NoneType
    assert list(instance.history) == [4.5, 0.0, 0.0]


def test_partial_history_retrieval(dummy_instance):
    """
    Test retrieving history when only part of the history is filled.
    """
    dummy_instance.tick_history(10.0)
    dummy_instance.tick_history(20.0)
    recent = dummy_instance.get_recent_history(1)
    assert recent == [20.0]


def test_history_full_behavior():
    """
    Test behavior when history is full, ensuring old entries are removed.
    """
    max_len = 3
    instance = DummyClass(max_history_len=max_len)
    instance.tick_history(1.0)
    instance.tick_history(2.0)
    instance.tick_history(3.0)
    assert list(instance.history) == [1.0, 2.0, 3.0]

    # Add another entry, should remove the oldest (1.0)
    instance.tick_history(4.0)
    assert list(instance.history) == [2.0, 3.0, 4.0]


def test_history_persistence_after_serialization(dummy_instance):
    """
    Ensure that history persists correctly after multiple serializations and deserializations.
    """
    dummy_instance.tick_history(1.0)
    dummy_instance.tick_history(2.0)
    dummy_instance.tick_history(3.0)

    # First serialization
    state1 = dummy_instance.to_dict()
    json1 = json.dumps(state1)
    state1_deserialized = json.loads(json1)
    restored1 = HistoryMixin.from_dict(state1_deserialized)

    assert restored1.max_history_len == dummy_instance.max_history_len
    assert list(restored1.history) == list(dummy_instance.history)

    # Modify original and serialize again
    dummy_instance.tick_history(4.0)
    state2 = dummy_instance.to_dict()
    json2 = json.dumps(state2)
    state2_deserialized = json.loads(json2)
    restored2 = HistoryMixin.from_dict(state2_deserialized)

    assert list(restored2.history) == [1.0, 2.0, 3.0, 4.0]


if __name__=='__main__':
    import pytest
    pytest.main(__file__)
