from __future__ import annotations

import argparse
from datetime import date

from .backtest import run_trend_backtest
from .config import Settings
from .engine import Scanner
from .ingestion import demo_history, load_catalysts, load_portfolio, load_prices, load_universe
from .marketdata import MarketDataError, refresh_yahoo_prices
from .report import as_json, render
from .storage import Store


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="egx-scan", description="Portfolio-aware EGX scanner")
    sub = p.add_subparsers(dest="command", required=True)

    scan = sub.add_parser("scan", help="rank portfolio and new opportunities")
    scan.add_argument("--fresh-capital", type=float, default=20000)
    scan.add_argument("--as-of", type=date.fromisoformat, default=date.today())
    scan.add_argument("--json", action="store_true")
    scan.add_argument("--refresh-prices", action="store_true",
                      help="fetch real Yahoo Finance daily EGX history before scoring")
    scan.add_argument("--price-days", type=int, default=420)

    refresh = sub.add_parser("refresh-prices", help="download real daily EGX OHLCV")
    refresh.add_argument("--tickers", nargs="*", help="defaults to all STOCK rows in universe.csv")
    refresh.add_argument("--days", type=int, default=420)

    backtest = sub.add_parser("backtest", help="run the V1 trend backtest")
    backtest.add_argument("--ticker", required=True)
    backtest.add_argument("--demo", action="store_true", help="explicitly allow synthetic test history when no CSV exists")
    sub.add_parser("init-db", help="initialize SQLite storage")
    return p


def _universe_tickers(settings: Settings, requested: list[str] | None = None) -> list[str]:
    if requested:
        return [x.upper() for x in requested]
    return [s.ticker for s in load_universe(settings.data_dir / "universe.csv") if s.asset_type == "STOCK"]


def _refresh(settings: Settings, tickers: list[str], days: int) -> bool:
    failures = 0
    for ticker in tickers:
        try:
            results = refresh_yahoo_prices([ticker], settings.data_dir, days)
            r = results[0]
            print(f"{r.ticker}: {r.bars} bars through {r.last_date} ({r.provider_symbol})")
        except MarketDataError as exc:
            failures += 1
            print(f"{ticker}: REFRESH FAILED - {exc}")
    if failures:
        print(f"Price refresh finished with {failures}/{len(tickers)} failures. Existing files were left untouched for failed tickers.")
    return failures == 0


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    settings = Settings(); settings.validate(); store = Store(settings.db_path)

    if args.command == "init-db":
        store.initialize(); print(f"Initialized {settings.db_path}"); return 0

    if args.command == "refresh-prices":
        tickers = _universe_tickers(settings, args.tickers)
        return 0 if _refresh(settings, tickers, args.days) else 2

    if args.command == "backtest":
        ticker = args.ticker.upper()
        bars = load_prices(settings.data_dir / "prices", ticker)
        if not bars and args.demo:
            security = next((s for s in load_universe(settings.data_dir / "universe.csv") if s.ticker == ticker), None)
            if security is None: raise SystemExit(f"Unknown ticker: {ticker}")
            bars = demo_history(ticker, security.price)
        if not bars:
            raise SystemExit(f"No real price history for {ticker}. Run `egx-scan refresh-prices --tickers {ticker}` or use --demo for testing only.")
        result = run_trend_backtest(ticker, bars, settings.transaction_cost_bps_each_side)
        print(f"{result.ticker}: return {result.return_pct:.1f}% | max drawdown {result.max_drawdown_pct:.1f}% | trades {result.trades}")
        return 0

    securities = load_universe(settings.data_dir / "universe.csv")
    if args.refresh_prices:
        # A failed network refresh does not overwrite known-good files; quality gating then decides eligibility.
        _refresh(settings, [s.ticker for s in securities if s.asset_type == "STOCK"], args.price_days)
    holdings = load_portfolio(settings.data_dir / "portfolio.csv")
    catalysts = load_catalysts(settings.data_dir / "disclosures.json")
    scanner = Scanner(settings)
    cards, histories = scanner.score(securities, holdings, catalysts, args.as_of)
    recs = scanner.recommend(securities, holdings, cards, histories, args.fresh_capital)
    run_id = store.save_scan(args.as_of.isoformat(), args.fresh_capital, recs)
    print(as_json(recs) if args.json else render(recs, args.fresh_capital, settings.reserve_pct))
    if not args.json: print(f"\nSaved scan #{run_id}")
    return 0
