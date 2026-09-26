from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Iterable, Mapping

from .evidence_manifest import require_frozen_manifest_authorized
from .manifest import fingerprint_records
from .panel import PanelRow
from .splits import DEVELOPMENT_END


def panel_fingerprint(rows: Iterable[PanelRow]) -> str:
    serialised = []
    for row in sorted(rows, key=lambda r: (r.session_date, r.canonical_security_id)):
        serialised.append({
            "canonical_security_id": row.canonical_security_id,
            "session_date": row.session_date.isoformat(),
            "values": dict(sorted(row.values.items())),
        })
    return fingerprint_records(serialised)


def validate_frozen_development_panel_manifest(
    manifest: Mapping[str, Any],
) -> None:
    required = {
        "kind","created_at","code_ref","row_count","security_count",
        "first_session","last_session","panel_fingerprint","evidence_fingerprint",
        "evidence_manifest_code_ref","development_cutoff",
        "authorized_for_model_development",
    }
    missing = required - set(manifest)
    if missing:
        raise ValueError(f"development panel manifest missing fields: {sorted(missing)}")
    if manifest["kind"] != "frozen-development-panel-manifest":
        raise ValueError("unexpected development panel manifest kind")
    if int(manifest["row_count"]) <= 0:
        raise ValueError("development panel row_count must be positive")
    if int(manifest["security_count"]) <= 0:
        raise ValueError("development panel security_count must be positive")
    if str(manifest["development_cutoff"]) != DEVELOPMENT_END.isoformat():
        raise ValueError("development cutoff does not match repository contract")
    if str(manifest["last_session"]) > DEVELOPMENT_END.isoformat():
        raise ValueError("development panel crosses the frozen cutoff")
    if len(str(manifest["panel_fingerprint"])) < 16:
        raise ValueError("panel fingerprint is too short")
    if len(str(manifest["evidence_fingerprint"])) < 16:
        raise ValueError("evidence fingerprint is too short")
    if not bool(manifest["authorized_for_model_development"]):
        raise ValueError("development panel manifest is not authorized")


def freeze_development_panel_manifest(
    rows: Iterable[PanelRow],
    *,
    frozen_evidence_manifest: Mapping[str, Any],
    code_ref: str,
    created_at: str | None = None,
) -> dict[str, Any]:
    rows = tuple(rows)
    if not rows:
        raise ValueError("cannot freeze an empty development panel")
    require_frozen_manifest_authorized(frozen_evidence_manifest)

    seen: set[tuple[str, object]] = set()
    for row in rows:
        key = (row.canonical_security_id, row.session_date)
        if key in seen:
            raise ValueError(f"duplicate development panel grain: {key}")
        seen.add(key)
        if row.session_date > DEVELOPMENT_END:
            raise RuntimeError("development panel crosses frozen cutoff")

    sessions = sorted(row.session_date for row in rows)
    securities = {row.canonical_security_id for row in rows}
    manifest = {
        "kind": "frozen-development-panel-manifest",
        "created_at": created_at or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "code_ref": code_ref,
        "row_count": len(rows),
        "security_count": len(securities),
        "first_session": sessions[0].isoformat(),
        "last_session": sessions[-1].isoformat(),
        "panel_fingerprint": panel_fingerprint(rows),
        "evidence_fingerprint": frozen_evidence_manifest["data_evidence_fingerprint"],
        "evidence_manifest_code_ref": frozen_evidence_manifest["code_ref"],
        "development_cutoff": DEVELOPMENT_END.isoformat(),
        "authorized_for_model_development": True,
    }
    validate_frozen_development_panel_manifest(manifest)
    return manifest


def require_panel_matches_evidence(
    panel_manifest: Mapping[str, Any],
    evidence_manifest: Mapping[str, Any],
) -> None:
    validate_frozen_development_panel_manifest(panel_manifest)
    require_frozen_manifest_authorized(evidence_manifest)
    if panel_manifest["evidence_fingerprint"] != evidence_manifest["data_evidence_fingerprint"]:
        raise RuntimeError("development panel fingerprint is linked to different evidence")
    if panel_manifest["evidence_manifest_code_ref"] != evidence_manifest["code_ref"]:
        raise RuntimeError("development panel is linked to a different evidence code ref")
