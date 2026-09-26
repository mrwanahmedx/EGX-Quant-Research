from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Any

from .gates import DataEvidence, require_modeling_allowed


SUPPORTED_FAMILIES = {
    "linear",
    "lasso",
    "lightgbm",
    "xgboost_ranker",
    "catboost",
}


@dataclass(frozen=True)
class ModelSpec:
    family: str
    target: str
    feature_set: str
    params: Mapping[str, Any]


def validate_model_spec(spec: ModelSpec) -> None:
    if spec.family not in SUPPORTED_FAMILIES:
        raise ValueError(f"unsupported model family: {spec.family}")
    if spec.target not in {"residual_return_20d", "residual_return_63d"}:
        raise ValueError(f"unsupported target: {spec.target}")
    if not spec.feature_set.strip():
        raise ValueError("feature set is required")


def authorize_training(spec: ModelSpec, evidence: DataEvidence) -> None:
    """Validate spec and fail closed when data evidence is incomplete."""
    validate_model_spec(spec)
    require_modeling_allowed(evidence)
