from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

from .acceptance import AcceptanceThresholds


def _validate_threshold_ranges(thresholds: AcceptanceThresholds) -> None:
    if not thresholds.frozen:
        raise ValueError("all acceptance thresholds must be populated before freeze")
    if not -1 <= float(thresholds.min_mean_rank_ic) <= 1:
        raise ValueError("min_mean_rank_ic must be between -1 and 1")
    if not 0 <= float(thresholds.min_positive_ic_fraction) <= 1:
        raise ValueError("min_positive_ic_fraction must be between 0 and 1")
    if not 0 <= float(thresholds.max_one_way_turnover) <= 1:
        raise ValueError("max_one_way_turnover must be between 0 and 1")
    if not 0 <= float(thresholds.max_drawdown_abs) <= 1:
        raise ValueError("max_drawdown_abs must be between 0 and 1")
    if not str(thresholds.multiple_testing_method).strip():
        raise ValueError("multiple_testing_method is required")


def freeze_acceptance_thresholds(
    thresholds: AcceptanceThresholds,
    *,
    code_ref: str,
    development_evidence_ref: str,
    rationale: str,
    holdout_unopened: bool,
    frozen_at: str | None = None,
) -> dict[str, Any]:
    _validate_threshold_ranges(thresholds)

    if not code_ref.strip():
        raise ValueError("code_ref is required")
    if not development_evidence_ref.strip():
        raise ValueError("development_evidence_ref is required")
    if len(rationale.strip()) < 20:
        raise ValueError("rationale is too short to document a pre-holdout decision")
    if not holdout_unopened:
        raise RuntimeError(
            "acceptance thresholds cannot be frozen after inspecting the holdout"
        )

    payload = {
        "status": "frozen",
        "frozen_at": frozen_at
        or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "code_ref": code_ref,
        "development_evidence_ref": development_evidence_ref,
        "holdout_unopened": True,
        "thresholds": {
            "min_mean_rank_ic": thresholds.min_mean_rank_ic,
            "min_positive_ic_fraction": thresholds.min_positive_ic_fraction,
            "max_one_way_turnover": thresholds.max_one_way_turnover,
            "min_net_return": thresholds.min_net_return,
            "max_drawdown_abs": thresholds.max_drawdown_abs,
        },
        "multiple_testing_method": thresholds.multiple_testing_method,
        "trial_registry_required": thresholds.trial_registry_required,
        "rationale": rationale.strip(),
        "note": (
            "Frozen from development reasoning before one-shot holdout evaluation."
        ),
    }
    validate_frozen_acceptance_payload(payload)
    return payload


def validate_frozen_acceptance_payload(payload: Mapping[str, Any]) -> None:
    required = {
        "status",
        "frozen_at",
        "code_ref",
        "development_evidence_ref",
        "holdout_unopened",
        "thresholds",
        "multiple_testing_method",
        "trial_registry_required",
        "rationale",
    }
    missing = required - set(payload)
    if missing:
        raise ValueError(f"frozen acceptance payload missing fields: {sorted(missing)}")
    if payload["status"] != "frozen":
        raise ValueError("acceptance payload status must be frozen")
    if payload["holdout_unopened"] is not True:
        raise RuntimeError("holdout_unopened must be true")
    threshold_map = payload["thresholds"]
    thresholds = AcceptanceThresholds(
        min_mean_rank_ic=threshold_map.get("min_mean_rank_ic"),
        min_positive_ic_fraction=threshold_map.get("min_positive_ic_fraction"),
        max_one_way_turnover=threshold_map.get("max_one_way_turnover"),
        min_net_return=threshold_map.get("min_net_return"),
        max_drawdown_abs=threshold_map.get("max_drawdown_abs"),
        multiple_testing_method=payload.get("multiple_testing_method"),
        trial_registry_required=bool(payload.get("trial_registry_required", True)),
    )
    _validate_threshold_ranges(thresholds)
    if len(str(payload["rationale"]).strip()) < 20:
        raise ValueError("rationale is too short")
