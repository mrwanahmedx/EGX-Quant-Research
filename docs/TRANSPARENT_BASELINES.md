# Transparent Baseline Runner

Issue #4 requires transparent baselines before tree-model challengers.

The repository now contains a baseline evaluator, but **real execution remains blocked** until the evidence and development-panel gates authorize modeling.

## Baseline inputs

The evaluator expects one row per:

```text
session_date × canonical_security_id
```

with:

- a transparent score,
- the matching forward residual-return target.

The first intended real scores are simple cross-sectional momentum / relative-strength signals, followed by the linear and Lasso baselines once the frozen feature matrix exists.

## Metrics

The dependency-free rank baseline calculates:

- per-session Rank IC,
- mean Rank IC,
- positive-IC fraction,
- Top-K selection,
- one-way turnover,
- gross mean period return,
- net mean period return after explicit bps costs.

The mean-period-return fields are descriptive development metrics, **not a cumulative performance claim**.

## Guardrail

The CLI calls the repository readiness gate before reading model observations.

Today it exits BLOCKED because Issues #1-#3 are incomplete.

This is intentional. The baseline code can be tested with synthetic fixtures without allowing a real-data model run to bypass the frozen evidence contract.

## Future real run

After the exact quarantine register, dated security master, benchmark series, frozen acceptance thresholds, row-level evidence manifest and frozen development panel are authorized:

1. generate the development-only baseline observations,
2. record an experiment manifest and data fingerprint,
3. run the transparent baseline,
4. register the trial,
5. compare development metrics with the pre-frozen acceptance rules,
6. only then consider tree challengers.

The February-June 2026 holdout is not part of baseline tuning.
