"""Source integrity and incremental CGEL coverage regression for Chapter 3 pp. 171–178."""
from pathlib import Path
from collections import Counter
import json
import unittest
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[1]
START,END=236,286
class Cambridge171178(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog=json.loads((ROOT/"grammar/rules/other.json").read_text(encoding="utf-8"))
        cls.rules=[r for r in cls.catalog if r["id"].startswith("OTH-") and START<=int(r["id"][4:])<=END]
        cls.pages=json.loads((ROOT/"grammar/coverage/cgel_ledger.json").read_text(encoding="utf-8"))["pages"]
        cls.schema=json.loads((ROOT/"grammar/schema.json").read_text(encoding="utf-8"))
    def test_contiguous_unique_ids(self):
        self.assertEqual([r["id"] for r in self.rules],[f"OTH-{n:03d}" for n in range(START,END+1)])
        self.assertEqual(len({r["id"] for r in self.catalog}),len(self.catalog))
    def test_source_page_provenance(self):
        cited={p for r in self.rules for s in r["sources"] for p in s["pages"]}
        self.assertEqual(cited,set(range(171,179)))
        for p in range(171,179):
            row=self.pages[p-1]
            self.assertEqual(row["status"],"extracted")
            self.assertEqual(row["evidence"],"sources/cambridge/chapter_03/PHASE_B_PP171_178_REPORT.md")
            self.assertTrue((ROOT/row["evidence"]).is_file())
    def test_schema_and_original_examples(self):
        validator=Draft202012Validator(self.schema)
        self.assertEqual(Counter(r["rule_type"] for r in self.rules),{"classification":51})
        for rule in self.rules:
            self.assertFalse(list(validator.iter_errors(rule)),rule["id"])
            self.assertTrue(all(s["chapter"]==3 for s in rule["sources"]))
            self.assertGreaterEqual(len(rule["examples"]["correct"]),2)
            self.assertTrue(all(ex["origin"]=="ai_authored" for ex in rule["examples"]["correct"]))
            self.assertIsNone(rule["diagnostic"])
            self.assertGreaterEqual(len(rule["exceptions"]),1)
    def test_chapter_three_retains_extracted_pages(self):
        self.assertGreaterEqual(sum(p["chapter"]==3 and p["status"]=="extracted" for p in self.pages),105)
