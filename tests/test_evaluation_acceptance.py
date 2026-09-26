import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

from egx_quant.acceptance import (
    AcceptanceThresholds,
    evaluate_acceptance,
    load_acceptance_thresholds,
)
from egx_quant.evaluation import (
    PredictionObservation,
    max_drawdown,
    rank_ic_by_session,
    summarize_rank_ic,
)


class EvaluationAcceptanceTests(unittest.TestCase):
    def test_rank_ic_is_computed_cross_sectionally_by_session(self):
        rows = [
            PredictionObservation(date(2025, 1, 1), "A", 1.0, 0.1),
            PredictionObservation(date(2025, 1, 1), "B", 2.0, 0.2),
            PredictionObservation(date(2025, 1, 2), "A", 1.0, 0.3),
            PredictionObservation(date(2025, 1, 2), "B", 2.0, 0.1),
        ]
        values = rank_ic_by_session(rows)
        self.assertEqual(values[date(2025, 1, 1)], 1.0)
        self.assertEqual(values[date(2025, 1, 2)], -1.0)
        summary = summarize_rank_ic(values.values())
        self.assertAlmostEqual(summary.mean_rank_ic, 0.0)
        self.assertAlmostEqual(summary.positive_fraction, 0.5)

    def test_max_drawdown(self):
        self.assertAlmostEqual(
            max_drawdown([1.0, 1.2, 0.9, 1.1]),
            -0.25,
        )

    def test_template_thresholds_cannot_accept_model(self):
        thresholds = load_acceptance_thresholds(
            "config/acceptance.template.json"
        )
        decision = evaluate_acceptance(
            {
                "mean_rank_ic": 1.0,
                "positive_ic_fraction": 1.0,
                "one_way_turnover": 0.0,
                "net_return": 10.0,
                "max_drawdown": 0.0,
            },
            thresholds,
            trial_registry_present=True,
        )
        self.assertFalse(decision.passed)
        self.assertEqual(decision.status, "thresholds_not_frozen")

    def test_frozen_thresholds_evaluate_all_gates(self):
        thresholds = AcceptanceThresholds(
            min_mean_rank_ic=0.01,
            min_positive_ic_fraction=0.51,
            max_one_way_turnover=0.50,
            min_net_return=0.0,
            max_drawdown_abs=0.25,
            multiple_testing_method="declared-test-method",
            trial_registry_required=True,
        )
        metrics = {
            "mean_rank_ic": 0.02,
            "positive_ic_fraction": 0.60,
            "one_way_turnover": 0.30,
            "net_return": 0.05,
            "max_drawdown": -0.20,
        }
        self.assertTrue(
            evaluate_acceptance(
                metrics,
                thresholds,
                trial_registry_present=True,
            ).passed
        )
        self.assertFalse(
            evaluate_acceptance(
                metrics,
                thresholds,
                trial_registry_present=False,
            ).passed
        )


if __name__ == "__main__":
    unittest.main()
