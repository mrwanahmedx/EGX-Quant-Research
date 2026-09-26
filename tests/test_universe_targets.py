import unittest
from datetime import date, datetime, timezone

from egx_quant.targets import forward_return, residual_return
from egx_quant.universe import (
    MembershipRecord,
    membership_is_usable,
    require_point_in_time_membership,
)


class UniverseTargetTests(unittest.TestCase):
    def test_future_membership_publication_is_not_usable(self):
        record = MembershipRecord(
            canonical_security_id="EGX:A",
            effective_from=date(2025, 1, 1),
            effective_to=None,
            published_at=datetime(2026, 2, 1, tzinfo=timezone.utc),
            source="fixture",
        )
        decision_time = datetime(2026, 1, 15, tzinfo=timezone.utc)
        self.assertFalse(
            membership_is_usable(
                record,
                session_date=date(2026, 1, 15),
                decision_time=decision_time,
            )
        )
        with self.assertRaises(RuntimeError):
            require_point_in_time_membership(
                record,
                session_date=date(2026, 1, 15),
                decision_time=decision_time,
            )

    def test_residual_target_is_asset_minus_benchmark(self):
        asset = forward_return(100, 110)
        benchmark = forward_return(100, 104)
        self.assertAlmostEqual(residual_return(asset, benchmark), 0.06)


if __name__ == "__main__":
    unittest.main()
