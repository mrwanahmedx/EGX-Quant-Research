import unittest

from egx_quant.gates import DataEvidence
from egx_quant.modeling import ModelSpec, authorize_real_training, authorize_training
from egx_quant.portfolio import RankedSecurity, dropout_rebalance, one_way_turnover, top_k


class PortfolioModelingTests(unittest.TestCase):
    def setUp(self):
        self.ranked = [
            RankedSecurity("B", 0.7),
            RankedSecurity("A", 0.9),
            RankedSecurity("C", 0.5),
            RankedSecurity("D", 0.4),
        ]

    def test_top_k_is_deterministic(self):
        self.assertEqual(top_k(self.ranked, 2), ("A", "B"))

    def test_dropout_keeps_buffered_incumbent(self):
        self.assertEqual(
            dropout_rebalance(["B", "C"], self.ranked, k=2, drop_buffer=1),
            ("B", "C"),
        )

    def test_turnover_counts_new_names(self):
        self.assertAlmostEqual(one_way_turnover(["A", "B"], ["B", "C"]), 0.5)

    def test_model_training_fails_closed_without_evidence(self):
        spec = ModelSpec(
            family="linear",
            target="residual_return_20d",
            feature_set="alpha158-egx-v1",
            params={},
        )
        blocked = DataEvidence(True, True, False, False, True, False)
        with self.assertRaises(RuntimeError):
            authorize_training(spec, blocked)

    def test_real_training_requires_frozen_row_level_manifest(self):
        spec = ModelSpec(
            family="linear",
            target="residual_return_20d",
            feature_set="alpha158-egx-v1",
            params={},
        )
        aggregate_pass = DataEvidence(True, True, True, True, True, True)
        blocked_manifest = {
            "kind": "preholdout-data-evidence-manifest",
            "decision_time": "2026-01-31T23:59:59+02:00",
            "code_ref": "abc123",
            "modeling_authorized": False,
            "record_count": 100,
            "eligible_record_count": 96,
            "blocked_record_count": 4,
            "data_evidence_fingerprint": "a" * 64,
            "source_snapshot_fingerprint": "s" * 64,
        }
        blocked_panel = {
            "kind": "frozen-development-panel-manifest",
            "created_at": "2026-09-26T00:00:00Z",
            "code_ref": "panel123",
            "row_count": 100,
            "security_count": 10,
            "first_session": "2025-01-02",
            "last_session": "2026-01-30",
            "panel_fingerprint": "p" * 64,
            "evidence_fingerprint": "a" * 64,
            "evidence_manifest_code_ref": "abc123",
            "development_cutoff": "2026-01-31",
            "authorized_for_model_development": True,
        }
        with self.assertRaises(RuntimeError):
            authorize_real_training(
                spec,
                aggregate_pass,
                blocked_manifest,
                blocked_panel,
            )

        allowed_manifest = {
            "kind": "preholdout-data-evidence-manifest",
            "decision_time": "2026-01-31T23:59:59+02:00",
            "code_ref": "abc123",
            "modeling_authorized": True,
            "record_count": 100,
            "eligible_record_count": 100,
            "blocked_record_count": 0,
            "data_evidence_fingerprint": "a" * 64,
            "source_snapshot_fingerprint": "s" * 64,
        }
        authorize_real_training(
            spec,
            aggregate_pass,
            allowed_manifest,
            blocked_panel,
        )

        mismatched_panel = dict(blocked_panel)
        mismatched_panel["evidence_fingerprint"] = "x" * 64
        with self.assertRaises(RuntimeError):
            authorize_real_training(
                spec,
                aggregate_pass,
                allowed_manifest,
                mismatched_panel,
            )


if __name__ == "__main__":
    unittest.main()
