from endersgame.gameconfig import HORIZON
from typing import Dict

class BaseAttacker:
    """
    [Your extensive docstring here]
    """

    def __init__(self):
        pass

    def tick(self, x: float):
        """
        Assimilate the current data point somehow into the model's state
        :param x:
        :return:
        """
        pass

    def predict(self, horizon: int = HORIZON) -> float:
        """
        :param horizon:  Horizon
        :return: Usually returns 0. Sometimes returns a positive number or negative number.
        """
        # Remark: some will create the class and attach predict later, so we don't want this abstract
        raise NotImplementedError('predict must be implemented by derived class')

    def tick_and_predict(self, x: float, horizon: int = HORIZON) -> float:
        """
        :param x:   The current data point in the sequence.
        :param horizon:   The prediction horizon
        :return:    A float indicating directional opinion, if any (1=up, 0=neither, -1=down)
        """
        self.tick(x=x)
        return self.predict(horizon=horizon)

    def to_dict(self):
        return {}

    @classmethod
    def from_dict(cls, state:Dict):
        return cls.__new__(cls)
