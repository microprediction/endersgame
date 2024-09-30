from signal import signal

# test_signalpnl.py

import numpy as np
from endersgame.accounting.signalpnl import SignalPnl


def test_initialization_defaults():
    """Test that the class initializes correctly with default thresholds and decay."""
    pnl = SignalPnl()
    assert isinstance(pnl.thresholds, np.ndarray), "Thresholds should be a numpy array."
    assert pnl.current_ndx == 0, "Current index should start at 0."
    assert hasattr(pnl, 'signal_mean'), "signal_mean attribute should exist."
    assert hasattr(pnl, 'signal_var'), "signal_var attribute should exist."
    assert isinstance(pnl.pnl, dict), "PnL should be a dictionary."

def test_initialization_custom_thresholds():
    """Test that the class initializes correctly with custom thresholds."""
    custom_thresholds = [2, 4]
    pnl = SignalPnl(thresholds=custom_thresholds, fading_factor=0.95)
    assert np.array_equal(pnl.thresholds, np.array(custom_thresholds)), "Custom thresholds are incorrect."

def test_signal_processing():
    """Test that signals are processed and standardized without errors."""
    pnl = SignalPnl()
    signals = [1, 2, 3, 4, 5]
    x = 100
    k = 2
    for signal in signals:
        pnl.tick(x, k, signal)
        assert hasattr(pnl, 'current_standardized_signal'), "Standardized signal should be calculated."
        assert isinstance(pnl.current_standardized_signal, float), "Standardized signal should be a float."
        # We won't check the exact value of the standardized signal here.


def test_threshold_exceedance():
    """Test that standardized signals exceeding thresholds are added to pending signals."""
    thresholds = [1,2,3]
    pnl = SignalPnl(thresholds=thresholds)
    x = 100
    k = 2
    # Provide initial signals to establish mean and variance
    initial_signals = [1, 1, 1, 1]  # Constant signals to set mean
    for s in initial_signals:
        pnl.tick(x, k, s)

    # Now provide a signal that should, when standardized, exceed some thresholds
    import random
    signal = random.choice([5,-5])  # Raw signal
    pnl.tick(x, k, signal)
    standardized_signal = pnl.current_standardized_signal

    for threshold in pnl.thresholds:
        if standardized_signal > threshold:
            pending = pnl.pnl[threshold]['positive']['pending_signals']
            assert len(pending) > 0, f"Standardized signal exceeding threshold {threshold} should be pending."
        else:
            pending = pnl.pnl[threshold]['positive']['pending_signals']
            assert len(pending) == 0, f"Standardized signal not exceeding threshold {threshold} should not be pending."
        if standardized_signal < -threshold:
            pending = pnl.pnl[threshold]['negative']['pending_signals']
            assert len(pending) > 0, f"Standardized signal below -{threshold} should be pending."
        else:
            pending = pnl.pnl[threshold]['negative']['pending_signals']
            assert len(pending) == 0, f"Standardized signal not below -{threshold} should not be pending."




