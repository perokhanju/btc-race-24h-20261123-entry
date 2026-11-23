import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))
import makefun_bars

SYMBOL = "CBBTC"
FAST_EMA_LEN = 16
SLOW_EMA_LEN = 60
TREND_EMA_LEN = 90
EDGE_BPS = 40
STOP_BPS = 800
TAKE_BPS = 900
SLIP_BPS = 400

closes = []


def ema(values, length):
    k = 2 / (length + 1)
    e = values[0]
    for v in values[1:]:
        e = v * k + e * (1 - k)
    return e


def on_batch(state, batch):
    for bar in batch["bars"]:
        if bar["symbol"] == SYMBOL:
            closes.append(int(bar["c"]))

    if state.warming_up or len(closes) < TREND_EMA_LEN + 5:
        return []

    price = state.close(SYMBOL)

    fast = ema(closes[-3 * FAST_EMA_LEN:], FAST_EMA_LEN)
    slow = ema(closes[-3 * SLOW_EMA_LEN:], SLOW_EMA_LEN)
    trend = ema(closes[-(TREND_EMA_LEN + 5):], TREND_EMA_LEN)

    holding = state.positions.get(SYMBOL)
    if holding is not None and holding.qty > 0:
        symbol = state.symbols[SYMBOL]
        scale = 10 ** (symbol["qty_scale"] + symbol["price_scale"] - state.hello["capital"]["quote_scale"])
        entry_price = holding.cost * scale // holding.qty
        gain = (price - entry_price) * 10000 // entry_price
        if gain >= TAKE_BPS or gain <= -STOP_BPS:
            return [
                {
                    "side": "sell",
                    "symbol": SYMBOL,
                    "qty": holding.qty,
                    "max_slippage_bps": SLIP_BPS,
                }
            ]
        return []

    if fast > slow and price > trend:
        drift = (fast - slow) * 10000 // slow
        if drift >= EDGE_BPS and state.cash >= 1000000:
            return [
                {
                    "side": "buy",
                    "symbol": SYMBOL,
                    "notional_quote_units": state.cash,
                    "max_slippage_bps": SLIP_BPS,
                }
            ]
        return []

    return []


makefun_bars.run(on_batch)
