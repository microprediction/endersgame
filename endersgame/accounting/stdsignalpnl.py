# endersgame/accounting/stdsignalpnl.py

import numpy as np
import math
from endersgame import EPSILON
from endersgame.riverstats.fewvar import FEWVar
from endersgame.riverstats.fewmean import FEWMean


class StdSignalPnl:
    """
    Creates a standardized signal from an attacker's decisions,
    then tracks hypothetical PnL for threshold-based choices,
    and uses this in it's predict() method

    To use:

        stdsignalpnl.tick(x, k, signal)         # Registers current data point and decision made by attacker
        different_decision = pnl.predict(k)     # Offers a decision based on moving average empirical results
    """

    def __init__(self, thresholds=None, fading_factor=0.01, epsilon=EPSILON, ignore_signal_mean=True):
        """
        Initializes the SignalPnl object with thresholds and fading factor.
        The closer fading_factor is to 1 the more the statistic will adapt to recent values.
        """
        if thresholds is None:
            self.thresholds = [1.0, 2.0, 3.0]  # Default thresholds as floats
        else:
            self.thresholds = [float(t) for t in thresholds]  # Ensure all thresholds are floats
        self.current_standardized_signal = 0.0
        self.epsilon = epsilon
        self.current_ndx = 0
        self.fading_factor = fading_factor
        self.signal_var = FEWVar(fading_factor=fading_factor)
        self.pnl = {}
        for threshold in self.thresholds:
            self.pnl[threshold] = {
                'positive': {
                    'ewa_pnl': FEWMean(fading_factor=fading_factor),
                    'pending_signals': []
                },
                'negative': {
                    'ewa_pnl': FEWMean(fading_factor=fading_factor),
                    'pending_signals': []
                }
            }


    def tick(self, x: float, horizon: int, signal: float):
        """
        Processes the signal at the current time step.

        Parameters:
        - x (float):  Current data point.
        - k (int):    Prediction horizon.
        - signal (float):  The generated signal.
        """

        signal_mean = self.signal_var.get_mean()
        signal_var = self.signal_var.get()

        # Calculate standard deviation and handle zero variance
        signal_std = math.sqrt(signal_var) if signal_var > 0 else 1.0

        standardized_signal = (signal - signal_mean) / signal_std

        self._add_signal_to_queues(x=x, horizon=horizon, standardized_signal=standardized_signal)
        self._resolve_signals_on_queues(x=x)
        self.current_ndx += 1
        self.current_standardized_signal = standardized_signal

        self.signal_var.update(signal)

    def _add_signal_to_queues(self, x: float, horizon: int, standardized_signal: float):
        """
        For each threshold, determine if the standardized signal exceeds the threshold,
        and store pending actions accordingly.

        Parameters:
        - x (float):      Current data point.
        - k (int):        Prediction horizon.
        - standardized_signal (float): The standardized signal.
        """
        for threshold in self.thresholds:
            if standardized_signal > threshold:
                # Signal exceeds threshold: potential positive action
                self.pnl[threshold]['positive']['pending_signals'].append({
                    'start_ndx': self.current_ndx,
                    'x_prev': x,
                    'k': horizon
                })
            if standardized_signal < -threshold:
                # Signal falls below negative threshold: potential negative action
                self.pnl[threshold]['negative']['pending_signals'].append({
                    'start_ndx': self.current_ndx,
                    'x_prev': x,
                    'k': horizon
                })

    def _resolve_signals_on_queues(self, x: float):
        for threshold in self.thresholds:
            for side in ['positive', 'negative']:
                pending_signals = self.pnl[threshold][side]['pending_signals']
                resolved_signals = []
                for signal_info in pending_signals:
                    num_steps = self.current_ndx - signal_info['start_ndx']
                    if num_steps >= signal_info['k']:
                        # Time to resolve the signal
                        x_prev = signal_info['x_prev']
                        if side == 'positive':
                            pnl_value = x - x_prev  # Long position
                        else:
                            pnl_value = x_prev - x  # Short position

                        # Update EWA PnL using EWMean
                        ewa_pnl = self.pnl[threshold][side]['ewa_pnl']
                        ewa_pnl.update(pnl_value)

                        resolved_signals.append(signal_info)

                # Remove resolved signals
                self.pnl[threshold][side]['pending_signals'] = [
                    s for s in pending_signals if s not in resolved_signals
                ]

    def get_expected_pnl(self, signal: float, epsilon: float) -> dict:
        """
        Estimate the expected PnL for the current standardized signal based on thresholds.

        Parameters:
        - signal (float): The standardized signal.
        - epsilon (float): The transaction cost or threshold.

        Returns:
        - expected_pnls (dict): A dictionary with thresholds as keys and dictionaries
          containing expected PnLs for 'positive' and 'negative' sides.
        """
        expected_pnls = {}
        for threshold in self.thresholds:
            expected_pnls[threshold] = {'positive': 0.0, 'negative': 0.0}
            # Positive side
            if signal > threshold:
                ewa_pnl = self.pnl[threshold]['positive']['ewa_pnl']
                ewa_mean = ewa_pnl.get()
                expected_pnl = ewa_mean - epsilon
                expected_pnls[threshold]['positive'] = expected_pnl
            # Negative side
            if signal < -threshold:
                ewa_pnl = self.pnl[threshold]['negative']['ewa_pnl']
                ewa_mean = ewa_pnl.get()
                expected_pnl = ewa_mean - epsilon
                expected_pnls[threshold]['negative'] = expected_pnl
        return expected_pnls

    def predict(self, epsilon: float = None):
        """
        Decide whether to take a positive action (1), negative action (-1), or no action (0)
        based on the current standardized signal and the expected PnL for each threshold.

        Parameters:
        - epsilon (float): Transaction cost or threshold.

        Returns:
        - best_decision (int): 1 for positive action, -1 for negative action, 0 for no action.
        """
        if epsilon is None:
            epsilon = self.epsilon

        std_sig = self.current_standardized_signal
        best_pnl = 0.0
        best_decision = 0

        for threshold in self.thresholds:
            # Positive side
            if std_sig > threshold:
                ewa_pnl_obj = self.pnl[threshold]['positive']['ewa_pnl']
                ewa_pnl = ewa_pnl_obj.get()
                if ewa_pnl > best_pnl:
                    best_pnl = ewa_pnl
                    best_decision = 1  # Positive action

            # Negative side
            if std_sig < -threshold:
                ewa_pnl_obj = self.pnl[threshold]['negative']['ewa_pnl']
                ewa_pnl = ewa_pnl_obj.get()
                if ewa_pnl > best_pnl:
                    best_pnl = ewa_pnl
                    best_decision = -1  # Negative action

        return best_decision



    def to_dict(self):
        """
        Serializes the state of the StdSignalPnl object to a dictionary.
        """
        return {
            'thresholds': self.thresholds,  # List of floats
            'current_standardized_signal': self.current_standardized_signal,
            'epsilon': self.epsilon,
            'current_ndx': self.current_ndx,
            'fading_factor': self.fading_factor,
            'signal_var': self.signal_var.to_dict(),
            'pnl': {
                threshold: {
                    'positive': {
                        'ewa_pnl': self.pnl[threshold]['positive']['ewa_pnl'].to_dict(),
                        'pending_signals': self.pnl[threshold]['positive']['pending_signals']
                    },
                    'negative': {
                        'ewa_pnl': self.pnl[threshold]['negative']['ewa_pnl'].to_dict(),
                        'pending_signals': self.pnl[threshold]['negative']['pending_signals']
                    }
                } for threshold in self.thresholds
            }
        }

    @classmethod
    def from_dict(cls, data):
        """
        Deserializes the state from a dictionary into a new StdSignalPnl instance.
        Handles string keys in the 'pnl' dictionary by converting them back to floats.
        """
        # Ensure thresholds are floats
        thresholds = [float(t) for t in data['thresholds']]

        instance = cls(
            thresholds=thresholds,
            fading_factor=data['fading_factor'],
            epsilon=data['epsilon']
        )
        instance.current_standardized_signal = data['current_standardized_signal']
        instance.current_ndx = data['current_ndx']
        instance.signal_var = FEWVar.from_dict(data['signal_var'])

        # Restore PnL
        for threshold_str, pnl_entry in data['pnl'].items():
            threshold = float(threshold_str)  # Convert key back to float
            if threshold in instance.thresholds:
                instance.pnl[threshold]['positive']['ewa_pnl'] = FEWMean.from_dict(pnl_entry['positive']['ewa_pnl'])
                instance.pnl[threshold]['positive']['pending_signals'] = pnl_entry['positive']['pending_signals']
                instance.pnl[threshold]['negative']['ewa_pnl'] = FEWMean.from_dict(pnl_entry['negative']['ewa_pnl'])
                instance.pnl[threshold]['negative']['pending_signals'] = pnl_entry['negative']['pending_signals']

        return instance


