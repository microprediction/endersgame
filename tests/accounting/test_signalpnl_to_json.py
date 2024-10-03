

import pytest
import json
from endersgame.accounting.stdsignalpnl import StdSignalPnl


def test_stdsignalpnl_to_dict():
    # Initialize and update StdSignalPnl
    std_signal_pnl = StdSignalPnl(fading_factor=0.01)
    std_signal_pnl.tick(5.0, horizon=10, signal=1.0)
    std_signal_pnl.tick(6.0, horizon=10, signal=-1.0)

    # Serialize to dictionary
    state = std_signal_pnl.to_dict()

    # Assert the serialized dictionary contains the correct state
    assert state['current_standardized_signal'] == std_signal_pnl.current_standardized_signal
    assert state['current_ndx'] == std_signal_pnl.current_ndx
    assert state['thresholds'] == std_signal_pnl.thresholds  # Now handled as list of floats
    assert state['epsilon'] == std_signal_pnl.epsilon
    assert 'signal_var' in state
    assert 'pnl' in state

    # Additional assertions to verify signal_var and pnl structures
    assert state['signal_var']['fading_factor'] == std_signal_pnl.signal_var.fading_factor
    assert state['signal_var']['ewa'] == std_signal_pnl.signal_var.ewa
    assert state['signal_var']['ewv'] == std_signal_pnl.signal_var.ewv
    assert state['signal_var']['weight_sum'] == std_signal_pnl.signal_var.weight_sum

    for threshold in std_signal_pnl.thresholds:
        assert threshold in state['pnl']
        pnl_entry = state['pnl'][threshold]
        assert 'positive' in pnl_entry
        assert 'negative' in pnl_entry

        # Check positive side
        positive_pnl = pnl_entry['positive']
        assert 'ewa_pnl' in positive_pnl
        assert 'pending_signals' in positive_pnl
        assert positive_pnl['ewa_pnl']['fading_factor'] == std_signal_pnl.pnl[threshold]['positive']['ewa_pnl'].fading_factor
        assert positive_pnl['ewa_pnl']['ewa'] == std_signal_pnl.pnl[threshold]['positive']['ewa_pnl'].ewa
        assert positive_pnl['ewa_pnl']['weight_sum'] == std_signal_pnl.pnl[threshold]['positive']['ewa_pnl'].weight_sum

        # Check negative side
        negative_pnl = pnl_entry['negative']
        assert 'ewa_pnl' in negative_pnl
        assert 'pending_signals' in negative_pnl
        assert negative_pnl['ewa_pnl']['fading_factor'] == std_signal_pnl.pnl[threshold]['negative']['ewa_pnl'].fading_factor
        assert negative_pnl['ewa_pnl']['ewa'] == std_signal_pnl.pnl[threshold]['negative']['ewa_pnl'].ewa
        assert negative_pnl['ewa_pnl']['weight_sum'] == std_signal_pnl.pnl[threshold]['negative']['ewa_pnl'].weight_sum


