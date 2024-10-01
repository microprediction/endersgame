from collections import deque
from endersgame.attackers.attackerwithsimplepnl import BaseAttacker
from abc import abstractmethod
from endersgame.mixins.historymixin import HistoryMixin
import numpy as np


class BaseAttackerWithHistoryMixin(BaseAttacker, HistoryMixin):
    """
        Demonstrates how to use the HistoryMixin to add a 'history' property
        Derived classes need only implement predict_using_history
    """

    def __init__(self, max_history_len=200, **kwargs):
        super().__init__(**kwargs)
        HistoryMixin.__init__(self, max_history_len=max_history_len)  # Initialize HistoryMixin

    def tick(self, x: float) -> None:
        """
        Adds the latest observation `x` to the history deque.
        Automatically removes the oldest value if the max length is reached.
        """
        self.tick_history(x)

    @abstractmethod
    def predict_using_history(self, xs:[float], horizon:int)->float:
        # Create a decision using chronologicaly ordered fixed length vector xs
        pass

    def predict(self,horizon: int = None) -> float:
        if self.is_history_full():
            return self.predict_from_sequence(list(self.history))
        else:
            return 0


class ExampleHistoricalAttacker(BaseAttackerWithHistoryMixin):

    """
        An example of an attacker that takes a fixed length history
        and simply applies a function to it
    """

    def __init__(self, max_history_len=200):
        super().__init__(max_history_len=max_history_len)

    def predict_using_history(self, xs:[float], horizon:int) ->float:
        if xs[-1]>np.median(xs)+1:
            return 1


