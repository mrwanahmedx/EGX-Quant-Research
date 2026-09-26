# Benchmarks and Shadow Ledger

## Benchmarks

A benchmark is not accepted merely because its name appears in the research protocol.

The machine-readable catalog in `config/benchmark_catalog.json` tracks:
- methodology evidence,
- whether the historical series is frozen,
- the series fingerprint,
- whether the benchmark is approved for model comparison.

The current catalog intentionally approves **zero** benchmarks because the historical series artifacts have not yet been frozen in the repository evidence layer.

This prevents a model report from quietly switching between:
- price return and total return,
- revised and unrevised histories,
- different cash-rate conventions,
- different fixed-income horizons.

## Fixed-income comparison

An Egyptian T-bill or overnight-rate comparator must use a return convention matched to the model holding horizon.

An annual quoted yield is not directly compared with a 20-session or 63-session equity return without converting the cash-flow / compounding convention.

The repository does not currently freeze a T-bill or CONIA history, so those comparisons remain blocked.

## Shadow ledger

The prediction-ledger schema records information at prediction time:
- model ID,
- security ID,
- decision timestamp,
- score and rank,
- target horizon,
- source vintage,
- data fingerprint,
- execution convention.

Realized outcomes are attached later and must have an observation timestamp strictly after the decision timestamp.

The ledger is deliberately separated from live brokerage execution. It is a research audit trail, not an order-routing system.

## Why this matters

Without a prediction ledger, a forward test can silently become hindsight:
- predictions can be edited after the session,
- ranks can be recomputed with revised inputs,
- failed names can disappear,
- source vintages can change.

An append-only ledger plus frozen fingerprints prevents those behaviors from being mistaken for genuine forward evidence.
