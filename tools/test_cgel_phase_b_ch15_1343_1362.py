"""Phase B source-boundary, case, and nonactivation regressions for final Ch15 batch."""
import json
import unittest
from pathlib import Path
from tools.cgel_batch_gate import check_batch

ROOT = Path(__file__).resolve().parents[1]
def load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))

class Chapter15FinalSourceBatch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = load("sources/cambridge/chapter_15/PP1343_1362_AUDIT.json")
        cls.ledger = load("grammar/coverage/cgel_ledger.json")["pages"]
        cls.rules = {r["id"]: r for r in load("grammar/rules/clauses.json")}

    def test_entire_chapter_has_no_unprocessed_pages(self):
        chapter = [p for p in self.ledger if p["chapter"] == 15]
        self.assertEqual(len(chapter), 90)
        self.assertEqual(sum(p["status"] == "extracted" for p in chapter), 88)
        self.assertEqual(sum(p["status"] == "skipped_with_reason" for p in chapter), 2)
        self.assertTrue(all(p["status"] != "unprocessed" for p in chapter))

    def test_complete_consecutive_source_manifest(self):
        self.assertEqual([p["page"] for p in self.manifest["page_checks"]], list(range(1343, 1363)))
        self.assertEqual(check_batch(self.manifest), [])
        for item in self.manifest["page_checks"]:
            self.assertEqual(item["status"], "extracted")
            self.assertTrue(item["source_checked"])
            self.assertTrue(item["exceptions_checked"])
            self.assertTrue(item["layout_checked"])
            self.assertFalse(item["unresolved_items"])

    def test_source_ids_and_nonactivation(self):
        ids = self.manifest["added_rule_ids"]
        self.assertEqual(len(ids), 59)
        self.assertEqual(ids[0], "CLS-1037")
        self.assertEqual(ids[-1], "CLS-1095")
        for rid in ids:
            with self.subTest(rule_id=rid):
                rule = self.rules[rid]
                self.assertEqual(rule["status"], "NEEDS_REVIEW")
                self.assertTrue(all(m["relation"] == "unverified" for m in rule["burton_roberts_mapping"]))
                self.assertGreaterEqual(len(rule["examples"]["correct"]), 2)
                self.assertTrue(all(ex["origin"] == "ai_authored" for ex in rule["examples"]["correct"]))
                for source in rule["sources"]:
                    self.assertEqual(source["chapter"], 15)
                    self.assertEqual(source["pdf_pages"], [p + 20 for p in source["pages"]])
                if rule["rule_type"] == "constraint":
                    self.assertEqual(rule["diagnostic"]["detector"], "spec_only")
                    self.assertGreaterEqual(len(rule["examples"]["incorrect"]), 2)
                    self.assertGreaterEqual(len(rule["diagnostic"]["minimal_pairs"]), 2)
                    self.assertGreaterEqual(len(rule["diagnostic"]["false_positive_guards"]), 2)
                else:
                    self.assertIsNone(rule["diagnostic"])
                    self.assertFalse(rule["examples"]["incorrect"])

    def test_legitimate_special_syntax_is_not_declared_a_general_error(self):
        by_concept = {self.rules[rid]["concept"]: self.rules[rid] for rid in self.manifest["added_rule_ids"]}
        for concept in (
            "Delayed right constituent coordination",
            "Narrow scope of postposed coordinate",
            "Supplementation versus dependency and coordination",
            "Supplementary apposition and substitution entailment",
            "Main-clause supplements and content-supplying explanation",
            "Coordinator-introduced material can be supplementary",
            "Exceptional agreement sensitivity of coordinated supplements",
            "Or-introduced supplementary reformulation",
        ):
            with self.subTest(concept=concept):
                self.assertNotEqual(by_concept[concept]["rule_type"], "constraint")
                self.assertIsNone(by_concept[concept]["diagnostic"])

    def test_anchor_constraint_is_spec_only(self):
        rules = [self.rules[rid] for rid in self.manifest["added_rule_ids"] if self.rules[rid]["rule_type"] == "constraint"]
        self.assertEqual(len(rules), 1)
        rule = rules[0]
        self.assertEqual(rule["concept"], "Supplementary relative clause requires an antecedent anchor")
        for bad, pair in zip(rule["examples"]["incorrect"], rule["diagnostic"]["minimal_pairs"]):
            self.assertTrue(pair.startswith(bad["text"] + " ||| "))

if __name__ == "__main__":
    unittest.main()
