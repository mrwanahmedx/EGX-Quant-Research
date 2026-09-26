"""Core research controls for EGX Quant Research."""

from .contracts import Bar, ContractError, validate_bar, assert_unique
from .costs import ExecutionCostModel
from .gates import DataEvidence, GateDecision, evaluate_data_evidence, require_modeling_allowed
from .manifest import fingerprint_records, build_manifest
from .splits import classify_date, assert_publication_available, purged_walk_forward
from .targets import forward_return, residual_return

__all__ = [
    "Bar",
    "ContractError",
    "validate_bar",
    "assert_unique",
    "ExecutionCostModel",
    "DataEvidence",
    "GateDecision",
    "evaluate_data_evidence",
    "require_modeling_allowed",
    "fingerprint_records",
    "build_manifest",
    "classify_date",
    "assert_publication_available",
    "purged_walk_forward",
    "forward_return",
    "residual_return",
]
