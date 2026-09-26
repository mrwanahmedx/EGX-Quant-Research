# EGX Portfolio Scanner V1.1

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
