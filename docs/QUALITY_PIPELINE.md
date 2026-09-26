# Market-Data Quality Pipeline

## Principle

The QA layer identifies problems. It does **not** manufacture repairs.

An invalid or conflicting market row is:
- retained in the raw snapshot,
- flagged,
- quarantined when required,
- reconciled through explicit evidence.

It is never silently clipped into a valid OHLC range.

## Structural checks

The current QA module detects:
- non-finite OHLCV values,
- negative prices,
- negative volume,
- low above high,
- open outside the daily range,
- close outside the daily range,
- duplicate security/date/source grain.

These conditions are deterministic and do not require a statistical threshold.

## Discontinuities

Large close-to-close moves are **review flags**, not automatic proof of corruption.

The threshold is supplied explicitly by the calling research run and recorded in its manifest.

A discontinuity can reflect:
- a real market move,
- split / reverse split,
- stock dividend,
- rights issue,
- ticker / corporate restructuring,
- incompatible adjusted vs raw history,
- source error.

Corporate-action evidence is therefore checked before a large move is quarantined as erroneous.

## Cross-source conflicts

When two sources cover the same canonical security/date, price fields can be compared using a predeclared relative tolerance.

A conflict:
1. preserves both raw records,
2. identifies the fields that disagree,
3. enters the reconciliation workflow,
4. does not select a winner merely because one source is newer.

## Corporate actions and targets

A forward-return target crossing an unresolved corporate action is blocked.

A resolved action must record the adjustment basis used by the research panel.

This prevents a split or rights event from appearing as model alpha or an enormous negative return because two incompatible price bases were mixed.

## Reproducing the historical audit

Once the original source snapshots are recovered locally:

```bash
python scripts/profile_ohlcv.py canonical_source.csv \
  --discontinuity-threshold 0.30 \
  --output artifacts/qa/source-profile.json
```

The original 30% audit threshold is preserved in the historical reconciliation record; it is not hard-coded as a universal truth in the library.

## Promotion rule

Rows move into a frozen research panel only after:
- structural QA,
- duplicate-grain resolution,
- source reconciliation where needed,
- corporate-action resolution,
- quarantine application,
- point-in-time identity / universe checks.

The model layer cannot override this decision.
