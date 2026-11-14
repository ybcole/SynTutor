import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from audit_br_native_catalog import audit_book_corpus  # noqa: E402


class FinalD1DispositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(
            (ROOT / "docs/planning/br_final_d1_dispositions.json").read_text(encoding="utf-8"))
        cls.audit = audit_book_corpus(252)

    def test_every_audit_instance_has_one_disposition(self):
        audit_keys = {(row["record_id"], row["path"], row["signature"])
                      for row in self.audit["uncovered_instances"]}
        manifest_keys = {(row["record_id"], row["path"], row["signature"])
                         for row in self.data["uncovered_instances"]}
        self.assertEqual(len(manifest_keys), 130)
        self.assertEqual(manifest_keys, audit_keys)

    def test_all_252_source_records_have_a_record_decision(self):
        self.assertEqual(len(self.data["record_decisions"]), 252)
        ids = {row["record_id"] for row in self.data["record_decisions"]}
        self.assertEqual(len(ids), 252)

    def test_disposition_counts_and_reasons(self):
        counts = self.data["counts"]["dispositions"]
        self.assertEqual(counts["chapter_only"], 126)
        self.assertEqual(counts["source_anomaly"], 4)
        self.assertEqual(counts["chapter_only"], 126)
        self.assertEqual(counts.get("unresolved", 0), 0)
        for row in self.data["uncovered_instances"]:
            self.assertTrue(row["reason"])
            self.assertIn(row["disposition"],
                          {"chapter_only", "source_anomaly", "supported_final_rule", "unresolved"})
            if row["disposition"] in {"chapter_only", "source_anomaly"}:
                self.assertIsNone(row["runtime_rule"])
            self.assertFalse(row["independently_verified"])

    def test_manifest_does_not_claim_independent_review(self):
        policy = self.data["policy"]
        self.assertTrue(policy["do_not_claim_independent_review"])
        self.assertTrue(policy["unsupported_must_remain_unresolved"])
        self.assertFalse(self.data["pdf_required"])


if __name__ == "__main__":
    unittest.main()
