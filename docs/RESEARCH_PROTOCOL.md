# Research Protocol

## 1. Objective

Evaluate whether public EGX data can support a repeatable cross-sectional ranking model that adds information beyond simple benchmarks after realistic costs.

The protocol prioritises falsification. A failed gate is a valid outcome.

## 2. Time separation

- Development information cutoff: **2026-01-31**
- Untouched holdout: **2026-02-01 through 2026-06-30**
- Shadow period: **from 2026-09-01**

No feature, security membership, source revision, corporate action or model decision may use information first available after the relevant as-of date.

## 3. Targets

Primary targets:

- 20 trading-day residual return
- 63 trading-day residual return

Raw forward return is not enough. The intended target removes a documented market / sector component so the model is tested on cross-sectional selection rather than broad market direction.

Target definitions must record:
- entry timestamp,
- exit timestamp,
- benchmark / residualisation method,
- corporate-action basis,
- treatment of suspensions and missing prices.

## 4. Universe

Universe membership must be point-in-time. Current constituents cannot be projected backward.

Each security observation requires:
- canonical security ID,
- ticker valid on that date,
- listing / delisting effective dates where available,
- sector classification with effective date,
- liquidity eligibility,
- provenance.

## 5. Features

Initial feature families:
- price / volume momentum,
- volatility and range,
- turnover / liquidity,
- moving-average structure,
- gap / reversal measures,
- market-relative and sector-relative returns,
- Alpha158 / Qlib-style rolling operators,
- explicitly lagged event / public-fundamental features only when publication dates are evidenced.

All features must be computable using information available by the decision timestamp.

## 6. Model families

Baselines:
- linear regression / rank transform,
- Lasso.

Challengers:
- LightGBM,
- XGBoost ranker,
- CatBoost.

Foundation-model experiments, if any, are challengers only. They cannot replace a transparent baseline or bypass the same data and holdout gates.

## 7. Development

Use purged walk-forward development with:
- no random row shuffling,
- purge / embargo at least as large as target overlap requires,
- one experiment manifest per run,
- fixed seeds,
- registered feature set,
- immutable data fingerprint.

Hyperparameter search results are part of the multiple-testing burden.

## 8. Portfolio research

Candidate construction:
- Top-K,
- Top-K with dropout / turnover control.

Required adjustments:
- sector neutrality where feasible,
- beta control,
- liquidity filters,
- realistic lot / execution constraints,
- next-session execution,
- transaction costs and slippage.

## 9. Acceptance

Development metrics may include:
- mean and dispersion of Rank IC,
- IC information ratio,
- net-of-cost return / turnover,
- concentration,
- drawdown,
- PSR / DSR,
- PBO / CSCV,
- Reality Check-style multiple-testing controls when statistically defensible.

No single metric is an approval gate by itself.

## 10. Holdout

The holdout may be evaluated once, after:
- data QA passes,
- features and target are frozen,
- model selection is frozen,
- costs are frozen,
- benchmark definitions are frozen,
- the experiment manifest is committed.

If the holdout fails, it fails. It is not converted into another tuning set.

## 11. Shadow

Shadow testing is forward-looking observation after the holdout process. Any post-holdout change is versioned and treated as a new research generation.
