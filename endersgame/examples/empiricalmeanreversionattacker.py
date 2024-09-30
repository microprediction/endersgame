from endersgame.examples.meanreversionattacker import MeanReversionAttacker
from endersgame.attackers.empiricalattacker import EmpiricalAttacker
from tests.examples.test_bufferingattacker import attacker



if __name__=='__main__':
    mra = MeanReversionAttacker(a=0.04)
    emra = EmpiricalAttacker(attacker=mra)


