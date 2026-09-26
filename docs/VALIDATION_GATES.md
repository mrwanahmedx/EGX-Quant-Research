# Validation Gates

Model evaluation is downstream of data evidence.

## Gate A — Security identity

Required:
- stable canonical ID,
- unambiguous ticker mapping,
- effective-date handling for symbol changes,
- no unresolved identifier collisions.

Failure action: block affected security/date.

## Gate B — Price integrity

Required:
- OHLC geometry,
- non-negative volume,
- duplicate-grain check,
- unexplained discontinuity check,
- source-vintage provenance.

Failure action: quarantine observation.

## Gate C — Corporate actions

Required:
- documented adjustment basis,
- split / dividend / rights handling where relevant,
- no cross-source mixture of incompatible price bases.

Failure action: block return target across unresolved event.

## Gate D — Point-in-time universe

Required:
- historical membership / eligibility evidence,
- no current-membership backfill,
- historical sector where used.

Failure action: do not run historical cross-sectional selection.

## Gate E — Leakage

Required:
- source publication timestamp <= feature as-of timestamp,
- targets strictly forward,
- purge / embargo for overlapping horizons,
- transformations fitted only on development data.

Failure action: invalidate experiment.

## Gate F — Reproducibility

Required:
- data fingerprint,
- code / commit reference,
- experiment manifest,
- feature-set ID,
- model parameters,
- random seed,
- cost assumptions.

Failure action: result cannot enter model registry.

## Gate G — Execution realism

Required:
- next-session execution convention,
- explicit costs,
- slippage assumption,
- liquidity / exit-capacity checks,
- suspension treatment.

Failure action: portfolio result may not be presented as executable.

## Gate H — Statistical acceptance

Required:
- performance stability across development folds,
- multiple-testing awareness,
- turnover and concentration review,
- benchmark comparison,
- documented failure thresholds before holdout.

Failure action: do not open holdout.

## Gate I — Holdout

The February-June 2026 holdout is evaluated only after Gates A-H pass and the research specification is frozen.

There is no retroactive threshold change after seeing holdout performance.
