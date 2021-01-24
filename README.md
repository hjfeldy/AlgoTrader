# AlgoTrader
Programmatically identify entry and exit points for a given security

The purpose of this program is to identify the best metrics by which to implement a trading bot by examining historical data.
The trading bot in question identifies buy and sell signals using the following method:

1. Examine price movement
2. Smooth price movement
3. Normalize price movement
4. Identify extreme values as buy/sell signals 
5. Enter positions at buy signals
6. Exit positions whenever a certain profit threshold has been met OR a sell-signal is identified

In order to smooth the price movement, we must choose a window of time to compute a rolling average.
In order to identify extreme values, we must choose a threshold that defines "extreme."
In order to take profits, we must choose a profit threshold.

Optimize.cpp takes two csv files as inputs (bid and ask) and outputs a complete dataset of every possible input-combination and its corresponding simulated profit and transaction count

