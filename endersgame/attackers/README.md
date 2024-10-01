


# Attackers

See also [endersnotebooks](https://github.com/microprediction/endersnotebooks). 

## Overview

The `BaseAttacker` class provides a pattern designing and implementing an "attacker" model that consumes a univariate sequence of numerical data points (such as stock prices, bond prices, or any time series) $x_1, x_2, \dots x_t$ and attempts to predict its future movement. It looks for small deviations from a martingale property, which is to say that we expect the series $x_t$ to satisfy:

$$ E[x_{t+k}] \approx x_t $$

The attacker’s need only *occasionally* signal whether the future value will deviate upward or downward from the current point. This is useful in scenarios where the attacker attempts to exploit trends or patterns for profit. However, it is also beneficial in much greater generally, as a means of performing ongoing analysis of prediction model residuals in any application in any industry. 

## Usage

To create an attacker, you extend the `BaseAttacker` class (or similar) and implement the required methods (`tick` and `predict`). For example:

```python
class MyAttacker(BaseAttacker):
    def tick(self, x: float):
        # Put your logic for internal state updating here
    
    def predict(self, horizon: int = None) -> float:
        # Put your prediction logic here. Return a directional prediction: -1 for down, 1 for up, 0 for no opinion
        
```

Now to use, we simply instantiate and feed it one data point at a time:

```python
attacker = MyAttacker()

for x in enumerate(sequence_of_data):
    prediction = attacker.tick_and_predict(x, horizon=100)
    print(f" Price {x}, Prediction {prediction}")
```

The `BaseAttacker` framework is intentionally minimalist to allow flexibility in how you design your predictive strategies. 

## What happens when an attacker is launched

Notice in the code above that when your attacker is run only the `tick_and_predict` method will be called, once for each data point. However `tick_and_predict` is implemented in the parent classes and we'd *advise* that your attacker *typically* implement the following
separately instead (e.g. so you don't
need to think about profit and loss tracking, per [PnL](https://github.com/microprediction/endersgame/blob/main/endersgame/accounting/pnl.py) for instance. )
- **Tick**: It consumes and processes the current data point in the sequence, assimilating it into the model’s state.
- **Predict**: Based on the attacker’s internal state and logic, it may predict whether the future value is likely to be higher (returns a positive number), lower (returns a negative number), or it may abstain (returns zero).
  
You are strongly advised to read the [FAQ](https://github.com/microprediction/endersgame/blob/main/endersgame/attackers/FAQ.md) which discusses these methods.  

## How Attackers Are Judged

As might be inferred from the above, attackers are judged by their ability to profit from correctly predicting the directional change in a sequence over a future time horizon $k$, with a reward equal to the change in value. For example, if the attacker signals "up" at time $t$ and the value at $t+k$ is indeed higher than the value at $t$, then the attacker’s decision is considered profitable. The profit can be measured as $x_{t+k} - x_t -\epsilon$. Conversely, a loss might be incurred if the direction chosen is wrong, or the change in the right direction less than $\epsilon$. 

There's no need to implement this yourself. Use the [SimplePnl](https://github.com/microprediction/endersgame/blob/main/endersgame/accounting/simplepnl.py) mixin as demonstrated in [attackerwithsimplepnl.py](https://github.com/microprediction/endersgame/blob/main/endersgame/attackers/attackerwithsimplepnl.py). 

## Core Methods to Implement
When creating your own attacker, it is recommended that
you derive from `Attacker` or `AttackerWithSimplePnL` or something in 
[attackers](https://github.com/microprediction/endersgame/tree/main/endersgame/attackers), then implement the
following methods:

1. **`tick(self, x: float)`**:
    - Assimilate the current data point into the model’s state.
    - If you wish to maintain a fixed length buffer of lagged values, we suggest taking a look at the pattern provided in [BaseAttackerWithHistoryMixin](https://github.com/microprediction/endersgame/blob/main/endersgame/attackers/baseattackerwithhistorymixin.py). 
   
2. **`predict(self, k: int = None) -> float`**:
    - Based on the internal state and logic, return a prediction for the future movement of the sequence.
    - Return a positive value if you expect the future value to be higher, a negative value if lower, and zero if no prediction.



### Optional Component to Implement

4. **Tick and Predict**: The combined method `tick_and_predict(x, k)` will be called to test your attacker, but you usually don't need to separately implement it. 

### Conventions


- **Consistent prediction Horizon (`horizon`)**: You can generally expect the same prediction horizon to be fed to the attacker over and over again. 

- **History**  We generally encourage attackers to be designed using incremental calculations rather than batch but, as noted above, you can
easily add a buffer of past values with the `HistoryMixin` class (see [BaseAttackerWithHistoryMixin](https://github.com/microprediction/endersgame/blob/main/endersgame/attackers/baseattackerwithhistorymixin.py)) not impose strict rules on how to maintain or store historical data.)




