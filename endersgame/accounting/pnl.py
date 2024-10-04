from typing import Dict
import numpy as np
from endersgame import EPSILON
from endersgame.accounting.pnlutil import add_pnl_summaries, zero_pnl_summary

class Pnl:
    """
    Simple logging of PnL (Profit and Loss) for all decisions made by an attacker.

    - Non-zero decisions are tracked in a list of dictionaries.
    - Each decision is resolved when the corresponding future value becomes available.
    - Decisions made within self.backoff data points of the last non-zero decision are ignored.

    """

    def __init__(self, epsilon: float = EPSILON, backoff: int = 100):
        self.epsilon = epsilon
        self.backoff = backoff
        self.current_ndx = 0
        self.last_attack_ndx = None
        self.pending_decisions = []
        self.pnl_data = []
        self.pnl_columns = ['decision_ndx', 'resolution_ndx', 'horizon', 'decision', 'y_decision', 'y_resolution',
                            'pnl']


    def tick(self, x: float, horizon: int, decision: float):
        """

            Adds non-zero 'decision' to a queue so it can be judged later
            And uses revealed ground truth y to evaluate past decisions

        """
        self._add_decision_to_queue(x=x, horizon=horizon, decision=decision)
        self._resolve_decisions_on_queue(x=x)

    def reset_pnl(self):
        """Resets all PnL tracking variables within the accounting property."""
        self.current_ndx = 0
        self.last_attack_ndx = None
        self.pending_decisions.clear()
        self.pnl_data.clear()

    def _add_decision_to_queue(self, x: float, horizon: int, decision: float):
        """
        Store a decision made at the current time step.

        - y:        The last value seen when making the decision
        - decision: The decision made (positive for up, negative for down).
        """
        # Don't record a decision if another decision has recently been made
        # (We want to cut out machine gun attacks)
        if self.last_attack_ndx is not None and \
                (self.current_ndx - self.last_attack_ndx) < self.backoff:
            self.current_ndx += 1
            return

        # Store the decision and the time it was made
        if decision != 0:
            self.pending_decisions.append((self.current_ndx, x, horizon, decision))
            self.last_attack_ndx = self.current_ndx

        # Increment total observations
        self.current_ndx += 1

    def _resolve_decisions_on_queue(self, x: float):
        """
        Resolve pending decisions by calculating PnL when enough time has passed and the future value is available.

        - y: The newly arrived data point (the current value of the sequence).
        """
        resolved_decision_ndxs = []
        current_ndx = self.current_ndx
        for pending_ndx, (decision_ndx, x_prev, horizon_, decision) in enumerate(self.pending_decisions):
            num_observations_since_decision = current_ndx - decision_ndx  # Horizon passed since the decision
            if num_observations_since_decision >= horizon_:
                # Calculate PnL based on whether the decision was positive or negative
                if decision > 0:
                    pnl = x - x_prev - self.epsilon
                elif decision < 0:
                    pnl = x_prev - x - self.epsilon
                else:
                    raise ValueError('A non-zero decision was logged to the queue')

                # ['decision_ndx','resolution_ndx','k','decision','y_decision','y_resolution','pnl']
                pnl_data = (decision_ndx, current_ndx, horizon_, decision, x_prev, x, pnl)
                resolved_decision_ndxs.append(pending_ndx)
                self.pnl_data.append(pnl_data)

        # resolved_decision_ndxs contains a list of indexes into self.accounting["pending_decisions"] that we remove:
        self.pending_decisions = [d for (pndx, d) in enumerate(self.pending_decisions) if
                                  pndx not in resolved_decision_ndxs]

    def get_pnl_tuples(self):
        """
          Takes resolved decision tuples and coverts them into a format that is easily consumed as a dataframe
          pnl_data = (decision_ndx, current_ndx, y_prev, y, decision, pnl )
        """
        return self.pnl_data

    def to_records(self) -> [Dict]:
        records = [dict(zip(self.pnl_columns, pnl_rec)) for pnl_rec in self.pnl_data]
        return records

    def summary(self):
        """Returns a summary of PnL-related statistics from the resolved decisions."""
        pnl_values = [entry[-1] for entry in self.pnl_data if entry[-1] is not None]
        total_profit = sum(pnl_values)
        num_resolved = len(pnl_values)

        if num_resolved == 0:
            return {
                "current_ndx": self.current_ndx,
                "num_resolved_decisions": num_resolved,
                "total_profit": total_profit,
                "win_loss_ratio": None,
                "average_profit_per_decision": None,
                "avg_profit_per_decision_std_ratio": None
            }

        wins = sum(1 for pnl in pnl_values if pnl > 0)
        losses = sum(1 for pnl in pnl_values if pnl < 0)
        win_loss_ratio = wins / losses if losses != 0 else float('inf')  # Avoid division by zero

        avg_profit_per_decision = total_profit / num_resolved
        pnl_std = np.std(pnl_values) if num_resolved > 1 else 0  # Handle std for single entry case
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

    def to_dict(self):
        """
        Serializes the state of the PnL object to a dictionary.
        """
        return {
            'epsilon': self.epsilon,
            'backoff': self.backoff,
            'current_ndx': self.current_ndx,
            'last_attack_ndx': self.last_attack_ndx,
            'pending_decisions': self.pending_decisions,
            'pnl_data': self.pnl_data
        }


    @classmethod
    def from_dict(cls, state):
        """
        Deserializes the state from a dictionary into a new PnL instance.
        """
        instance = cls(
            epsilon=state.get('epsilon',EPSILON),
            backoff=state.get('backoff', 100),  # TODO put in config
        )
        instance.current_ndx = state.get('current_ndx',0)
        instance.last_attack_ndx = state.get('last_attack_ndx')
        instance.pending_decisions = state.get('pending_decisions',[])
        instance.pnl_data = state.get('pnl_data',[])
        return instance
