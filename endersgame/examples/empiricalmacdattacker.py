from endersgame.examples.macdattacker import MacdAttacker
from endersgame.attackers.calibratedattacker import CalibratedAttacker


if __name__=='__main__':
    mac = MacdAttacker()
    emac = CalibratedAttacker(attacker=mac)

