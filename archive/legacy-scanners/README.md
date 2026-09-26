# Legacy EGX Scanner Archive

This archive preserves the scanner generations that preceded the current research framework. Failed, blocked and superseded approaches are intentionally retained as model-development evidence rather than erased.

## Version index

| Version | Artifact state | Test evidence | Final status | Why archived |
| --- | --- | ---: | --- | --- |
| V1 | History only | Not independently recovered | DISCONTINUED / SUPERSEDED | Early foundation; source artifact not found in accessible saved files |
| V1.1 | Recovered sanitized source | **3 passed** on archival rerun | DISCONTINUED — NOT ELIGIBLE FOR DEPLOYMENT | Stale/illustrative inputs and incomplete live-data adapters |
| V1.2 | Recovered sanitized source | **5 passed** on archival rerun | DISCONTINUED — NOT ELIGIBLE FOR DEPLOYMENT | Price ingestion improved, but fundamentals/catalysts and point-in-time evidence remained incomplete |
| V1.2-fixed | History only | Historical record: 6 tests | DISCONTINUED / SUPERSEDED | Hardened missing/stale-data behavior; later architecture replaced it |
| V2 | History only | Not independently recovered | DISCONTINUED / SUPERSEDED | Broader structured scanner generation; replaced by evidence-focused versions |
| V2.1 | History only | Historical record: 9 tests | DISCONTINUED — DATA BLOCKED | Incomplete market/fundamental coverage |
| V2.2 | History only | Historical record: 11 tests | DISCONTINUED — PARTIAL EVIDENCE | Coverage improved but remained too narrow for broad eligibility claims |
| V2.3 | History only | Historical record: 16 tests | DISCONTINUED / SUPERSEDED | Event Intelligence generation; later historical-validation work superseded it |
| V2.4 | History only | Historical record: 19 tests | DISCONTINUED — FAILED HISTORICAL-VALIDATION ELIGIBILITY | Point-in-time evidence was insufficient to claim historical validation |

## Preservation rules

- Recovered V1.1 and V1.2 code is kept as browsable source rather than rewritten into modern style.
- User-specific portfolio inputs and generated working databases are **not public**. Their hashes are recorded beside the recovered source so omission is explicit and auditable.
- Cache files and generated Python bytecode are not retained.
- Missing V1/V1.2-fixed/V2–V2.4 source is **not reconstructed or fabricated**. Those directories preserve verified project history only.
- Passing legacy unit tests demonstrate code mechanics, not validated alpha, profitability or production readiness.
- The active project at repository root is a separate later research framework and remains subject to its current QA/evidence gates.
