


# Attackers

## Overview

The `BaseAttacker` class provides a pattern designing and implementing an "attacker" model that consumes a univariate sequence of numerical data points (such as stock prices, bond prices, or any time series) and attempts to predict its future movement. The core idea behind this framework is to detect deviations from a martingale-like property, where the expectation of the future value is equal to the current value. That is:

    $$ E[x_{t+k}] \approx x_t $$

The attacker’s goal is to analyze incoming data points and occasionally signal whether the future value will deviate upward or downward from the current point. This is useful in scenarios where the attacker attempts to exploit trends or patterns for profit or performance measures. However, it is also useful much greater generally, as a means of performing ongoing analysis of prediction model residuals in any application in any industry. 

## Key Responsibilities of an Attacker

An attacker typically does the following:
- **Tick**: It consumes and processes the current data point in the sequence, assimilating it into the model’s state.
- **Predict**: Based on the attacker’s internal state and logic, it may predict whether the future value is likely to be higher (returns a positive number), lower (returns a negative number), or it may abstain (returns zero).
  
### When to Signal
- If the attacker believes the series will on average increase in value: return a positive number (indicating "up").


          $$ E[x_{t+k}] >  x_t + \epsilon $$

  
- If the attacker believes the series will on average decrease in value: return a negative number (indicating "down").


       $$ E[x_{t+k}] <  x_t - \epsilon $$


- In all other cases, return zero to indicate no opinion. The constant $\epsilon$ is game dependent. 

## How Attackers Are Judged

Attackers are judged by their ability to profit from correctly predicting the directional change in a sequence over a future time horizon $k$, with a reward equal to the change in value. For example, if the attacker signals "up" at time $t$ and the value at $t+k$ is indeed higher than the value at $t$, then the attacker’s decision is considered profitable. The profit can be measured as $x_{t+k} - x_t$. Conversely, a loss might be incurred if the direction chosen is wrong. 

There's no need to implement this yourself. Use the [SimplePnl](https://github.com/microprediction/endersgame/blob/main/endersgame/accounting/simplepnl.py) mixin as demonstrated in [attackerwithsimplepnl.py](https://github.com/microprediction/endersgame/blob/main/endersgame/attackers/attackerwithsimplepnl.py). 

### Core Components to Implement
When creating your own attacker, you should implement the following methods:

1. **`tick(self, x: float)`**:
    - Assimilate the current data point into the model’s state.
    - This function is responsible for updating the internal state with each new incoming observation.

2. **`predict(self, k: int = None) -> float`**:
    - Based on the internal state and logic, return a prediction for the future movement of the sequence.
    - Return a positive value if you expect the future value to be higher, a negative value if lower, and zero if no prediction.

3. **`fit(self)`** (optional):
    - This method is periodically called after large batches of observations (e.g., every 10,000 observations).
    - Use it to perform more intensive fitting or retraining processes that require additional computation.

### 

Here is an example of how the attacker might function in practice:

4. **Tick and Predict**: The combined method `tick_and_predict(x, k)` will be called to test your attacker, but you usually don't need to separately implement it. 

### Prediction horizon

- **Prediction Horizon (`k`)**: The horizon $k$ is a consistent future time step over which the attacker is expected to predict. In most cases, you can assume $k$ will remain constant throughout the sequence.

### History
  
While the framework does not impose strict rules on how to maintain or store historical data. You may choose to do so and an example is provided in [bufferingattacker](https://github.com/microprediction/endersgame/blob/main/endersgame/examples/bufferingattacker.py). 


## Fitting the Attacker
If your attacker requires periodic training or retraining, implement the `fit()` method, which will be called every epoch (a large number of observations, such as 10,000). This allows you to update your model without needing to compute intensive operations for every data point.

## Conclusion
The `BaseAttacker` framework is intentionally minimalist to allow flexibility in how you design your predictive strategies. By implementing only the `tick()` and `predict()` methods, you can create a wide range of attack strategies suited to different types of time series data. The modular design also allows you to combine this with other predictive models and frameworks to build powerful forecasting tools.


## Example 

To create an attacker, you simply extend the `BaseAttacker` class and implement the required methods (`tick` and `predict`). For example:

```python
class MyAttacker(BaseAttacker):
    def tick(self, x: float):
        # Update internal state with the new data point
        pass
    
    def predict(self, k: int = None) -> float:
        # Return a directional prediction: -1 for down, 1 for up, 0 for no opinion
        pass
```

Now to use, we simply instantiate and feed it one data point at a time:

```python
attacker = MyAttacker()

for t, x in enumerate(sequence_of_data):
    prediction = attacker.tick_and_predict(x, k=100)
    print(f"Time {t}: Price {x}, Prediction {prediction}")
```


