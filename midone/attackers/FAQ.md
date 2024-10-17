
# Frequently Asked Questions

When implementing an [attacker](https://github.com/microprediction/midone/tree/main/midone/attackers) keep the following in mind. 

### FAQ 1: Should I implement `tick_and_predict` ? 
Only if you really want to. It's already in the base class. 

You *could* overwrite it or even just create a fresh class with a `tick_and_predict` method, if that's your fancy. However, the reason we
advocate implementing `tick` and `predict` separately and leaving the base `tick_and_predict` alone is that
it will make it easier to swap out your use of `BaseAttacker` as parent class for something with more functionality such as [AttackerWithSimplePnl](https://github.com/microprediction/midone/blob/main/midone/attackers/attackerwithsimplepnl.py) where
the `tick_and_predict` logic is a fraction more involved than just `tick` then `predict`. 

### FAQ 2: What should `tick` do? Should it log history?

There is no requirement on what `tick` should do (though it must satisfy the method signature). It is merely your opportunity to assimilate information from the current data
point in the sequence *quickly*, somehow. Presumably this updates the models state - whatever you choose that state to be. 

For some people the state might include a fixed-length buffer of recent values of the series. We generally encourage attackers to be designed using incremental calculations rather than repeating the same calculation on the entire
history every data point, but that's ultimately your choice and we've made the second pattern easy with the `HistoryMixin` class. See [BaseAttackerWithHistoryMixin](https://github.com/microprediction/midone/blob/main/midone/attackers/baseattackerwithhistorymixin.py) for this
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
provided for you by the [CalibratedAttacker](https://github.com/microprediction/midone/blob/main/midone/attackers/calibratedattacker.py) that makes it easy to wrap an
attacker with some basic economic empirical logic, so that it only actually trades when the signal is strong enough to indicate that in the past such a trade would have been profitable.  

### FAQ 4: What does the `horizon` parameter mean? Will it change? 

You can generally expect the same prediction `horizon` to be fed to the attacker over and over again.  

### FAQ 5: Do data points arrive equally spaced in time?

Yes. 

For this reason we have simplified the API considerably by removing time. The `horizon` refers to a count of data points. 

### FAQ 6: How can the attacker deal with trading breaks, outages and switching from one series to another?

This is a very important question and the answer is that you should always implement some kind of burn-in logic for your attacker. For example you could decide not to make any non-zero predictions
for the first 500 data points received. 


## See also 

 - Colab [notebooks](https://github.com/microprediction/endersnotebooks) demonstrating `Attacker`
 - Recommended [attacker.md](https://github.com/microprediction/midone/blob/main/midone/attackers/attacker.md)
 - Attacker [FAQ.md](https://github.com/microprediction/midone/blob/main/midone/attackers/FAQ.md)
 - The tournament at [CrunchDAO.com](https://www.crunchdao.com) where you can use them to win rewards. 
