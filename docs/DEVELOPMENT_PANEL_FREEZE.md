# Development Panel Freeze

The development panel is the final dataset allowed to reach baseline-model code.

It is downstream of the row-level evidence manifest. A panel cannot be frozen merely because a CSV exists.

## Required order

```text
raw sources
  -> security identity
  -> price/corporate-action QA
  -> point-in-time membership
  -> row-level evidence manifest
  -> evidence authorization
  -> development panel
  -> development panel manifest
  -> baseline research
```

## Freeze command

After the row-level evidence manifest is authorized:

```bash
python scripts/freeze_development_panel.py \
  --panel /path/to/development_panel.json \
  --evidence-manifest evidence/frozen_preholdout_manifest.json \
  --code-ref COMMIT_SHA \
  --output evidence/frozen_development_panel.json
```

The panel input uses one row per `canonical_security_id × session_date`.

## Manifest guarantees

The generated manifest records the panel row count, unique security count, first and last session, deterministic panel fingerprint, exact row-level evidence fingerprint, evidence manifest code reference, repository development cutoff and panel code reference.

A manifest is invalid if its last session exceeds **2026-01-31**.

## Why the link matters

Without linking the panel fingerprint to the exact evidence fingerprint, a clean evidence audit could be followed by modeling a different file.

The manifest makes that substitution detectable.

## Current state

This repository does not yet contain an authorized real development panel. The freeze tooling exists so the transition can happen reproducibly when the missing evidence gates are satisfied.
