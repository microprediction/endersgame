
# RegressionAttacker 

### `tick` Method

The `tick` method processes a new incoming data point and updates the attacker's state accordingly:

- **Increment the Time Index**: The method updates `self.current_ndx` to track the current observation index.
- **Maintain Input History**: It retrieves the recent history of `num_lags` values and appends the new input vector (`X_t`) to the `input_queue`, associating it with the current index.
- **Update the Model**: The method checks if it has received enough future data (after `HORIZON` steps) to use an earlier input vector as a training example. If so, it pairs the input vector from `HORIZON` steps ago with the current data point `x` (used as the target value `y`) and incrementally updates the online regression model.

### `predict` Method

The `predict` method makes a decision based on the model’s prediction for the value `HORIZON` steps ahead:

- **Burn-in Check**: If the number of processed data points is less than the `burn_in` threshold, the model refrains from making predictions.
- **Prepare Input Features**: It checks if there's enough history to form an input vector of `num_lags` values. If there is, it prepares a dictionary of lagged values (`X_t_dict`) to be used by the model.
- **Prediction**: The method predicts the next value `HORIZON` steps ahead using the online regression model.
- **Decision Logic**: It calculates the expected profit by comparing the predicted future value with the last known value. If the expected profit exceeds a threshold (a multiple of `EPSILON`), it returns:
  - `1` (buy) if the profit is positive,
  - `-1` (sell) if the profit is negative,
  - `0` (hold) if the profit is too small to act upon.