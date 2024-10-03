from collections import deque
from endersgame.attackers.attackerwithpnl import BaseAttacker
from endersgame.gameconfig import HORIZON, EPSILON, DEFAULT_HISTORY_LEN
from endersgame.mixins.historymixin import HistoryMixin
import numpy as np


class AttackerWithHistoryMixin(BaseAttacker, HistoryMixin):
    """
        Demonstrates how to use the HistoryMixin to add a 'history' property
        Derived classes need only implement predict_using_history
    """

    def __init__(self, max_history_len=DEFAULT_HISTORY_LEN, epsilon=EPSILON):
        super().__init__()
        HistoryMixin.__init__(self, max_history_len=max_history_len)  # Initialize HistoryMixin

    def tick(self, x: float) -> None:
        """
        Adds the latest observation `x` to the history deque.
        Automatically removes the oldest value if the max length is reached.
        """
        self.tick_history(x)

    def predict_using_history(self, xs:[float], horizon:int=HORIZON)->float:
        # Create a decision using chronologicaly ordered fixed length vector xs
        raise NotImplementedError("You derived from AttackerWithHistoryMixin but failed to implement either predict_using_history or predict")

    def predict(self,horizon: int = HORIZON) -> float:
        """
        :param horizon:
        :return:
        """
        if self.is_history_full():
            return self.predict_using_history(xs=list(self.history), horizon=horizon)
        else:
            return 0


class ExampleHistoricalAttacker(AttackerWithHistoryMixin):

    """
        An example of an attacker that takes a fixed length history
        and simply applies a function to it
    """

    def __init__(self, max_history_len=200):
        super().__init__(max_history_len=max_history_len)

    def predict_using_history(self, xs:[float], horizon:int=HORIZON) ->float:
        if xs[-1]>np.median(xs)+1:
            return 1


