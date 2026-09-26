# Point-in-Time Universe Design

## Problem

A cross-sectional model needs a historically valid answer to:

> Which securities were eligible to be ranked on each decision date?

Using today's EGX30 / EGX70 membership in older dates would create survivorship and future-membership leakage.

## Route A — dated index review reconstruction

The repository now contains a partial EGX30 review-event ledger for 2024-2025 in:

`evidence/index_reviews/egx30_review_events_2024_2025.json`

The ledger records:
- publication date,
- effective date,
- additions,
- deletions,
- source URL,
- source type.

The 2025 events are sourced from republications of EGX statements. The 2024 events currently use dated secondary reporting of EGX review results.

### Why this is not yet enough

The events alone do not create a full historical membership series.

A complete reconstruction also needs:
1. a verified full baseline constituent set at some starting date,
2. canonical identity mapping for every addition / deletion,
3. a continuous chain of review events from the baseline to each research date.

Accordingly, the committed event members deliberately retain `canonical_security_id = null` until the security-master mapping is verified.

The code refuses to apply an event whose identities are unresolved.

## Route B — lagged liquidity-defined research universe

A research universe does not have to equal an official index.

A second defensible route is a rule defined only from information available before the decision date, for example:
- require sufficient valid historical sessions,
- rank by lagged traded value / liquidity,
- select the top N eligible securities,
- exclude quarantined or identity-unresolved names.

The repository includes a generic `select_lagged_liquidity_universe` implementation that uses observations strictly before the decision date.

### Why this may be preferable

It can reduce dependence on incomplete historical index membership while keeping the research universe broad and reproducible.

### What is not decided

No live research threshold has been frozen yet.

The repository does **not** currently declare:
- lookback length,
- minimum observation count,
- top-N size,
- absolute turnover threshold.

Those parameters must be selected and frozen on development evidence without inspecting the February-June 2026 holdout.

## Decision rule

Neither route is automatically approved.

The production research universe must ultimately satisfy:
- point-in-time identity,
- no future observations,
- reproducible inclusion rule,
- sufficient liquidity for the execution assumption,
- no quarantined security/date,
- frozen policy before holdout evaluation.
