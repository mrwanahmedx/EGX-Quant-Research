from __future__ import annotations

from datetime import datetime
from typing import Iterable, Mapping, Any

from .evidence import (
    DataEvidenceRecord,
    QuarantineRange,
    assert_evidence_grain,
    evidence_fingerprint,
    evidence_is_model_eligible,
)
from .manifest_validation import validate_frozen_evidence_manifest


def freeze_preholdout_evidence_manifest(
    records: Iterable[DataEvidenceRecord],
    *,
    decision_time: datetime,
    code_ref: str,
    quarantines: Iterable[QuarantineRange] = (),
) -> dict[str, Any]:
    records = tuple(records)
    quarantines = tuple(quarantines)
    assert_evidence_grain(records)

    eligible = [
        record
        for record in records
        if evidence_is_model_eligible(
            record,
            decision_time=decision_time,
            quarantines=quarantines,
        )
    ]
    blocked = len(records) - len(eligible)

    manifest = {
        "kind": "preholdout-data-evidence-manifest",
        "decision_time": decision_time.isoformat(),
        "code_ref": code_ref,
        "record_count": len(records),
        "eligible_record_count": len(eligible),
        "blocked_record_count": blocked,
        "data_evidence_fingerprint": evidence_fingerprint(records),
        "modeling_authorized": bool(records) and blocked == 0,
    }
    validate_frozen_evidence_manifest(manifest)
    return manifest


def require_frozen_manifest_authorized(manifest: Mapping[str, Any]) -> None:
    try:
        validate_frozen_evidence_manifest(manifest)
    except (TypeError, ValueError, KeyError) as exc:
        raise RuntimeError(
            "frozen data-evidence manifest is invalid and cannot authorize modeling"
        ) from exc
    if not manifest.get("modeling_authorized", False):
        raise RuntimeError(
            "real modeling is not authorized by the frozen data-evidence manifest"
        )
