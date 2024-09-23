from endersgame.attackers.attackerwithsimplepnl import AttackerWithSimplePnL
import numpy as np


class RandomAttacker(AttackerWithSimplePnL):

    def __init__(self):
        super().__init__()

    def tick_and_predict(self, y: float, k: int = None) -> float:
        decision = int(0.5*np.random.randn())
        self.tick_pnl(y=y, k=k, decision=decision)
        return decision



if __name__ == '__main__':
        # Generate 500 points of Brownian motion
        y_values = np.cumsum(np.random.randn(500))

        # Instantiate the attacker
        attacker = RandomAttacker()

        k = 10  # horizon

        # Process each point and make decisions
        for y in y_values:
            decision = attacker.tick_and_predict(y=y,k=k)
            print(f"Price: {y:.2f}, Decision: {decision}")

        # Print the final PnL summary after 500 points
        summary = attacker.get_pnl_summary()
        print("\nPnL Summary after 500 points:")
        print(f"Current Index: {summary['current_ndx']}")
        print(f"Number of Resolved Decisions: {summary['num_resolved_decisions']}")
        print(f"Total Profit: {summary['total_profit']:.2f}")
