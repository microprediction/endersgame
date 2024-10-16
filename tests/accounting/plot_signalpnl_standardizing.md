

# Standardizing Stochastic Signals Demo

The script [plot_signalpnl_standardizing.py](https://github.com/microprediction/midone/blob/main/tests/accounting/plot_signalpnl_standardizing.py)  illustrates the process of standardizing a stochastic signal generated using an Ornstein-Uhlenbeck process. The signals are standardized using exponentially weighted mean and variance to compute Z-scores, allowing for threshold-based decision-making.

## Description

- **Ornstein-Uhlenbeck Process**: A mean-reverting stochastic process is used to generate signals, simulating price changes or other time series data.
- **Standardized Signals**: These signals are standardized in real-time using a fading factor to track the exponentially weighted mean and variance.
- **Thresholds**: Points where the standardized signals exceed a positive or negative threshold are highlighted for potential actions.

## Plot Example

![Standardizing Signal PnL](https://github.com/microprediction/midone/blob/main/assets/images/standardizing_signal_pnl.png)

## How to Run

1. Install the required dependencies:
   ```bash
   pip install numpy matplotlib
