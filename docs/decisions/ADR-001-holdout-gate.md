# ADR-001 — Keep the February–June 2026 holdout unopened until the data-evidence gate passes

**Status:** Accepted  
**Date:** 2026-09-26

## Context

The research protocol defines a January 2026 development freeze and an untouched February–June 2026 holdout. Public EGX data reconciliation has exposed material price-quality, provenance, point-in-time membership, and corporate-action issues.

Opening the holdout while those inputs remain unresolved would convert a data-quality problem into model-selection information.

## Decision

Do not inspect, tune on, or otherwise use the February–June 2026 holdout until the pre-holdout evidence manifest passes the required data and timing controls.

## Required preconditions

- canonical security identity and symbol history,
- accepted price source / adjustment basis,
- point-in-time eligibility evidence,
- corporate-action status,
- benchmark provenance,
- leakage-safe timing,
- frozen development snapshot,
- reproducible execution / cost assumptions.

## Consequences

- model-approved universe can remain zero,
- attractive synthetic or partial backtests do not override the gate,
- blocked validation is recorded as a valid research result,
- the holdout retains evidentiary value for future validation.
