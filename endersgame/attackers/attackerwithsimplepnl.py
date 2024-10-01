from endersgame.accounting.pnl import PnL
from endersgame.attackers.baseattacker import BaseAttacker


class AttackerWithSimplePnL(BaseAttacker):

    def __init__(self, epsilon:float):
        BaseAttacker.__init__(self)
        self.pnl = PnL(epsilon=epsilon)

    def tick_and_predict(self, x: float, horizon: int = None) -> float:
        """
            Boilerplate for an attacker with profit and loss tracking
        """
        self.tick(x=x)
        decision = self.predict(horizon=horizon)
        self.pnl.tick(x=x, horizon=horizon, decision=decision)
        return decision

    def tick(self, x):
        # Your logic goes here
        pass

    def predict(self, horizon:int=None)->float:
        # Your logic goes here
        return 0

