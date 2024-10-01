from endersgame.examples.meanreversionattacker import MeanReversionAttacker
from endersgame.attackers.calibratedattacker import CalibratedAttacker
from tests.examples.test_baseattackerwithhistorymixin import attacker



if __name__=='__main__':
    mra = MeanReversionAttacker(a=0.04)
    emra = CalibratedAttacker(attacker=mra)


