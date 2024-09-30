# empiricalmeanreversionattacker.py

from endersgame.accounting.signalpnl import SignalPnl
from endersgame.accounting.pnl import PnL


class EmpiricalAttacker:
    """
        It will take an attacker's decisions and act on them when empirically justified
    """

    def __init__(self, attacker, epsilon=0.005, decay=0.999, min_weight=1.0):
        """
             attacker:   Any attacker with a tick_and_predict function
             decay:      Decay factor for tracking the pnl of thresholded standardized decisions (see accounting.signalpnl.SignalPnl)
        """
        self.pnl = PnL(epsilon=epsilon)
        self.signal_pnl = SignalPnl(decay=decay, thresholds=None)
        self.attacker = attacker

    def tick_and_predict(self, x: float, k: int = 1):
        """
             Boilerplate for an 'empirical' attacker
        """
        signal = self.attacker.tick_and_predict(x)
        self.signal_pnl.tick(x=x, k=k, signal=signal)
        decision = self.signal_pnl.predict(signal=signal)
        self.pnl.tick(x=x, k=k, decision=decision)
        return decision


