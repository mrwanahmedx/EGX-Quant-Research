import unittest
from datetime import date

from egx_quant.baseline import (
    BaselineObservation,
    evaluate_transparent_rank_baseline,
    require_readiness,
)
from egx_quant.costs import ExecutionCostModel
from egx_quant.readiness import ReadinessCheck, ReadinessReport


class BaselineRunnerTests(unittest.TestCase):
    def sample(self):
        return [
            BaselineObservation(date(2025, 1, 2), "A", 3.0, 0.08),
            BaselineObservation(date(2025, 1, 2), "B", 2.0, 0.03),
            BaselineObservation(date(2025, 1, 2), "C", 1.0, -0.02),
            BaselineObservation(date(2025, 1, 3), "A", 1.0, -0.01),
            BaselineObservation(date(2025, 1, 3), "B", 3.0, 0.07),
            BaselineObservation(date(2025, 1, 3), "C", 2.0, 0.02),
        ]

    def test_baseline_metrics_are_deterministic(self):
        result = evaluate_transparent_rank_baseline(
            self.sample(),
            k=1,
            cost_model=ExecutionCostModel(slippage_bps=10),
        )
        self.assertEqual(result.session_count, 2)
        self.assertEqual(result.observation_count, 6)
        self.assertAlmostEqual(result.mean_rank_ic, 1.0)
        self.assertAlmostEqual(result.positive_ic_fraction, 1.0)
        self.assertLess(
            result.net_mean_period_return,
            result.gross_mean_period_return,
        )

    def test_duplicate_observation_grain_is_rejected(self):
        rows = self.sample()
        with self.assertRaises(ValueError):
            evaluate_transparent_rank_baseline(
                [rows[0], rows[0]],
                k=1,
                cost_model=ExecutionCostModel(),
            )

    def test_readiness_blocks_real_execution(self):
        report = ReadinessReport(
            modeling_authorized=False,
            checks=(
                ReadinessCheck(
                    "security_master",
                    False,
                    "not populated",
                ),
            ),
        )
        with self.assertRaises(RuntimeError):
            require_readiness(report)

    def test_authorized_readiness_allows_runner(self):
        report = ReadinessReport(
            modeling_authorized=True,
            checks=(
                ReadinessCheck("all", True, "passed"),
            ),
        )
        require_readiness(report)


if __name__ == "__main__":
    unittest.main()
