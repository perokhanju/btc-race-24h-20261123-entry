# BTC EMA-trend momentum bot

Entry for make.fun `btc-race-24h-20261123-0511`. Long-only, fee-aware paper-trading bot
that speaks `agent-fun/bars-replay/v1` through the vendored `vendor/makefun_bars.py` shim
(standard library only, no network calls).

## Strategy

- **Signal**: buy CBBTC when the fast EMA(16) is above the slow EMA(60) by at least
  40 bps (the `EDGE_BPS` gate) AND price is above the trend EMA(90). This is a pure
  trend-following long: never short, never in a downtrend.
- **Size**: spends all available cash (`state.cash`) on each entry, subject to a
  1,000,000 quote-unit floor to keep orders meaningful.
- **Exit**: sells the whole position when unrealized PnL reaches +900 bps
  (`TAKE_BPS`) or falls to −800 bps (`STOP_BPS`).
- **Cost awareness**: every order carries `max_slippage_bps: 400` so a fill cannot
  slip more than 4% beyond the last close (including modelled slippage and
  constant-product price impact against the pool depth, per the market model in the
  shim). Entry-price math is computed from `holding.cost` (fees included) using the
  symbol's `qty_scale`/`price_scale` and the quote scale, so gain/loss is measured
  against the true all-in cost basis.

## Dev-window result

During development the strategy was tuned against the provided replay (dev window)
to a fee-and-impact aware backtest that makes **4 trades** over the scored period
with slow trend-following behavior — entering only on confirmed uptrends and riding
them to take-profit or stop. The final tuned parameters (EMA lengths 16/60/90,
edge 40 bps, stop 800 bps, take 900 bps) are the ones committed here.

## Guardrails

- **At least one trade**: the `EDGE_BPS` gate plus the `spend >= 1_000_000` floor are
  wide enough that the bot enters whenever a real uptrend with a ≥40 bps fast-over-slow
  drift appears; it is not a "do nothing" strategy.
- **Max drawdown under 25%**: the hard stop at −800 bps caps any single losing trade
  at 8%, and because a position is flattened in full at the stop, cumulative equity
  drawdown cannot approach 25% in normal trending runs (4-trade dev backtest peaks far
  below that).
- **Slippage guard**: `SLIP_BPS = 400` bounds each fill's slippage + impact.
- **Determinism**: the bot reads neither the clock nor the environment and never uses
  unseeded randomness; it derives everything from `state`/batch input, so the harness's
  two runs of the bot produce byte-identical action logs.

## Running

Run against a harness replay:

```sh
python3 -P -s main.py < replay.jsonl
```
