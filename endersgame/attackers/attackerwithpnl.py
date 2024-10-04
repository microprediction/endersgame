from endersgame.accounting.pnl import Pnl
from endersgame.attackers.baseattacker import BaseAttacker
from endersgame import EPSILON
from endersgame.gameconfig import HORIZON
from typing import Dict, Any

class AttackerWithPnl(BaseAttacker):
    """
    An attacker that tracks profit and loss (PnL).
    """

    def __init__(self, epsilon: float = EPSILON):
        super().__init__()
        self.pnl = Pnl(epsilon=epsilon)

    def tick_and_predict(self, x: float, horizon: int = HORIZON) -> float:
        """
        Assimilate the current data point, make a prediction, and track PnL.
        :param x: The current data point in the sequence.
        :param horizon: The prediction horizon.
        :return: A float indicating directional opinion, if any (1=up, 0=neither, -1=down).
        """
        self.tick(x=x)
        decision = self.predict(horizon=horizon)
        self.pnl.tick(x=x, horizon=horizon, decision=decision)
        return decision

    def tick(self, x: float):
        """
        Implement the tick method.
        Assimilate the current data point into the model's state.
        :param x: The current data point.
        """
        # Example implementation: Update internal state based on x
        # For now, we'll pass. Subclasses can override this method.
        pass

    def predict(self, horizon: int = HORIZON) -> float:
        """
        Implement the predict method.
        Provide a simple prediction based on PnL data.
        :param horizon: The prediction horizon.
        :return: A float indicating directional opinion, if any (1=up, 0=neither, -1=down).
        """
        # Example prediction logic based on PnL data
        # For simplicity, return 0.0
        return 0.0

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize the instance's state to a dictionary.
        :return: A dictionary representing the instance's state.
        """
        state = super().to_dict()
        state['pnl'] = self.pnl.to_dict()
        return state

    @classmethod
    def from_dict(cls, state: Dict[str, Any]) -> 'AttackerWithPnl':
        epsilon_with_fallback = state.get('pnl',{'epsilon':EPSILON}).get('epsilon')
        attacker = cls(epsilon=epsilon_with_fallback)
        attacker.pnl = Pnl.from_dict(state.get('pnl',{}))
        return attacker
