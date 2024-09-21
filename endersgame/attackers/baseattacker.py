from abc import ABC, abstractmethod

class BaseAttacker(ABC):

    """

        An "attacker" consumes a sequence of numbers y1, y2, ... one at a time
        We assume this sequence is very close to being a martingale, meaning for example that
               E[y_{t+k}] = y_t
        where y_t is the current arriving data point and y_{t+k} is a future one (k=100 say).

        In other words, it consumes something *like* a stock price. The attacker's job is to look for deviations
        from this martingale property and provide a simple up or down signal. The attacker usually returns zero

        But sometimes, ... (speaking loosely) ...

            1. If the attacker believes that the series of values are likely to be higher in the future:
                  -> it will instead return a positive number (it doesn't matter which one)

            2. If the attacker believes that the series of values are likely to be lower in the future:
                  -> it will return a negative number (it doesn't matter which one)

        It is up to you to design an attacker. The base attacker is extremely minimalist, but we also provide
        examples of other attackers you can fork or mixin.

        Judging attackers
        -----------------

        Attackers will typically be judged by the difference between y_{t+k} and y_t. For example if the attacker
        indicates at time t that the series is going to go up by time t+h, and it does indeed go up, then the
        profit for the attacker if y_{t+k} - y_t. However, the converse also applies.

        Conventions
        -----------

        1) Fitting. You can assume that every epoch (a large, unspecified number of observations ... say 10000 to be concrete) your
        attacker's fit() method will be called. You can use this for periodic time-intensive fitting that can take (again, to be
        concrete, a few minutes up to an hour).

        2) Horizon. It is safe to assume that 'k' will be consistent from one invocation to the next.


    """


    def __init__(self):
        self.fitted = False

    @abstractmethod
    def __call__(self, y: float, k:int=None)->float:
        """Should handle all online learning and buffering of history as needed."""
        return 0

    @abstractmethod
    def fit(self):
        """Fit method to be implemented by subclasses."""
        self.fitted=True




