# tests/accounting/test_signalpnl_standardization.py

import pytest
import numpy as np
from midone.accounting.stdsignalpnl import StdSignalPnl


def test_initialization_defaults():
    pnl = StdSignalPnl()
    assert pnl.signal_var.get_mean() == 0.0, "Initial signal mean should be 0.0"
    assert pnl.signal_var.get() == 0.0, "Initial signal variance should be 0.0"
    for threshold in pnl.thresholds:
        assert threshold in pnl.pnl, f"Threshold {threshold} missing in pnl"
        for side in ['positive', 'negative']:
            assert 'pending_signals' in pnl.pnl[threshold][side], "Missing 'pending_signals'"


def test_single_tick():
    pnl = StdSignalPnl(fading_factor=0.0)  # Set decay=1.0 to make EWMean and EWVar equivalent to simple mean and var
    x = 100
    k = 5
    signal = 2.0
    pnl.tick(x, k, signal)

    # After one tick, mean should be the signal, variance should be 0
    assert pnl.signal_var.get_mean() == signal, "Signal mean after one tick incorrect"
    assert pnl.signal_var.get() == 0.0, "Signal variance after one tick should be 0.0"

    # Standardized signal should be zero (since variance is zero, std is set to 1.0)
    expected_standardized_signal = 0.0
    assert pnl.current_standardized_signal == signal, \
        f"Expected standardized signal {expected_standardized_signal}, got {pnl.current_standardized_signal}"


# tests/accounting/test_signalpnl_standardizing.py


def test_zero_variance_handling():
    pnl = StdSignalPnl(fading_factor=0.0)
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
