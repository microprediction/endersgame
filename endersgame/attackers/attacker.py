from endersgame.attackers.attackerwithpnl import AttackerWithPnl
from endersgame.mixins.historymixin import HistoryMixin
from endersgame import EPSILON
from endersgame.gameconfig import HORIZON, DEFAULT_HISTORY_LEN
from typing import Dict, Any
import numpy as np


ATTACKER_DESCRIPTION = """

     A recommended attacker for everyday use, providing the following conveniences:  
       
     Lagged values: 
         self.get_recent_history(n) 
         self.pnl.summary()->dict 

     You need only implement the following in your derived class:
          tick(x)                              To add your own logic that assimilated the incoming data point ...
          predict()                            To provide a decision by any means or ...
          predict_from_history(xs:[float])     To provide a decision only using the lagged values
          
     You probably want to keep the provided tick_and_predict() method as this will handle pnl and history for you. 
     
     

"""


class Attacker(AttackerWithPnl,  HistoryMixin):

    def __init__(self, epsilon:float=EPSILON, max_history_len= DEFAULT_HISTORY_LEN):
        super().__init__(epsilon=epsilon)
        HistoryMixin.__init__(self, max_history_len=max_history_len)  # Initialize HistoryMixin

    def tick_and_predict(self, x: float, horizon: int = HORIZON) -> float:
        """
            Boilerplate for an attacker with history, profit and loss tracking
            There's probably no need to change this.
        """
        self.tick(x=x)
        self.tick_history(x=x)
        decision = self.predict(horizon=horizon)
        self.pnl.tick(x=x, horizon=horizon, decision=decision)
        return decision

    def tick(self, x):
        # Your logic goes here for all data assimilation
        # You don't need to worry about any kind of updates for the future profit tracking.
        # You don't need to worry about maintaining the history buffer
        # Maybe you can just leave it as is!
        pass

    def predict_using_history(self, xs: [float], horizon: int = HORIZON) -> float:
        """
        :param xs:         Recent observations in chronological ordering
        :param horizon:    The number of observations to predict ahead (you can safely assume it is always HORIZON)
        :return:
        """
        # Create a decision using chronologicaly ordered fixed length vector xs
        raise NotImplementedError(
            "You derived from AttackerWithHistoryMixin but failed to implement either predict_using_history or predict")

    def predict(self, horizon: int = HORIZON) -> float:
        """
        :param horizon:
        :return:
        """
        if self.is_history_full():
            return self.predict_using_history(xs=list(self.history), horizon=horizon)
        else:
            return 0

    def to_dict(self) -> Dict[str, Any]:
        base_state = super().to_dict()
        history_state = HistoryMixin.to_dict(self)
        base_state.update(history_state)
        return base_state

    @classmethod
    def from_dict(cls, state: Dict[str, Any]):
        max_history_len_with_fallback = state.get('max_history_len', DEFAULT_HISTORY_LEN)
        instance = super().from_dict(state)
        history_data = state.get('history', [])
        instance.history = HistoryMixin.set_history(history_data=history_data, maxlen=max_history_len_with_fallback)
        instance.max_history_len = max_history_len_with_fallback
        return instance


if __name__=='__main__':

    # Example of creating your own attacker

    class MyMomentumAttacker(Attacker):

        def __init__(self, **kwargs):
            super().__init__(**kwargs)   # Boilerplate

        def predict_using_history(self, xs:[float], horizon:int):
            """  An example of taking lagged values
            :param xs:
            :return:
            """
            short_term_mean = np.mean(xs[-10:])
            long_term_mean = np.mean(xs[-100:])
            devo = np.std(np.diff(xs))
            momentum = 10*(long_term_mean - short_term_mean)/(long_term_mean*devo)
            signal = int(momentum)    # Usually zero, +1 for buy, -1 for sell
            return signal

    # Example of using it

    attacker = MyMomentumAttacker(max_history_len=100) # <-- By default no predictions will occur until the buffer is full
    xs = np.cumsum(np.random.randn(110)+0.01)
    for k,x in enumerate(xs):
        decision = attacker.tick_and_predict(x=x)
        if decision>0:
            print(f'Buy now at time {k} !', flush=True)
        if decision<0:
            print(f'Sell now at time {k}!')



