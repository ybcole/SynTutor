"""Source and ledger regressions for CGEL Chapter 3 printed pages 147–154."""
import json
from pathlib import Path
import unittest
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[1]

class Chapter3RemoteAndBackshiftTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog=json.loads((ROOT/"grammar/rules/other.json").read_text(encoding="utf-8"))
        cls.rules=[r for r in cls.catalog if 118<=int(r["id"][4:])<=152]
        cls.ledger=json.loads((ROOT/"grammar/coverage/cgel_ledger.json").read_text(encoding="utf-8"))
        cls.schema=json.loads((ROOT/"grammar/schema.json").read_text(encoding="utf-8"))
    def test_id_continuity_and_uniqueness(self):
        self.assertEqual([r["id"] for r in self.rules],[f"OTH-{n:03d}" for n in range(118,153)])
        self.assertEqual(len({r["id"] for r in self.catalog}),len(self.catalog))
    def test_schema_and_original_examples(self):
        v=Draft202012Validator(self.schema)
        for r in self.rules:
            self.assertEqual(list(v.iter_errors(r)),[],r["id"])
            self.assertTrue(all(s["chapter"]==3 and all(147<=p<=154 for p in s["pages"]) for s in r["sources"]))
            self.assertGreaterEqual(len(r["examples"]["correct"]),2)
            self.assertTrue(all(e["origin"]=="ai_authored" for e in r["examples"]["correct"]))
            self.assertIsNone(r["diagnostic"])
    def test_no_unjustified_error_constraints(self):
        from collections import Counter
        counts=Counter(r["rule_type"] for r in self.rules)
        self.assertEqual(counts,{"classification":32,"descriptive_generalization":2,"stylistic_or_prescriptive":1})
    def test_page_ledger_and_evidence(self):
        pages=self.ledger["pages"]
        cited={p for r in self.rules for s in r["sources"] for p in s["pages"]}
        self.assertEqual(cited,set(range(147,155)))
        for p in range(147,155):
            self.assertEqual(pages[p-1]["status"],"extracted")
            self.assertEqual(pages[p-1]["evidence"],"sources/cambridge/chapter_03/PHASE_B_PP147_154_REPORT.md")
        self.assertEqual(pages[154]["status"],"unprocessed")
    def test_incomplete_chapter_not_certified(self):
        pages=self.ledger["pages"]
        self.assertEqual(sum(p["status"]=="unprocessed" for p in pages),1668)
        self.assertEqual(sum(p["status"]=="extracted" and p["chapter"]==3 for p in pages),81)
        self.assertTrue(all(pages[p-1]["status"]=="unprocessed" for p in range(155,213)))
