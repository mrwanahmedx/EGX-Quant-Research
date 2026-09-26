# Pre-Holdout Source Snapshot Freeze

Real research should be reproducible without publishing third-party market files.

The source-snapshot manifest solves that by freezing **metadata about the exact local public datasets** used for the development generation.

## What gets committed

For each local source snapshot:

- source catalog ID,
- dataset / provider version,
- SHA-256 of the local snapshot,
- row count,
- first and last session,
- license status,
- local-only flag,
- notes.

The raw dataset itself remains outside Git.

## Development cutoff

A source snapshot authorized for this research generation must contain only observations through **2026-01-31**.

If a provider download contains later observations, create a deterministic pre-holdout extract locally and fingerprint that extract instead of freezing the mixed-period file.

This keeps February-June 2026 outside the development-generation bytes, not merely outside a later DataFrame filter.

## License consistency

The manifest's license status must match the committed source catalog.

This is not a legal determination; it prevents a local artifact from silently being recorded under a different redistribution assumption than the source inventory.

## Composite fingerprint

The manifest computes one deterministic fingerprint across all source snapshots.

That fingerprint can be linked to:

- row-level evidence,
- frozen development panel,
- experiment manifests.

## Current state

No real source snapshot manifest is committed yet.

That is correct until the local Kaggle / Yahoo / reference inputs are recovered, filtered to the development cutoff, checksummed and reconciled.
