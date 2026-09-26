from __future__ import annotations

from dataclasses import dataclass

from .domain import Bar
from .models import sma


@dataclass
class BacktestResult:
    ticker: str
    return_pct: float
    max_drawdown_pct: float
    trades: int


def run_trend_backtest(ticker: str, bars: list[Bar], transaction_cost_bps_each_side: float = 35) -> BacktestResult:
    """Long when close > MA20 > MA50; next-close execution; includes round-trip costs."""
    if len(bars) < 55:
        return BacktestResult(ticker, 0, 0, 0)
    equity, peak, max_dd, in_market, entry, trades = 1.0, 1.0, 0.0, False, 0.0, 0
    closes = [b.close for b in bars]
    one_side = transaction_cost_bps_each_side / 10_000
    for i in range(50, len(bars)-1):
        ma20, ma50 = sma(closes[:i+1], 20), sma(closes[:i+1], 50)
        signal = closes[i] > ma20 > ma50
        execution = closes[i+1]
        if signal and not in_market:
            entry, in_market, trades = execution * (1 + one_side), True, trades + 1
        elif not signal and in_market:
            exit_price = execution * (1 - one_side)
            equity *= exit_price / entry
            in_market = False
            peak = max(peak, equity)
            max_dd = min(max_dd, equity / peak - 1)
    if in_market:
        equity *= (closes[-1] * (1 - one_side)) / entry
    peak = max(peak, equity)
    max_dd = min(max_dd, equity / peak - 1)
    return BacktestResult(ticker, (equity-1)*100, max_dd*100, trades)
