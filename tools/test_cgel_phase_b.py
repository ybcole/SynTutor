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

    def test_chapter3_123_130_source_coverage(self):
        other=json.loads((ROOT/"grammar/rules/other.json").read_text(encoding="utf-8"))
        new=[r for r in other if r["id"].startswith("OTH-") and 47<=int(r["id"].split("-")[1])<=66]
        self.assertEqual(len(new),20)
        self.assertEqual([r["id"] for r in new],[f"OTH-{n:03d}" for n in range(47,67)])
        self.assertTrue(all(r["rule_type"]=="classification" for r in new))
        self.assertTrue(all(r["status"]=="NEEDS_REVIEW" for r in new))
        self.assertEqual(set(range(123,131)),set(p for r in new for s in r["sources"] for p in s["pages"]))
        self.assertTrue(all(self.ledger["pages"][p-1]["status"]=="extracted" for p in range(123,131)))

    def test_chapter3_131_138_source_coverage(self):
        other=json.loads((ROOT/"grammar/rules/other.json").read_text(encoding="utf-8"))
        fresh=[r for r in other if r["id"].startswith("OTH-") and 67<=int(r["id"].split("-")[1])<=87]
        self.assertEqual(len(fresh),21)
        self.assertEqual([r["id"] for r in fresh],[f"OTH-{n:03d}" for n in range(67,88)])
        self.assertTrue(all(r["rule_type"]=="classification" for r in fresh))
        self.assertTrue(all(r["diagnostic"] is None for r in fresh))
        self.assertEqual(set(range(131,139)),set(p for r in fresh for s in r["sources"] for p in s["pages"]))
        self.assertTrue(all(self.ledger["pages"][p-1]["status"]=="extracted" for p in range(131,139)))
