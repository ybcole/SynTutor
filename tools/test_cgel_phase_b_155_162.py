"""Source, schema and stable incremental coverage checks for Cambridge Chapter 3 pp 155–162."""
from pathlib import Path
import json
import unittest
from collections import Counter
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[1]
FIRST,LAST=153,187
class Cambridge155162(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rules=json.loads((ROOT/"grammar/rules/other.json").read_text(encoding="utf-8"))
        cls.batch=[r for r in cls.rules if r["id"].startswith("OTH-") and FIRST<=int(r["id"][4:])<=LAST]
        cls.pages=json.loads((ROOT/"grammar/coverage/cgel_ledger.json").read_text(encoding="utf-8"))["pages"]
        cls.schema=json.loads((ROOT/"grammar/schema.json").read_text(encoding="utf-8"))
    def test_contiguous_unique_ids(self):
        self.assertEqual([r["id"] for r in self.batch],[f"OTH-{n:03d}" for n in range(FIRST,LAST+1)])
        self.assertEqual(len({r["id"] for r in self.rules}),len(self.rules))
    def test_complete_page_provenance(self):
        cited={p for r in self.batch for s in r["sources"] for p in s["pages"]}
        self.assertEqual(cited,set(range(155,163)))
        for p in range(155,163):
            self.assertEqual(self.pages[p-1]["status"],"extracted")
            self.assertEqual(self.pages[p-1]["evidence"],"sources/cambridge/chapter_03/PHASE_B_PP155_162_REPORT.md")
    def test_schema_original_examples_and_diagnostics(self):
        schema=Draft202012Validator(self.schema)
        for r in self.batch:
            self.assertEqual(list(schema.iter_errors(r)),[],r["id"])
            self.assertTrue(all(s["chapter"]==3 for s in r["sources"]))
            self.assertGreaterEqual(len(r["examples"]["correct"]),2)
            self.assertTrue(all(e["origin"]=="ai_authored" for e in r["examples"]["correct"]))
        kinds=Counter(r["rule_type"] for r in self.batch)
        self.assertEqual(kinds,{"classification":33,"constraint":2})
        for r in self.batch:
            if r["rule_type"]!="constraint":
                self.assertIsNone(r["diagnostic"])
                continue
            self.assertEqual(r["diagnostic"]["detector"],"spec_only")
            self.assertGreaterEqual(len(r["examples"]["incorrect"]),2)
            self.assertGreaterEqual(len(r["diagnostic"]["minimal_pairs"]),2)
            self.assertGreaterEqual(len(r["diagnostic"]["false_positive_guards"]),3)
    def test_chapter_three_retains_extracted_pages(self):
        self.assertGreaterEqual(sum(p["chapter"]==3 and p["status"]=="extracted" for p in self.pages),89)
