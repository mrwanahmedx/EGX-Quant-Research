from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class BenchmarkDefinition:
    benchmark_id: str
    name: str
    kind: str
    source_id: str
    methodology_evidenced: bool
    historical_series_frozen: bool
    series_fingerprint: str | None
    approved_for_model_comparison: bool
    notes: str = ""

    def __post_init__(self) -> None:
        if self.approved_for_model_comparison:
            if not self.methodology_evidenced:
                raise ValueError(
                    f"{self.benchmark_id}: approved benchmark lacks methodology evidence"
                )
            if not self.historical_series_frozen:
                raise ValueError(
                    f"{self.benchmark_id}: approved benchmark series is not frozen"
                )
            if not self.series_fingerprint or len(self.series_fingerprint) < 16:
                raise ValueError(
                    f"{self.benchmark_id}: approved benchmark lacks a strong fingerprint"
                )


def load_benchmark_catalog(
    path: str | Path = "config/benchmark_catalog.json",
) -> tuple[BenchmarkDefinition, ...]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, list) or not raw:
        raise ValueError("benchmark catalog must be a non-empty list")
    benchmarks = tuple(BenchmarkDefinition(**item) for item in raw)
    validate_benchmark_catalog(benchmarks)
    return benchmarks


def validate_benchmark_catalog(
    benchmarks: Iterable[BenchmarkDefinition],
) -> None:
    benchmarks = tuple(benchmarks)
    ids = [item.benchmark_id for item in benchmarks]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate benchmark IDs")


def approved_benchmarks(
    benchmarks: Iterable[BenchmarkDefinition],
) -> tuple[BenchmarkDefinition, ...]:
    return tuple(
        benchmark
        for benchmark in benchmarks
        if benchmark.approved_for_model_comparison
    )


def require_benchmark_approved(
    benchmarks: Iterable[BenchmarkDefinition],
    benchmark_id: str,
) -> BenchmarkDefinition:
    matches = [
        benchmark
        for benchmark in benchmarks
        if benchmark.benchmark_id == benchmark_id
    ]
    if len(matches) != 1:
        raise RuntimeError(f"benchmark not found or ambiguous: {benchmark_id}")
    benchmark = matches[0]
    if not benchmark.approved_for_model_comparison:
        raise RuntimeError(
            f"benchmark {benchmark_id} is not approved for model comparison"
        )
    return benchmark
