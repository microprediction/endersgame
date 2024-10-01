from endersgame.examples.macdattacker import MacdAttacker
from endersgame.attackers.calibratedattacker import CalibratedAttacker
from endersgame.syntheticdata.momentumregimes import momentum_regimes
from pprint import pprint

if __name__=='__main__':
    mac = MacdAttacker()
    emac = CalibratedAttacker(attacker=mac)
    xs = momentum_regimes(n=20000)
    for x in xs:
        emac.tick_and_predict(x=x, horizon=10)

    pprint(emac.pnl.summary())
