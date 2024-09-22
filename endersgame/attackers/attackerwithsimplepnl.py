from endersgame.accounting.simplepnl import SimplePnL
from endersgame.attackers.baseattacker import BaseAttacker

# Illustrates how to mixin some simple accounting to your attacker

class AttackerWithSimplePnL(BaseAttacker, SimplePnL):

    def __init__(self):
        BaseAttacker.__init__(self)
        SimplePnL.__init__(self)

    def tick_and_predict(self, y: float, k: int = None) -> float:
        self.tick(y=y)
        decision = self.predict(k=k)
        self.tick_pnl(y=y, k=k, decision=decision)
        return decision

    def tick(self, y):
        pass

    def predict(self, k):
        return 0

    def fit(self):
        # Your fitting logic here
        pass


