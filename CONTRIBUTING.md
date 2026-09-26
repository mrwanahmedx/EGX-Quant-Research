# Contributing

This repository is a personal research project, but changes still follow a strict evidence-first standard.

## Before adding model logic

Confirm that the required data passes the relevant gates in `docs/VALIDATION_GATES.md`.

## Pull-request expectations

A change should state:
- intended data grain,
- information availability / publication timing,
- target horizon if applicable,
- data fingerprint / experiment manifest for empirical results,
- transaction-cost assumption for portfolio results,
- tests added or updated.

## Prohibited shortcuts

Do not:
- backfill current constituents into historical periods,
- repair ambiguous prices by clipping or interpolation and then treat them as observed truth,
- use post-date fundamentals in earlier features,
- tune on the frozen holdout,
- publish synthetic or toy results as real EGX performance,
- commit private or employer data.

A blocked experiment is preferable to a misleading result.
