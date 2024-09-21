from endersgame.accounting.baseaccountant import BaseAccountant
from endersgame.attackers.baseattacker import BaseAttacker



class AttackerWithPnL(BaseAttacker, BaseAccountant):

    def __init__(self):
        BaseAttacker.__init__(self)
        BaseAccountant.__init__(self)

    def __call__(self, y: float, k: int = None) -> float:
        decision = 0
        self.record_decision(current_time=self.total_observations, decision=decision)
        return decision

    def fit(self):
        # Your fitting logic here
        pass

