"""CGEL Chapter 3 progressive aspectuality: source/ledger/schema regression, printed pp.163–170."""
from pathlib import Path
import json
import unittest
from collections import Counter
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[1]
START,END=188,235
class Cambridge163170(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog=json.loads((ROOT/"grammar/rules/other.json").read_text(encoding="utf-8"))
        cls.rules=[r for r in cls.catalog if r["id"].startswith("OTH-") and START<=int(r["id"][4:])<=END]
        cls.pages=json.loads((ROOT/"grammar/coverage/cgel_ledger.json").read_text(encoding="utf-8"))["pages"]
        cls.schema=json.loads((ROOT/"grammar/schema.json").read_text(encoding="utf-8"))
    def test_unique_sequential_ids(self):
        self.assertEqual([r["id"] for r in self.rules],[f"OTH-{n:03d}" for n in range(START,END+1)])
        self.assertEqual(len({r["id"] for r in self.catalog}),len(self.catalog))
    def test_page_evidence_in_range(self):
        cited={p for r in self.rules for s in r["sources"] for p in s["pages"]}
        self.assertEqual(cited,set(range(163,171)))
        for p in range(163,171):
            row=self.pages[p-1]
            self.assertEqual(row["status"],"extracted")
            self.assertEqual(row["evidence"],"sources/cambridge/chapter_03/PHASE_B_PP163_170_REPORT.md")
            self.assertTrue((ROOT/row["evidence"]).is_file())
    def test_schema_original_english_and_exception_guards(self):
        v=Draft202012Validator(self.schema)
        for rule in self.rules:
            self.assertEqual(list(v.iter_errors(rule)),[],rule["id"])
            self.assertTrue(all(s["chapter"]==3 for s in rule["sources"]))
            self.assertGreaterEqual(len(rule["examples"]["correct"]),2)
            self.assertTrue(all(e["origin"]=="ai_authored" for e in rule["examples"]["correct"]))
        self.assertEqual(Counter(r["rule_type"] for r in self.rules),
                         {"classification":46,"constraint":1,"descriptive_generalization":1})
        d=[r for r in self.rules if r["rule_type"]=="constraint"]
        self.assertEqual(len(d),1)
        self.assertEqual(d[0]["diagnostic"]["detector"],"spec_only")
        self.assertGreaterEqual(len(d[0]["examples"]["incorrect"]),2)
        self.assertGreaterEqual(len(d[0]["diagnostic"]["minimal_pairs"]),2)
        self.assertGreaterEqual(len(d[0]["diagnostic"]["false_positive_guards"]),4)
        for r in self.rules:
            if r["rule_type"]!="constraint":
                self.assertIsNone(r["diagnostic"])
    def test_chapter_three_retains_extracted_pages(self):
        self.assertGreaterEqual(sum(p["chapter"]==3 and p["status"]=="extracted" for p in self.pages),97)
