# EGX Portfolio Scanner V1.2

Portfolio-aware EGX decision engine for **Core + Active** strategies.

## What changed from V1

- Normal scans **never fabricate missing price history**. Synthetic history exists only behind explicit `backtest --demo`.
- Added data-quality gating so stale/incomplete names cannot silently become BUY signals.
- Core and Active now use different sizing logic.
- `active_capital_pct`, `max_sector_pct`, reserve and max-position settings are actually enforced.
- Fund rows are no longer scored as if historical fund returns were company earnings growth; funds now stay neutral until a dedicated NAV/holdings model is supplied.
- Rotation now points from a weak holding to a stronger candidate rather than self-referencing.
- Backtest includes configurable transaction-cost assumptions.

## Quick start

```powershell
python -m egx_scanner scan --fresh-capital 20000 --as-of 2026-08-28
python -m egx_scanner scan --fresh-capital 20000 --json
python -m egx_scanner backtest --ticker ABUK
python -m egx_scanner backtest --ticker ABUK --demo   # testing only
python -m egx_scanner init-db
```

## Required inputs

- `data/portfolio.csv`: executed holdings only
- `data/universe.csv`: latest normalized fundamental snapshot; optionally add `asset_type,data_as_of`
- `data/prices/TICKER.csv`: real `date,open,high,low,close,volume` history
- `data/disclosures.json`: verified catalysts/disclosures

The bundled data is illustrative and stale by design. **Do not trade from it.** The next development step is source adapters that refresh the EGX universe, EOD prices, disclosures and fund NAV/holdings before a scan.

## Architecture

`real data -> validation/data quality -> fundamentals/valuation + technicals + catalysts -> Core/Active -> portfolio fit -> risk/sizing -> allocator -> actions -> SQLite`

Actions: `BUY / ADD / HOLD / TRIM / SELL / ROTATE / WATCH`.

## V1.2 — real price ingestion

The scanner can now fetch **real daily EGX OHLCV history** from Yahoo Finance's public chart endpoint. EGX listings commonly use the Cairo suffix `.CA` (for example `COMI.CA` and `SWDY.CA`); `data/symbol_map.csv` overrides symbols when necessary.

```powershell
# refresh every STOCK in data/universe.csv
egx-scan refresh-prices

# refresh selected names only
egx-scan refresh-prices --tickers QNBE ADIB CIEB MASR TMGH ABUK ETEL --days 500

# refresh, then scan in one command
egx-scan scan --fresh-capital 20000 --refresh-prices
```

Each successful refresh writes `data/prices/TICKER.csv` plus `TICKER.meta.json` containing provider, provider symbol, retrieval time, and latest bar date. Writes are atomic: a failed download does **not** destroy the last known-good file.

Data-quality scoring now checks **price freshness as well as history depth**. Old history cannot qualify as live technical evidence merely because it contains many rows.

### Important boundary

V1.2 solves the first live-data layer: **market prices/history**. Fundamentals in `universe.csv` and catalysts in `disclosures.json` are still normalized inputs and must be refreshed from verified company/EGX/IR sources. The scanner deliberately does not scrape an unofficial fundamental number and label it authoritative. Those adapters are the next ingestion layer.
