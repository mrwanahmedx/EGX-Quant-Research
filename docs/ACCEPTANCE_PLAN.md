# Acceptance Plan

The project separates **data acceptance**, **research acceptance** and **holdout acceptance**.

## Stage 1 — Data acceptance

All mandatory evidence gates must pass before real model development.

Required outcomes:
- no unresolved identity collision,
- intended row grain unique,
- OHLC geometry valid or quarantined,
- source basis known,
- point-in-time eligibility supported,
- corporate-action treatment supported,
- benchmark provenance documented,
- frozen source snapshot fingerprinted.

A security/date that fails a mandatory condition is excluded or blocks the panel depending on scope.

## Stage 2 — Development research

Use purged walk-forward folds only.

Evaluate at minimum:
- cross-sectional Rank IC by fold,
- IC dispersion / stability,
- turnover,
- concentration,
- sector / beta exposure,
- gross and net-of-cost portfolio results,
- sensitivity to Top-K and dropout choices,
- comparison with simple baselines.

No hyperparameter search result is interpreted without its trial count.

## Stage 3 — Multiple-testing / robustness

Where sample size supports it, add:
- Probabilistic Sharpe Ratio,
- Deflated Sharpe Ratio,
- PBO / CSCV,
- bootstrap / Reality Check style controls,
- challenger-family separation.

If an advanced statistic is not defensible for the available sample, document that limitation instead of manufacturing precision.

## Stage 4 — Pre-holdout freeze

Before opening the holdout, commit:
- data fingerprint,
- feature-set ID,
- target definition,
- model family and parameters,
- portfolio construction,
- transaction-cost assumptions,
- benchmark definition,
- acceptance criteria,
- experiment manifest.

## Stage 5 — One-shot holdout

Evaluate February-June 2026 once.

Permitted outcomes:
- pass,
- fail,
- inconclusive due to a predeclared statistical limitation.

A failed holdout is not converted into a tuning set.

## Stage 6 — Shadow

Any strategy surviving the holdout moves to versioned shadow testing from September 2026 onward.

Shadow records must preserve:
- prediction timestamp,
- source vintage,
- rank / score,
- hypothetical execution convention,
- costs,
- realised outcome,
- attribution.

No live-trading claim is made merely because a shadow result exists.
