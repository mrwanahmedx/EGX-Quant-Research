import unittest
from datetime import date, timedelta

from egx_quant.walkforward import (
    LabeledSample,
    build_development_folds,
    purge_overlapping_labels,
)


class WalkForwardTests(unittest.TestCase):
    def sessions(self, count):
        start = date(2025, 1, 1)
        return [start + timedelta(days=i) for i in range(count)]

    def test_session_fold_has_purge_and_embargo(self):
        folds = build_development_folds(
            self.sessions(30),
            train_sessions=10,
            validation_sessions=5,
            purge_sessions=3,
            embargo_sessions=2,
            expanding=True,
        )
        self.assertTrue(folds)
        first = folds[0]
        self.assertEqual(len(first.train_sessions), 10)
        self.assertEqual(len(first.purge_sessions), 3)
        self.assertEqual(len(first.validation_sessions), 5)
        self.assertEqual(len(first.embargo_sessions), 2)
        self.assertLess(first.train_sessions[-1], first.validation_start)

    def test_holdout_session_is_rejected(self):
        sessions = [
            date(2026, 1, 30),
            date(2026, 1, 31),
            date(2026, 2, 1),
        ]
        with self.assertRaises(RuntimeError):
            build_development_folds(
                sessions,
                train_sessions=1,
                validation_sessions=1,
                purge_sessions=0,
            )

    def test_overlapping_forward_labels_are_purged(self):
        validation_start = date(2025, 3, 1)
        samples = [
            LabeledSample("A", date(2025, 1, 1), date(2025, 2, 20)),
            LabeledSample("B", date(2025, 1, 2), date(2025, 3, 1)),
            LabeledSample("C", date(2025, 1, 3), date(2025, 3, 5)),
        ]
        kept = purge_overlapping_labels(
            samples,
            validation_start=validation_start,
        )
        self.assertEqual([sample.canonical_security_id for sample in kept], ["A"])


if __name__ == "__main__":
    unittest.main()