def test_signal_resolution():
    """Test that pending signals are resolved after k=2 steps and mean PnL is right."""
    thresholds = [1, 2, 3]
    fading_factor = 0.05
    signal_pnl = SignalPnl(thresholds=thresholds, fading_factor=fading_factor)
    k = 2

    # Establish mean and variance with initial signals
    initial_x_values = [100, 105, 110, 115, 120,120]*10+[100,100,100,100,100]
    initial_signals = [1, -1, 1, -1, 1,-1]*10+[0,0,0,0,0]  # Adjusted to match the length of x_values
    for s, x in zip(initial_signals, initial_x_values):
        signal_pnl.tick(x, k, s)
        if False:
            print(f'After {s} signal the signal mean is {signal_pnl.signal_mean.get()}')

    assert len(signal_pnl.pnl[1]['positive']['pending_signals'])==0,'No signal expected yet'

    # Generate a big signal that should exceed thresholds when standardized
    big_signal = 10
    x = 130
    signal_pnl.tick(x=x, k=k, signal=big_signal)   # Should generate pending signals

    assert len(signal_pnl.pnl[1]['positive']['pending_signals']) == 1, 'One pending expected'

    # Advance time
    signal_pnl.tick(x=135, k=k, signal=0)
    assert len(signal_pnl.pnl[1]['positive']['pending_signals']) == 1, 'One pending expected'

    # Now time again and now it is time to resolve:
    signal_pnl.tick(x=140, k=k, signal=0)
    assert len(signal_pnl.pnl[1]['positive']['pending_signals']) == 0, 'No pending expected'

    running_pnl_mean = signal_pnl.pnl[1]['positive']['ewa_pnl'].get()
    assert abs(running_pnl_mean-10)<1, 'Expected to see an average pnl of 10 because we decided on "up" at 130'

    # Now let's test whether it will recommend a trade
    signal_pnl.tick(x=140,k=2,signal=10)
    decision = signal_pnl.predict(epsilon=0)
    assert decision>0


def test_signal_resolution_negative():
    """Test that pending signals are resolved after k=2 steps and mean PnL is right for negative signals."""
    thresholds = [3]
    fading_factor = 0.05
    signal_pnl = SignalPnl(thresholds=thresholds, fading_factor=fading_factor)
    k = 2

    # Establish mean and variance with initial signals
    initial_x_values = [100, 105, 110, 115, 120] * 10
    initial_signals = [-1, 1, -1, 1, -1, 1] * 10   # Adjusted to match the length of x_values
    for s, x in zip(initial_signals, initial_x_values):
        signal_pnl.tick(x, k, s)
        assert len(signal_pnl.pnl[3]['negative']['pending_signals']) == 0, 'No negative signal expected yet'

    additional_x_values = [100, 100, 100, 100, 100]
    additional_signals = [0, 0, 0, 0, 0]
    for s, x in zip(additional_signals, additional_x_values):
        signal_pnl.tick(x, k, s)
        assert len(signal_pnl.pnl[3]['negative']['pending_signals']) == 0, 'No negative signal expected yet'

    # Generate a big negative signal that should exceed thresholds when standardized
    big_negative_signal = -5
    x = 130
    signal_pnl.tick(x=x, k=k, signal=big_negative_signal)   # Should generate a pending negative signal

    # Assert that a pending negative signal has been added for threshold=1
    assert len(signal_pnl.pnl[3]['negative']['pending_signals']) == 1, 'One negative pending expected'

    # Advance time by one step (still within k=2 steps)
    signal_pnl.tick(x=125, k=k, signal=0)
    assert len(signal_pnl.pnl[3]['negative']['pending_signals']) == 1, 'One negative pending expected after first advancement'

    # Advance time by another step to resolve the pending signal
    signal_pnl.tick(x=120, k=k, signal=0)
    assert len(signal_pnl.pnl[3]['negative']['pending_signals']) == 0, 'No negative pending expected after resolution'

    # Check the running PnL mean for the negative threshold
    running_pnl_mean = signal_pnl.pnl[3]['negative']['ewa_pnl'].get()
    expected_pnl = 10.0  # With fading_factor=1.0, ewa_pnl = 1.0 * 10 = 10
    assert abs(running_pnl_mean - expected_pnl) < 1.0, f'Expected to see an average pnl of {expected_pnl}, got {running_pnl_mean}'

    # Now let's test whether it will recommend a negative trade
    signal_pnl.tick(x=120, k=k, signal=-10)
    decision = signal_pnl.predict(epsilon=0)
    assert decision < 0, 'Expected decision to be negative (-1)'






def test_predict_no_data():
    """Test that predict returns no action when there is insufficient data."""
    pnl = SignalPnl()
    decision = pnl.predict()
    assert decision == 0, "Decision should be 0 when there is insufficient data."



# Running all tests using pytest
if __name__ == "__main__":
    import pytest
    pytest.main([__file__])
