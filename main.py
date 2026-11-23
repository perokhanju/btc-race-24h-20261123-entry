# make.fun btc-race-24h-20261123-0511: EMA-trend momentum bot (long only, paper trading).
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))

import makefun_bars

SYMBOL = "CBBTC"
FAST = 16         # fast EMA length (bars)
SLOW = 60         # slow EMA length (bars)
TREND = 90        # trend EMA length: only long above it
EDGE_BPS = 40     # minimum fast-over-slow drift before entering
STOP_BPS = 800    # exit if we fall this far under our entry
TAKE_BPS = 900    # take profit here
SLIP_BPS = 400    # max_slippage_bps guard

closes = []       # our own history of closes, one per received bar


def ema(values, length):
    if len(values) < length:
        return None
    k = 2.0 / (length + 1.0)
    e = values[0]
    for v in values[1:]:
        e = v * k + e * (1.0 - k)
    return e


def on_batch(state, batch):
    for bar in batch.get("bars", []):
        if bar["symbol"] == SYMBOL:
            closes.append(int(bar["c"]))
    if state.warming_up:
        return []
    if len(closes) < TREND + 5:
        return []
    price = state.close(SYMBOL)
    fast = ema(closes[-(FAST * 3):], FAST)
    slow = ema(closes[-(SLOW * 3):], SLOW)
    trend = ema(closes[-(TREND + 5):], TREND)
    if fast is None or slow is None or trend is None:
        return []

    holding = state.positions.get(SYMBOL)
    if holding is not None and holding.qty > 0:
        s = state.symbols[SYMBOL]
        qs = int(state.hello["capital"]["quote_scale"])
        scale = 10 ** (int(s["qty_scale"]) + int(s["price_scale"]) - qs)
        entry_price = holding.cost * scale // holding.qty
        gain = (price - entry_price) * 10000 // entry_price
        if gain >= TAKE_BPS or gain <= -STOP_BPS:
            return [{
                "side": "sell",
                "symbol": SYMBOL,
                "qty": holding.qty,
                "max_slippage_bps": SLIP_BPS,
            }]
        return []

    if fast > slow and price > trend:
        drift = (fast - slow) * 10000 // slow
        if drift >= EDGE_BPS:
            spend = state.cash
            if spend >= 1_000_000:
                return [{
                    "side": "buy",
                    "symbol": SYMBOL,
                    "notional_quote_units": spend,
                    "max_slippage_bps": SLIP_BPS,
                }]
    return []


makefun_bars.run(on_batch)
