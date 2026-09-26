# Pre-Holdout Evidence Manifest

The next real-data deliverable is not another model. It is the evidence manifest that determines whether a security/date is allowed into the development panel.

## Intended grain

One evidence row per:

```text
canonical_security_id × session_date × source_vintage
```

## Mandatory fields

Each row must state:

- canonical security ID,
- session date,
- accepted price source,
- source vintage,
- source checksum when available,
- price basis,
- OHLC QA status,
- quarantine status and reason,
- point-in-time membership status,
- corporate-action status,
- benchmark status,
- observation / publication timing,
- final evidence-complete flag.

## Fail-closed behavior

A panel row is model-eligible only when all mandatory conditions pass.

Unknown is not treated as passed.

Quarantined is not treated as partially usable.

Missing evidence does not fall back to a synthetic replacement.

## Current repository state

The repository currently contains the aggregate reconciliation status but **not** the full 47-range quarantine manifest. Therefore the model-approved universe remains zero.

This is deliberate. The repository must not invent ticker/date ranges that have not been recovered from the actual audit artifacts.

## Next data action

Recover the detailed quarantine / arbitration output from the local EGX research workspace, attach source-vintage fingerprints, and write the first machine-readable evidence manifest.

Only then should the panel builder be run against real rows.
