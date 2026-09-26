# Data Contract

## Core principle

A row is not trustworthy merely because it exists in a CSV.

Every observation entering research must carry enough information to answer:

**What was known, for which security, from which source, and when?**

## Canonical OHLCV grain

One row per:

```text
canonical_security_id × trading_date × source_vintage
```

Minimum fields:

| Field | Requirement |
| --- | --- |
| canonical_security_id | stable internal identifier |
| symbol | source symbol |
| trading_date | exchange-local session date |
| open/high/low/close | numeric, same price basis |
| volume | non-negative |
| source | provider / dataset |
| source_vintage | snapshot or retrieval version |
| observed_at | when the record became available |
| adjustment_basis | raw / split-adjusted / total-return etc. |
| qa_status | pass / quarantine / rejected |

## Bar geometry

For an ordinary daily bar:

```text
low <= open <= high
low <= close <= high
volume >= 0
```

Rows violating the contract are quarantined. They are not clipped into range.

## Duplicate policy

No downstream dataset may silently contain multiple rows for the intended grain.

Duplicate resolution requires:
- source priority,
- exact conflict fields,
- selected record,
- reason,
- provenance of the discarded record.

## Point-in-time fields

The following require effective / publication dates:
- index membership,
- sector,
- corporate actions,
- issuer fundamentals,
- macro data,
- event labels.

A current classification without historical effective dates is not valid historical evidence.

## Corporate actions

Price histories must explicitly document treatment of:
- cash dividends,
- stock dividends,
- splits / reverse splits,
- rights issues,
- ticker changes,
- mergers / restructurings,
- long suspensions.

Never mix raw and adjusted OHLC fields within one bar.

## Source conflicts

When sources disagree:
1. preserve both raw observations,
2. run geometry / continuity / corporate-action checks,
3. compare against an independent reference if available,
4. create an auditable resolution record,
5. quarantine if unresolved.

## Missing data

Missing evidence is not replaced with fabricated or synthetic market data in the real-data pipeline.

The correct state is **missing / blocked**.
