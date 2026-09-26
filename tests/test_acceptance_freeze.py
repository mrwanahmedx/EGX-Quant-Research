import unittest

from egx_quant.acceptance import AcceptanceThresholds
from egx_quant.acceptance_freeze import (
    freeze_acceptance_thresholds,
    validate_frozen_acceptance_payload,
)


class AcceptanceFreezeTests(unittest.TestCase):
    def thresholds(self, **overrides):
        values = dict(
            min_mean_rank_ic=0.01,
            min_positive_ic_fraction=0.55,
            max_one_way_turnover=0.50,
            min_net_return=0.0,
            max_drawdown_abs=0.25,
            multiple_testing_method="DSR_and_CSCV",
            trial_registry_required=True,
        )
        values.update(overrides)
        return AcceptanceThresholds(**values)

    def test_freeze_requires_unopened_holdout(self):
        with self.assertRaises(RuntimeError):
            freeze_acceptance_thresholds(
                self.thresholds(),
                code_ref="abc123",
                development_evidence_ref="dev-manifest",
                rationale="Predeclared from development stability and turnover evidence.",
                holdout_unopened=False,
            )

    def test_freeze_requires_complete_thresholds(self):
        with self.assertRaises(ValueError):
            freeze_acceptance_thresholds(
                self.thresholds(min_mean_rank_ic=None),
                code_ref="abc123",
                development_evidence_ref="dev-manifest",
                rationale="Predeclared from development stability and turnover evidence.",
                holdout_unopened=True,
            )

    def test_frozen_payload_is_self_validating(self):
        payload = freeze_acceptance_thresholds(
            self.thresholds(),
            code_ref="abc123",
            development_evidence_ref="dev-manifest",
            rationale="Predeclared from development stability and turnover evidence.",
            holdout_unopened=True,
            frozen_at="2026-09-26T00:00:00Z",
        )
        self.assertEqual(payload["status"], "frozen")
        self.assertTrue(payload["holdout_unopened"])
        validate_frozen_acceptance_payload(payload)

    def test_invalid_fraction_is_rejected(self):
        with self.assertRaises(ValueError):
            freeze_acceptance_thresholds(
                self.thresholds(min_positive_ic_fraction=1.2),
                code_ref="abc123",
                development_evidence_ref="dev-manifest",
                rationale="Predeclared from development stability and turnover evidence.",
                holdout_unopened=True,
            )


if __name__ == "__main__":
    unittest.main()
