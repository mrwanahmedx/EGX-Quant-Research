# Point-in-Time Index Membership Reconstruction

The repository now has dated EGX30 review events for 2024-2025, but those events are not yet sufficient to build a historical constituent panel.

## What is known

Each review event records:

- index ID,
- publication date,
- effective date,
- source,
- additions,
- deletions.

This is materially better than applying today's constituents backward.

## What still blocks reconstruction

The current review file deliberately leaves company-to-canonical-security mappings unresolved.

In addition, a complete membership history requires a **dated seed constituent set** before the first review event.

Without both pieces, the project cannot truthfully claim a complete point-in-time EGX30 universe.

## Fail-closed behavior

The index-review parser therefore:

1. ignores review events not yet published at the decision timestamp,
2. refuses unresolved company identities in strict mode,
3. materializes only resolved add/delete deltas,
4. requires a seed membership set before a full constituent set can be reconstructed.

## Why this matters

A current-membership backfill creates survivorship and selection leakage.

The correct next evidence task is:

- resolve review company names to canonical security IDs using dated identity evidence,
- obtain a dated seed constituent list from an official or auditable source,
- then materialize the membership history and compare it with independently dated review publications.

The February-June 2026 holdout remains outside this process.
