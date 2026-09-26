from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping


REQUIRED_MANIFEST_FIELDS = {
    "experiment_id",
    "created_at",
    "code_ref",
    "data_fingerprint",
    "feature_set",
    "target",
    "split",
    "model",
    "seed",
    "cost_model",
}


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    ).encode("utf-8")


def fingerprint_records(records: Iterable[Mapping[str, Any]]) -> str:
    digest = hashlib.sha256()
    for record in records:
        digest.update(_canonical(record))
        digest.update(b"\n")
    return digest.hexdigest()


def build_manifest(
    *,
    experiment_id: str,
    code_ref: str,
    data_fingerprint: str,
    feature_set: str,
    target: str,
    split: str,
    model: str,
    seed: int,
    cost_model: Mapping[str, Any],
    params: Mapping[str, Any] | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    manifest = {
        "experiment_id": experiment_id,
        "created_at": created_at
        or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "code_ref": code_ref,
        "data_fingerprint": data_fingerprint,
        "feature_set": feature_set,
        "target": target,
        "split": split,
        "model": model,
        "params": dict(params or {}),
        "seed": int(seed),
        "cost_model": dict(cost_model),
    }
    missing = REQUIRED_MANIFEST_FIELDS - manifest.keys()
    if missing:
        raise ValueError(f"manifest missing fields: {sorted(missing)}")
    if len(data_fingerprint) < 16:
        raise ValueError("data fingerprint is too short")
    return manifest
