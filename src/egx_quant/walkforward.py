from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Iterable, Sequence

from .splits import DEVELOPMENT_END


@dataclass(frozen=True)
class SessionFold:
    fold_id: int
    train_sessions: tuple[date, ...]
    purge_sessions: tuple[date, ...]
    validation_sessions: tuple[date, ...]
    embargo_sessions: tuple[date, ...]

    @property
    def validation_start(self) -> date:
        return self.validation_sessions[0]

    @property
    def validation_end(self) -> date:
        return self.validation_sessions[-1]


@dataclass(frozen=True)
class LabeledSample:
    canonical_security_id: str
    as_of_date: date
    label_end_date: date


def _sorted_unique_sessions(sessions: Iterable[date]) -> tuple[date, ...]:
    ordered = tuple(sorted(set(sessions)))
    if not ordered:
        raise ValueError("at least one session is required")
    return ordered


def build_development_folds(
    sessions: Iterable[date],
    *,
    train_sessions: int,
    validation_sessions: int,
    purge_sessions: int,
    embargo_sessions: int = 0,
    expanding: bool = True,
) -> tuple[SessionFold, ...]:
    """Create deterministic session-based folds that never cross the dev freeze."""
    ordered = _sorted_unique_sessions(sessions)
    if ordered[-1] > DEVELOPMENT_END:
        raise RuntimeError("development fold input crosses frozen cutoff")
    if min(train_sessions, validation_sessions) <= 0:
        raise ValueError("train and validation lengths must be positive")
    if purge_sessions < 0 or embargo_sessions < 0:
        raise ValueError("purge and embargo lengths cannot be negative")

    folds: list[SessionFold] = []
    cursor = train_sessions
    fold_id = 1

    while True:
        purge_start = cursor
        validation_start = purge_start + purge_sessions
        validation_end = validation_start + validation_sessions
        embargo_end = validation_end + embargo_sessions

        if validation_end > len(ordered):
            break

        if expanding:
            train_slice = ordered[:cursor]
        else:
            train_slice = ordered[cursor - train_sessions : cursor]

        folds.append(
            SessionFold(
                fold_id=fold_id,
                train_sessions=tuple(train_slice),
                purge_sessions=tuple(ordered[purge_start:validation_start]),
                validation_sessions=tuple(ordered[validation_start:validation_end]),
                embargo_sessions=tuple(ordered[validation_end:min(embargo_end, len(ordered))]),
            )
        )

        if embargo_end >= len(ordered):
            break
        cursor = embargo_end
        fold_id += 1

    return tuple(folds)


def purge_overlapping_labels(
    samples: Sequence[LabeledSample],
    *,
    validation_start: date,
) -> tuple[LabeledSample, ...]:
    """Keep only training labels fully realized before validation begins."""
    return tuple(
        sample
        for sample in samples
        if sample.as_of_date < validation_start
        and sample.label_end_date < validation_start
    )
