from endersgame.attackers.baseattacker import BaseAttacker
import numpy as np



class BufferingAttacker(BaseAttacker):

    """
         An example of an attacker that maintains a history and applies a function to the buffer
         This style is not encouraged, but its a free country (well, we hope you live in one)
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._history = []
        self._max_history_len = 20000
        self._warmup = 1000
        self._prediction_period = 25       # How often to predict


    def tick(self,y:float)->float:
        self._history.append(y)
        if len(self._history) > self._max_history_len:
            self._history = self._history[-19000:]


    def _predict_using_buffer(self)->float:
        # Just an example
        recent = self._history[-50:]
        prior = self._history[-100:-50]
        diff = (np.mean(recent) - np.mean(prior)) / (np.std(recent) + np.std(prior) + 1e-6)
        direction = int(diff)
        return direction

    def predict(self, k:int=None)->float:
        """
            Merely to illustrate the pattern of using saved history
        """
        if len(self._history)<self._warmup:
            return 0   # Not warmed up
        if (len(self._history) % self._prediction_period) != 0:
            return 0   # Don't predict too often

        return self._predict_using_buffer()

    def fit(self):
        pass

if __name__=='__main__':
    ys = np.cumsum(np.random.randn(500))
    attacker = BufferingAttacker()
    for y in ys:
        decision = attacker.tick_and_predict(y=y)
        print(decision)










