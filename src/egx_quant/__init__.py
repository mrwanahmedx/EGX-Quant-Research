"""Core research controls for EGX Quant Research."""

from .contracts import Bar, ContractError, validate_bar, assert_unique
from .costs import ExecutionCostModel
from .evidence import (
    DataEvidenceRecord,
    QuarantineRange,
    assert_evidence_grain,
    evidence_fingerprint,
    evidence_is_model_eligible,
)
from .evidence_manifest import (
    freeze_preholdout_evidence_manifest,
    require_frozen_manifest_authorized,
)
from .gates import DataEvidence, GateDecision, evaluate_data_evidence, require_modeling_allowed
from .manifest import fingerprint_records, build_manifest
from .security_master import SecurityMasterRecord, resolve_symbol, sector_as_of
from .splits import classify_date, assert_publication_available, purged_walk_forward
from .targets import forward_return, residual_return

__all__ = [
    "Bar",
    "ContractError",
    "validate_bar",
    "assert_unique",
    "ExecutionCostModel",
    "DataEvidenceRecord",
    "QuarantineRange",
    "assert_evidence_grain",
    "evidence_fingerprint",
    "evidence_is_model_eligible",
    "freeze_preholdout_evidence_manifest",
    "require_frozen_manifest_authorized",
    "DataEvidence",
    "GateDecision",
    "evaluate_data_evidence",
    "require_modeling_allowed",
    "fingerprint_records",
    "build_manifest",
    "SecurityMasterRecord",
    "resolve_symbol",
    "sector_as_of",
    "classify_date",
    "assert_publication_available",
    "purged_walk_forward",
    "forward_return",
    "residual_return",
]
