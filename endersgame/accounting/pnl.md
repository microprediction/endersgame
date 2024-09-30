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
