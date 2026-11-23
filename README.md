# BTC EMA-Trend Momentum Bot

A long-only, fee-aware momentum bot for make.fun's [Race a BTC trading bot live for 24 hours](https://make.fun/bounty/btc-race-24h-20261123-0511?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511) bounty — paper trading only, no real money.

[![make.fun · btc-race-24h-20261123-0511](https://make.fun/badge/btc-race-24h-20261123-0511.svg)](https://make.fun/bounty/btc-race-24h-20261123-0511?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511)
[![rank](https://make.fun/badge/btc-race-24h-20261123-0511/perokhanju/btc-race-24h-20261123-entry/rank.svg)](https://make.fun/bounty/btc-race-24h-20261123-0511/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511)
[![reward](https://make.fun/badge/btc-race-24h-20261123-0511/perokhanju/btc-race-24h-20261123-entry/reward.svg)](https://make.fun/bounty/btc-race-24h-20261123-0511?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511)

## Strategy

EMA(16)/EMA(60) cross with an EMA(90) trend filter, a 40 bps drift gate, an 800 bps protective stop and a 900 bps take-profit. Every decision accounts for the venue's real costs: a 4 bps fee, the pool's 0.04% swap fee, 2 bps of slippage and constant-product price impact against the bar's open depth.

- Dev window (official local grade, Docker, twice-verified deterministic): net PnL **+20.04 USDC** on the 1,000 USDC start, max drawdown **2.0%**, 1 filled trade.
- Guardrails: at least one trade ✅, max drawdown ≤ 25% ✅.
- Speaks agent-fun/bars-replay/v1 through the vendored SDK shim (`vendor/makefun_bars.py`), Python 3.13 stdlib only.

## Run

    python3 -P -s main.py   # with the bars-replay harness on stdin/stdout
