from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from math import isfinite
from typing import Iterable


@dataclass(frozen=True)
class OHLCVRecord:
    canonical_security_id: str
    session_date: date
    open: float
    high: float
    low: float
    close: float
    volume: float
    source: str


@dataclass(frozen=True)
class QualityIssue:
    canonical_security_id: str
    session_date: date
    source: str
    issue_type: str
    details: str


@dataclass(frozen=True)
class DiscontinuityFlag:
    canonical_security_id: str
    previous_date: date
    session_date: date
    source: str
    previous_close: float
    current_close: float
    absolute_return: float


def bar_issues(record: OHLCVRecord) -> tuple[QualityIssue, ...]:
    issues: list[QualityIssue] = []
    values = (record.open, record.high, record.low, record.close, record.volume)
    if not all(isfinite(v) for v in values):
        issues.append(
            QualityIssue(
                record.canonical_security_id,
                record.session_date,
                record.source,
                "non_finite_value",
                "one or more OHLCV values are non-finite",
            )
        )
        return tuple(issues)

    if min(record.open, record.high, record.low, record.close) < 0:
        issues.append(
            QualityIssue(
                record.canonical_security_id,
                record.session_date,
                record.source,
                "negative_price",
                "one or more price fields are negative",
            )
        )
    if record.volume < 0:
        issues.append(
            QualityIssue(
                record.canonical_security_id,
                record.session_date,
                record.source,
                "negative_volume",
                "volume is negative",
            )
        )
    if record.low > record.high:
        issues.append(
            QualityIssue(
                record.canonical_security_id,
                record.session_date,
                record.source,
                "low_above_high",
                "low exceeds high",
            )
        )
    if record.low > record.open or record.open > record.high:
        issues.append(
            QualityIssue(
                record.canonical_security_id,
                record.session_date,
                record.source,
                "open_outside_range",
                "open is outside [low, high]",
            )
        )
    if record.low > record.close or record.close > record.high:
        issues.append(
            QualityIssue(
                record.canonical_security_id,
                record.session_date,
                record.source,
                "close_outside_range",
                "close is outside [low, high]",
            )
        )
    return tuple(issues)


def duplicate_grain_issues(
    records: Iterable[OHLCVRecord],
) -> tuple[QualityIssue, ...]:
    seen: set[tuple[str, date, str]] = set()
    issues: list[QualityIssue] = []
    for record in records:
        key = (
            record.canonical_security_id,
            record.session_date,
            record.source,
        )
        if key in seen:
            issues.append(
                QualityIssue(
                    record.canonical_security_id,
                    record.session_date,
                    record.source,
                    "duplicate_source_grain",
                    "multiple rows exist for security/date/source",
                )
            )
        seen.add(key)
    return tuple(issues)


def profile_quality(records: Iterable[OHLCVRecord]) -> dict[str, object]:
    records = tuple(records)
    row_issues = tuple(
        issue
        for record in records
        for issue in bar_issues(record)
    )
    duplicates = duplicate_grain_issues(records)
    all_issues = row_issues + duplicates
    by_type: dict[str, int] = {}
    for issue in all_issues:
        by_type[issue.issue_type] = by_type.get(issue.issue_type, 0) + 1
    affected = {
        (issue.canonical_security_id, issue.session_date, issue.source)
        for issue in all_issues
    }
    return {
        "record_count": len(records),
        "issue_count": len(all_issues),
        "affected_source_grain_count": len(affected),
        "issue_counts": dict(sorted(by_type.items())),
    }


def detect_close_discontinuities(
    records: Iterable[OHLCVRecord],
    *,
    absolute_return_threshold: float,
) -> tuple[DiscontinuityFlag, ...]:
    if absolute_return_threshold <= 0:
        raise ValueError("discontinuity threshold must be positive")

    grouped: dict[tuple[str, str], list[OHLCVRecord]] = {}
    for record in records:
        grouped.setdefault(
            (record.canonical_security_id, record.source),
            [],
        ).append(record)

    flags: list[DiscontinuityFlag] = []
    for (security_id, source), rows in grouped.items():
        rows.sort(key=lambda row: row.session_date)
        for previous, current in zip(rows, rows[1:]):
            if previous.close <= 0:
                continue
            move = current.close / previous.close - 1.0
            if abs(move) >= absolute_return_threshold:
                flags.append(
                    DiscontinuityFlag(
                        canonical_security_id=security_id,
                        previous_date=previous.session_date,
                        session_date=current.session_date,
                        source=source,
                        previous_close=previous.close,
                        current_close=current.close,
                        absolute_return=abs(move),
                    )
                )
    return tuple(flags)


def overlap_conflicts(
    left: Iterable[OHLCVRecord],
    right: Iterable[OHLCVRecord],
    *,
    relative_tolerance: float,
) -> tuple[QualityIssue, ...]:
    if relative_tolerance < 0:
        raise ValueError("relative tolerance cannot be negative")

    right_by_key = {
        (row.canonical_security_id, row.session_date): row
        for row in right
    }
    issues: list[QualityIssue] = []

    for row in left:
        other = right_by_key.get(
            (row.canonical_security_id, row.session_date)
        )
        if other is None:
            continue
        comparisons = {
            "open": (row.open, other.open),
            "high": (row.high, other.high),
            "low": (row.low, other.low),
            "close": (row.close, other.close),
        }
        conflict_fields = []
        for field, (a, b) in comparisons.items():
            scale = max(abs(a), abs(b), 1e-12)
            if abs(a - b) / scale > relative_tolerance:
                conflict_fields.append(field)
        if conflict_fields:
            issues.append(
                QualityIssue(
                    row.canonical_security_id,
                    row.session_date,
                    f"{row.source}|{other.source}",
                    "overlap_price_conflict",
                    "fields exceed tolerance: " + ",".join(conflict_fields),
                )
            )
    return tuple(issues)
