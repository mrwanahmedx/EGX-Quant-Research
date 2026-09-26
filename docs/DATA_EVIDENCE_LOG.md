# Data Evidence Log

This log records evidence decisions separately from model results.

## 2026-09-26 — price-conflict reconciliation

The pre-holdout source audit reviewed 49 material conflict tickers.

Classification:
- 39 corporate-action / adjusted-versus-unadjusted basis conflicts,
- 10 source-corruption / non-comparable OHLC conflicts,
- 0 unresolved after the audit,
- 0 confirmed ticker-alias issues in the audited set.

Action:
- quarantined 47 ticker/date ranges,
- quarantined 31,860 execution rows covering 2021-2023,
- preserved source observations rather than rewriting them,
- retained the existing Eyad execution path for EGBE and KZPC after direct pre-2024 arbitration.

Universe state after those quarantines:
- latest liquidity universe: 116,
- names unaffected by those quarantines: 96,
- model-approved universe: 0 because the broader evidence gate is still incomplete.

## Interpretation

"Resolved conflict" does **not** mean "model-ready security."

A price-source conflict can be resolved while point-in-time membership, corporate-action completeness, benchmark provenance or publication timing is still missing.

This distinction is why the repository tracks:
1. source-conflict status,
2. quarantine status,
3. model-eligibility status

as separate concepts.

## Evidence that must exist before promotion

For each security/date entering the research panel:

- canonical security ID,
- provider symbol,
- source vintage / checksum,
- accepted price basis,
- corporate-action status,
- point-in-time membership evidence,
- sector evidence if used,
- liquidity eligibility,
- benchmark availability,
- quarantine reason where applicable.

The machine-readable evidence manifest is the next major data deliverable.
