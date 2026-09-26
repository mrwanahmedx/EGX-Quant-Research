import json
import unittest
from pathlib import Path


class EvidenceStatusTests(unittest.TestCase):
    def setUp(self):
        self.status = json.loads(
            Path("config/evidence_status.json").read_text(encoding="utf-8")
        )

    def test_real_modeling_remains_blocked(self):
        self.assertEqual(self.status["state"], "blocked")
        self.assertFalse(self.status["holdout_opened"])
        self.assertEqual(
            self.status["summary"]["model_approved_universe"],
            0,
        )

    def test_detailed_ranges_are_not_fabricated(self):
        self.assertFalse(
            self.status["detailed_range_manifest_available_in_repo"]
        )
        self.assertTrue(self.status["blocking_reasons"])


if __name__ == "__main__":
    unittest.main()
