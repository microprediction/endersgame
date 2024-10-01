from endersgame.accounting.pnl import PnL
from endersgame.attackers.baseattacker import BaseAttacker
from endersgame import EPSILON
from endersgame.gameconfig import HORIZON
from abc import abstractmethod

class AttackerWithSimplePnL(BaseAttacker):

    def __init__(self, epsilon:float=EPSILON):
        super().__init__()
        self.pnl = PnL(epsilon=epsilon)

    def tick_and_predict(self, x: float, horizon: int = HORIZON) -> float:
        """
            Boilerplate for an attacker with profit and loss tracking
        """
        self.tick(x=x)
        decision = self.predict(horizon=horizon)
        self.pnl.tick(x=x, horizon=horizon, decision=decision)
        return decision

    @abstractmethod
    def tick(self, x):
        # Your logic goes here
        pass

    def predict(self, horizon:int=HORIZON)->float:
        # Your logic goes here
        return 0

