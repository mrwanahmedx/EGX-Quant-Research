# Evidence layer

This directory stores **small, auditable research evidence metadata**, not raw market datasets.

## Current committed state

`reconciliation_summary.json` preserves the verified aggregate state of the latest source-conflict audit.

It deliberately does **not** reconstruct the missing exact 47 quarantine rows from memory. The original machine-readable register must be recovered and imported before the quarantine backlog item can be closed.

Expected source artifacts from that reconciliation include:

- `egx_conflict_reconciliation_report.md`
- `egx_overlap_conflict_register.csv`
- `egx_qa_rerun.json`
- `egx_qa_eligibility_rerun.json`
- `egx_qa_eligibility_report.md`
- `egx_impossible_ohlc_profile_by_source...`

## Intended machine-readable flow

1. Parse original provider snapshots locally.
2. Produce exact quarantine rows matching `schemas/quarantine_range.schema.json`.
3. Produce one evidence row per intended security/date grain matching `schemas/data_evidence_record.schema.json`.
4. Validate point-in-time security identity against `schemas/security_master_record.schema.json`.
5. Freeze the exact pre-holdout source snapshot metadata and composite fingerprint.
6. Freeze a row-level evidence manifest explicitly linked to that source snapshot fingerprint.
7. Freeze a development panel linked to the authorized evidence generation.
8. Permit model development only when every lineage link and evidence gate passes.

No exact ticker/date range should be recreated from a narrative summary.


## Lineage chain

The model-development lineage is deliberately cryptographic:

```text
local public source extract
  -> source snapshot SHA-256 + composite fingerprint
  -> row-level evidence manifest + source_snapshot_fingerprint
  -> development panel manifest + evidence fingerprint/code ref
  -> experiment manifest
```

A row-level evidence manifest from a different source generation must not authorize the current development panel.
