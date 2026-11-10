"""Regression tests for Chapter 3 Phase B source candidate coverage."""
import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class Chapter3PhaseB(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rules=[x for x in json.loads((ROOT/"grammar/rules/morphology.json").read_text(encoding="utf-8")) if x["id"].startswith("MORPH-") and 24<=int(x["id"].split("-")[1])<=58]
        cls.ledger=json.loads((ROOT/"grammar/coverage/cgel_ledger.json").read_text(encoding="utf-8"))
    def test_new_rule_count_and_stable_ids(self):
        self.assertEqual(len(self.rules),35)
        self.assertEqual([r["id"] for r in self.rules],[f"MORPH-{n:03d}" for n in range(24,59)])
    def test_no_approval_or_automatic_activation(self):
        for r in self.rules:
            self.assertEqual(r["status"],"NEEDS_REVIEW")
            self.assertEqual(r["protocol_version"],"1.1")
            self.assertTrue(all(s["chapter"]==3 for s in r["sources"]))
    def test_all_constraints_are_explicitly_spec_only(self):
        constraints=[r for r in self.rules if r["rule_type"]=="constraint"]
        self.assertEqual(len(constraints),5)
        for r in constraints:
            self.assertEqual(r["diagnostic"]["detector"],"spec_only")
            self.assertGreaterEqual(len(r["examples"]["correct"]),2)
            self.assertGreaterEqual(len(r["examples"]["incorrect"]),2)
            self.assertGreaterEqual(len(r["diagnostic"]["minimal_pairs"]),2)
            self.assertGreaterEqual(len(r["diagnostic"]["false_positive_guards"]),2)
    def test_page_coverage_is_truthful(self):
        rows=self.ledger["pages"]
        self.assertTrue(all(rows[p-1]["status"]=="skipped_with_reason" for p in range(71,74)))
        self.assertTrue(all(rows[p-1]["status"]=="extracted" for p in range(74,91)))
        self.assertTrue(all(rows[p-1]["status"]=="extracted" for p in range(91,115)))
