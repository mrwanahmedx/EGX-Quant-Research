from __future__ import annotations

import math
from datetime import date

from .domain import Bar, Catalyst, Holding, Security


def clamp(value: float, low: float = 0, high: float = 100) -> float:
    return max(low, min(high, value))


def sma(values: list[float], period: int) -> float | None:
    return sum(values[-period:]) / period if len(values) >= period else None


def ema_series(values: list[float], period: int) -> list[float]:
    if not values:
        return []
    k = 2 / (period + 1)
    out = [values[0]]
    for value in values[1:]:
        out.append(value * k + out[-1] * (1 - k))
    return out


def rsi(values: list[float], period: int = 14) -> float | None:
    if len(values) <= period:
        return None
    changes = [b - a for a, b in zip(values[-period-1:-1], values[-period:])]
    gain = sum(max(c, 0) for c in changes) / period
    loss = sum(max(-c, 0) for c in changes) / period
    if loss == 0:
        return 100
    return 100 - 100 / (1 + gain / loss)


def atr(bars: list[Bar], period: int = 14) -> float:
    if len(bars) < 2:
        return 0
    subset = bars[-(period + 1):]
    tr = [max(b.high - b.low, abs(b.high - prev.close), abs(b.low - prev.close))
          for prev, b in zip(subset[:-1], subset[1:])]
    return sum(tr) / len(tr) if tr else 0


def technical_score(bars: list[Bar]) -> tuple[float, float, list[str]]:
    if len(bars) < 20:
        return 50, 50, ["no/limited real price history"]
    close = [b.close for b in bars]
    last = close[-1]
    ma20, ma50 = sma(close, 20), sma(close, 50)
    weekly = [close[i] for i in range(4, len(close), 5)]
    w10 = sma(weekly, 10)
    score = 50.0
    reasons: list[str] = []
    if ma20 and last > ma20:
        score += 12; reasons.append("above 20-day trend")
    else:
        score -= 10
    if ma50 and last > ma50:
        score += 12; reasons.append("above 50-day trend")
    elif ma50:
        score -= 12
    momentum = (last / close[-11] - 1) if len(close) > 10 else 0
    score += max(-12, min(12, momentum * 180))
    avg_vol = sum(b.volume for b in bars[-20:]) / min(20, len(bars))
    rv = bars[-1].volume / max(1, avg_vol)
    if rv > 1.4 and momentum > 0:
        score += 8; reasons.append("volume confirms momentum")
    current_rsi = rsi(close)
    if current_rsi is not None:
        if 48 <= current_rsi <= 68:
            score += 7
        if current_rsi > 78:
            score -= 14; reasons.append("overextended RSI")
        if current_rsi < 32:
            score -= 5; reasons.append("weak/oversold momentum")
    weekly_score = 50 + (18 if w10 and last > w10 else -10)
    if len(weekly) > 5:
        weekly_score += max(-18, min(18, (weekly[-1] / weekly[-5] - 1) * 140))
    return clamp(score), clamp(weekly_score), reasons


def _metric(s: Security, key: str) -> float | None:
    direct = getattr(s, key, None)
    return direct if direct is not None else s.sector_metrics.get(key)


