# Data

Raw and processed third-party market datasets are intentionally **not committed**.

## Local layout

```text
data/
  raw/         untouched provider snapshots
  interim/     parsed / mapped but not model-ready
  processed/   frozen, QA-passed research panels
```

These directories are ignored by Git.

## Candidate sources

The current free-data route includes public EGX histories from Kaggle, Yahoo extensions where available, Hugging Face security metadata and official public disclosures for reference checks.

A dataset is not promoted from `raw` to `processed` until:
- schema is known,
- source vintage is recorded,
- security IDs are mapped,
- duplicates are resolved,
- OHLC checks pass,
- corporate-action basis is known,
- point-in-time eligibility is defensible.

## Required provenance record

```json
{
  "source": "provider-or-dataset-name",
  "retrieved_at": "ISO-8601",
  "source_version": "version-or-snapshot",
  "file_sha256": "sha256",
  "rows": 0,
  "notes": ""
}
```

Do not commit proprietary data, private brokerage exports or employer information.
