from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping

from .benchmark_series import validate_frozen_benchmark_series_manifest
from .benchmarks import BenchmarkDefinition
from .sources import SourceDefinition


def _source_role_allowed(
    benchmark: BenchmarkDefinition,
    source: SourceDefinition,
) -> bool:
    if benchmark.kind == "fixed_income":
        roles = {"fixed_income_benchmark_candidate", "benchmark_reference"}
    else:
        roles = {"benchmark_reference"}
    return any(source.allows(role) for role in roles)


def validate_benchmark_source_links(
    benchmarks: Iterable[BenchmarkDefinition],
    sources: Iterable[SourceDefinition],
) -> None:
    source_by_id = {source.source_id: source for source in sources}
    for benchmark in benchmarks:
        source = source_by_id.get(benchmark.source_id)
        if source is None:
            raise ValueError(
                f"{benchmark.benchmark_id}: source not found: {benchmark.source_id}"
            )
        if not _source_role_allowed(benchmark, source):
            raise ValueError(
                f"{benchmark.benchmark_id}: source {benchmark.source_id} "
                "does not have an approved benchmark role"
            )


def approve_frozen_benchmark(
    benchmark: BenchmarkDefinition,
    source: SourceDefinition,
    frozen_manifest: Mapping[str, Any],
    *,
    frozen_manifest_ref: str,
    reviewer: str,
    methodology_reviewed: bool,
    source_snapshot_reviewed: bool,
    return_convention_reviewed: bool,
    reviewed_at: str | None = None,
    notes: str = "",
) -> tuple[BenchmarkDefinition, dict[str, Any]]:
    validate_frozen_benchmark_series_manifest(frozen_manifest)

    if benchmark.benchmark_id != frozen_manifest["benchmark_id"]:
        raise RuntimeError("benchmark ID does not match frozen series manifest")
    if benchmark.source_id != frozen_manifest["source_id"]:
        raise RuntimeError("benchmark source does not match frozen series manifest")
    if source.source_id != benchmark.source_id:
        raise RuntimeError("source definition does not match benchmark catalog")
    if not _source_role_allowed(benchmark, source):
        raise RuntimeError("source is not approved for this benchmark role")
    if not benchmark.methodology_evidenced:
        raise RuntimeError("benchmark methodology is not evidenced")

    review_checks = {
        "methodology_reviewed": methodology_reviewed,
        "source_snapshot_reviewed": source_snapshot_reviewed,
        "return_convention_reviewed": return_convention_reviewed,
    }
    failed = [name for name, passed in review_checks.items() if not passed]
    if failed:
        raise RuntimeError(
            "benchmark approval review incomplete: " + ", ".join(failed)
        )
    if not frozen_manifest_ref.strip():
        raise ValueError("frozen_manifest_ref is required")
    if not reviewer.strip():
        raise ValueError("reviewer is required")

    approved = replace(
        benchmark,
        historical_series_frozen=True,
        series_fingerprint=str(frozen_manifest["series_fingerprint"]),
        approved_for_model_comparison=True,
    )
    approved.__post_init__()

    review = {
        "kind": "benchmark-approval-review",
        "benchmark_id": benchmark.benchmark_id,
        "source_id": benchmark.source_id,
        "series_fingerprint": frozen_manifest["series_fingerprint"],
        "frozen_manifest_ref": frozen_manifest_ref,
        "reviewed_at": reviewed_at
        or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "reviewer": reviewer,
        "methodology_reviewed": True,
        "source_snapshot_reviewed": True,
        "return_convention_reviewed": True,
        "approved_for_model_comparison": True,
        "notes": notes,
    }
    validate_benchmark_approval_review(review)
    return approved, review


def validate_benchmark_approval_review(review: Mapping[str, Any]) -> None:
    required = {
        "kind",
        "benchmark_id",
        "source_id",
        "series_fingerprint",
        "frozen_manifest_ref",
        "reviewed_at",
        "reviewer",
        "methodology_reviewed",
        "source_snapshot_reviewed",
        "return_convention_reviewed",
        "approved_for_model_comparison",
    }
    missing = required - set(review)
    if missing:
        raise ValueError(f"benchmark approval review missing fields: {sorted(missing)}")
    if review["kind"] != "benchmark-approval-review":
        raise ValueError("unexpected benchmark approval review kind")
    if len(str(review["series_fingerprint"])) < 16:
        raise ValueError("benchmark approval fingerprint is too short")
    for key in (
        "methodology_reviewed",
        "source_snapshot_reviewed",
        "return_convention_reviewed",
        "approved_for_model_comparison",
    ):
        if review[key] is not True:
            raise ValueError(f"{key} must be true")
