# Benchmark Freeze Runbook

Benchmark data is part of the research contract. It cannot be swapped after model development begins.

## Official source references

The source catalog now identifies:

- Central Bank of Egypt CONIA pages for the official overnight benchmark and linked historical data,
- Central Bank of Egypt EGP Treasury Bill auction pages for official auction results,
- Egyptian Exchange official index pages for equity-index methodology/reference data.

Identifying an official source is not the same as freezing a usable historical benchmark.

## Freeze format

Prepare a local CSV:

```csv
date,value
2025-01-02,100.0
2025-01-03,100.5
```

Then freeze a manifest:

```bash
python scripts/freeze_benchmark_series.py \
  --series /path/to/series.csv \
  --benchmark-id conia \
  --source-id cbe_conia \
  --source-snapshot-ref SHA256_OR_ARCHIVE_REFERENCE \
  --return-convention daily_compounded_index \
  --methodology-ref OFFICIAL_METHODOLOGY_REFERENCE \
  --code-ref COMMIT_SHA \
  --output evidence/benchmarks/conia.json
```

The tool deliberately writes the manifest as **not yet approved**.

## Separate freeze from approval

A series is approved for model comparison only after review confirms:

1. official source / methodology,
2. reproducible historical snapshot,
3. no post-2026-01-31 observations in development,
4. explicit return convention,
5. correct horizon treatment,
6. fingerprint consistency,
7. no silent price-return / total-return substitution.

For T-bills, the raw auction yield is not automatically the matched-horizon investment return. The return convention must define tenor selection, discount/yield conversion, reinvestment and horizon matching.

## Current state

The repository has authoritative source references but no benchmark series is yet approved. This is intentional and keeps the readiness gate blocked until actual historical observations are frozen.
