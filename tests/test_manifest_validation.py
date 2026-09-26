import unittest

from egx_quant.manifest_validation import (
    assert_manifest_code_ref,
    validate_frozen_evidence_manifest,
)


class FrozenManifestValidationTests(unittest.TestCase):
    def manifest(self, **overrides):
        value = {
            "kind": "preholdout-data-evidence-manifest",
            "decision_time": "2026-01-31T23:59:59+02:00",
            "code_ref": "abc123",
            "record_count": 2,
            "eligible_record_count": 1,
            "blocked_record_count": 1,
            "data_evidence_fingerprint": "a" * 64,
            "modeling_authorized": False,
        }
        value.update(overrides)
        return value

    def test_valid_blocked_manifest_passes(self):
        validate_frozen_evidence_manifest(self.manifest())

    def test_authorization_cannot_disagree_with_counts(self):
        with self.assertRaises(ValueError):
            validate_frozen_evidence_manifest(
                self.manifest(modeling_authorized=True)
            )

    def test_counts_must_reconcile(self):
        with self.assertRaises(ValueError):
            validate_frozen_evidence_manifest(
                self.manifest(record_count=3)
            )

    def test_code_ref_must_match_requested_generation(self):
        with self.assertRaises(RuntimeError):
            assert_manifest_code_ref(self.manifest(), "different")


if __name__ == "__main__":
    unittest.main()
