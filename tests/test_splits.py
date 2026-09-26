import unittest
from datetime import date, datetime, timezone

from egx_quant.splits import (
    HOLDOUT_END,
    HOLDOUT_START,
    SHADOW_START,
    assert_publication_available,
    classify_date,
    purged_walk_forward,
)


class SplitTests(unittest.TestCase):
    def test_frozen_regions(self):
        self.assertEqual(classify_date(date(2026, 1, 31)), "development")
        self.assertEqual(classify_date(HOLDOUT_START), "holdout")
        self.assertEqual(classify_date(HOLDOUT_END), "holdout")
        self.assertEqual(classify_date(date(2026, 7, 15)), "gap")
        self.assertEqual(classify_date(SHADOW_START), "shadow")

    def test_future_publication_is_rejected(self):
        as_of = datetime(2026, 1, 15, 10, tzinfo=timezone.utc)
        future = datetime(2026, 1, 16, 9, tzinfo=timezone.utc)
        with self.assertRaises(ValueError):
            assert_publication_available(as_of, future)

    def test_purge_separates_train_and_validation(self):
        folds = list(
            purged_walk_forward(
                date(2025, 1, 1),
                date(2025, 12, 31),
                train_days=90,
                validation_days=30,
                purge_days=63,
            )
        )
        self.assertTrue(folds)
        for fold in folds:
            self.assertGreater((fold.validation_start - fold.train_end).days, 63)


if __name__ == "__main__":
    unittest.main()
