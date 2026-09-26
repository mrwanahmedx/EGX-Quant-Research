# Changelog

## 0.2.0 - 2026-09-26

### Added
- Legacy scanner archive with explicit version-by-version lifecycle status.
- Sanitized, browsable recovered source for V1.1 and V1.2.
- Archival test reruns: V1.1 **3 passed**; V1.2 **5 passed**.
- Hash records for omitted user-specific portfolio and working-database artifacts.
- History-only records for V1, V1.2-fixed and V2–V2.4 where exact source artifacts were not recoverable.

### Integrity
- Missing legacy source is not reconstructed or fabricated.
- Every legacy generation is marked discontinued / superseded / blocked according to the available evidence.
- The active quantitative-research framework remains separate and subject to its current QA/evidence gates.

## 0.1.0 - 2026-09-26

### Added
- Research-first repository architecture.
- Immutable development / holdout / shadow date contract.
- OHLC and duplicate-grain validation helpers.
- Point-in-time publication checks.
- Transaction-cost model.
- Deterministic experiment manifests and fingerprints.
- Evidence gates that block modeling when source evidence is incomplete.
- CI checks and unit tests.
- Documentation of the current real-data QA failure and remediation roadmap.

### Status
No real EGX model has been accepted or promoted. Real holdout evaluation remains blocked by data-evidence gates.
