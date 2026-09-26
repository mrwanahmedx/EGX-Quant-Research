from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from math import isfinite
from typing import Iterable, Mapping, Any

from .manifest import fingerprint_records
from .splits import DEVELOPMENT_END


@dataclass(frozen=True)
class BenchmarkObservation:
    session_date: date
    value: float

    def __post_init__(self) -> None:
        if not isfinite(self.value):
            raise ValueError("benchmark observation must be finite")
        if self.session_date > DEVELOPMENT_END:
            raise ValueError("benchmark observation crosses frozen development cutoff")


def validate_benchmark_observations(
    observations: Iterable[BenchmarkObservation],
) -> tuple[BenchmarkObservation, ...]:
    rows = tuple(observations)
    if not rows:
        raise ValueError("benchmark series is empty")

    dates = [row.session_date for row in rows]
    if len(dates) != len(set(dates)):
        raise ValueError("duplicate benchmark session dates")
    if dates != sorted(dates):
        raise ValueError("benchmark observations must be sorted by date")
    return rows


def benchmark_series_fingerprint(
    observations: Iterable[BenchmarkObservation],
) -> str:
    rows = validate_benchmark_observations(observations)
    return fingerprint_records(
        [
            {
                "session_date": row.session_date.isoformat(),
                "value": row.value,
            }
            for row in rows
        ]
    )


def freeze_benchmark_series_manifest(
    observations: Iterable[BenchmarkObservation],
    *,
    benchmark_id: str,
    source_id: str,
    source_snapshot_ref: str,
    return_convention: str,
    methodology_ref: str,
    code_ref: str,
    approved_for_model_comparison: bool = False,
) -> dict[str, Any]:
    rows = validate_benchmark_observations(observations)

    for name, value in {
        "benchmark_id": benchmark_id,
        "source_id": source_id,
        "source_snapshot_ref": source_snapshot_ref,
        "return_convention": return_convention,
        "methodology_ref": methodology_ref,
        "code_ref": code_ref,
    }.items():
        if not str(value).strip():
            raise ValueError(f"{name} is required")

    manifest = {
        "kind": "frozen-benchmark-series-manifest",
        "benchmark_id": benchmark_id,
        "source_id": source_id,
        "source_snapshot_ref": source_snapshot_ref,
        "return_convention": return_convention,
        "methodology_ref": methodology_ref,
        "observation_count": len(rows),
        "first_date": rows[0].session_date.isoformat(),
        "last_date": rows[-1].session_date.isoformat(),
        "series_fingerprint": benchmark_series_fingerprint(rows),
        "code_ref": code_ref,
        "development_cutoff": DEVELOPMENT_END.isoformat(),
        "approved_for_model_comparison": bool(approved_for_model_comparison),
    }
    validate_frozen_benchmark_series_manifest(manifest)
    return manifest


def validate_frozen_benchmark_series_manifest(
    manifest: Mapping[str, Any],
) -> None:
    required = {
        "kind",
        "benchmark_id",
        "source_id",
        "source_snapshot_ref",
        "return_convention",
        "methodology_ref",
        "observation_count",
        "first_date",
        "last_date",
        "series_fingerprint",
        "code_ref",
        "development_cutoff",
        "approved_for_model_comparison",
    }
    missing = required - set(manifest)
    if missing:
        raise ValueError(f"benchmark manifest missing fields: {sorted(missing)}")
    if manifest["kind"] != "frozen-benchmark-series-manifest":
        raise ValueError("unexpected benchmark manifest kind")
    if int(manifest["observation_count"]) <= 0:
        raise ValueError("benchmark manifest has no observations")
    if str(manifest["last_date"]) > DEVELOPMENT_END.isoformat():
        raise ValueError("benchmark manifest crosses development cutoff")
    if str(manifest["development_cutoff"]) != DEVELOPMENT_END.isoformat():
        raise ValueError("benchmark cutoff does not match repository contract")
    if len(str(manifest["series_fingerprint"])) < 16:
        raise ValueError("benchmark series fingerprint is too short")
