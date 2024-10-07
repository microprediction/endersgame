
# https://github.com/microprediction/endersnotebooks/blob/main/momentum_attacker.ipynb

from endersgame import Attacker
from endersgame import stream_generator_generator
from pprint import pprint
from endersgame import FEWMean, FEWVar
import math

class MyAttacker(Attacker):

     def __init__(self, fast_fading_factor:dict=0.1, slow_fading_factor=0.01, diff_fading_factor=0.001, threshold = 2, burn_in=100, **kwargs):
         super().__init__(**kwargs)
         self.threshold = threshold
         self.fast_ewa = FEWMean(fading_factor=fast_fading_factor)
         self.slow_ewa = FEWMean(fading_factor=slow_fading_factor)
         self.diff_var = FEWVar(fading_factor=diff_fading_factor)    # Tracks mean and var of the difference
         self.countdown = burn_in

     def tick(self, x:float):
         self.fast_ewa.tick(x=x)
         self.slow_ewa.tick(x=x)
         fast_minus_slow = self.fast_ewa.get() - self.slow_ewa.get()
         self.diff_var.tick(x=fast_minus_slow)
         self.countdown -= 1

     def predict(self, horizon: int = None) -> float:
         """
               We buy if signal > threshold*(trailing std of signal)
         """
         if self.countdown>0:
             return 0    # Not warmed up
         fast_minus_slow = self.fast_ewa.get() - self.slow_ewa.get()
         try:
             fast_minus_slow_std = math.sqrt( self.diff_var.get())
             signal = int(fast_minus_slow/(self.threshold*fast_minus_slow_std))
             return signal
         except ArithmeticError:
             return 0

def test_momentum_attacker():
    from endersgame.accounting.pnlutil import zero_pnl_summary, add_pnl_summaries
    gen_gen = stream_generator_generator(category='test')
    attacker = MyAttacker()
    total_pnl = zero_pnl_summary()
    stream_count = 0
    for stream in gen_gen:
        for message in stream:
            attacker.tick_and_predict(x=message['x'])
        stream_pnl = attacker.pnl.summary()
        total_pnl = add_pnl_summaries(total_pnl,stream_pnl)
        stream_count += 1
        if stream_count>=2:
            break

    total_pnl.update({'profit_per_decision':total_pnl['total_profit']/total_pnl['num_resolved_decisions']})
    pprint(total_pnl)
