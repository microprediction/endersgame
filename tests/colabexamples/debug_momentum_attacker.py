
# https://github.com/microprediction/endersnotebooks/blob/main/momentum_attacker.ipynb

from endersgame import Attacker
from endersgame import stream_generator, stream_generator_generator
import numpy as np
import types
from pprint import pprint
import json
import scipy.optimize as opt
from typing import Iterable, Iterator
from pprint import pprint


class MyAttacker(Attacker):

     def __init__(self, **kwargs):
        super().__init__(**kwargs)

     def tick(self, x:float):
        pass

     def predict(self, horizon: int = None) -> float:
        return 0


if __name__=='__main__':
    from endersgame.accounting.pnlutil import zero_pnl_summary, add_pnl_summaries
    gen_gen = stream_generator_generator(category='train')
    attacker = MyAttacker()
    total_pnl = zero_pnl_summary()
    for stream in gen_gen:
        for message in stream:
            attacker.tick_and_predict(x=message['x'])
        stream_pnl = attacker.pnl.summary()
        total_pnl = add_pnl_summaries(total_pnl,stream_pnl)

    total_pnl.update({'profit_per_decision':total_pnl['total_profit']/total_pnl['num_resolved_decisions']})
    pprint(total_pnl)
