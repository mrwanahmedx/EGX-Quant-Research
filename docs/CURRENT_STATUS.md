# Current Status

Updated: 2026-09-26

## Executive state

**REAL MODELING BLOCKED BY DATA QA**

The research protocol and model-validation harness are ahead of the trustworthy real-data layer. That is intentional: the project is designed to stop rather than manufacture a clean backtest from weak evidence.

## Real-data ingestion findings

The latest pre-holdout ingestion work combined:

- the Eyad Kaggle EGX history,
- the Mahmoud Kaggle EGX 2021-2026 history,
- a direct Yahoo extension,
- EGX security metadata used to reconcile identifiers.

Current reconciliation totals:

| Check | Current result |
| --- | ---: |
| Pre-holdout OHLCV rows ingested | 966,215 |
| Identifiers reconciled | 289 |
| Impossible OHLC rows detected | 140,518 |
| Real holdout opened | No |
| Real model accepted | No |

"Impossible OHLC" means observations violating basic bar geometry or equivalent source-consistency rules. They cannot be silently repaired without an auditable rule and source evidence.

## What has already been tested

The project previously built a synthetic research harness to exercise:

- Alpha158-style feature generation,
- 20d / 63d residual-return targets,
- Linear / Lasso / LightGBM / XGBoost ranker / CatBoost model families,
- sector and beta neutralisation,
- Top-K / dropout construction,
- purged walk-forward logic,
- model / trial registries,
- acceptance statistics and leakage checks.

That work is infrastructure validation only. It is **not** a substitute for real EGX validation.

## Immediate blockers

1. Resolve impossible OHLC observations source by source.
2. Build a canonical symbol / security master with effective dates.
3. Obtain or reconstruct point-in-time constituent membership without current-membership leakage.
4. Apply auditable corporate-action adjustments.
5. Establish benchmark histories with date and methodology provenance.
6. Lock the pre-holdout data snapshot.
7. Only then generate real features and development folds.

The February-June 2026 holdout remains untouched by design.
