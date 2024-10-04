
# https://github.com/microprediction/endersnotebooks/blob/main/mean_reversion_attacker.ipynb


from endersgame.attackers.attackerwithpnl import AttackerWithPnl
from endersgame.rivertransformers.macd import MACD
from endersgame.datasources.streamgenerator import stream_generator
from river import stats
import numpy as np
import math
import types
from pprint import pprint
import json
import scipy.optimize as opt
from endersgame.datasources.streamgeneratorgenerator import stream_generator_generator
from endersgame.gameconfig import HORIZON
from typing import Iterable, Iterator



def test_colab_notebook_example():

    class MyAttacker(AttackerWithPnl):

         def __init__(self, a=0.01, **kwargs):
            super().__init__(**kwargs)
            self.state = {'running_avg':None,
                          'current_value':None}
            self.params = {'a':a}

         def tick(self, x:float):
             # Maintains an expon moving average of the data
             self.state['current_value'] = x
             if not np.isnan(x):
                if self.state['running_avg'] is None:
                    self.state['running_avg'] = x
                else:
                    self.state['running_avg'] = (1-self.params['a'])*self.state['running_avg'] + self.params['a']*x


    x_train_stream = stream_generator(stream_id=0,category='train', return_float=True)
    attacker = MyAttacker()
    for x in x_train_stream:
        attacker.tick(x)

    print(f"After processing the entire stream, the current value is  {attacker.state['current_value']} and the moving average is {attacker.state['running_avg']}")
    print(attacker.state)

    def predict(self, horizon: int = None) -> float:
        if self.state['current_value'] > self.state['running_avg'] + 2:
            return -1
        if self.state['current_value'] < self.state['running_avg'] - 2:
            return 1
        return 0

    attacker = MyAttacker()
    attacker.predict = types.MethodType(predict,
                                        attacker)  # <-- Attach the predict method to our existing instance of attacker

    attacker.state['current_value'] = 10
    attacker.state['running_avg'] = 5
    print(attacker.predict())

    horizon = 100       # Horizon
    x_test_stream = stream_generator(stream_id=1,category='train', return_float=True)
    attacker = MyAttacker()
    attacker.predict = types.MethodType(predict, attacker)     #  <-- If you get sick of doing this then put the method in the class at the outset
    for x in x_test_stream:
        y = attacker.tick_and_predict(x=x,horizon=horizon)

    pprint(attacker.state)
    pprint(attacker.pnl.summary())