def test_stdsignalpnl_from_dict():
    # Define the serialized state with float thresholds
    state = {
        'thresholds': [1.0, 2.0, 3.0],
        'current_standardized_signal': 0.5,
        'epsilon': 0.01,
        'current_ndx': 2,
        'fading_factor': 0.01,
        'signal_var': {
            'fading_factor': 0.01,
            'ewa': 5.0,
            'ewv': 0.25,
            'weight_sum': 2
        },
        'pnl': {
            '1.0': {  # Threshold as string
                'positive': {
                    'ewa_pnl': {
                        'fading_factor': 0.01,
                        'ewa': 0.5,
                        'weight_sum': 2
                    },
                    'pending_signals': [{'start_ndx': 1, 'x_prev': 5.0, 'k': 10}]
                },
                'negative': {
                    'ewa_pnl': {
                        'fading_factor': 0.01,
                        'ewa': -0.5,
                        'weight_sum': 2
                    },
                    'pending_signals': [{'start_ndx': 1, 'x_prev': 6.0, 'k': 10}]
                }
            },
            '2.0': {  # Additional thresholds can be added similarly
                'positive': {
                    'ewa_pnl': {
                        'fading_factor': 0.01,
                        'ewa': 0.0,
                        'weight_sum': 0
                    },
                    'pending_signals': []
                },
                'negative': {
                    'ewa_pnl': {
                        'fading_factor': 0.01,
                        'ewa': 0.0,
                        'weight_sum': 0
                    },
                    'pending_signals': []
                }
            },
            '3.0': {  # Additional thresholds can be added similarly
                'positive': {
                    'ewa_pnl': {
                        'fading_factor': 0.01,
                        'ewa': 0.0,
                        'weight_sum': 0
                    },
                    'pending_signals': []
                },
                'negative': {
                    'ewa_pnl': {
                        'fading_factor': 0.01,
                        'ewa': 0.0,
                        'weight_sum': 0
                    },
                    'pending_signals': []
                }
            }
        }
    }

    # Deserialize into StdSignalPnl
    restored_signal_pnl = StdSignalPnl.from_dict(state)

    # Assert the restored object matches the expected state
    assert restored_signal_pnl.current_standardized_signal == 0.5
    assert restored_signal_pnl.current_ndx == 2
    assert restored_signal_pnl.epsilon == 0.01
    assert restored_signal_pnl.thresholds == [1.0, 2.0, 3.0]  # Now a list of floats
    assert restored_signal_pnl.signal_var.get_mean() == 5.0
    assert restored_signal_pnl.signal_var.get() == 0.25
    assert restored_signal_pnl.signal_var.weight_sum == 2

    # Check PnL for each threshold
    for threshold in [1.0, 2.0, 3.0]:
        pnl_entry = restored_signal_pnl.pnl[threshold]
        # Positive side
        positive_pnl = pnl_entry['positive']['ewa_pnl']
        assert positive_pnl.fading_factor == state['pnl'][str(threshold)]['positive']['ewa_pnl']['fading_factor']
        assert positive_pnl.ewa == state['pnl'][str(threshold)]['positive']['ewa_pnl']['ewa']
        assert positive_pnl.weight_sum == state['pnl'][str(threshold)]['positive']['ewa_pnl']['weight_sum']
        assert restored_signal_pnl.pnl[threshold]['positive']['pending_signals'] == state['pnl'][str(threshold)]['positive']['pending_signals']

        # Negative side
        negative_pnl = pnl_entry['negative']['ewa_pnl']
        assert negative_pnl.fading_factor == state['pnl'][str(threshold)]['negative']['ewa_pnl']['fading_factor']
        assert negative_pnl.ewa == state['pnl'][str(threshold)]['negative']['ewa_pnl']['ewa']
        assert negative_pnl.weight_sum == state['pnl'][str(threshold)]['negative']['ewa_pnl']['weight_sum']
        assert restored_signal_pnl.pnl[threshold]['negative']['pending_signals'] == state['pnl'][str(threshold)]['negative']['pending_signals']


def test_stdsignalpnl_round_trip_serialization():
    # Initialize and perform some ticks
    std_signal_pnl = StdSignalPnl(fading_factor=0.01)
    std_signal_pnl.tick(5.0, horizon=10, signal=1.0)
    std_signal_pnl.tick(6.0, horizon=10, signal=-1.0)

    # Serialize to dictionary
    state_before = std_signal_pnl.to_dict()

    # Serialize dictionary to JSON string
    json_string = json.dumps(state_before)

    # Deserialize JSON string back to dictionary
    state_from_json = json.loads(json_string)

    # Deserialize from the dictionary
    restored_signal_pnl = StdSignalPnl.from_dict(state_from_json)

    # Serialize the restored object to a dictionary again
    state_after = restored_signal_pnl.to_dict()

    # Assert that the two dictionaries are identical
    assert state_before == state_after


def test_stdsignalpnl_full_round_trip():
    # Initialize and perform some ticks
    std_signal_pnl = StdSignalPnl(fading_factor=0.01)
    std_signal_pnl.tick(5.0, horizon=10, signal=1.0)
    std_signal_pnl.tick(6.0, horizon=10, signal=-1.0)

    # Serialize to dictionary
    state_before = std_signal_pnl.to_dict()

    # Serialize dictionary to JSON string
    json_string = json.dumps(state_before)

    # Deserialize JSON string back to dictionary
    state_from_json = json.loads(json_string)

    # Deserialize from the dictionary
    restored_signal_pnl = StdSignalPnl.from_dict(state_from_json)

    # Perform some ticks on the restored instance
    restored_signal_pnl.tick(7.0, horizon=10, signal=0.5)
    restored_signal_pnl.tick(8.0, horizon=10, signal=-0.5)

    # Serialize the restored object to a dictionary again
    state_after = restored_signal_pnl.to_dict()

    # Initialize another instance from the original serialized state
    another_instance = StdSignalPnl.from_dict(state_before)
    another_instance.tick(7.0, horizon=10, signal=0.5)
    another_instance.tick(8.0, horizon=10, signal=-0.5)
    state_another = another_instance.to_dict()

    # Compare the two restored states after performing the same ticks
    assert state_after == state_another