def fundamental_scores(s: Security) -> tuple[float, float, list[str]]:
    """Absolute V1 scoring. Sector-specific metrics matter; missing data stays neutral."""
    reasons: list[str] = []
    if s.asset_type == "FUND":
        return 50, 50, ["fund requires holdings/NAV-specific model"]

    eg = s.earnings_growth
    rg = s.revenue_growth
    roe = s.roe
    de = s.debt_to_equity

    fundamental = 50.0
    if eg is not None:
        fundamental += max(-22, min(22, eg * .55))
        if eg >= 15: reasons.append("earnings growth")
        elif eg < 0: reasons.append("earnings contraction")
    if rg is not None:
        fundamental += max(-10, min(12, rg * .25))
        if rg >= 15: reasons.append("revenue growth")
    if roe is not None:
        fundamental += max(-8, min(15, (roe - 12) * .45))
        if roe >= 20: reasons.append("strong ROE")
    if de is not None and s.sector != "Banks":
        fundamental -= max(0, de - 1.0) * 7

    if s.sector == "Banks":
        npl = _metric(s, "npl_ratio")
        car = _metric(s, "capital_adequacy")
        if npl is not None:
            fundamental += max(-10, min(8, (5 - npl) * 2.0))
        if car is not None:
            fundamental += max(-5, min(8, (car - 14) * .55))
    elif s.sector == "Real Estate":
        presales = _metric(s, "presales_growth")
        backlog = _metric(s, "backlog_growth")
        if presales is not None: fundamental += max(-8, min(12, presales * .20))
        if backlog is not None: fundamental += max(-6, min(10, backlog * .16))
    elif s.sector in {"Industrials", "Technology", "Telecom"}:
        margin = _metric(s, "margin_growth")
        exports = _metric(s, "export_share")
        if margin is not None: fundamental += max(-8, min(8, margin * .22))
        if exports is not None: fundamental += max(0, min(6, exports * .06))

    valuation_parts: list[tuple[float, float]] = []
    if s.pe is not None and s.pe > 0:
        pe_score = 100 - max(0, s.pe - 4) * 4.2
        valuation_parts.append((clamp(pe_score), .60))
    if s.pb is not None and s.pb > 0:
        anchor = 1.0 if s.sector == "Banks" else .8
        pb_score = 86 - max(0, s.pb - anchor) * 16
        valuation_parts.append((clamp(pb_score), .25))
    if s.dividend_yield is not None:
        valuation_parts.append((clamp(45 + min(s.dividend_yield, 15) * 3.0), .15))
    if valuation_parts:
        weight = sum(w for _, w in valuation_parts)
        valuation = sum(v * w for v, w in valuation_parts) / weight
    else:
        valuation = 50.0
    if valuation >= 70: reasons.append("attractive valuation")
    return clamp(fundamental), clamp(valuation), reasons[:4]


POSITIVE = {"growth", "profit", "contract", "award", "buyback", "dividend", "upgrade", "record", "expansion"}
NEGATIVE = {"loss", "decline", "dilution", "fine", "default", "delay", "suspension", "investigation"}


def catalyst_score(items: list[Catalyst], as_of: date) -> tuple[float, list[str]]:
    score, reasons = 50.0, []
    for item in items:
        if item.published > as_of:
            continue
        age = max(0, (as_of - item.published).days)
        decay = math.exp(-age / 45)
        words = set((item.headline + " " + item.text).lower().replace("/", " ").split())
        impact = len(words & POSITIVE) - len(words & NEGATIVE)
        score += impact * 9 * decay
        if impact:
            reasons.append(("positive: " if impact > 0 else "negative: ") + item.headline)
    return clamp(score), reasons[:2]


def portfolio_fit(s: Security, holdings: list[Holding], universe: dict[str, Security]) -> float:
    total = sum(h.market_value for h in holdings) or 1
    current = next((h.market_value for h in holdings if h.ticker == s.ticker), 0)
    sector_value = sum(h.market_value for h in holdings if universe.get(h.ticker) and universe[h.ticker].sector == s.sector)
    score = 75 - current / total * 120 - max(0, sector_value / total - .25) * 150
    if current == 0 and sector_value / total < .15:
        score += 12
    return clamp(score)


def liquidity_score(bars: list[Bar]) -> float:
    if not bars:
        return 35
    traded = sum(b.volume * b.close for b in bars[-20:]) / min(20, len(bars))
    return clamp(25 + math.log10(max(traded, 1)) * 9)


def data_quality_score(s: Security, bars: list[Bar], catalysts: list[Catalyst], as_of: date) -> float:
    score = 10.0
    if s.data_as_of is not None:
        age = max(0, (as_of - s.data_as_of).days)
        score += 30 if age <= 7 else 20 if age <= 30 else 8 if age <= 90 else 0
    if len(bars) >= 60: score += 35
    elif len(bars) >= 20: score += 20
    populated = sum(v is not None for v in (s.pe, s.pb, s.roe, s.earnings_growth, s.revenue_growth))
    score += populated * 4
    if any(c.published <= as_of and (as_of - c.published).days <= 60 for c in catalysts):
        score += 10
    return clamp(score)
