# Source-to-Evidence Lineage

The research evidence layer must be tied to the exact local public-data generation from which it was derived.

## Problem prevented

Without an explicit link, two artifacts could independently pass validation while referring to different source snapshots:

- the repository could contain a valid frozen source manifest for generation A,
- and a valid row-level evidence manifest built from generation B.

That would make the readiness gate look green without proving reproducible lineage.

## Contract

The frozen row-level evidence manifest now requires:

```text
source_snapshot_fingerprint
```

This value must equal the `composite_fingerprint` of the validated pre-holdout source snapshot manifest.

The evidence freeze CLI therefore requires a source-snapshot manifest and validates it against the source catalog before creating the evidence manifest.

## Readiness

Repository readiness now compares the two artifacts directly.

A valid source snapshot plus a valid evidence manifest is **not enough** when their fingerprints differ.

## Full lineage

```text
public source snapshot bytes (local only)
    |
    | SHA-256 / cutoff / license metadata
    v
frozen source snapshot manifest
    |
    | composite_fingerprint
    v
frozen row-level evidence manifest
    |
    | data_evidence_fingerprint + code_ref
    v
frozen development panel
    |
    v
experiment manifest / trial registry
```

This does not make weak source data trustworthy by itself. It makes the research generation reproducible and prevents silent source substitution.
