import unittest

from authority import build_authority_manifest


class AuthorityManifestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = build_authority_manifest(
            br_status="normalized", runtime_registry={"active_rules": []})

    def test_structure_authority_is_br_not_benepar(self):
        structure = self.manifest["structure"]
        self.assertEqual(structure["authority"], "burton_roberts")
        self.assertTrue(structure["derived"])
        self.assertFalse(structure["book_verified"])

    def test_legacy_detector_is_labeled_diagnostic(self):
        detection = self.manifest["detection"]
        self.assertEqual(detection["authority"], "legacy_matrix")
        self.assertFalse(detection["book_verified"])
        self.assertGreater(detection["legacy_rulebook_rules"], 100)

    def test_cambridge_runtime_is_fail_closed(self):
        cambridge = self.manifest["cambridge"]
        self.assertEqual(cambridge["runtime_enabled"], 0)
        self.assertTrue(cambridge["candidate_only"])
        self.assertGreaterEqual(cambridge["diagnostic_specs"], 204)
        self.assertGreaterEqual(cambridge["constraint_specs"], 203)


    def test_repository_pilot_is_owner_waived_not_independent(self):
        manifest = build_authority_manifest(br_status="normalized")
        self.assertEqual(manifest["cambridge"]["runtime_enabled"], 193)
        self.assertFalse(manifest["cambridge"]["candidate_only"])

    def test_channels_are_explicit(self):
        explanations = self.manifest["explanations"]
        self.assertEqual(explanations["structural"], "B-R only")
        self.assertEqual(explanations["grammatical"], "Cambridge only")
        self.assertEqual(explanations["remediation"], "Cambridge only")
        self.assertEqual(explanations["legacy_prose"],
                         "withheld when shared evidence exists")


if __name__ == "__main__":
    unittest.main()
