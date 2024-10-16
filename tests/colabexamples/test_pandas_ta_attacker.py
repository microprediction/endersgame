from midone import Attacker, HORIZON, EPSILON
from river import linear_model
from collections import deque
from midone import stream_generator_generator
from pprint import pprint
import pandas as pd
import pandas_ta as ta


def compute_indicators(data: pd.Series):
    """
    Computes several technical indicators based on the recent history.

    Parameters:
    - data (pd.Series): The recent historical data as a pandas Series.

    Returns:
    - indicators (dict): A dictionary of computed technical indicators.
    """
    indicators = {}

    # Compute Relative Strength Index (RSI)
    rsi = ta.rsi(data, length=14)
    if rsi is not None and not rsi.empty:
        indicators['rsi'] = rsi.iloc[-1]
    else:
        indicators['rsi'] = 0  # Default value if not enough data

    # Compute Simple Moving Average (SMA)
    sma_50 = ta.sma(data, length=50)
    if sma_50 is not None and not sma_50.empty:
        indicators['sma_50'] = sma_50.iloc[-1]
    else:
        indicators['sma_50'] = 0  # Default value if not enough data

    # Compute Exponential Moving Average (EMA)
    ema_20 = ta.ema(data, length=20)
    if ema_20 is not None and not ema_20.empty:
        indicators['ema_20'] = ema_20.iloc[-1]
    else:
        indicators['ema_20'] = 0  # Default value if not enough data

    return indicators


class TechnicalIndicatorAttacker(Attacker):
    """
    An attacker that computes technical indicators based on recent history and uses
    an online linear regression model to predict future values and make trading decisions.

    Remarks:
       - pip install pandas_ta
       - Performance is hindered because features are computed repeatedly every data point
       - But it supports many features https://github.com/twopirllc/pandas-ta?tab=readme-ov-file#indicators-by-category

    """

    def __init__(self, max_history_len=500, threshold: float = 1.0, burn_in=1000, **kwargs):
        """
        Initializes the attacker.

        Parameters:
        - max_history_len (int): Number of recent data points to use for computing technical indicators.
        - threshold (float): Multiplier for EPSILON to decide when to act.
        - burn_in (int): Number of initial observations to skip before making predictions.
        """
        super().__init__(max_history_len=max_history_len, **kwargs)
        self.num_lags = max_history_len                # Number of recent values to use for technical indicators
        self.model = linear_model.LinearRegression(    # Online linear regression model
            intercept_init=0.0,                        # Initialize intercept to 0
            intercept_lr=0.0                            # Freeze the intercept (no learning)
        )
        self.input_queue = deque()                     # Queue to store input vectors and time indices
        self.current_ndx = 0                           # Observation index
        self.threshold = threshold
        self.burn_in = burn_in

    def tick(self, x):
        """
        Processes the new data point.

        - Maintains a queue of input vectors.
        - When the future value arrives after HORIZON steps, updates the model.

        Parameters:
        - x (float): The new data point.
        """
        self.current_ndx += 1  # Increment the observation index

        # Get recent history and convert to pandas Series
        history = self.get_recent_history(n=self.num_lags)
        if len(history) >= self.num_lags:
            history_series = pd.Series(history)

            # Compute technical indicators from the history
            indicators = compute_indicators(history_series)

            # Store the indicators and current index in the input queue
            self.input_queue.append({'ndx': self.current_ndx, 'indicators': indicators})

        # Check if we can update the model with data from HORIZON steps ago
        while self.input_queue and self.input_queue[0]['ndx'] <= self.current_ndx - HORIZON:
            # Retrieve the indicator vector and its time index
            past_data = self.input_queue.popleft()
            X_past = past_data['indicators']

            # The target value y is the data point at 'time_past + HORIZON'
            y = x  # Current data point is the target for the input from HORIZON steps ago

            # Update the model incrementally
            self.model.learn_one(X_past, y)

    def predict(self, horizon=HORIZON):
        """
        Makes a prediction for HORIZON steps ahead and decides whether to buy, sell, or hold.

        Parameters:
        - horizon (int): The prediction horizon (should be HORIZON).

        Returns:
        - int: 1 for buy, -1 for sell, 0 for hold.
        """
        if self.current_ndx < self.burn_in:
            return 0  # Not enough data for model to be reliable

        # Get recent history and convert to pandas Series
        history = self.get_recent_history(n=self.num_lags)
        if len(history) >= self.num_lags:
            history_series = pd.Series(history)

            # Compute technical indicators for the prediction
            indicators = compute_indicators(history_series)

            # Predict the future value HORIZON steps ahead
            y_pred = self.model.predict_one(indicators)

            # Get the last known value
            last_value = history_series.iloc[-1]

            # Calculate the expected profit
            expected_profit = y_pred - last_value

            # Decide based on whether expected profit exceeds threshold * EPSILON
            if expected_profit > self.threshold * EPSILON:
                return 1  # Buy
            elif expected_profit < -self.threshold * EPSILON:
                return -1  # Sell
            else:
                return 0  # Hold
        else:
            return 0  # Not enough history to make a prediction


def run_technical_indicator_attacker(max_history_len: int = 500, threshold: float = 1.0, burn_in: int = 1000,
                                     category: str = 'train', max_streams: int = 10000):
    from midone.accounting.pnlutil import zero_pnl_summary, add_pnl_summaries

    gen_gen = stream_generator_generator(category=category)
    attacker = TechnicalIndicatorAttacker(max_history_len=max_history_len, threshold=threshold, burn_in=burn_in)
    total_pnl = zero_pnl_summary()
    stream_count = 0
    for stream in gen_gen:
        for message in stream:
            attacker.tick_and_predict(x=message['x'])
        stream_pnl = attacker.pnl.summary()
        total_pnl = add_pnl_summaries(total_pnl, stream_pnl)
        stream_count += 1
        if stream_count >= max_streams:
            break

    if total_pnl['num_resolved_decisions'] > 0:
        total_pnl.update({'profit_per_decision': total_pnl['total_profit'] / total_pnl['num_resolved_decisions']})
    else:
        total_pnl.update({'profit_per_decision': 0})
    pprint(total_pnl)


def test_technical_indicator_attacker():
    run_technical_indicator_attacker(max_history_len=5, max_streams=2)


if __name__ == '__main__':
    run_technical_indicator_attacker(max_history_len=10, threshold=4, burn_in=2000, category='train')
