import unittest
from dataclasses import replace

from egx_quant.benchmark_approval import (
    approve_frozen_benchmark,
    validate_benchmark_source_links,
)
from egx_quant.benchmark_series import (
    BenchmarkObservation,
    freeze_benchmark_series_manifest,
)
from egx_quant.benchmarks import BenchmarkDefinition, load_benchmark_catalog
from egx_quant.sources import SourceDefinition, load_source_catalog
from datetime import date


class BenchmarkApprovalTests(unittest.TestCase):
    def setUp(self):
        self.benchmark = BenchmarkDefinition(
            benchmark_id="conia",
            name="CONIA",
            kind="overnight_cash_rate",
            source_id="cbe_conia",
            methodology_evidenced=True,
            historical_series_frozen=False,
            series_fingerprint=None,
            approved_for_model_comparison=False,
        )
        self.source = SourceDefinition(
            source_id="cbe_conia",
            name="CBE CONIA",
            source_url="https://example.com",
            authority="official_central_bank",
            license_status="official",
            coverage_claim="fixture",
            approved_roles=("benchmark_reference",),
            prohibited_roles=(),
            point_in_time_membership_proven=False,
        )
        self.manifest = freeze_benchmark_series_manifest(
            (
                BenchmarkObservation(date(2025, 1, 2), 100.0),
                BenchmarkObservation(date(2025, 1, 3), 100.1),
            ),
            benchmark_id="conia",
            source_id="cbe_conia",
            source_snapshot_ref="sha256-fixture",
            return_convention="compounded_index",
            methodology_ref="official-methodology",
            code_ref="abc123",
        )

    def test_catalog_source_links_are_valid(self):
        validate_benchmark_source_links(
            load_benchmark_catalog(),
            load_source_catalog(),
        )

    def test_review_must_be_complete(self):
        with self.assertRaises(RuntimeError):
            approve_frozen_benchmark(
                self.benchmark,
                self.source,
                self.manifest,
                frozen_manifest_ref="evidence/benchmarks/conia.json",
                reviewer="reviewer",
                methodology_reviewed=True,
                source_snapshot_reviewed=False,
                return_convention_reviewed=True,
            )

    def test_source_and_manifest_must_match(self):
        wrong = dict(self.manifest)
        wrong["source_id"] = "wrong-source"
        with self.assertRaises(RuntimeError):
            approve_frozen_benchmark(
                self.benchmark,
                self.source,
                wrong,
                frozen_manifest_ref="manifest",
                reviewer="reviewer",
                methodology_reviewed=True,
                source_snapshot_reviewed=True,
                return_convention_reviewed=True,
            )

    def test_approval_links_exact_series_fingerprint(self):
        approved, review = approve_frozen_benchmark(
            self.benchmark,
            self.source,
            self.manifest,
            frozen_manifest_ref="evidence/benchmarks/conia.json",
            reviewer="reviewer",
            methodology_reviewed=True,
            source_snapshot_reviewed=True,
            return_convention_reviewed=True,
            reviewed_at="2026-09-26T00:00:00Z",
        )
        self.assertTrue(approved.approved_for_model_comparison)
        self.assertTrue(approved.historical_series_frozen)
        self.assertEqual(
            approved.series_fingerprint,
            self.manifest["series_fingerprint"],
        )
        self.assertEqual(
            review["series_fingerprint"],
            self.manifest["series_fingerprint"],
        )

    def test_unproven_methodology_cannot_be_approved(self):
        with self.assertRaises(RuntimeError):
            approve_frozen_benchmark(
                replace(self.benchmark, methodology_evidenced=False),
                self.source,
                self.manifest,
                frozen_manifest_ref="manifest",
                reviewer="reviewer",
                methodology_reviewed=True,
                source_snapshot_reviewed=True,
                return_convention_reviewed=True,
            )


if __name__ == "__main__":
    unittest.main()
