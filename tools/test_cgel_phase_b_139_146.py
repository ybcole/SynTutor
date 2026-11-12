"""Source-citation, scope and page-ledger regressions for Cambridge Chapter 3 pp. 139–146."""
import json
from pathlib import Path
import unittest
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[1]
class Chapter3PastPerfectBatch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog=json.loads((ROOT/"grammar/rules/other.json").read_text(encoding="utf-8"))
        cls.rules=[r for r in cls.catalog if r["id"].startswith("OTH-") and 88<=int(r["id"][4:])<=117]
        cls.pages=json.loads((ROOT/"grammar/coverage/cgel_ledger.json").read_text(encoding="utf-8"))["pages"]
        cls.schema=json.loads((ROOT/"grammar/schema.json").read_text(encoding="utf-8"))
    def test_unique_contiguous_source_ids(self):
        self.assertEqual([r["id"] for r in self.rules],[f"OTH-{n:03d}" for n in range(88,118)])
        self.assertEqual(len({r["id"] for r in self.catalog}),len(self.catalog))
    def test_rules_are_schema_valid(self):
        validator=Draft202012Validator(self.schema)
        for rule in self.rules:
            self.assertEqual(list(validator.iter_errors(rule)),[],rule["id"])
            self.assertTrue(all(s["chapter"]==3 for s in rule["sources"]))
            self.assertTrue(all(139<=p<=146 for s in rule["sources"] for p in s["pages"]))
    def test_two_guarded_diagnostic_specs(self):
        constrained=[r for r in self.rules if r["rule_type"]=="constraint"]
        self.assertEqual(len(constrained),2)
        for rule in constrained:
            self.assertEqual(rule["diagnostic"]["detector"],"spec_only")
            self.assertGreaterEqual(len(rule["diagnostic"]["minimal_pairs"]),2)
            self.assertGreaterEqual(len(rule["diagnostic"]["false_positive_guards"]),3)
            self.assertGreaterEqual(len(rule["examples"]["incorrect"]),2)
        self.assertEqual(sum(r["rule_type"]=="classification" for r in self.rules),24)
        self.assertEqual(sum(r["rule_type"]=="descriptive_generalization" for r in self.rules),4)
    def test_all_eight_pages_have_source_evidence(self):
        cited={p for rule in self.rules for s in rule["sources"] for p in s["pages"]}
        self.assertEqual(cited,set(range(139,147)))
        for p in range(139,147):
            row=self.pages[p-1]
            self.assertEqual(row["status"],"extracted")
            self.assertEqual(row["evidence"],"sources/cambridge/chapter_03/PHASE_B_PP139_146_REPORT.md")
