import unittest
from datetime import date

from egx_quant.quality import (
    OHLCVRecord,
    bar_issues,
    detect_close_discontinuities,
    overlap_conflicts,
    profile_quality,
)


class QualityTests(unittest.TestCase):
    def row(self, **overrides):
        values = dict(
            canonical_security_id="EGX:A",
            session_date=date(2025, 1, 1),
            open=10.0,
            high=11.0,
            low=9.0,
            close=10.5,
            volume=1000.0,
            source="source-a",
        )
        values.update(overrides)
        return OHLCVRecord(**values)

    def test_impossible_bar_is_flagged_without_mutation(self):
        row = self.row(high=9.5, close=10.5)
        issues = bar_issues(row)
        self.assertTrue(
            any(issue.issue_type == "close_outside_range" for issue in issues)
        )
        self.assertEqual(row.high, 9.5)
        self.assertEqual(row.close, 10.5)

    def test_duplicate_source_grain_is_counted(self):
        row = self.row()
        report = profile_quality([row, row])
        self.assertEqual(
            report["issue_counts"]["duplicate_source_grain"],
            1,
        )

    def test_discontinuity_is_flag_not_automatic_repair(self):
        rows = [
            self.row(session_date=date(2025, 1, 1), close=10),
            self.row(session_date=date(2025, 1, 2), close=5),
        ]
        flags = detect_close_discontinuities(
            rows,
            absolute_return_threshold=0.30,
        )
        self.assertEqual(len(flags), 1)
        self.assertAlmostEqual(flags[0].absolute_return, 0.5)

    def test_overlap_conflict_reports_fields(self):
        left = [self.row(source="a", close=10.0)]
        right = [self.row(source="b", close=12.0, high=12.5)]
        issues = overlap_conflicts(
            left,
            right,
            relative_tolerance=0.01,
        )
        self.assertEqual(len(issues), 1)
        self.assertIn("close", issues[0].details)

    def test_overlap_tolerance_is_explicit(self):
        with self.assertRaises(ValueError):
            overlap_conflicts([], [], relative_tolerance=-0.1)


if __name__ == "__main__":
    unittest.main()
