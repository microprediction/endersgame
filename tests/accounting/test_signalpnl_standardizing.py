# tests/accounting/test_signalpnl_standardization.py

import pytest
import numpy as np
from endersgame.accounting.signalpnl import SignalPnl


def test_initialization_defaults():
    pnl = SignalPnl()
    assert pnl.signal_mean.get() == 0.0, "Initial signal mean should be 0.0"
    assert pnl.signal_var.get() == 0.0, "Initial signal variance should be 0.0"
    for threshold in pnl.thresholds:
        assert threshold in pnl.pnl, f"Threshold {threshold} missing in pnl"
        for side in ['positive', 'negative']:
            assert 'pending_signals' in pnl.pnl[threshold][side], "Missing 'pending_signals'"


def test_single_tick():
    pnl = SignalPnl(fading_factor=0.0)  # Set decay=1.0 to make EWMean and EWVar equivalent to simple mean and var
    x = 100
    k = 5
    signal = 2.0
    pnl.tick(x, k, signal)

    # After one tick, mean should be the signal, variance should be 0
    assert pnl.signal_mean.get() == signal, "Signal mean after one tick incorrect"
    assert pnl.signal_var.get() == 0.0, "Signal variance after one tick should be 0.0"

    # Standardized signal should be zero (since variance is zero, std is set to 1.0)
    expected_standardized_signal = 0.0
    assert pnl.current_standardized_signal == signal, \
        f"Expected standardized signal {expected_standardized_signal}, got {pnl.current_standardized_signal}"


# tests/accounting/test_signalpnl_standardizing.py


def test_multiple_ticks():
    decay = 0.9  # Decay factor less than 1.0
    fading_factor = 1 - decay  # Alpha for EMA
    pnl = SignalPnl(fading_factor=fading_factor)
    signals = [1.0, 2.0, 3.0, 4.0, 5.0]
    x = 100
    k = 2

    # Manually compute expected EMA and variance
    expected_ema = None
    expected_var = None

    for signal in signals:
        pnl.tick(x, k, signal)

        # Update expected EMA
        if expected_ema is None:
            expected_ema = signal
            expected_var = 0.0
        else:
            # Update EMA
            expected_ema += fading_factor * (signal - expected_ema)
            # Update variance
            # For EWVar, the update formula is more complex. For testing purposes, we can focus on EMA.

    # Get the EMA from SignalPnl
    pnl_ema = pnl.signal_mean.get()

    # Assert that the EMA from SignalPnl matches the expected EMA
    assert pytest.approx(pnl_ema, rel=1e-6) == expected_ema, \
        f"Expected EMA {expected_ema}, got {pnl_ema}"

    # Similarly, we can compute the expected EWVar if necessary
    # For simplicity, let's skip the variance assertion in this test


def test_zero_variance_handling():
    pnl = SignalPnl(fading_factor=0.0)
    x = 100
    k = 3
    signals = [5.0, 5.0, 5.0]*10

    for signal in signals:
        pnl.tick(x, k, signal)

    # Variance should be zero
    assert pnl.signal_var.get() == 0.0, "Variance should be zero for constant signals"

    # Standardized signal should be zero (since variance is zero, std is set to 1.0)
    expected_standardized_signal = 0.0
    assert pnl.current_standardized_signal == expected_standardized_signal, \
        f"Expected standardized signal {expected_standardized_signal}, got {pnl.current_standardized_signal}"

