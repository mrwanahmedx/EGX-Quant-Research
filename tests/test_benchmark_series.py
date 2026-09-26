import unittest
from datetime import date

from egx_quant.benchmark_series import (
    BenchmarkObservation,
    benchmark_series_fingerprint,
    freeze_benchmark_series_manifest,
    validate_benchmark_observations,
)


class BenchmarkSeriesTests(unittest.TestCase):
    def rows(self):
        return (
            BenchmarkObservation(date(2025, 1, 2), 100.0),
            BenchmarkObservation(date(2025, 1, 3), 100.5),
            BenchmarkObservation(date(2025, 1, 5), 100.7),
        )

    def test_series_fingerprint_is_deterministic(self):
        self.assertEqual(
            benchmark_series_fingerprint(self.rows()),
            benchmark_series_fingerprint(self.rows()),
        )

    def test_duplicate_dates_are_rejected(self):
        with self.assertRaises(ValueError):
            validate_benchmark_observations(
                (
                    BenchmarkObservation(date(2025, 1, 2), 100.0),
                    BenchmarkObservation(date(2025, 1, 2), 101.0),
                )
            )

    def test_post_cutoff_observation_is_rejected(self):
        with self.assertRaises(ValueError):
            BenchmarkObservation(date(2026, 2, 1), 100.0)

    def test_freeze_records_methodology_and_source(self):
        manifest = freeze_benchmark_series_manifest(
            self.rows(),
            benchmark_id="conia",
            source_id="cbe_conia",
            source_snapshot_ref="snapshot-sha256",
            return_convention="daily_compounded_index",
            methodology_ref="official-cbe-conia-methodology",
            code_ref="abc123",
        )
        self.assertEqual(manifest["benchmark_id"], "conia")
        self.assertFalse(manifest["approved_for_model_comparison"])
        self.assertEqual(manifest["development_cutoff"], "2026-01-31")


if __name__ == "__main__":
    unittest.main()
