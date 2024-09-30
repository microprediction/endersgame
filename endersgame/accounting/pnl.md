# PnL Tracker

The class [PnL](https://github.com/microprediction/endersgame/blob/main/endersgame/accounting/pnl.py) tracks and logs profit and loss (PnL) for decisions made by an attacker based on future price movements.

## Features
- **Decision Tracking**: Logs non-zero decisions and resolves them when future data becomes available.
- **Backoff Mechanism**: Ignores decisions made too soon after the last one.
- **PnL Calculation**: Calculates PnL based on the difference between the predicted and actual values, adjusted by a threshold (`epsilon`).
- **Statistics**: Provides a summary of total profit, win/loss ratio, and standardized profit per decision.

## Key Methods
- `tick(x, k, decision)`: Adds and resolves decisions based on incoming data.
- `to_records()`: Converts resolved PnL data into records.
- `summary()`: Returns PnL statistics, including win/loss ratio and profit per decision.

## Usage Example
```python
pnl_tracker = PnL(epsilon=0.005)
for x in data_stream:
    decision = model.predict(x)
    pnl_tracker.tick(x, k=5, decision=decision)

summary = pnl_tracker.summary()
print(summary)
```


## profit and loss provided by this class
We will buy and hold for `k` data points. The profit or loss is then adjusted by a trading cost `epsilon`. 

At present this class assumes instantaneous trading, so in usual usage, a decision made after x(5) is received will incur profit 

```python
   profit = x(15) - x(5) - epsilon
```
in the case of a buy. 


## Slight difference in profit and loss measured in live scoring
We do not know how long an attacker will take to respond. If it is virtually instantaneous, the result may be identical to the above. However in many cases the attacker's decision will be received later. To illustrate, assume decision > 0. 
 
For example if the prediction is driven by x(5) and received between x(5) and x(6) and k=10 then actually:

```python
    profit = x(16) - x(6) - epsilon 
```

