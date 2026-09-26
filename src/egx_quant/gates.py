from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DataEvidence:
    security_master: bool
    ohlc_qa: bool
    corporate_actions: bool
    point_in_time_universe: bool
    publication_timestamps: bool
    benchmark_provenance: bool


@dataclass(frozen=True)
class GateDecision:
    passed: bool
    blockers: tuple[str, ...]


def evaluate_data_evidence(evidence: DataEvidence) -> GateDecision:
    checks = {
        "security master unresolved": evidence.security_master,
        "OHLC QA unresolved": evidence.ohlc_qa,
        "corporate actions unresolved": evidence.corporate_actions,
        "point-in-time universe unresolved": evidence.point_in_time_universe,
        "publication timestamps unresolved": evidence.publication_timestamps,
        "benchmark provenance unresolved": evidence.benchmark_provenance,
    }
    blockers = tuple(label for label, passed in checks.items() if not passed)
    return GateDecision(passed=not blockers, blockers=blockers)


def require_modeling_allowed(evidence: DataEvidence) -> None:
    decision = evaluate_data_evidence(evidence)
    if not decision.passed:
        raise RuntimeError(
            "modeling blocked by data-evidence gates: "
            + "; ".join(decision.blockers)
        )
