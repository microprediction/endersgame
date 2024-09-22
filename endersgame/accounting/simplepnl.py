from typing import Dict


class SimplePnL:
    """
    A mixin to track the PnL (Profit and Loss) of decisions made by an attacker.

    Usage:
          .update_pnl(y=y,decision=decision)
       after every data point is received and an attack decision made


    All state is stored under the `.accounting` property to avoid any conflicts.

    - Non-zero decisions are tracked in a list of dictionaries.
    - Each decision is resolved when the corresponding future value becomes available.
    - Decisions made within 100 data points of the last attack are ignored.
    """

    def __init__(self):
        self.reset_pnl()

    def tick_pnl(self, y:float, k:int, decision:float):
        """

            Adds non-zero 'decision' to a queue so it can be judged later
            And uses revealed ground truth y to evaluate past decisions

        """
        self._add_decision_to_queue(y=y, k=k, decision=decision)
        self._resolve_decisions_on_queue(y=y)

    def reset_pnl(self):
        """Resets all PnL tracking variables within the accounting property."""
        self.simplepnl = {
            "backoff":100,              # Minimum time between non-zero predictions
            "current_ndx": 0,
            "last_attack_ndx": None,
            "pending_decisions": [],   # Store decisions waiting for future values
            "pnl_data": [],            # List to store the resolved predictions
            "pnl_columns": ['decision_ndx','resolution_ndx','horizon','decision','y_decision','y_resolution','pnl']
        }

    def _add_decision_to_queue(self, y:float, k:int, decision: float):
        """
        Store a decision made at the current time step.

        - y:        The last value seen when making the decision
        - decision: The decision made (positive for up, negative for down).
        """
        # Don't record a decision if another decision has recently been made
        # (We want to cut out machine gun attacks)
        if self.simplepnl["last_attack_ndx"] is not None and \
                (self.simplepnl['current_ndx'] - self.simplepnl["last_attack_ndx"]) < self.simplepnl['backoff']:
            self.simplepnl["current_ndx"] += 1
            return

        # Store the decision and the time it was made
        if decision != 0:
            self.simplepnl["pending_decisions"].append((self.simplepnl['current_ndx'], y, k, decision))
            self.simplepnl["last_attack_ndx"] = self.simplepnl['current_ndx']

        # Increment total observations
        self.simplepnl["current_ndx"] += 1

    def _resolve_decisions_on_queue(self, y: float):
        """
        Resolve pending decisions by calculating PnL when enough time has passed and the future value is available.

        - y: The newly arrived data point (the current value of the sequence).
        """
        resolved_decision_ndxs = []
        current_ndx = self.simplepnl['current_ndx']
        for pending_ndx, (decision_ndx, y_prev, k, decision) in enumerate(self.simplepnl["pending_decisions"]):
            num_observations_since_decision = current_ndx - decision_ndx  # Horizon passed since the decision
            if num_observations_since_decision >= k:  # Adjust '100' to your desired prediction horizon
                # Calculate PnL based on whether the decision was positive or negative
                if decision > 0:
                    pnl = y - y_prev  
                elif decision < 0:
                    pnl = y_prev - y  
                else:
                    raise ValueError('A non-zero decision was logged to the queue')

                # ['decision_ndx','resolution_ndx','k','decision','y_decision','y_resolution','pnl']
                pnl_data = (decision_ndx, current_ndx, k, decision, y_prev, y, pnl )
                resolved_decision_ndxs.append(pending_ndx)
                self.simplepnl["pnl_data"].append(pnl_data)

        # resolved_decision_ndxs contains a list of indexes into self.accounting["pending_decisions"] that we remove:
        self.simplepnl["pending_decisions"] = [d for (pndx, d) in enumerate(self.simplepnl['pending_decisions']) if pndx not in resolved_decision_ndxs]

    def get_pnl_tuples(self):
        """
          Takes resolved decision tuples and coverts them into a format that is easily consumed as a dataframe
          pnl_data = (decision_ndx, current_ndx, y_prev, y, decision, pnl )
        """
        return self.simplepnl["pnl_data"]


    def get_pnl_records(self)->[Dict]:
        records = [dict(zip(self.simplepnl['pnl_columns'], pnl_rec)) for pnl_rec in self.simplepnl["pnl_data"]]
        return records


    def get_pnl_summary(self):
        """
        Returns a summary of PnL-related statistics from the resolved decisions.
        """
        total_profit = sum([entry[-1] for entry in self.simplepnl["pnl_data"] if entry[-1] is not None])
        return {
            "current_ndx": self.simplepnl["current_ndx"],
            "num_resolved_decisions": len(self.simplepnl["pnl_data"]),
            "total_profit": total_profit
        }


