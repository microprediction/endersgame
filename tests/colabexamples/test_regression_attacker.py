from endersgame import Attacker, HORIZON, EPSILON
from river import linear_model
from collections import deque
from endersgame import Attacker
from endersgame import stream_generator_generator
from pprint import pprint


class RegressionAttacker(Attacker):
    """
    An attacker that uses an online linear regression model to predict future values
    and make trading decisions based on the expected profit exceeding EPSILON.
    """

    def __init__(self, num_lags=5, threshold:float=1.0, burn_in=1000, **kwargs):
        """
        Initializes the attacker.

        Parameters:
        - lag (int): Number of lagged values to use as features.
        """
        super().__init__(**kwargs)
        self.num_lags = num_lags                      # Number of lagged values to use as features
        self.model = linear_model.LinearRegression(   # Online linear regression model
            intercept_init=0.0,  # Initialize intercept to 0
            intercept_lr=0.0     # Freeze the intercept (no learning)
        )
        self.input_queue = deque()                    # Queue to store input vectors and time indices
        self.current_ndx = 0                          # Observation index
        self.threshold = threshold
        self.burn_in = burn_in

    def tick(self, x):
        """
        Processes the new data point.

        - Updates the time index.
        - Maintains a queue of input vectors.
        - When the future value arrives after HORIZON steps, updates the model.

        Parameters:
        - x (float): The new data point.
        """
        # The history is maintained by the parent class; no need to call tick_history()

        self.current_ndx += 1  
        X_t = self.get_recent_history(n=self.num_lags)
        if len(X_t) >= self.num_lags:
            self.input_queue.append({'ndx': self.current_ndx, 'X': X_t})

        # Check if we can update the model with data from HORIZON steps ago
        while self.input_queue and self.input_queue[0]['ndx'] <= self.current_ndx - HORIZON:
            # Retrieve the input vector and its time index
            past_data = self.input_queue.popleft()
            X_past = past_data['X']

            # The target value y is the data point at time 'time_past + HORIZON'
            # Since we're at 'current_time', and 'current_time = time_past + HORIZON', we can use 'x' as y
            y = x  # Current data point is the target for the input from HORIZON steps ago

            # Prepare the feature dictionary in the form demanded by river package
            X_past_dict = {f'lag_{i}': value for i, value in enumerate(X_past)}

            # Update the model incrementally
            self.model.learn_one(X_past_dict, y)

    def predict(self, horizon=HORIZON):
        """
        Makes a prediction for HORIZON steps ahead and decides whether to buy, sell, or hold.

        Parameters:
        - horizon (int): The prediction horizon (should be HORIZON).

        Returns:
        - int: 1 for buy, -1 for sell, 0 for hold.
        """
        if self.current_ndx < self.burn_in:
            return 0   # Not enough data for model to be reliable

        # Ensure we have enough history to make a prediction
        if len(self.history) >= self.num_lags:
            # Create the input vector using the most recent 'lag' values
            X_t = list(self.history)[-self.num_lags:]
            X_t_dict = {f'lag_{i}': value for i, value in enumerate(X_t)}

            # Predict the future value HORIZON steps ahead
            y_pred = self.model.predict_one(X_t_dict)

            # Get the last known value
            last_value = X_t[-1]

            # Calculate the expected profit
            expected_profit = y_pred - last_value

            # Decide based on whether expected profit exceeds EPSILON
            if expected_profit > self.threshold*EPSILON:
                return 1  # Buy
            elif expected_profit < -self.threshold*EPSILON:
                return -1  # Sell
            else:
                return 0  # Hold
        else:
            return 0  # Not enough history to make a prediction


def run_regression_attacker(num_lags:int, threshold:float=1.0, burn_in:int=500, category:str= 'train', max_streams=10000):
    from endersgame.accounting.pnlutil import zero_pnl_summary, add_pnl_summaries
    gen_gen = stream_generator_generator(category=category)
    attacker = RegressionAttacker(num_lags=num_lags, threshold=threshold, burn_in=burn_in)
    total_pnl = zero_pnl_summary()
    stream_count = 0
    for stream in gen_gen:
        for message in stream:
            attacker.tick_and_predict(x=message['x'])
        stream_pnl = attacker.pnl.summary()
        total_pnl = add_pnl_summaries(total_pnl,stream_pnl)
        stream_count += 1
        if stream_count>=max_streams:
            break

    total_pnl.update({'profit_per_decision':total_pnl['total_profit']/total_pnl['num_resolved_decisions']})
    pprint(total_pnl)

def test_regression_attacker():
    run_regression_attacker(num_lags=5, max_streams=2)


if __name__=='__main__':
    run_regression_attacker(num_lags=10, threshold=4, burn_in=2000, category='train')