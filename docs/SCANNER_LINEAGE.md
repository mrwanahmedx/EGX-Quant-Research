# Scanner and Research Lineage

This repository is the continuation of a longer EGX research process. The purpose of this document is to preserve the lessons from earlier scanner generations without pretending that older experiments were more validated than they were.

## V1 / V1.1 / V1.2

Early scanner work focused on basic market history, technical scoring and portfolio actions.

The important lesson from this stage was negative: synthetic price fallback was unsafe for real recommendations and was removed. Missing or stale market evidence became a HOLD / WATCH condition rather than a reason to fabricate continuity.

V1.2-fixed had:
- real histories where available,
- missing/stale evidence gates,
- no fake backtest,
- six tests.

## V2

The scanner moved toward a structured research system with:
- provider refresh,
- scoring,
- allocation logic,
- reporting,
- SQLite logging,
- separate Core / Active concepts,
- safe gates preventing unsupported BUY / ADD actions.

## V2.1

Data provenance became more explicit:
- live OHLCV coverage improved,
- unresolved symbols were tracked rather than silently replaced,
- official EGX disclosures were introduced,
- verified fundamentals were still incomplete,
- nine tests were in place.

## V2.2

The scanner added:
- verified fundamentals for a small subset,
- explicit point-price and OHLCV coverage tracking,
- fund-NAV treatment separate from stocks,
- provenance, freshness, units, source tier and lineage,
- sector-specific schemas,
- 11 tests.

## V2.3 — Event Intelligence

This generation added:
- bilingual event processing,
- provenance / reliability / classification,
- materiality, novelty and contagion logic,
- price / volume reaction,
- breadth and regime checks,
- liquidity anomalies,
- corporate-action classification,
- RSS discovery,
- event-to-security mapping,
- 16 tests.

A key rule was established: **news alone cannot authorize a BUY / ADD**.

## V2.4 — Historical Validation

Historical validation added:
- point-in-time storage rules,
- revision controls,
- next-session execution,
- realistic costs,
- event horizons,
- benchmark gates,
- future-information and revision-leakage tests.

The correct verdict was **partial — not historically validated** because publication-time fundamentals, historical events, release-dated macro, portfolio snapshots, corporate actions, total-return benchmarks and fixed-income benchmarks were not complete enough.

This was the point where the project deliberately stopped treating the scanner as a normal stock screener and started treating it as a model-validation problem.

## Quant-research transition

The current repository formalizes that transition.

The active research design now emphasizes:
- point-in-time universe reconstruction,
- frozen development through 2026-01-31,
- untouched February-June 2026 holdout,
- September 2026 shadow testing,
- 20d / 63d residual-return targets,
- Alpha158 / Qlib-inspired features,
- transparent baselines before tree challengers,
- purged walk-forward development,
- experiment and trial registries,
- net-of-cost portfolio evaluation,
- statistical acceptance controls,
- hard stop when evidence is incomplete.

## Current status

The project currently remains blocked at the real-data QA / evidence layer.

That is not a failed engineering outcome. It is the expected behavior of a system designed not to turn unresolved source problems into a polished backtest.
