from collections import namedtuple
from endersgame.datasources.streamgenerator import stream_generator
import numpy as np
from pprint import pprint
from endersgame.attackers.attackerwithsimplepnl import AttackerWithSimplePnL

# Define named tuples for State and Params
State = namedtuple('State', ['running_avg', 'current_value'])
Params = namedtuple('Params', ['a'])


class MyAttacker(AttackerWithSimplePnL):
    def __init__(self, a=0.01, **kwargs):
        """
        Initialize MyAttacker with parameters and initial state.

        Args:
            a (float): Smoothing factor for exponential moving average.
            **kwargs: Additional keyword arguments for the base class.
        """
        super().__init__(**kwargs)
        self.params = Params(a=a)
        self.state = State(running_avg=None, current_value=None)

    def tick(self, x: float):
        """
        Update the state with a new value and compute the exponential moving average.

        Args:
            x (float): New data point.
        """
        # Update current_value
        self.state = self.state._replace(current_value=x)

        # Update running_avg if x is a valid number
        if not np.isnan(x):
            if self.state.running_avg is None:
                new_running_avg = x
            else:
                new_running_avg = (1 - self.params.a) * self.state.running_avg + self.params.a * x
            self.state = self.state._replace(running_avg=new_running_avg)

    def predict(self, horizon: int = None) -> float:
        """
        Make a prediction based on the current value and running average.

        Args:
            horizon (int, optional): Prediction horizon. Defaults to None.

        Returns:
            float: Prediction value (-1, 0, or 1).
        """
        if self.state.current_value is None or self.state.running_avg is None:
            return 0  # Default prediction if not enough data
        if self.state.current_value > self.state.running_avg + 2:
            return -1
        if self.state.current_value < self.state.running_avg - 2:
            return 1
        return 0

    def tick_and_predict(self, x: float, horizon: int = None) -> float:
        """
        Update the state with a new value and return the prediction.

        Args:
            x (float): New data point.
            horizon (int, optional): Prediction horizon. Defaults to None.

        Returns:
            float: Prediction value.
        """
        self.tick(x)
        return self.predict(horizon)


def test_colab_notebook_example():
    """
    Test function to demonstrate the functionality of MyAttacker using named tuples.
    """
    # Initialize the training stream
    x_train_stream = stream_generator(stream_id=0, category='train')

    # Initialize the attacker
    attacker = MyAttacker()

    # Process the training stream
    for x in x_train_stream:
        attacker.tick(x)

    # Display the state after processing the training stream
    print(
        f"After processing the entire stream, the current value is {attacker.state.current_value} and the moving average is {attacker.state.running_avg}")
    print("State:", attacker.state)

    # Manually set state for testing the predict method
    attacker.state = attacker.state._replace(current_value=10, running_avg=5)
    print(f"Prediction with current_value=10 and running_avg=5: {attacker.predict()}")

    # Initialize the test stream
    horizon = 100  # Horizon
    x_test_stream = stream_generator(stream_id=1, category='train')

    # Re-initialize the attacker for testing
    attacker = MyAttacker()

    # Process the test stream and make predictions
    for x in x_test_stream:
        y = attacker.tick_and_predict(x=x, horizon=horizon)
        # Here, you can collect predictions 'y' if needed

    # Display the final state and PnL summary after processing the test stream
    pprint("Final State:")
    pprint(attacker.state)
    pprint("PnL Summary:")
    pprint(attacker.pnl.summary())


# Run the test function if this script is executed directly
if __name__ == "__main__":
    test_colab_notebook_example()
