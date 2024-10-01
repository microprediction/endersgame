


# Attackers

See also [endersnotebooks](https://github.com/microprediction/endersnotebooks). 

The `BaseAttacker` class and cousins like `AttackerWithSimplePnL` can be found in 
[attackers](https://github.com/microprediction/endersgame/tree/main/endersgame/attackers). These 
provide patterns for designing and implementing an "attacker" model that consumes a univariate sequence of numerical data points (such as stock prices, bond prices, or any time series) $x_1, x_2, \dots x_t$ and attempts to predict its future movement. It looks for small deviations from a martingale property, which is to say that we expect the series $x_t$ to satisfy:

$$ E[x_{t+k}] \approx x_t $$

The attacker’s need only *occasionally* signal whether the future value will deviate upward or downward from the current point. This is useful in scenarios where the attacker attempts to exploit trends or patterns for profit. However, it is also beneficial in much greater generally, as a means of performing ongoing analysis of prediction model residuals in any application in any industry. 

See [baseattacker.md](https://github.com/microprediction/endersgame/blob/main/endersgame/attackers/baseattacker.md) for further explanation. 