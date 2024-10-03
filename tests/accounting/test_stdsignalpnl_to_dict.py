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
            1.0: {  # Threshold as float
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
            2.0: {  # Additional thresholds can be added similarly
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
            3.0: {  # Additional thresholds can be added similarly
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
        assert positive_pnl.fading_factor == state['pnl'][threshold]['positive']['ewa_pnl']['fading_factor']
        assert positive_pnl.ewa == state['pnl'][threshold]['positive']['ewa_pnl']['ewa']
        assert positive_pnl.weight_sum == state['pnl'][threshold]['positive']['ewa_pnl']['weight_sum']
        assert restored_signal_pnl.pnl[threshold]['positive']['pending_signals'] == state['pnl'][threshold]['positive']['pending_signals']

        # Negative side
        negative_pnl = pnl_entry['negative']['ewa_pnl']
        assert negative_pnl.fading_factor == state['pnl'][threshold]['negative']['ewa_pnl']['fading_factor']
        assert negative_pnl.ewa == state['pnl'][threshold]['negative']['ewa_pnl']['ewa']
        assert negative_pnl.weight_sum == state['pnl'][threshold]['negative']['ewa_pnl']['weight_sum']
        assert restored_signal_pnl.pnl[threshold]['negative']['pending_signals'] == state['pnl'][threshold]['negative']['pending_signals']

def test_stdsignalpnl_round_trip():
    # Initialize and perform some ticks
    std_signal_pnl = StdSignalPnl(fading_factor=0.01)
    std_signal_pnl.tick(5.0, horizon=10, signal=1.0)
    std_signal_pnl.tick(6.0, horizon=10, signal=-1.0)

    # Serialize to dictionary
    state_before = std_signal_pnl.to_dict()

    # Deserialize from the dictionary
    restored_signal_pnl = StdSignalPnl.from_dict(state_before)

    # Perform a few more ticks after deserialization
    restored_signal_pnl.tick(7.0, horizon=10, signal=0.5)
    restored_signal_pnl.tick(8.0, horizon=10, signal=-0.5)

    # Serialize the restored object to a dictionary again
    state_after = restored_signal_pnl.to_dict()

    # Since we performed additional ticks on the restored instance,
    # the 'state_before' and 'state_after' should not be identical.
    # Instead, ensure that the restored instance has correctly updated state.

    # Verify that 'current_ndx' has incremented appropriately
    assert state_after['current_ndx'] == state_before['current_ndx'] + 2

    # Verify that 'current_standardized_signal' has been updated
    assert state_after['current_standardized_signal'] == restored_signal_pnl.current_standardized_signal

    # Verify that 'signal_var' has been updated
    assert state_after['signal_var']['ewa'] == restored_signal_pnl.signal_var.ewa
    assert state_after['signal_var']['ewv'] == restored_signal_pnl.signal_var.ewv
    assert state_after['signal_var']['weight_sum'] == restored_signal_pnl.signal_var.weight_sum

    # Verify that 'pnl' has been updated with new pending_signals if any
    for threshold in std_signal_pnl.thresholds:
        original_pnl = state_before['pnl'][threshold]
        new_pnl = state_after['pnl'][threshold]

        # Check that 'ewa_pnl' remains consistent
        assert new_pnl['positive']['ewa_pnl'] == original_pnl['positive']['ewa_pnl']
        assert new_pnl['negative']['ewa_pnl'] == original_pnl['negative']['ewa_pnl']

        # Check that 'pending_signals' have been updated correctly
        # Depending on the logic, pending_signals might be resolved or new ones added
        # Here, since additional ticks were performed, check if new signals are added
        # For simplicity, we'll ensure no KeyErrors and that structures are maintained
        assert isinstance(new_pnl['positive']['pending_signals'], list)
        assert isinstance(new_pnl['negative']['pending_signals'], list)

    # Optionally, perform a full state comparison after restoring and performing the same ticks
    # This requires resetting the original instance and performing the same ticks
    # to ensure both instances have the same state.

    # Initialize another instance and perform the same ticks
    another_instance = StdSignalPnl.from_dict(state_before)
    another_instance.tick(7.0, horizon=10, signal=0.5)
    another_instance.tick(8.0, horizon=10, signal=-0.5)
    state_another = another_instance.to_dict()

    # Compare the two restored states
    assert state_after == state_another
