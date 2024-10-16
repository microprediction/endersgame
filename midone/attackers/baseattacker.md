


# BaseAttacker

A minimalist class outlining the task at hand.

## Overview

The `BaseAttacker` class provides a pattern for designing and implementing an "attacker" model that consumes a univariate sequence of numerical data points (such as stock prices, bond prices, or any time series) $x_1, x_2, \dots x_t$ and attempts to predict its future movement. It looks for small deviations from a martingale property, which is to say that we expect the series $x_t$ to satisfy:

$$ E[x_{t+k}] \approx x_t $$

The attacker need only *occasionally* signal whether the future value will deviate upward or downward from the current point. This is useful in scenarios where the attacker attempts to exploit trends or patterns for profit. However, it is also beneficial in much greater generally, as a means of performing ongoing analysis of prediction model residuals in any application in any industry. 

## Usage

To create an minimalist attacker, you might extend the `BaseAttacker` class and implement (`tick` and `predict`). For example:

```python
class MyAttacker(BaseAttacker):
    def tick(self, x: float):
        # Put your logic for internal state updating here
    
    def predict(self, horizon: int = None) -> float:
        # Put your prediction logic here. Return a directional prediction: -1 for down, 1 for up, 0 for no opinion
        
```
In Enders' Game your attacker's `tick_and_predict` method will be fed one data point at a time:

```python
attacker = MyAttacker()

for x in enumerate(xs):
    prediction = attacker.tick_and_predict(x, horizon=100)
    print(f"Price {x}, Prediction {prediction}")
```

See [FAQ](https://github.com/microprediction/midone/blob/main/midone/attackers/FAQ.md) for why we *don't* recommend implementing `tick_and_predict` explicitly. 

## Deployment

You will typically develop an attacker by modifying an example notebook selected from [Enders Notebooks](https://github.com/microprediction/endersnotebooks). In that notebook you can test your attacker on
history, train it and do whatever you like. When you are happy with the result you'll save the notebook and upload it to [www.crunchdao.com](https://www.crunchdoa.com). Then it will be run against real data, possibly in real-time. 

## Judging 

As might be inferred from the discussion of the `predict` method in the FAQ below, attackers are judged by their ability to profit from correctly predicting the directional
change in a sequence over the next `horizon` steps, with a reward equal to the change in value. For example, if the attacker signals "up" at or before observation index $t$ and the value at $t+k$ is indeed higher than the value at $t$, then the attacker’s decision is considered profitable. The profit can be measured as $x_{t+k} - x_t -\epsilon$. Conversely, a loss might be incurred if the direction chosen is wrong, or the change in the right direction less than $\epsilon$. 

Derive from [AttackerWithSimplePnl](https://github.com/microprediction/midone/blob/main/midone/attackers/attackerwithsimplepnl.py) to get a reasonable idea in advance of what that performance might be. 

## Design and responsibilities  

It is strongly recommended that you read the [FAQ](https://github.com/microprediction/midone/blob/main/midone/attackers/FAQ.md). 
