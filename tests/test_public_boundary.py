import tempfile
import unittest
from pathlib import Path

from scripts.check_public_boundary import check_repository


class PublicBoundaryTests(unittest.TestCase):
    def test_clean_source_tree_passes(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "src").mkdir()
            (root / "src" / "model.py").write_text("x = 1\n", encoding="utf-8")
            self.assertEqual(check_repository(root), [])

    def test_database_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "portfolio.sqlite").write_bytes(b"not-real")
            violations = check_repository(root)
            self.assertTrue(any("forbidden binary" in v for v in violations))

    def test_private_key_marker_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "note.txt").write_text(
                "-----BEGIN " + "PRIVATE KEY-----\nredacted\n",
                encoding="utf-8",
            )
            violations = check_repository(root)
            self.assertTrue(any("private-key" in v for v in violations))

    def test_unapproved_csv_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "exports").mkdir()
            (root / "exports" / "positions.csv").write_text(
                "ticker,value\nTEST,1\n",
                encoding="utf-8",
            )
            violations = check_repository(root)
            self.assertTrue(any("CSV is outside approved" in v for v in violations))

    def test_example_csv_is_allowed(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "examples").mkdir()
            (root / "examples" / "fixture.csv").write_text(
                "ticker,value\nTEST,1\n",
                encoding="utf-8",
            )
            self.assertEqual(check_repository(root), [])


if __name__ == "__main__":
    unittest.main()
