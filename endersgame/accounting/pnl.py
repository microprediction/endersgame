from typing import Dict, List, Tuple
import numpy as np
from endersgame import EPSILON

DEFAULT_TRADE_BACKOFF = 1  # The minimum time between non-zero decisions

class Pnl:
    def __init__(self, epsilon: float = EPSILON, backoff: int = DEFAULT_TRADE_BACKOFF):
        self.epsilon = epsilon
        self.backoff = backoff
        self.current_ndx = 0
        self.last_attack_ndx = None
        self.pending_decisions: Dict[int, Tuple[float, int, float]] = {}
        self.pnl_data: List[Tuple[int, int, int, float, float, float, float]] = []
        self.pnl_columns = ['decision_ndx', 'resolution_ndx', 'horizon',
                            'decision', 'y_decision', 'y_resolution', 'pnl']

    def tick(self, x: float, horizon: int, decision: float):
        """
        Processes a new data point, potentially making a decision and resolving pending decisions.
        """
        self._add_decision(x, horizon, decision)
        self._resolve_decisions(x)
        self.current_ndx += 1

    def _add_decision(self, x: float, horizon: int, decision: float):
        """
        Adds a non-zero decision to the pending decisions dictionary.
        """
        if decision != 0 and (self.last_attack_ndx is None or
                              self.current_ndx - self.last_attack_ndx >= self.backoff):
            self.pending_decisions[self.current_ndx] = (x, horizon, decision)
            self.last_attack_ndx = self.current_ndx

    def _resolve_decisions(self, x: float):
        """
        Resolves pending decisions by calculating PnL when the future value is available.
        """
        resolved_indices = []
        for decision_ndx, (x_prev, horizon, decision) in self.pending_decisions.items():
            if self.current_ndx - decision_ndx >= horizon:
                pnl = (x - x_prev if decision > 0 else x_prev - x) - self.epsilon
                self.pnl_data.append((
                    decision_ndx,
                    self.current_ndx,
                    horizon,
                    decision,
                    x_prev,
                    x,
                    pnl
                ))
                resolved_indices.append(decision_ndx)

        for idx in resolved_indices:
            del self.pending_decisions[idx]

    def reset_pnl(self):
        """Resets all PnL tracking variables."""
        self.current_ndx = 0
        self.last_attack_ndx = None
        self.pending_decisions.clear()
        self.pnl_data.clear()

    def get_pnl_tuples(self) -> List[Tuple]:
        """Returns the list of resolved PnL data tuples."""
        return self.pnl_data

    def to_records(self) -> List[Dict]:
        """Converts PnL data to a list of dictionaries."""
        return [dict(zip(self.pnl_columns, pnl_rec)) for pnl_rec in self.pnl_data]

    def summary(self) -> Dict:
        """Returns a summary of PnL-related statistics from the resolved decisions."""
        pnl_values = [entry[-1] for entry in self.pnl_data]
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
        """Deserializes the state from a dictionary into a new PnL instance."""
        instance = cls(
            epsilon=state.get('epsilon', EPSILON),
            backoff=state.get('backoff', DEFAULT_TRADE_BACKOFF),
        )
        instance.current_ndx = state.get('current_ndx', 0)
        instance.last_attack_ndx = state.get('last_attack_ndx')
        instance.pending_decisions = state.get('pending_decisions', {})
        instance.pnl_data = state.get('pnl_data', [])
        return instance
