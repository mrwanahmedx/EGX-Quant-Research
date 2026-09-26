from __future__ import annotations

from typing import Mapping, Any


def validate_frozen_evidence_manifest(manifest: Mapping[str, Any]) -> None:
    required = {
        "kind",
        "decision_time",
        "code_ref",
        "record_count",
        "eligible_record_count",
        "blocked_record_count",
        "data_evidence_fingerprint",
        "modeling_authorized",
    }
    missing = required - set(manifest)
    if missing:
        raise ValueError(f"manifest missing fields: {sorted(missing)}")
    if manifest["kind"] != "preholdout-data-evidence-manifest":
        raise ValueError("unexpected manifest kind")

    total = int(manifest["record_count"])
    eligible = int(manifest["eligible_record_count"])
    blocked = int(manifest["blocked_record_count"])
    if min(total, eligible, blocked) < 0:
        raise ValueError("manifest counts cannot be negative")
    if eligible + blocked != total:
        raise ValueError("eligible + blocked must equal total")

    fingerprint = str(manifest["data_evidence_fingerprint"])
    if len(fingerprint) < 16:
        raise ValueError("data evidence fingerprint is too short")

    expected_authorized = total > 0 and blocked == 0
    if bool(manifest["modeling_authorized"]) != expected_authorized:
        raise ValueError(
            "modeling_authorized is inconsistent with evidence counts"
        )


def assert_manifest_code_ref(
    manifest: Mapping[str, Any],
    expected_code_ref: str,
) -> None:
    if str(manifest.get("code_ref", "")) != expected_code_ref:
        raise RuntimeError(
            "frozen evidence manifest does not match the expected code reference"
        )
