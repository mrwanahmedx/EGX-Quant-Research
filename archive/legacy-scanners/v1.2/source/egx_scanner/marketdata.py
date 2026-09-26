from __future__ import annotations

import csv
import json
import time
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib.parse import urlencode, quote
from urllib.request import Request, urlopen

from .domain import Bar


class MarketDataError(RuntimeError):
    pass


@dataclass(frozen=True)
class RefreshResult:
    ticker: str
    provider_symbol: str
    bars: int
    first_date: date | None
    last_date: date | None
    path: Path


class YahooFinancePriceAdapter:
    """Fetch daily EGX OHLCV from Yahoo Finance's public chart endpoint.

    Most EGX listings use the `.CA` suffix (for Cairo), e.g. COMI.CA and SWDY.CA.
    `symbol_map.csv` can override symbols where needed. This adapter intentionally
    fetches price history only; it does not pretend Yahoo fundamentals are official.
    """

    provider = "yahoo_finance"

    def __init__(self, timeout: int = 20, user_agent: str | None = None):
        self.timeout = timeout
        self.user_agent = user_agent or "Mozilla/5.0 EGXPortfolioScanner/1.2"

    @staticmethod
    def default_symbol(ticker: str) -> str:
        return f"{ticker.upper()}.CA"

    def fetch_daily(self, ticker: str, symbol: str | None = None,
                    period_days: int = 420) -> tuple[str, list[Bar]]:
        symbol = symbol or self.default_symbol(ticker)
        now = int(time.time())
        start = now - max(30, period_days) * 86400
        params = urlencode({
            "period1": start,
            "period2": now + 86400,
            "interval": "1d",
            "events": "div,splits",
            "includeAdjustedClose": "true",
        })
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{quote(symbol)}?{params}"
        req = Request(url, headers={"User-Agent": self.user_agent, "Accept": "application/json"})
        try:
            with urlopen(req, timeout=self.timeout) as response:
                payload = json.load(response)
        except Exception as exc:  # network/HTTP/JSON are all a failed refresh
            raise MarketDataError(f"Yahoo request failed for {symbol}: {exc}") from exc

        chart = payload.get("chart") or {}
        if chart.get("error"):
            raise MarketDataError(f"Yahoo returned error for {symbol}: {chart['error']}")
        results = chart.get("result") or []
        if not results:
            raise MarketDataError(f"Yahoo returned no result for {symbol}")
        result = results[0]
        timestamps = result.get("timestamp") or []
        quote_rows = ((result.get("indicators") or {}).get("quote") or [{}])[0]
        opens = quote_rows.get("open") or []
        highs = quote_rows.get("high") or []
        lows = quote_rows.get("low") or []
        closes = quote_rows.get("close") or []
        volumes = quote_rows.get("volume") or []
        bars: list[Bar] = []
        for i, ts in enumerate(timestamps):
            try:
                o, h, l, c = opens[i], highs[i], lows[i], closes[i]
                v = volumes[i] if i < len(volumes) else 0
            except IndexError:
                continue
            if None in (o, h, l, c):
                continue
            d = datetime.fromtimestamp(ts, tz=timezone.utc).date()
            bars.append(Bar(d, float(o), float(h), float(l), float(c), float(v or 0)))
        bars.sort(key=lambda b: b.date)
        if not bars:
            raise MarketDataError(f"Yahoo returned no usable OHLCV bars for {symbol}")
        return symbol, bars


def load_symbol_map(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = csv.DictReader(handle)
        return {r["ticker"].strip().upper(): r["symbol"].strip()
                for r in rows if r.get("ticker") and r.get("symbol")}


def write_price_history(directory: Path, ticker: str, bars: Iterable[Bar],
                        provider: str, provider_symbol: str) -> RefreshResult:
    directory.mkdir(parents=True, exist_ok=True)
    rows = sorted(bars, key=lambda b: b.date)
    if not rows:
        raise MarketDataError(f"Refusing to write empty history for {ticker}")
    path = directory / f"{ticker.upper()}.csv"
    tmp = path.with_suffix(".csv.tmp")
    with tmp.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["date", "open", "high", "low", "close", "volume"])
        for b in rows:
            writer.writerow([b.date.isoformat(), f"{b.open:.8f}", f"{b.high:.8f}",
                             f"{b.low:.8f}", f"{b.close:.8f}", f"{b.volume:.0f}"])
    tmp.replace(path)
    meta = {
        "ticker": ticker.upper(),
        "provider": provider,
        "provider_symbol": provider_symbol,
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "first_date": rows[0].date.isoformat(),
        "last_date": rows[-1].date.isoformat(),
        "bars": len(rows),
    }
    path.with_suffix(".meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return RefreshResult(ticker.upper(), provider_symbol, len(rows), rows[0].date, rows[-1].date, path)


def refresh_yahoo_prices(tickers: Iterable[str], data_dir: Path, period_days: int = 420,
                         symbol_map_path: Path | None = None,
                         adapter: YahooFinancePriceAdapter | None = None) -> list[RefreshResult]:
    adapter = adapter or YahooFinancePriceAdapter()
    symbol_map = load_symbol_map(symbol_map_path or (data_dir / "symbol_map.csv"))
    output: list[RefreshResult] = []
    for ticker in dict.fromkeys(t.upper() for t in tickers):
        symbol = symbol_map.get(ticker) or adapter.default_symbol(ticker)
        provider_symbol, bars = adapter.fetch_daily(ticker, symbol, period_days)
        output.append(write_price_history(data_dir / "prices", ticker, bars,
                                          adapter.provider, provider_symbol))
    return output
