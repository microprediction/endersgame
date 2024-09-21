from endersgame.attackers.attackerwithsimplepnl import AttackerWithSimplePnL
import numpy as np


class RandomAttacker(AttackerWithSimplePnL):

    def __init__(self):
        super().__init__()

    def __call__(self, y: float, k: int = None) -> float:
        decision = np.sign(0.2*np.random.randn())
        self.update_pnl(y=y, decision=decision)
        return decision



if __name__=='__main__':
    # Process 500 Brownian motion points and then spit out the PnL
    from endersgame.attackers.attackerwithsimplepnl import AttackerWithSimplePnL
    import numpy as np


    class RandomAttacker(AttackerWithSimplePnL):

        def __init__(self):
            super().__init__()

        def __call__(self, y: float, k: int = None) -> float:
            # Generate a random decision (+1 or -1) based on a random Gaussian variable
            decision = int(np.random.randn())  # Random noise with standard deviation 0.2
            self.update_pnl(y=y, decision=decision)
            return decision


if __name__ == '__main__':
        # Generate 500 points of Brownian motion
        y_values = np.cumsum(np.random.randn(500))

        # Instantiate the attacker
        attacker = RandomAttacker()

        # Process each point and make decisions
        for y in y_values:
            decision = attacker(y=y)
            print(f"Price: {y:.2f}, Decision: {decision}")

        # Print the final PnL summary after 500 points
        summary = attacker.get_pnl_summary()
        print("\nPnL Summary after 500 points:")
        print(f"Current Index: {summary['current_ndx']}")
        print(f"Number of Resolved Decisions: {summary['num_resolved_decisions']}")
        print(f"Total Profit: {summary['total_profit']:.2f}")
