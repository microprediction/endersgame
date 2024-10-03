from endersgame.attackers.attackerwithpnl import AttackerWithPnl
import numpy as np


class RandomAttacker(AttackerWithPnl):

    def __init__(self, epsilon):
        super().__init__(epsilon)

    def tick(self, x):
        pass

    def predict(self, horizon:int) -> float:
        return int(0.5*np.random.randn())



if __name__ == '__main__':
        # Generate 500 points of Brownian motion
        y_values = np.cumsum(np.random.randn(500))

        # Instantiate the attacker
        attacker = RandomAttacker(epsilon=0.01)

        k = 10  # horizon

        # Process each point and make decisions
        for y in y_values:
            decision = attacker.tick_and_predict(x=y, horizon=k)
            print(f"Price: {y:.2f}, Decision: {decision}")

        # Print the final PnL summary after 500 points
        summary = attacker.pnl.summary()
        print("\nPnL Summary after 500 points:")
        print(f"Current Index: {summary['current_ndx']}")
        print(f"Number of Resolved Decisions: {summary['num_resolved_decisions']}")
        print(f"Total Profit: {summary['total_profit']:.2f}")
