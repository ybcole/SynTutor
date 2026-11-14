import unittest

from findings import build_unified_findings


class UnifiedFindingsTests(unittest.TestCase):
    def test_legacy_and_candidate_are_separate_authorities(self):
        details = {
            "n4": {
                "status": "error",
                "constraint": "C-SUBJECT-AGREEMENT",
                "span": [1, 2],
                "canonical_node_id": "w-reads",
                "canonical_binding": {"status": "mapped", "node_id": "w-reads"},
                "remediation": {
                    "violation": "The subject and verb do not match.",
                    "suggested_fix": "Change 'reads' to 'read'.",
                },
            },
            "n1": {"status": "valid"},
        }
        candidate = {
            "items": [{
                "finding_id": "f001",
                "rule_id": "MORPH-109",
                "tree_binding": {"affected_node_id": "w-paniced"},
                "explanation": {"short": "Add k before ed."},
                "source_pages": [1598],
            }]
        }
        result = build_unified_findings(details, candidate)
        self.assertFalse(result["production_enabled"])
        self.assertFalse(result["whole_sentence_certified"])
        self.assertEqual(result["counts"]["total"], 2)
        self.assertEqual(result["counts"]["legacy"], 1)
        self.assertEqual(result["counts"]["candidate"], 1)
        legacy = next(row for row in result["findings"] if row["authority"] == "legacy_matrix")
        candidate_row = next(row for row in result["findings"] if row["authority"] == "cambridge_candidate")
        self.assertEqual(legacy["claim_status"], "legacy_diagnostic_not_book_verified")
        self.assertTrue(legacy["production_path"])
        self.assertEqual(legacy["canonical_node_id"], "w-reads")
        self.assertEqual(candidate_row["claim_status"],
                         "candidate_observation_not_verified_error")
        self.assertFalse(candidate_row["production_path"])
        self.assertEqual(candidate_row["canonical_node_id"], "w-paniced")

    def test_no_findings_is_empty(self):
        result = build_unified_findings({}, None)
        self.assertEqual(result["findings"], [])
        self.assertEqual(result["counts"]["total"], 0)


if __name__ == "__main__":
    unittest.main()
