
from endersgame.accounting.stdsignalpnl import StdSignalPnl
from endersgame.accounting.pnl import Pnl
from endersgame.gameconfig import HORIZON


class CalibratedAttacker:
    """
        An example of using a raw "uncalibrated" attacker to make another one whose
        decisions are governed by empirical performance.

        The attacker's decisions (typically real valued) are treated as a signal in need of standardization.
        The P/L of trades that would be triggered by a standardized signal exceeding a threshold is tracked.
        Based on this, the predict method will provide a decision in {-1,0,1}
    """

    def __init__(self, attacker, epsilon=0.005, fading_factor=0.01, min_weight=1.0):
        """
             attacker:   Any attacker with a tick_and_predict function
             decay:      Decay factor for tracking the pnl of thresholded standardized decisions (see accounting.signalpnl.SignalPnl)
        """
        self.pnl = Pnl(epsilon=epsilon)
        self.signal_pnl = StdSignalPnl(fading_factor=fading_factor, thresholds=None)
        self.attacker = attacker

    def tick_and_predict(self, x: float, horizon: int = HORIZON):
        """
             Boilerplate for an 'empirical' attacker
        """
        signal = self.attacker.tick_and_predict(x)
        self.signal_pnl.tick(x=x, horizon=horizon, signal=signal)
        decision = self.signal_pnl.predict(epsilon=self.pnl.epsilon)
        self.pnl.tick(x=x, horizon=horizon, decision=decision)
        return decision


