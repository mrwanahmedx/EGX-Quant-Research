import unittest
from datetime import date, datetime, timezone

from egx_quant.security_master import (
    SecurityMasterRecord,
    resolve_symbol,
    sector_as_of,
)


UTC = timezone.utc


class SecurityMasterTests(unittest.TestCase):
    def record(self, **overrides):
        values = dict(
            canonical_security_id="EGX:A",
            symbol="AAA",
            effective_from=date(2025, 1, 1),
            effective_to=None,
            published_at=datetime(2025, 1, 1, tzinfo=UTC),
            source="fixture",
            mapping_confidence="verified",
            sector="Banks",
            sector_effective_from=date(2025, 1, 1),
            sector_published_at=datetime(2025, 1, 1, tzinfo=UTC),
        )
        values.update(overrides)
        return SecurityMasterRecord(**values)

    def test_point_in_time_symbol_resolution(self):
        record = self.record()
        resolved = resolve_symbol(
            [record],
            symbol="AAA",
            session_date=date(2026, 1, 10),
            decision_time=datetime(2026, 1, 10, 9, tzinfo=UTC),
        )
        self.assertEqual(resolved.canonical_security_id, "EGX:A")

    def test_future_mapping_is_rejected(self):
        record = self.record(
            published_at=datetime(2026, 2, 1, tzinfo=UTC)
        )
        with self.assertRaises(RuntimeError):
            resolve_symbol(
                [record],
                symbol="AAA",
                session_date=date(2026, 1, 10),
                decision_time=datetime(2026, 1, 10, 9, tzinfo=UTC),
            )

    def test_ambiguous_identity_is_rejected(self):
        first = self.record(canonical_security_id="EGX:A")
        second = self.record(canonical_security_id="EGX:B")
        with self.assertRaises(RuntimeError):
            resolve_symbol(
                [first, second],
                symbol="AAA",
                session_date=date(2026, 1, 10),
                decision_time=datetime(2026, 1, 10, 9, tzinfo=UTC),
            )

    def test_sector_must_be_effective_and_published(self):
        record = self.record()
        self.assertEqual(
            sector_as_of(
                record,
                session_date=date(2026, 1, 10),
                decision_time=datetime(2026, 1, 10, 9, tzinfo=UTC),
            ),
            "Banks",
        )
        future_sector = self.record(
            sector_published_at=datetime(2026, 2, 1, tzinfo=UTC)
        )
        with self.assertRaises(RuntimeError):
            sector_as_of(
                future_sector,
                session_date=date(2026, 1, 10),
                decision_time=datetime(2026, 1, 10, 9, tzinfo=UTC),
            )


if __name__ == "__main__":
    unittest.main()
