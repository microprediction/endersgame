


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

See FAQ below for why we *don't* recommend implementing `tick_and_predict` explicitly. 

## Deployment

You will typically develop an attacker by modifying an example notebook selected from [Enders Notebooks](https://github.com/microprediction/endersnotebooks). In that notebook you can test your attacker on
history, train it and do whatever you like. When you are happy with the result you'll save the notebook and upload it to [www.crunchdao.com](https://www.crunchdoa.com). Then it will be run against real data, possibly in real-time. 

## Judging 

As might be inferred from the discussion of the `predict` method in the FAQ below, attackers are judged by their ability to profit from correctly predicting the directional
change in a sequence over the next `horizon` steps, with a reward equal to the change in value. For example, if the attacker signals "up" at or before observation index $t$ and the value at $t+k$ is indeed higher than the value at $t$, then the attacker’s decision is considered profitable. The profit can be measured as $x_{t+k} - x_t -\epsilon$. Conversely, a loss might be incurred if the direction chosen is wrong, or the change in the right direction less than $\epsilon$. 

Derive from [AttackerWithSimplePnl](https://github.com/microprediction/endersgame/blob/main/endersgame/attackers/attackerwithsimplepnl.py) to get a reasonable idea in advance of what that performance might be. 


# Frequently Asked Questions

### FAQ 1: Should I implement `tick_and_predict` ? 
Only if you really want to. It's already in the base class. 

You *could* overwrite it or even just create a fresh class with a `tick_and_predict` method, if that's your fancy. However, the reason we
advocate implementing `tick` and `predict` separately and leaving the base `tick_and_predict` alone is that
it will make it easier to swap out your use of `BaseAttacker` as parent class for something with more functionality such as [AttackerWithSimplePnl](https://github.com/microprediction/endersgame/blob/main/endersgame/attackers/attackerwithsimplepnl.py) where
the `tick_and_predict` logic is a fraction more involved than just `tick` then `predict`. 

### FAQ 2: What should `tick` do? Should it log history?

There is no requirement on what `tick` should do (though it must satisfy the method signature). It is merely your opportunity to assimilate information from the current data
point in the sequence *quickly*, somehow. Presumably this updates the models state - whatever you choose that state to be. 

For some people the state might include a fixed-length buffer of recent values of the series. We generally encourage attackers to be designed using incremental calculations rather than repeating the same calculation on the entire
history every data point, but that's ultimately your choice and we've made the second pattern easy with the `HistoryMixin` class. See [BaseAttackerWithHistoryMixin](https://github.com/microprediction/endersgame/blob/main/endersgame/attackers/baseattackerwithhistorymixin.py) for this
pattern. If you go down this path, you can very easily create an attacker merely by implementing the method that takes past values and returns a decision.

### FAQ 2: How is the output of `predict` interpreted? 

Any positive value is a `buy` or `up` decision, and conversely. A zero means no no trade, and this should be the most common response. Informally, a positive return value will initiate a buy-and-hold for `horizon` data points. After the
next `horizon` data points to arrive, the profit or loss will be calculated. To be more formal, you should return a positive value if:

$$ E[x_{t+k}] >  x_t + \epsilon $$

where $k$ is the `horizon` and $t$ is the index of the next data point to arrive. On the other hand if the attacker believes the series will *on average* decrease in value more than $\epsilon$, then return a negative number (indicating "down").

$$ E[x_{t+k}] <  x_t - \epsilon $$

In all other cases, the attacker should zero to indicate that whatever opinion it has is deemed inadequate to overcome the expected profit threshold $\epsilon$. The constant $\epsilon$ is game dependent and analogous to a proportional trading cost.  

### FAQ 3: Does the magnitude of the prediction matter?

No. It makes not difference in the game. Only the sign is used. 

But ... you might want to use combinations of attackers in whatever patterns you devise, and in these arrangements it might well be beneficial to return a continuous signal rather than just 1, -1 or 0. An example is
provided for you by the [CalibratedAttacker](https://github.com/microprediction/endersgame/blob/main/endersgame/attackers/calibratedattacker.py) that makes it easy to wrap an
attacker with some basic economic empirical logic, so that it only actually trades when the signal is strong enough to indicate that in the past such a trade would have been profitable.  

### FAQ 4: What does the `horizon` parameter mean? Will it change? 

You can generally expect the same prediction `horizon` to be fed to the attacker over and over again.  

### FAQ 5: Do data points arrive equally spaced in time?

Yes. 

For this reason we have simplified the API considerably by removing time. The `horizon` refers to a count of data points. 

### FAQ 6: How can the attacker deal with trading breaks, outages and switching from one series to another?

This is a very important question and the answer is that you should always implement some kind of burn-in logic for your attacker. For example you could decide not to make any non-zero predictions
for the first 500 data points received. 






