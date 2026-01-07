"""
This script performs a technical analysis workflow on historical OHLCV market data
loaded from a CSV file and visualizes price action, indicators, and rule-based trade
signals.

Specifically, the script:
- Loads historical OHLCV data from a CSV file into a Pandas DataFrame.
- Normalizes column names to lowercase for consistency.
- Computes a set of common technical indicators using TA-Lib, including:
  - Simple Moving Average (SMA 20)
  - Exponential Moving Average (EMA 20)
  - Relative Strength Index (RSI 14)
  - Moving Average Convergence Divergence (MACD 12,26,9)
  - Bollinger Bands (20-period, 2 standard deviations)
  - Volume Weighted Average Price (VWAP)
- Generates basic buy and sell signals based on:
  - RSI overbought/oversold conditions
  - Price relative to VWAP
- Produces a multi-panel Matplotlib chart showing:
  - Price with moving averages, Bollinger Bands, VWAP, and buy/sell markers
  - RSI with overbought/oversold thresholds
  - MACD with signal line and histogram

The script is intended for exploratory analysis, strategy visualization, and
educational purposes. It does not execute trades and should not be considered
a complete trading system or backtesting framework.
"""


import pandas as pd
import talib
import matplotlib.pyplot as plt

# === Load Data ===
df = pd.read_csv('META_OHLC.csv')

# Ensure lowercase columns
df.columns = [c.lower() for c in df.columns]

# === Compute Indicators ===
df['SMA_20'] = talib.SMA(df['close'], timeperiod=20)
df['EMA_20'] = talib.EMA(df['close'], timeperiod=20)
df['RSI_14'] = talib.RSI(df['close'], timeperiod=14)
df['MACD'], df['MACD_signal'], df['MACD_hist'] = talib.MACD(
    df['close'], fastperiod=12, slowperiod=26, signalperiod=9
)
upper, middle, lower = talib.BBANDS(df['close'], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
df['BB_upper'], df['BB_middle'], df['BB_lower'] = upper, middle, lower
df['vwap'] = (df['close'] * df['volume']).cumsum() / df['volume'].cumsum()

# === Generate Buy/Sell Signals ===
df['Buy_Signal'] = (df['RSI_14'] < 30) & (df['close'] < df['vwap'])
df['Sell_Signal'] = (df['RSI_14'] > 70) & (df['close'] > df['vwap'])

# === Plot ===
plt.figure(figsize=(14, 10))

# --- Price + Indicators ---
plt.subplot(3, 1, 1)
plt.plot(df['close'], label='Close', color='black', linewidth=1)
plt.plot(df['SMA_20'], label='SMA 20', color='blue', linewidth=1)
plt.plot(df['EMA_20'], label='EMA 20', color='orange', linewidth=1)
plt.plot(df['BB_upper'], label='Bollinger Upper', color='green', linestyle='--', linewidth=0.8)
plt.plot(df['BB_lower'], label='Bollinger Lower', color='green', linestyle='--', linewidth=0.8)
plt.plot(df['vwap'], label='VWAP', color='purple', linewidth=1.2)

# --- Buy/Sell Markers ---
plt.scatter(df.index[df['Buy_Signal']], df['close'][df['Buy_Signal']],
            label='BUY', marker='^', color='lime', s=100, edgecolors='black', zorder=5)
plt.scatter(df.index[df['Sell_Signal']], df['close'][df['Sell_Signal']],
            label='SELL', marker='v', color='red', s=100, edgecolors='black', zorder=5)

plt.title('Price + SMA/EMA/Bollinger/VWAP + Buy/Sell Signals')
plt.legend(loc='upper left')
plt.grid(True, linestyle='--', alpha=0.3)

# --- RSI ---
plt.subplot(3, 1, 2)
plt.plot(df['RSI_14'], label='RSI (14)', color='red')
plt.axhline(70, color='gray', linestyle='--', linewidth=0.8)
plt.axhline(30, color='gray', linestyle='--', linewidth=0.8)
plt.fill_between(df.index, 70, 100, color='red', alpha=0.1)
plt.fill_between(df.index, 0, 30, color='lime', alpha=0.1)
plt.title('Relative Strength Index (RSI)')
plt.legend(loc='upper left')
plt.grid(True, linestyle='--', alpha=0.3)

# --- MACD ---
plt.subplot(3, 1, 3)
plt.plot(df['MACD'], label='MACD', color='blue')
plt.plot(df['MACD_signal'], label='Signal', color='orange')
plt.bar(df.index, df['MACD_hist'], label='Histogram', color='gray', alpha=0.4)
plt.title('MACD (12,26,9)')
plt.legend(loc='upper left')
plt.grid(True, linestyle='--', alpha=0.3)

plt.tight_layout()
plt.show()
