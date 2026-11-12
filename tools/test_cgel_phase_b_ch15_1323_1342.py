"""Regression contracts for CGEL Ch15 printed pp. 1323–1342.

These tests check structure and nonactivation, not independent linguistic approval.
"""
import json
import unittest
from pathlib import Path
from tools.cgel_batch_gate import check_batch

ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = "sources/cambridge/chapter_15/PP1323_1342_AUDIT.json"


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


class Chapter15CoordinationBatch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audit = load(AUDIT_PATH)
        cls.ledger = load("grammar/coverage/cgel_ledger.json")["pages"]
        cls.rules = {r["id"]: r for r in load("grammar/rules/clauses.json")}

    def test_full_consecutive_source_audit(self):
        self.assertEqual(
            [item["page"] for item in self.audit["page_checks"]],
            list(range(1323, 1343)),
        )
        self.assertEqual(check_batch(self.audit), [])
        for item in self.audit["page_checks"]:
            page = item["page"]
            self.assertEqual(self.ledger[page - 1]["status"], "extracted")
            self.assertTrue(item["source_checked"])
            self.assertTrue(item["exceptions_checked"])
            self.assertFalse(item["unresolved_items"])

    def test_new_records_have_source_grounding_and_no_runtime_activation(self):
        ids = self.audit["added_rule_ids"]
        self.assertEqual(len(ids), 41)
        self.assertEqual(ids[0], "CLS-996")
        self.assertEqual(ids[-1], "CLS-1036")
        for rule_id in ids:
            with self.subTest(rule_id=rule_id):
                rule = self.rules[rule_id]
                self.assertEqual(rule["status"], "NEEDS_REVIEW")
                self.assertGreaterEqual(len(rule["examples"]["correct"]), 2)
                self.assertTrue(all(
                    example["origin"] == "ai_authored"
                    for example in rule["examples"]["correct"]
                ))
                self.assertTrue(all(
                    mapping["relation"] == "unverified"
                    for mapping in rule["burton_roberts_mapping"]
                ))
                for source in rule["sources"]:
                    self.assertEqual(source["chapter"], 15)
                    self.assertEqual(
                        source["pdf_pages"], [p + 20 for p in source["pages"]]
                    )
                if rule["rule_type"] == "constraint":
                    self.assertEqual(rule["diagnostic"]["detector"], "spec_only")
                    self.assertEqual(len(rule["examples"]["incorrect"]), 2)
                    self.assertGreaterEqual(len(rule["diagnostic"]["false_positive_guards"]), 2)
                    self.assertGreaterEqual(len(rule["diagnostic"]["minimal_pairs"]), 2)
                else:
                    self.assertIsNone(rule["diagnostic"])
                    self.assertFalse(rule["examples"]["incorrect"])

    def test_nonbasic_structures_not_mislabelled_universal_errors(self):
        concepts = {
            self.rules[rule_id]["concept"]: self.rules[rule_id]
            for rule_id in self.audit["added_rule_ids"]
        }
        for name in (
            "Mixed-category adjunct coordination",
            "Coordination across unlike structural levels",
            "Gapped coordination with a medial predicator gap",
            "Right nonce-constituent coordination",
            "Structural parallelism in right nonce-constituent coordination",
            "Negation scope and nonce-constituent tree analysis",
        ):
            with self.subTest(concept=name):
                self.assertNotEqual(concepts[name]["rule_type"], "constraint")
                self.assertIsNone(concepts[name]["diagnostic"])

    def test_source_scoped_constraints_only(self):
        constraints = {
            self.rules[rule_id]["concept"]: self.rules[rule_id]
            for rule_id in self.audit["added_rule_ids"]
            if self.rules[rule_id]["rule_type"] == "constraint"
        }
        self.assertEqual(set(constraints), {
            "Basic coordination requires equivalent syntactic functions",
            "Infinitival and gerund-participial clause coordination restriction",
            "Singular-noun coordination cannot satisfy a plural determinative",
        })
        for rule in constraints.values():
            for index, wrong in enumerate(rule["examples"]["incorrect"]):
                self.assertTrue(
                    rule["diagnostic"]["minimal_pairs"][index].startswith(
                        wrong["text"] + " ||| "
                    )
                )


if __name__ == "__main__":
    unittest.main()
