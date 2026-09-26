from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Iterable, Mapping

from .evidence import (
    DataEvidenceRecord,
    QuarantineRange,
    assert_evidence_grain,
    evidence_is_model_eligible,
)
from .splits import DEVELOPMENT_END


@dataclass(frozen=True)
class PanelRow:
    canonical_security_id: str
    session_date: date
    values: Mapping[str, object]


def build_development_panel(
    rows: Iterable[PanelRow],
    evidence_records: Iterable[DataEvidenceRecord],
    *,
    decision_time: datetime,
    quarantines: Iterable[QuarantineRange] = (),
) -> tuple[PanelRow, ...]:
    rows = tuple(rows)
    evidence_records = tuple(evidence_records)
    quarantines = tuple(quarantines)
    assert_evidence_grain(evidence_records)

    evidence_by_key = {
        (e.canonical_security_id, e.session_date): e
        for e in evidence_records
    }

    output: list[PanelRow] = []
    seen: set[tuple[str, date]] = set()

    for row in rows:
        key = (row.canonical_security_id, row.session_date)
        if key in seen:
            raise ValueError(f"duplicate panel grain: {key}")
        seen.add(key)

        if row.session_date > DEVELOPMENT_END:
            raise RuntimeError("development panel attempted to cross frozen cutoff")

        evidence = evidence_by_key.get(key)
        if evidence is None:
            raise RuntimeError(f"missing evidence record for panel row: {key}")

        if evidence_is_model_eligible(
            evidence,
            decision_time=decision_time,
            quarantines=quarantines,
        ):
            output.append(row)

    return tuple(output)
