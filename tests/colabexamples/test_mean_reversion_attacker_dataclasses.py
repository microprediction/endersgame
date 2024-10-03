from endersgame.datasources.streamgenerator import stream_generator
import numpy as np
import types
from pprint import pprint
from endersgame.attackers.attackerwithpnl import AttackerWithPnl
from dataclasses import dataclass


@dataclass
class State:
    running_avg: float = None
    current_value: float = None


@dataclass
class Params:
    a: float = 0.01


class MyAttacker(AttackerWithPnl):
    def __init__(self, a: float = 0.01, **kwargs):
        super().__init__(**kwargs)
        self.state = State()
        self.params = Params(a=a)

    def tick(self, x: float):
        # Maintains an exponential moving average of the data
        self.state.current_value = x
        if not np.isnan(x):
            if self.state.running_avg is None:
                self.state.running_avg = x
            else:
                self.state.running_avg = (1 - self.params.a) * self.state.running_avg + self.params.a * x


def test_colab_notebook_example():
    x_train_stream = stream_generator(stream_id=0, category='train', return_float=True)
    attacker = MyAttacker()
    for x in x_train_stream:
        attacker.tick(x)

    print(f"After processing the entire stream, the current value is {attacker.state.current_value} and the moving average is {attacker.state.running_avg}")
    print(attacker.state)

    # Define the predict method
    def predict(self, horizon: int = None) -> float:
        if self.state.current_value > self.state.running_avg + 2:
            return -1
        if self.state.current_value < self.state.running_avg - 2:
            return 1
        return 0

    # Attach the predict method to the attacker instance
    attacker.predict = types.MethodType(predict, attacker)

    # Test the predict method
    attacker.state.current_value = 10
    attacker.state.running_avg = 5
    print(attacker.predict())

    # Testing with a horizon
    horizon = 100  # Horizon
    x_test_stream = stream_generator(stream_id=1, category='train', return_float=True)
    attacker = MyAttacker()
    attacker.predict = types.MethodType(predict, attacker)  # Attach predict method to attacker instance
    for x in x_test_stream:
        y = attacker.tick_and_predict(x=x, horizon=horizon)

    pprint(attacker.state)
    pprint(attacker.pnl.summary())


# Running the test function if this script is executed directly
if __name__ == "__main__":
    test_colab_notebook_example()
