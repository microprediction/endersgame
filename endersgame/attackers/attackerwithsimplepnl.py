from endersgame.accounting.pnl import PnL
from endersgame.attackers.baseattacker import BaseAttacker
from abc import abstractmethod


class AttackerWithSimplePnL(BaseAttacker):

    def __init__(self, epsilon:float):
        BaseAttacker.__init__(self)
        self.pnl = PnL(epsilon=epsilon)

    def tick_and_predict(self, x: float, k: int = None) -> float:
        """
            Boilerplate for an attacker with profit and loss tracking
        """
        self.tick(x=x)
        decision = self.predict(k=k)
        self.pnl.tick(x=x, k=k, decision=decision)
        return decision

    @abstractmethod
    def tick(self, x):
        # Your logic goes here
        pass

    @abstractmethod
    def predict(self, k:int=None)->float:
        # Your logic goes here
        return 0

