import numpy as np
from endersgame.attackers.baseattacker import BaseAttacker


class MeanReversionAttacker(BaseAttacker):

    def __init__(self, a=0.01):
        super().__init__()
        self.state = {'running_avg': None,
                      'current_value': None}
        self.params = {'a': a}

    def tick(self, x: float):
        # Maintains an expon moving average of the data
        self.state['current_value'] = x
        if not np.isnan(x):
            if self.state['running_avg'] is None:
                self.state['running_avg'] = x
            else:
                self.state['running_avg'] = (1 - self.params['a']) * self.state['running_avg'] + self.params['a'] * x


    def predict(self, horizon:int=None)->float:
        if self.state['current_value'] > self.state['running_avg'] + 1:
            return -1
        if self.state['current_value'] < self.state['running_avg'] - 1:
            return 1
        return 0




if __name__=='__main__':

    attacker = MeanReversionAttacker()  # Reset it

    xs = [1, 3, 4, 2, 4, 5, 1, 5, 2, 5, 10] * 100
    for x in xs:
        y = attacker.tick_and_predict(x=x)
        if abs(y):
            print(y)
    xs = [1, 3, 4, 2, 4, 5, 1, 5, 2, 5, 1] * 100
    attacker = MeanReversionAttacker()
    for x in xs:
        y = attacker.tick_and_predict(x=54)
