import json
import tempfile
import unittest
from pathlib import Path

from egx_quant.readiness_snapshot import build_readiness_snapshot, write_readiness_snapshot


class ReadinessSnapshotTests(unittest.TestCase):
    def test_current_repository_fails_closed(self):
        snapshot = build_readiness_snapshot(generated_at="2026-09-26T00:00:00Z")
        self.assertFalse(snapshot["modeling_authorized"])
        self.assertGreater(snapshot["blocker_count"], 0)
        ids = {check["check_id"] for check in snapshot["checks"]}
        self.assertIn("exact_quarantine_register", ids)
        self.assertIn("security_master", ids)
        self.assertIn("frozen_evidence_manifest", ids)

    def test_snapshot_serializes_deterministically_for_fixed_timestamp(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "snapshot.json"
            payload = write_readiness_snapshot(
                path,
                generated_at="2026-09-26T00:00:00Z",
            )
            loaded = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(payload, loaded)
            self.assertEqual(loaded["generated_at"], "2026-09-26T00:00:00Z")


if __name__ == "__main__":
    unittest.main()
