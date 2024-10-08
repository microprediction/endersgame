from endersgame.examples.meanreversionattacker import MeanReversionAttacker
from endersgame.attackers.calibratedattacker import CalibratedAttacker


if __name__=='__main__':
    mra = MeanReversionAttacker(a=0.04)
    emra = CalibratedAttacker(attacker=mra)


