# Walk-Forward Validation

## Why session-based folds

The older calendar-day helper remains useful for simple infrastructure tests, but actual market validation should operate on **trading sessions**, not elapsed calendar days.

The session-based engine in `src/egx_quant/walkforward.py` therefore accepts an already validated exchange session calendar.

## Fold structure

Each fold contains:

```text
TRAIN | PURGE | VALIDATION | EMBARGO
```

The purge prevents labels close to the validation boundary from sharing forward information with validation.

The embargo delays the next development window where required.

## Label overlap

A date split alone is not enough for 20-session and 63-session forward targets.

Every training sample must store:
- feature as-of date,
- label end date.

Before a validation fold is evaluated, training samples whose label end date reaches the validation start are removed.

## Frozen development boundary

`build_development_folds` rejects any supplied session later than 2026-01-31.

The holdout therefore cannot accidentally enter development simply because a caller passed a larger calendar.

## Acceptance

The repository now includes an acceptance template, but its thresholds are intentionally null.

This means the code cannot declare a development model accepted until numerical gates are explicitly selected and committed.

Candidate gates include:
- mean Rank IC,
- fraction of dates with positive IC,
- one-way turnover,
- net-of-cost return,
- drawdown,
- a declared multiple-testing method,
- presence of the trial registry.

The exact threshold values must be frozen before the holdout is opened.

## Advanced statistics

PSR, DSR, PBO / CSCV and Reality Check-style controls remain part of the research plan.

They should only be implemented / interpreted when the development sample and experiment structure meet the assumptions required by the selected method. The project will not output a sophisticated-looking statistic merely because a formula is available.
