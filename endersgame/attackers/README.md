


# README for `BaseAttacker` Framework

## Overview

The `BaseAttacker` class provides a foundational framework for designing and implementing an "attacker" model that consumes a sequence of numerical data points (such as stock prices, bond prices, or any time series) and attempts to predict its future movement. The core idea behind this framework is to detect deviations from a martingale-like property, where the expectation of the future value is equal to the current value. That is:

 $$ E[y_{t+k}] = y_t $$

In other words, the attacker’s goal is to analyze incoming data points and occasionally signal whether the future value will deviate upward or downward from the current point. This is useful in scenarios where the attacker attempts to exploit trends or patterns for profit or performance measures. However it is also useful much more generally, as a means of performing ongoing analysis of prediction model residuals in any industry. 

## Key Responsibilities of an Attacker

An attacker typically does the following:
- **Tick**: It consumes and processes the current data point in the sequence, assimilating it into the model’s state.
- **Predict**: Based on the attacker’s internal state and logic, it may predict whether the future value is likely to be higher (returns a positive number), lower (returns a negative number), or it may abstain (returns zero).
  
### When to Signal
- If the attacker believes the series will increase in value: return a positive number (indicating "up").
- If the attacker believes the series will decrease in value: return a negative number (indicating "down").
- In all other cases, return zero to indicate no opinion.

## How Attackers Are Judged

Attackers are judged by their ability to correctly predict the directional change in a sequence over a future time horizon \( k \). For example, if the attacker signals "up" at time \( t \) and the value at $t+k$ is indeed higher than the value at \( t \), then the attacker’s decision is considered profitable. The profit can be measured as \( y_{t+k} - y_t \). Similarly, if the attacker predicts "down" and the value decreases, the decision is successful.

### Core Components to Implement
When creating your own attacker, you should implement the following methods:

1. **`tick(self, y: float)`**:
    - Assimilate the current data point into the model’s state.
    - This function is responsible for updating the internal state with each new incoming observation.

2. **`predict(self, k: int = None) -> float`**:
    - Based on the internal state and logic, return a prediction for the future movement of the sequence.
    - Return a positive value if you expect the future value to be higher, a negative value if lower, and zero if no prediction.

3. **`fit(self)`** (optional):
    - This method is periodically called after large batches of observations (e.g., every 10,000 observations).
    - Use it to perform more intensive fitting or retraining processes that require additional computation.

### Example Workflow

Here is an example of how the attacker might function in practice:

1. **Tick**: Assimilate the current data point \( y_t \) by calling `tick(y)`.
2. **Predict**: After assimilating the data point, call `predict(k)` to issue a directional opinion for the future value \( y_{t+k} \).
3. **Tick and Predict**: The combined method `tick_and_predict(y, k)` allows you to both assimilate a new observation and issue a prediction in one step.

### Horizon and Assumptions

- **Prediction Horizon (`k`)**: The horizon \( k \) is a consistent future time step over which the attacker is expected to predict. In most cases, you can assume \( k \) will remain constant throughout the sequence.
- **History**: While the framework does not impose strict rules on how to maintain or store historical data, it is often useful to track prior observations to inform your model’s predictions.


## Fitting the Attacker
If your attacker requires periodic training or retraining, implement the `fit()` method, which will be called every epoch (a large number of observations, such as 10,000). This allows you to update your model without needing to compute intensive operations for every data point.

## Conclusion
The `BaseAttacker` framework is intentionally minimalist to allow flexibility in how you design your predictive strategies. By implementing only the `tick()` and `predict()` methods, you can create a wide range of attack strategies suited to different types of time series data. The modular design also allows you to combine this with other predictive models and frameworks to build powerful forecasting tools.


## Example 

To create an attacker, you simply extend the `BaseAttacker` class and implement the required methods (`tick` and `predict`). For example:

```python
class MyAttacker(BaseAttacker):
    def tick(self, y: float):
        # Update internal state with the new data point
        pass
    
    def predict(self, k: int = None) -> float:
        # Return a directional prediction: -1 for down, 1 for up, 0 for no opinion
        pass
```

Now to use, we simply instantiate and feed it one data point at a time:

```python
attacker = MyAttacker()

for t, y in enumerate(sequence_of_data):
    prediction = attacker.tick_and_predict(y, k=100)
    print(f"Time {t}: Price {y}, Prediction {prediction}")
```



