import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

from egx_quant.index_reviews import (
    IndexReviewEvent,
    ReviewMember,
    apply_review_event,
    canonical_identity_complete,
    load_index_review_events,
)


class IndexReviewTests(unittest.TestCase):
    def test_committed_review_ledger_is_dated_but_identity_unresolved(self):
        events = load_index_review_events(
            "evidence/index_reviews/egx30_review_events_2024_2025.json"
        )
        self.assertEqual(len(events), 4)
        self.assertTrue(
            all(event.published_date <= event.effective_date for event in events)
        )
        self.assertTrue(
            all(not canonical_identity_complete(event) for event in events)
        )

    def test_unresolved_review_cannot_be_applied(self):
        event = load_index_review_events(
            "evidence/index_reviews/egx30_review_events_2024_2025.json"
        )[0]
        with self.assertRaises(RuntimeError):
            apply_review_event({"EGX:X"}, event, as_of=event.effective_date)

    def test_verified_review_applies_only_on_effective_date(self):
        event = IndexReviewEvent(
            index_id="EGX30",
            published_date=date(2025, 1, 29),
            effective_date=date(2025, 2, 2),
            source_url="https://example.com",
            source_type="official",
            additions=(ReviewMember("A", "EGX:A", "verified"),),
            deletions=(ReviewMember("B", "EGX:B", "verified"),),
        )
        before = apply_review_event(
            {"EGX:B", "EGX:C"},
            event,
            as_of=date(2025, 2, 1),
        )
        self.assertEqual(before, {"EGX:B", "EGX:C"})
        after = apply_review_event(
            {"EGX:B", "EGX:C"},
            event,
            as_of=date(2025, 2, 2),
        )
        self.assertEqual(after, {"EGX:A", "EGX:C"})


if __name__ == "__main__":
    unittest.main()
