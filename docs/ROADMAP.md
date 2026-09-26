# Roadmap

The roadmap is deliberately data-first. Modeling starts only after the evidence chain is defensible.

## Phase 1 — Canonicalise the free-data layer

### Source inventory
Candidate inputs:
- Eyad Kaggle EGX history,
- Mahmoud Kaggle EGX 2021-2026 history,
- Yahoo history / extension where available,
- Hugging Face EGX symbol and metadata resources,
- public issuer / EGX disclosures for reference events.

For every source record:
- license / usage notes,
- coverage dates,
- ticker convention,
- adjustment basis,
- known gaps.

### Resolve the impossible-OHLC population
Current QA has identified a large invalid population.

Work item:
- classify by source / ticker / date,
- detect swapped columns, incompatible adjustment basis, malformed numeric parsing, unit errors and corporate-action discontinuities,
- compare overlap sessions across independent sources,
- quarantine rather than auto-correct ambiguous rows.

### Security master
Build:
- canonical security ID,
- symbol aliases,
- listing status,
- sector,
- mapping confidence,
- source lineage.

Hugging Face metadata is useful as a mapping input, not unquestioned price truth.

## Phase 2 — Point-in-time reconstruction

Priority evidence:
- historical EGX index membership,
- listing / delisting,
- sector changes,
- corporate actions,
- suspensions,
- benchmark methodology.

If full historical membership cannot be supported, narrow the research claim rather than pretending current constituents are historical.

## Phase 3 — Lock the pre-holdout snapshot

Create:
- raw-source checksums,
- canonical dataset fingerprint,
- QA report,
- coverage matrix,
- frozen development universe through 2026-01-31.

Only this frozen snapshot may feed model development.

## Phase 4 — Baselines first

Build:
1. cross-sectional momentum baseline,
2. linear model,
3. Lasso.

Measure:
- Rank IC by fold,
- turnover,
- net-of-cost Top-K,
- sector / beta exposure,
- concentration,
- stability.

## Phase 5 — Tree challengers

Only after baselines are trustworthy:
- LightGBM,
- XGBoost ranker,
- CatBoost.

Use the same folds, features, costs and manifests.

## Phase 6 — Foundation-model challengers

Research public model-hub candidates only if:
- inputs map to EGX data without hidden leakage,
- inference is reproducible,
- the model uses the same target and holdout contract,
- it beats a transparent baseline after costs.

No foundation model gets an easier validation standard.

## Phase 7 — Statistical acceptance

Add:
- DSR / PSR where assumptions are supportable,
- CSCV / PBO,
- Reality Check / bootstrap controls,
- trial-registry accounting,
- model-family challenger separation.

## Phase 8 — One-shot holdout

Freeze model, features, costs and thresholds.

Then and only then evaluate February-June 2026.

## Phase 9 — Shadow

Use September 2026 onward as shadow / forward evidence.

Maintain:
- prediction ledger,
- source vintage,
- decision timestamp,
- execution assumption,
- realized outcome,
- post-trade attribution.
