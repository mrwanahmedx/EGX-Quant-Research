import unittest
from datetime import datetime, timedelta, timezone

from egx_quant.benchmarks import (
    load_benchmark_catalog,
    require_benchmark_approved,
)
from egx_quant.readiness import build_repository_readiness_report
from egx_quant.shadow import ShadowPrediction, attach_realized_outcome


UTC = timezone.utc


class ReadinessBenchmarkShadowTests(unittest.TestCase):
    def test_no_benchmark_is_currently_approved(self):
        benchmarks = load_benchmark_catalog()
        self.assertTrue(benchmarks)
        self.assertTrue(
            all(not item.approved_for_model_comparison for item in benchmarks)
        )
        with self.assertRaises(RuntimeError):
            require_benchmark_approved(benchmarks, "egx30_total_return")

    def test_repository_correctly_reports_modeling_blocked(self):
        report = build_repository_readiness_report()
        self.assertFalse(report.modeling_authorized)
        blocker_ids = {item.check_id for item in report.blockers}
        self.assertIn("source_snapshot", blocker_ids)
        self.assertIn("exact_quarantine_register", blocker_ids)
        self.assertIn("security_master", blocker_ids)
        self.assertIn("benchmark_series", blocker_ids)
        self.assertIn("acceptance_thresholds", blocker_ids)
        self.assertIn("frozen_evidence_manifest", blocker_ids)
        self.assertIn("frozen_development_panel", blocker_ids)

    def test_shadow_outcome_cannot_exist_at_decision_time(self):
        decision = datetime(2026, 9, 1, 10, tzinfo=UTC)
        base = dict(
            prediction_id="p1",
            model_id="m1",
            canonical_security_id="EGX:A",
            decision_time=decision,
            target_horizon=20,
            score=0.1,
            rank=1,
            source_vintage="v1",
            data_fingerprint="a" * 64,
            execution_convention="next_session_open",
        )
        with self.assertRaises(ValueError):
            ShadowPrediction(
                **base,
                realized_target=0.05,
                outcome_observed_at=decision,
            )

    def test_outcome_attachment_is_forward_only(self):
        decision = datetime(2026, 9, 1, 10, tzinfo=UTC)
        prediction = ShadowPrediction(
            prediction_id="p1",
            model_id="m1",
            canonical_security_id="EGX:A",
            decision_time=decision,
            target_horizon=20,
            score=0.1,
            rank=1,
            source_vintage="v1",
            data_fingerprint="a" * 64,
            execution_convention="next_session_open",
        )
        completed = attach_realized_outcome(
            prediction,
            realized_target=0.05,
            observed_at=decision + timedelta(days=30),
        )
        self.assertEqual(completed.realized_target, 0.05)
        with self.assertRaises(RuntimeError):
            attach_realized_outcome(
                completed,
                realized_target=0.06,
                observed_at=decision + timedelta(days=31),
            )


if __name__ == "__main__":
    unittest.main()
