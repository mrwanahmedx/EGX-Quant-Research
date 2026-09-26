import unittest
from datetime import date, datetime, timezone

from egx_quant.corporate_actions import (
    CorporateAction,
    action_known_by,
    require_target_window_resolved,
)


UTC = timezone.utc


class CorporateActionTests(unittest.TestCase):
    def test_unresolved_action_blocks_target_window(self):
        action = CorporateAction(
            action_id="ca-1",
            canonical_security_id="EGX:A",
            action_type="split",
            effective_date=date(2025, 1, 15),
            published_at=datetime(2025, 1, 10, tzinfo=UTC),
            source_url="https://example.com",
            status="unresolved",
        )
        with self.assertRaises(RuntimeError):
            require_target_window_resolved(
                [action],
                canonical_security_id="EGX:A",
                entry_date=date(2025, 1, 1),
                exit_date=date(2025, 1, 31),
            )

    def test_resolved_action_requires_adjustment_basis(self):
        with self.assertRaises(ValueError):
            CorporateAction(
                action_id="ca-1",
                canonical_security_id="EGX:A",
                action_type="split",
                effective_date=date(2025, 1, 15),
                published_at=datetime(2025, 1, 10, tzinfo=UTC),
                source_url="https://example.com",
                status="resolved",
            )

    def test_resolved_action_allows_target_window(self):
        action = CorporateAction(
            action_id="ca-1",
            canonical_security_id="EGX:A",
            action_type="split",
            effective_date=date(2025, 1, 15),
            published_at=datetime(2025, 1, 10, tzinfo=UTC),
            source_url="https://example.com",
            status="resolved",
            adjustment_basis="split_adjusted",
        )
        require_target_window_resolved(
            [action],
            canonical_security_id="EGX:A",
            entry_date=date(2025, 1, 1),
            exit_date=date(2025, 1, 31),
        )
        self.assertTrue(
            action_known_by(
                action,
                decision_time=datetime(2025, 1, 11, tzinfo=UTC),
            )
        )


if __name__ == "__main__":
    unittest.main()
