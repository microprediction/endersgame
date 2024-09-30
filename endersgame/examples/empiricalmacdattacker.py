from endersgame.examples.macdattacker import MacdAttacker
from endersgame.attackers.empiricalattacker import EmpiricalAttacker


if __name__=='__main__':
    mac = MacdAttacker()
    emac = EmpiricalAttacker(attacker=mac)

