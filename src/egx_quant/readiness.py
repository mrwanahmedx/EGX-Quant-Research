from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .acceptance import load_acceptance_thresholds
from .benchmarks import approved_benchmarks, load_benchmark_catalog


@dataclass(frozen=True)
class ReadinessCheck:
    check_id: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class ReadinessReport:
    modeling_authorized: bool
    checks: tuple[ReadinessCheck, ...]

    @property
    def blockers(self) -> tuple[ReadinessCheck, ...]:
        return tuple(check for check in self.checks if not check.passed)


def _load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def build_repository_readiness_report(
    *,
    reconciliation_summary_path: str | Path = "evidence/reconciliation_summary.json",
    acceptance_path: str | Path = "config/acceptance.template.json",
    benchmark_catalog_path: str | Path = "config/benchmark_catalog.json",
    exact_quarantine_register_path: str | Path = "evidence/quarantine_register.csv",
    frozen_evidence_manifest_path: str | Path = "evidence/frozen_preholdout_manifest.json",
    frozen_development_panel_manifest_path: str | Path = "evidence/frozen_development_panel.json",
    security_master_path: str | Path = "evidence/security_master.json",
) -> ReadinessReport:
    summary = _load_json(reconciliation_summary_path)
    thresholds = load_acceptance_thresholds(acceptance_path)
    benchmarks = load_benchmark_catalog(benchmark_catalog_path)

    exact_register_committed = bool(
        summary.get("exact_quarantine_register_committed")
    ) and Path(exact_quarantine_register_path).exists()

    security_master_present = Path(security_master_path).exists()
    evidence_manifest_present = Path(frozen_evidence_manifest_path).exists()
    panel_manifest_present = Path(frozen_development_panel_manifest_path).exists()
    benchmark_ready = bool(approved_benchmarks(benchmarks))

    checks = (
        ReadinessCheck(
            "exact_quarantine_register",
            exact_register_committed,
            (
                "exact machine-readable quarantine register is committed"
                if exact_register_committed
                else "exact 47-range quarantine register has not been recovered/imported"
            ),
        ),
        ReadinessCheck(
            "security_master",
            security_master_present,
            (
                "point-in-time security master is present"
                if security_master_present
                else "real point-in-time security master is not populated"
            ),
        ),
        ReadinessCheck(
            "benchmark_series",
            benchmark_ready,
            (
                "at least one benchmark is approved with frozen series evidence"
                if benchmark_ready
                else "no benchmark series is frozen and approved"
            ),
        ),
        ReadinessCheck(
            "acceptance_thresholds",
            thresholds.frozen,
            (
                "development acceptance thresholds are frozen"
                if thresholds.frozen
                else "acceptance thresholds remain intentionally unfrozen"
            ),
        ),
        ReadinessCheck(
            "frozen_evidence_manifest",
            evidence_manifest_present,
            (
                "pre-holdout evidence manifest is present"
                if evidence_manifest_present
                else "pre-holdout row-level evidence manifest is not frozen"
            ),
        ),
        ReadinessCheck(
            "frozen_development_panel",
            panel_manifest_present,
            (
                "development panel manifest is present"
                if panel_manifest_present
                else "development panel is not frozen"
            ),
        ),
    )

    return ReadinessReport(
        modeling_authorized=all(check.passed for check in checks),
        checks=checks,
    )
