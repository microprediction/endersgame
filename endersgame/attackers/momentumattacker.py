from endersgame.attackers.baseattacker import BaseAttacker
import numpy as np


class MomentumAttacker(BaseAttacker):

    # This will receive one value at a time
    # If it thinks that the values will be higher than the current one in the future, it returns a positive number
    # Here "future" means 100

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._buffer = []

    def __call__(self,x:float)->float:
        self._buffer.append(x)
        if len(self._buffer)<100:
            return 0
        else:
            recent = self._buffer[-50:]
            prior  = self._buffer[-100:-50]
            diff = (np.mean(recent)-np.mean(prior))/(np.std(recent)+np.std(prior)+1e-6)
            direction = int(diff)
            return direction


if __name__=='__main__':
    xs = np.cumsum(np.random.randn(500))
    attacker = MomentumAttacker()
    for x in xs:
        decision = attacker(x)
        print(decision)










