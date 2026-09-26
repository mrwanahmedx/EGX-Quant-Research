from __future__ import annotations

import csv
import json
import shutil
from datetime import date, datetime
from pathlib import Path
from typing import Iterable

from .io import load_quarantine_csv, load_security_master_json
from .splits import DEVELOPMENT_END


def validate_exact_quarantine_register(
    source_path: str | Path,
    *,
    expected_count: int,
    development_end: date = DEVELOPMENT_END,
) -> tuple[object, ...]:
    rows = load_quarantine_csv(source_path)
    if len(rows) != expected_count:
        raise ValueError(
            f"expected {expected_count} quarantine ranges, got {len(rows)}"
        )
    ids = [row.quarantine_id for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate quarantine IDs")
    for row in rows:
        if not row.quarantine_id.strip():
            raise ValueError("blank quarantine ID")
        if row.end_date > development_end:
            raise ValueError(
                f"quarantine range {row.quarantine_id} crosses frozen "
                f"development cutoff {development_end}"
            )
        if row.disposition == "accepted_source_override" and not row.accepted_source:
            raise ValueError(
                f"{row.quarantine_id} accepts a source override without "
                "accepted_source"
            )
        if row.disposition == "quarantine" and not row.evidence_ref.strip():
            raise ValueError(f"{row.quarantine_id} has no evidence reference")
    return rows


def import_exact_quarantine_register(
    source_path: str | Path,
    destination_path: str | Path,
    *,
    expected_count: int,
) -> tuple[object, ...]:
    rows = validate_exact_quarantine_register(
        source_path,
        expected_count=expected_count,
    )
    destination = Path(destination_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source_path, destination)
    # Re-read the copied artifact so the destination bytes, not only the input,
    # are proven parseable.
    copied = validate_exact_quarantine_register(
        destination,
        expected_count=expected_count,
    )
    if copied != rows:
        raise RuntimeError("copied quarantine register changed during import")
    return copied


def validate_preholdout_security_master(
    source_path: str | Path,
    *,
    decision_time: datetime,
) -> tuple[object, ...]:
    rows = load_security_master_json(source_path)
    if not rows:
        raise ValueError("security master is empty")

    seen: set[tuple[str, str, date]] = set()
    for row in rows:
        key = (row.canonical_security_id, row.symbol, row.effective_from)
        if key in seen:
            raise ValueError(f"duplicate security-master grain: {key}")
        seen.add(key)

        if row.published_at > decision_time:
            raise ValueError(
                f"{row.symbol} mapping was published after the pre-holdout "
                "decision time"
            )
        if row.effective_from > DEVELOPMENT_END:
            raise ValueError(
                f"{row.symbol} mapping starts after the development cutoff"
            )
        if row.sector_published_at is not None and row.sector_published_at > decision_time:
            raise ValueError(
                f"{row.symbol} sector evidence was published after the "
                "pre-holdout decision time"
            )
        if row.mapping_confidence == "unresolved":
            raise ValueError(
                f"{row.symbol} has unresolved mapping confidence and cannot "
                "enter the frozen security master"
            )

    return rows


def import_preholdout_security_master(
    source_path: str | Path,
    destination_path: str | Path,
    *,
    decision_time: datetime,
) -> tuple[object, ...]:
    rows = validate_preholdout_security_master(
        source_path,
        decision_time=decision_time,
    )
    destination = Path(destination_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    parsed = json.loads(Path(source_path).read_text(encoding="utf-8"))
    destination.write_text(
        json.dumps(parsed, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    copied = validate_preholdout_security_master(
        destination,
        decision_time=decision_time,
    )
    if copied != rows:
        raise RuntimeError("security master changed during canonical import")
    return copied


def update_reconciliation_import_state(
    summary_path: str | Path,
    *,
    exact_quarantine_register_committed: bool,
) -> dict[str, object]:
    path = Path(summary_path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["exact_quarantine_register_committed"] = bool(
        exact_quarantine_register_committed
    )
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return payload
