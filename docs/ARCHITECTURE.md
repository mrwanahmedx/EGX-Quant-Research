# Architecture

## Layers

### 1. Source layer
Immutable local snapshots from public data providers.

### 2. Identity layer
Maps provider symbols to a stable canonical security ID with effective dates and confidence.

### 3. QA / evidence layer
Checks:
- OHLC geometry,
- duplicate grain,
- continuity,
- corporate actions,
- source-vintage conflicts,
- point-in-time eligibility.

Failed observations remain quarantined.

### 4. Research panel
Only QA-passed, provenance-bearing observations are promoted to the panel used by feature generation.

### 5. Feature / target layer
Produces lagged Alpha158-inspired and EGX-relative features plus 20d / 63d residual-return targets.

### 6. Development layer
Runs purged walk-forward folds and writes an immutable experiment manifest and trial-registry entry.

### 7. Portfolio layer
Converts rankings into Top-K / dropout candidates with sector/beta controls and transaction costs.

### 8. Acceptance layer
Aggregates stability, multiple-testing, turnover and benchmark evidence.

### 9. Holdout / shadow
The holdout is one-shot. Shadow testing is versioned forward evidence after the frozen research generation.

## Separation of concerns

The repository intentionally keeps:
- data truth separate from model logic,
- development separate from holdout,
- research metrics separate from execution assumptions,
- model families separate in the registry,
- raw evidence separate from cleaned panels.

This makes it harder for a convenient backtest result to silently change the data contract.
