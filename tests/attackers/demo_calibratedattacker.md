# Calibrated Attacker Demo

This demo illustrates how to create and use a `CalibratedAttacker`, which adjusts the decisions of a "raw" attacker based on empirical performance. In this example, the uncalibrated attacker generates real-valued signals based on a moving average of price changes, while the calibrated attacker standardizes these signals and makes empirical decisions.

## Description

- **Uncalibrated Attacker**: Generates real-valued signals based on the average of the most recent price changes.
- **Calibrated Attacker**: Takes the uncalibrated attacker's signals, tracks their performance, and outputs discrete decisions: `-1` (sell), `0` (hold), or `1` (buy).

The script simulates a time series of price changes and plots both the raw signals from the uncalibrated attacker and the decisions made by the calibrated attacker.

## Plot Example

![Calibrated Attacker Plot](https://github.com/microprediction/endersgame/blob/main/assets/images/calibratedattacker.png)

## How to Run

1. Install the required dependencies:
   ```bash
   pip install numpy matplotlib
