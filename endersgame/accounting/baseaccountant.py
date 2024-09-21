
class BaseAccountant:
    """
    A mixin to track the PnL (Profit and Loss) of decisions made by an attacker.

    All state is stored under the `.accounting` property to avoid any conflicts.

    - Non-zero decisions are tracked in a list of dictionaries.
    - Each decision is resolved when the corresponding future value becomes available.
    - Decisions made within 100 data points of the last attack are ignored.

    The result is stored in a Python list of dictionaries, which can easily be processed later.
    """

    def __init__(self):
        self.reset_pnl()

    def reset_pnl(self):
        """Resets all PnL tracking variables within the accounting property."""
        self.accounting = {
            "current_observation_ndx": 0,
            "last_attack_ndx": None,
            "pending_decisions": [],  # Store decisions waiting for future values
            "pnl_data": []  # List to store the resolved predictions
        }

    def record_decision(self, current_ndx: int, decision: float):
        """
        Store a decision made at the current time step.

        Parameters:

        - current_time: The current time step in the sequence.
        - decision: The decision made (positive for up, negative for down).

        """
        # Increment total observations
        self.accounting["current_observation_ndx"] += 1

        # Ignore decision if made within 100 steps of the last attack
        if self.accounting["last_attack_ndx"] is not None and \
                (current_ndx - self.accounting["last_attack_ndx"]) < 100:
            return

        # Store the decision and the time it was made
        if decision != 0:
            self.accounting["pending_decisions"].append((current_ndx, decision))
            self.accounting["last_attack_ndx"] = current_ndx

    def resolve_decisions(self, current_ndx: int, y_current: float):
        """
        Resolve pending decisions by calculating PnL when enough time has passed and the future value is available.

        Parameters:
        - current_time: The current time step in the sequence.
        - y_current: The newly arrived data point (the current value of the sequence).
        """
        resolved_decisions = []
        for decision_ndx, decision in self.accounting["pending_decisions"]:
            k = current_ndx - decision_ndx  # Horizon passed since the decision
            if k >= 100:  # Adjust '100' to your desired prediction horizon
                # Calculate PnL based on whether the decision was positive or negative
                past_value = y_current  # The future value we predicted
                pnl = None

                if decision > 0:
                    pnl = current_ndx - past_value  # Profit if series went up
                elif decision < 0:
                    pnl = past_value - current_ndx  # Profit if series went down

                # Add the resolved decision to the list in dictionary format
                self.accounting["pnl_data"].append({
                    "decision_time": decision_ndx,
                    "resolution_time": current_ndx,
                    "decision": decision,
                    "pnl": pnl
                })

                resolved_decisions.append((decision_ndx, decision))

        # Remove resolved decisions from the pending list
        self.accounting["pending_decisions"] = [
            d for d in self.accounting["pending_decisions"] if d not in resolved_decisions
        ]

    def to_list(self):
        """
        Returns the list of resolved predictions.
        """
        return self.accounting["pnl_data"]

    def get_pnl_summary(self):
        """
        Returns a summary of PnL-related statistics from the resolved decisions.
        """
        total_profit = sum([entry['pnl'] for entry in self.accounting["pnl_data"] if entry['pnl'] is not None])
        return {
            "current_observation_ndx": self.accounting["current_observation_ndx"],
            "num_resolved_decisions": len(self.accounting["pnl_data"]),
            "total_profit": total_profit
        }
