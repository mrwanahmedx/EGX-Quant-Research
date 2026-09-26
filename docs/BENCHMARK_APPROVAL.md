# Benchmark Approval

Freezing a historical benchmark series and approving it for model comparison are separate actions.

## Why

A reproducible file can still be the wrong benchmark if:
- it uses price return where total return was intended,
- the source does not match the catalog,
- the return convention is inappropriate,
- the methodology is not evidenced,
- a revised series has silently replaced the frozen snapshot.

## Approval requirements

The approval guard checks:

1. benchmark ID matches the frozen series manifest,
2. source ID matches the benchmark catalog,
3. source has an approved benchmark role,
4. methodology is already evidenced in the catalog,
5. a human/research review explicitly confirms:
   - methodology,
   - source snapshot,
   - return convention,
6. the exact series fingerprint is copied into the benchmark catalog,
7. a separate approval-review artifact is written.

## Command

After a real benchmark series has been frozen and reviewed:

```bash
python scripts/approve_benchmark.py \
  --benchmark-id conia \
  --manifest evidence/benchmarks/conia.json \
  --manifest-ref evidence/benchmarks/conia.json \
  --reviewer REVIEWER_NAME \
  --review-output evidence/benchmarks/conia.approval.json \
  --confirm-methodology \
  --confirm-source-snapshot \
  --confirm-return-convention
```

Omitting any confirmation causes approval to fail.

## Current state

No benchmark is currently approved. This document does not authorize changing that state without an actual frozen historical series and documented review.
