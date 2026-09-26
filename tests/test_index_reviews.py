import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

from egx_quant.index_reviews import (
    IndexReviewEvent,
    MembershipDelta,
    ReviewMember,
    apply_review_event,
    canonical_identity_complete,
    load_index_review_events,
    materialize_membership_deltas,
    reconstruct_membership,
    unresolved_identity_count,
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
        self.assertGreater(unresolved_identity_count(events), 0)

    def test_unresolved_review_cannot_be_applied(self):
        event = load_index_review_events(
            "evidence/index_reviews/egx30_review_events_2024_2025.json"
        )[0]
        with self.assertRaises(RuntimeError):
            apply_review_event({"EGX:X"}, event, as_of=event.effective_date)

    def test_current_ledger_blocks_strict_delta_materialization(self):
        events = load_index_review_events(
            "evidence/index_reviews/egx30_review_events_2024_2025.json"
        )
        with self.assertRaises(RuntimeError):
            materialize_membership_deltas(
                events,
                decision_date=date(2026, 1, 31),
                strict=True,
            )

    def test_future_review_is_not_visible(self):
        event = IndexReviewEvent(
            index_id="EGX30",
            published_date=date(2025, 7, 29),
            effective_date=date(2025, 8, 3),
            source_url="https://example.com",
            source_type="official",
            additions=(ReviewMember("A", "EGX:A", "verified"),),
            deletions=(),
        )
        deltas = materialize_membership_deltas(
            [event],
            decision_date=date(2025, 7, 28),
        )
        self.assertEqual(deltas, ())

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

        deltas = materialize_membership_deltas(
            [event],
            decision_date=date(2025, 1, 30),
        )
        self.assertEqual(len(deltas), 2)

    def test_reconstruction_applies_deltas_to_seed(self):
        deltas = [
            MembershipDelta(
                index_id="EGX30",
                effective_date=date(2025, 2, 2),
                canonical_security_id="EGX:A",
                action="add",
                source_url="https://example.com",
                published_date=date(2025, 1, 29),
            ),
            MembershipDelta(
                index_id="EGX30",
                effective_date=date(2025, 2, 2),
                canonical_security_id="EGX:B",
                action="delete",
                source_url="https://example.com",
                published_date=date(2025, 1, 29),
            ),
        ]
        members = reconstruct_membership(
            seed_members=["EGX:B", "EGX:C"],
            deltas=deltas,
            index_id="EGX30",
            as_of=date(2025, 2, 3),
        )
        self.assertEqual(members, frozenset({"EGX:A", "EGX:C"}))

    def test_loader_rejects_duplicate_review_grain(self):
        row = {
            "index_id": "EGX30",
            "published_date": "2025-01-29",
            "effective_date": "2025-02-02",
            "source_url": "https://example.com",
            "source_type": "official",
            "additions": [],
            "deletions": [],
        }
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "reviews.json"
            path.write_text(json.dumps([row, row]), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_index_review_events(path)


if __name__ == "__main__":
    unittest.main()
