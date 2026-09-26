from __future__ import annotations

import argparse
from datetime import date

from .backtest import run_trend_backtest
from .config import Settings
from .engine import Scanner
from .ingestion import demo_history, load_catalysts, load_portfolio, load_prices, load_universe
from .report import as_json, render
from .storage import Store


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="egx-scan", description="Portfolio-aware EGX scanner")
    sub = p.add_subparsers(dest="command", required=True)
    scan = sub.add_parser("scan", help="rank portfolio and new opportunities")
    scan.add_argument("--fresh-capital", type=float, default=20000)
    scan.add_argument("--as-of", type=date.fromisoformat, default=date.today())
    scan.add_argument("--json", action="store_true")
    backtest = sub.add_parser("backtest", help="run the V1 trend backtest")
    backtest.add_argument("--ticker", required=True)
    backtest.add_argument("--demo", action="store_true", help="explicitly allow synthetic test history when no CSV exists")
    sub.add_parser("init-db", help="initialize SQLite storage")
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    settings = Settings(); settings.validate(); store = Store(settings.db_path)
    if args.command == "init-db":
        store.initialize(); print(f"Initialized {settings.db_path}"); return 0
    if args.command == "backtest":
        ticker = args.ticker.upper()
        bars = load_prices(settings.data_dir / "prices", ticker)
        if not bars and args.demo:
            security = next((s for s in load_universe(settings.data_dir / "universe.csv") if s.ticker == ticker), None)
            if security is None: raise SystemExit(f"Unknown ticker: {ticker}")
            bars = demo_history(ticker, security.price)
        if not bars:
            raise SystemExit(f"No real price history for {ticker}. Add data/prices/{ticker}.csv or use --demo for testing only.")
        result = run_trend_backtest(ticker, bars, settings.transaction_cost_bps_each_side)
        print(f"{result.ticker}: return {result.return_pct:.1f}% | max drawdown {result.max_drawdown_pct:.1f}% | trades {result.trades}")
        return 0
    securities = load_universe(settings.data_dir / "universe.csv")
    holdings = load_portfolio(settings.data_dir / "portfolio.csv")
    catalysts = load_catalysts(settings.data_dir / "disclosures.json")
    scanner = Scanner(settings)
    cards, histories = scanner.score(securities, holdings, catalysts, args.as_of)
    recs = scanner.recommend(securities, holdings, cards, histories, args.fresh_capital)
    run_id = store.save_scan(args.as_of.isoformat(), args.fresh_capital, recs)
    print(as_json(recs) if args.json else render(recs, args.fresh_capital, settings.reserve_pct))
    if not args.json: print(f"\nSaved scan #{run_id}")
    return 0
