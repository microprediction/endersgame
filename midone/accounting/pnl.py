from typing import Dict, List, Tuple
import numpy as np
from collections import OrderedDict
from midone import EPSILON

DEFAULT_TRADE_BACKOFF = 1  # The minimum time between non-zero decisions


class Pnl:
    """
Simple logging of PnL (Profit and Loss) for all decisions made by an attacker.
- Non-zero decisions are tracked in a OrderedDict of dictionaries.
- Each decision is resolved when the corresponding future value becomes available.
- Decisions made within self.backoff data points of the last non-zero decision are ignored.
"""

    def __init__(self, epsilon: float = EPSILON, backoff: int = DEFAULT_TRADE_BACKOFF, with_trading_lag: bool = False):
        self.epsilon = epsilon
        self.backoff = backoff
        self.with_trading_lag = with_trading_lag
        self.current_ndx = 0
        self.last_attack_ndx = None

        self._pending_decisions: OrderedDict[int, Dict] = OrderedDict()
        self._pnl_data: OrderedDict[int, Dict] = OrderedDict()
        self.pnl_columns = ['decision_ndx', 'resolution_ndx', 'horizon',
                            'decision', 'y_decision', 'y_resolution', 'pnl']

    @property
    def pending_decisions(self) -> List[Dict]:
        return [{'index': k, **v} for k, v in self._pending_decisions.items()]

    @property
    def pnl_data(self) -> List[Dict]:
        return list(self._pnl_data.values())

    def tick(self, x: float, horizon: int = 0, decision: float = 0.):
        """
        Processes a new data point, potentially making a decision and resolving pending decisions.
        """
        if decision != 0. and horizon == 0:
            raise ValueError("Cannot make a decision with a non-zero horizon")
        self._add_decision(x, horizon, decision)
        if self.with_trading_lag:
            self._update_anchor(x)
        self._resolve_decisions(x)
        self.current_ndx += 1

    def _add_decision(self, x: float, horizon: int, decision: float):
        """
        Adds a non-zero decision to the pending decisions' dictionary.
        """
        if decision == 0 or (self.last_attack_ndx is not None and
                              self.current_ndx - self.last_attack_ndx < self.backoff):
            return
        anchor = None if self.with_trading_lag else x
        self._pending_decisions[self.current_ndx] = {
            'x': x,
            'anchor': anchor,
            'horizon': horizon,
            'decision': decision
        }
        self.last_attack_ndx = self.current_ndx

    def _update_anchor(self, x: float):
        """
        For all pending decisions created at index - 1: we set the anchor
        """
        lookup = self.current_ndx - 1
        if self.current_ndx - 1 in self._pending_decisions:
            self._pending_decisions[self.current_ndx - 1]['anchor'] = x

    def _resolve_decisions(self, x: float):
        """
        Resolves pending decisions by calculating PnL when the future value is available.
        """
        resolved_indices = []
        for decision_ndx, pending in self._pending_decisions.items():
            final_decision = decision_ndx + pending['horizon']
            if self.with_trading_lag:
                final_decision += 1
            if self.current_ndx != final_decision:
                continue
            anchor = pending['anchor']
            decision = pending['decision']

            pnl = (x - anchor if  decision > 0 else anchor - x) - self.epsilon
            self._pnl_data[decision_ndx] = {
                    'decision_ndx': decision_ndx,
                    'resolution_ndx': self.current_ndx,
                    'horizon': pending['horizon'],
                    'decision': decision,
                    'y_decision': anchor,
                    'y_resolution': x,
                    'pnl': pnl
                }
            resolved_indices.append(decision_ndx)

        for idx in resolved_indices:
            del self._pending_decisions[idx]

    def reset_pnl(self):
        """Resets all PnL tracking variables."""
        self.current_ndx = 0
        self.last_attack_ndx = None
        self._pending_decisions.clear()
        self._pnl_data.clear()

    def get_pnl_tuples(self) -> List[Tuple]:
        """Returns the list of resolved PnL data tuples."""
        return [tuple(entry.values()) for entry in self._pnl_data.values()]

    def to_records(self) -> List[Dict]:
        """Converts PnL data to a list of dictionaries."""
        return self.pnl_data

    def summary(self) -> Dict:
        """Returns a summary of PnL-related statistics from the resolved decisions."""
        pnl_values = [entry['pnl'] for entry in self.pnl_data]
        total_profit = sum(pnl_values)
        num_resolved = len(pnl_values)

        if num_resolved == 0:
            return {
                "current_ndx": self.current_ndx,
                "num_resolved_decisions": 0,
                "total_profit": 0,
                "win_loss_ratio": None,
                "average_profit_per_decision": None,
                "avg_profit_per_decision_std_ratio": None
            }

        wins = sum(1 for pnl in pnl_values if pnl > 0)
        losses = sum(1 for pnl in pnl_values if pnl < 0)
        win_loss_ratio = wins / losses if losses != 0 else float('inf')

        avg_profit_per_decision = total_profit / num_resolved
        pnl_std = np.std(pnl_values) if num_resolved > 1 else 0
        standardized_profit = avg_profit_per_decision / pnl_std if pnl_std != 0 else float('inf')

        return {
            "current_ndx": self.current_ndx,
            "num_resolved_decisions": num_resolved,
            "total_profit": total_profit,
            "wins": wins,
            "losses": losses,
            "win_loss_ratio": win_loss_ratio,
            "profit_per_decision": avg_profit_per_decision,
            "standardized_profit_per_decision": standardized_profit
        }

    def to_dict(self) -> Dict:
        """Serializes the state of the PnL object to a dictionary."""
        return {
            'epsilon': self.epsilon,
            'backoff': self.backoff,
            'current_ndx': self.current_ndx,
            'last_attack_ndx': self.last_attack_ndx,
            'pending_decisions': self.pending_decisions,
            'pnl_data': self.pnl_data
        }

    @classmethod
    def from_dict(cls, state: Dict):
        """Deserializes the state from a dictionary into a new Pnl instance."""
        instance = cls(
            epsilon=state.get('epsilon', EPSILON),
            backoff=state.get('backoff', DEFAULT_TRADE_BACKOFF),
        )
        instance.current_ndx = state.get('current_ndx', 0)
        instance.last_attack_ndx = state.get('last_attack_ndx')

        for decision in state.get('pending_decisions', []):
            index = decision.pop('index')
            instance._pending_decisions[index] = decision

        for pnl_entry in state.get('pnl_data', []):
            instance._pnl_data[pnl_entry['decision_ndx']] = pnl_entry

        return instance
