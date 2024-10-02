from endersgame.datasources.streamgenerator import stream_generator
import numpy as np
from pprint import pprint
from endersgame.attackers.attackerwithsimplepnl import AttackerWithSimplePnL
from dataclasses import dataclass, field


@dataclass
class MyAttacker(AttackerWithSimplePnL):
    a: float = 0.01
    running_avg: float = field(default=None)
    current_value: float = field(default=None)

    def __post_init__(self):
        super().__init__()
        # Any additional initialization can be done here if necessary

    def tick(self, x: float):
        """
        Maintains an exponential moving average of the data.
        """
        self.current_value = x
        if not np.isnan(x):
            if self.running_avg is None:
                self.running_avg = x
            else:
                self.running_avg = (1 - self.a) * self.running_avg + self.a * x

    def predict(self, horizon: int = None) -> float:
        """
        Predicts based on the current value and the running average.
        """
        if self.current_value is None or self.running_avg is None:
            return 0  # Default prediction if not enough data
        if self.current_value > self.running_avg + 2:
            return -1
        if self.current_value < self.running_avg - 2:
            return 1
        return 0

    def tick_and_predict(self, x: float, horizon: int = None) -> float:
        """
        Ticks with the new value and returns the prediction.
        """
        self.tick(x)
        return self.predict(horizon)


def test_colab_notebook_example():
    # Initialize the training stream
    x_train_stream = stream_generator(stream_id=0, category='train', return_float=True)

    # Initialize the attacker
    attacker = MyAttacker()

    # Process the training stream
    for x in x_train_stream:
        attacker.tick(x)

    print(
        f"After processing the entire stream, the current value is {attacker.current_value} and the moving average is {attacker.running_avg}")
    print(attacker)

    # Test the predict method
    attacker.current_value = 10
    attacker.running_avg = 5
    print(f"Prediction with current_value=10 and running_avg=5: {attacker.predict()}")

    # Initialize the test stream
    horizon = 100  # Horizon
    x_test_stream = stream_generator(stream_id=1, category='train', return_float=True)

    # Re-initialize the attacker for testing
    attacker = MyAttacker()

    # Process the test stream and make predictions
    for x in x_test_stream:
        y = attacker.tick_and_predict(x=x, horizon=horizon)

    pprint(attacker)
    pprint(attacker.pnl.summary())


# Running the test function if this script is executed directly
if __name__ == "__main__":
    test_colab_notebook_example()
