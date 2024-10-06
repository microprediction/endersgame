# Attacker Class

The `MyMomentumAttacker` illustrates `Attacker` class use. 

Here we create an attacker instance that tracks its own profit and loss, and makes
predictions using a function of lagged values. 

## Usage

### 1. **Import the Class**

First, import the `Attacker` class from your module:

```python
from endersgame import Attacker
import numpy as np 

  class MyMomentumAttacker(Attacker):

        def __init__(self, **kwargs):
            super().__init__(**kwargs)   # Boilerplate
            
        def predict_using_history(self, xs:[float], horizon:int):
            """  An example of taking lagged values and making an up or down decision
            :param xs:
            :return:
            """
            short_term_mean = np.mean(xs[-10:])
            long_term_mean = np.mean(xs[-100:])
            devo = np.std(np.diff(xs))
            momentum = 10*(long_term_mean - short_term_mean)/(long_term_mean*devo)
            signal = int(momentum)    # Usually zero, +1 for buy, -1 for sell
            return signal
```
All we've done it tell it how to take the chronological values `xs` most recently observed and
return an up or down opinion. Any `decision`>0 is a `buy`, any `decision<0` is a sell. The attacker is 
ready for use as follows: 

```python
    attacker = MyMomentumAttacker(max_history_len=100) # <-- By default no predictions will occur until the buffer is full
    xs = np.cumsum(np.random.randn(110)+0.01)
    for k,x in enumerate(xs):
        decision = attacker.tick_and_predict(x=x)
        if decision>0:
            print(f'Buy now at time {k} !', flush=True)
        if decision<0:
            print(f'Sell now at time {k}!')

```


## See also 

 - Colab [notebooks](https://github.com/microprediction/endersnotebooks) demonstrating `Attacker`
 - Recommended [attacker.md](https://github.com/microprediction/endersgame/blob/main/endersgame/attackers/attacker.md)
 - Attacker [FAQ.md](https://github.com/microprediction/endersgame/blob/main/endersgame/attackers/FAQ.md)
 - The tournament at [CrunchDAO.com](https://www.crunchdao.com) where you can use them to win rewards. 

