from __future__ import annotations

import csv
import json
import random
from datetime import date
from pathlib import Path

from .domain import Bar, Catalyst, Holding, Security, Strategy


def _num(row: dict[str, str], key: str) -> float | None:
    raw = (row.get(key) or "").strip()
    return float(raw) if raw else None


def _date(row: dict[str, str], key: str) -> date | None:
    raw = (row.get(key) or "").strip()
    return date.fromisoformat(raw) if raw else None


def load_universe(path: Path) -> list[Security]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = csv.DictReader(handle)
        result = []
        base = {"ticker", "name", "sector", "price", "pe", "pb", "roe", "earnings_growth",
                "revenue_growth", "dividend_yield", "debt_to_equity", "asset_type", "data_as_of"}
        for r in rows:
            metrics = {k: float(v) for k, v in r.items() if k not in base and v and v.strip()}
            result.append(Security(
                r["ticker"].upper(), r["name"], r["sector"], float(r["price"]),
                _num(r, "pe"), _num(r, "pb"), _num(r, "roe"), _num(r, "earnings_growth"),
                _num(r, "revenue_growth"), _num(r, "dividend_yield"), _num(r, "debt_to_equity"),
                metrics, (r.get("asset_type") or "STOCK").upper(), _date(r, "data_as_of")
            ))
    return result


def load_portfolio(path: Path) -> list[Holding]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [Holding(r["ticker"].upper(), float(r["quantity"]), float(r["avg_cost"]),
                        float(r["market_value"]), Strategy(r["bucket"].upper()))
                for r in csv.DictReader(handle)]


def load_prices(directory: Path, ticker: str) -> list[Bar]:
    path = directory / f"{ticker.upper()}.csv"
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as handle:
        bars = [Bar(date.fromisoformat(r["date"]), float(r["open"]), float(r["high"]),
                    float(r["low"]), float(r["close"]), float(r["volume"]))
                for r in csv.DictReader(handle)]
    return sorted(bars, key=lambda b: b.date)


def load_catalysts(path: Path) -> list[Catalyst]:
    if not path.exists():
        return []
    rows = json.loads(path.read_text(encoding="utf-8"))
    return [Catalyst(r["ticker"].upper(), date.fromisoformat(r["published"]), r["headline"],
                     r.get("text", ""), r.get("source", "manual")) for r in rows]


class FeedAdapter:
    """Interface for a real EGX/vendor feed. Adapters must return normalized objects."""

    def securities(self) -> list[Security]:
        raise NotImplementedError

    def prices(self, ticker: str) -> list[Bar]:
        raise NotImplementedError

    def catalysts(self) -> list[Catalyst]:
        raise NotImplementedError


def demo_history(ticker: str, last_price: float, periods: int = 90) -> list[Bar]:
    """Synthetic history for UI/testing demos only. Never used by a normal scan."""
    rng = random.Random(ticker)
    prices = [last_price]
    for _ in range(periods - 1):
        prices.append(prices[-1] / (1 + rng.gauss(.0012, .014)))
    prices.reverse()
    start = date(2026, 4, 20)
    bars = []
    for i, close in enumerate(prices):
        spread = abs(rng.gauss(.012, .004))
        opened = close * (1 + rng.gauss(0, .004))
        bars.append(Bar(date.fromordinal(start.toordinal()+i), opened,
                        max(opened, close)*(1+spread/2), min(opened, close)*(1-spread/2),
                        close, 450_000 * (1 + rng.random()*1.5)))
    return bars
