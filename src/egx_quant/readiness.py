from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .acceptance import load_acceptance_thresholds
from .benchmarks import approved_benchmarks, load_benchmark_catalog
from .io import load_quarantine_csv, load_security_master_json
from .manifest_validation import validate_frozen_evidence_manifest
from .panel_manifest import (
    require_panel_matches_evidence,
    validate_frozen_development_panel_manifest,
)


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


def _validated_quarantine_register(path: Path, expected_count: int | None) -> tuple[bool, str]:
    if not path.exists():
        return False, "exact quarantine register is not present"
    try:
        rows = load_quarantine_csv(path)
    except Exception as exc:
        return False, f"quarantine register is invalid: {exc}"
    if not rows:
        return False, "quarantine register is empty"
    ids = [row.quarantine_id for row in rows]
    if len(ids) != len(set(ids)):
        return False, "quarantine register has duplicate quarantine IDs"
    if expected_count is not None and len(rows) != expected_count:
        return False, (
            f"quarantine register has {len(rows)} rows; "
            f"expected {expected_count} exact ranges"
        )
    return True, f"validated {len(rows)} exact quarantine ranges"


def _validated_security_master(path: Path) -> tuple[bool, str]:
    if not path.exists():
        return False, "real point-in-time security master is not populated"
    try:
        rows = load_security_master_json(path)
    except Exception as exc:
        return False, f"security master is invalid: {exc}"
    if not rows:
        return False, "security master is empty"
    verified = sum(row.mapping_confidence == "verified" for row in rows)
    if verified == 0:
        return False, "security master has no verified mappings"
    return True, f"security master contains {verified} verified mapping records"


def _validated_frozen_manifest(path: Path) -> tuple[bool, str]:
    if not path.exists():
        return False, "pre-holdout row-level evidence manifest is not frozen"
    try:
        manifest = _load_json(path)
        validate_frozen_evidence_manifest(manifest)
    except Exception as exc:
        return False, f"frozen evidence manifest is invalid: {exc}"
    if not manifest["modeling_authorized"]:
        return False, (
            "frozen evidence manifest exists but does not authorize modeling: "
            f"{manifest['blocked_record_count']} blocked rows"
        )
    return True, (
        "frozen evidence manifest authorizes "
        f"{manifest['eligible_record_count']} rows"
    )


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

    expected_quarantine_count = (
        summary.get("quarantine", {}).get("ticker_date_ranges")
    )
    register_valid, register_detail = _validated_quarantine_register(
        Path(exact_quarantine_register_path),
        int(expected_quarantine_count) if expected_quarantine_count is not None else None,
    )
    exact_register_committed = bool(
        summary.get("exact_quarantine_register_committed")
    ) and register_valid
    if not summary.get("exact_quarantine_register_committed"):
        register_detail = (
            "aggregate audit is preserved, but the exact original quarantine "
            "register is not marked as recovered/imported"
        )

    security_master_valid, security_master_detail = _validated_security_master(
        Path(security_master_path)
    )
    manifest_valid, manifest_detail = _validated_frozen_manifest(
        Path(frozen_evidence_manifest_path)
    )

    panel_path = Path(frozen_development_panel_manifest_path)
    panel_manifest_valid = False
    panel_manifest_detail = "development panel is not frozen"
    if panel_path.exists():
        try:
            panel_manifest = _load_json(panel_path)
            validate_frozen_development_panel_manifest(panel_manifest)
            if manifest_valid:
                evidence_manifest = _load_json(frozen_evidence_manifest_path)
                require_panel_matches_evidence(panel_manifest, evidence_manifest)
                panel_manifest_valid = True
                panel_manifest_detail = (
                    "development panel is frozen and linked to the authorized "
                    f"evidence generation: {panel_manifest['row_count']} rows"
                )
            else:
                panel_manifest_detail = (
                    "development panel manifest exists but evidence manifest "
                    "is not authorized"
                )
        except Exception as exc:
            panel_manifest_detail = f"development panel manifest is invalid: {exc}"

    benchmark_ready = bool(approved_benchmarks(benchmarks))

    checks = (
        ReadinessCheck(
            "exact_quarantine_register",
            exact_register_committed,
            register_detail,
        ),
        ReadinessCheck(
            "security_master",
            security_master_valid,
            security_master_detail,
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
            manifest_valid,
            manifest_detail,
        ),
        ReadinessCheck(
            "frozen_development_panel",
            panel_manifest_valid,
            panel_manifest_detail,
        ),
    )

    return ReadinessReport(
        modeling_authorized=all(check.passed for check in checks),
        checks=checks,
    )
