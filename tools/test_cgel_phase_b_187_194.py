"""Incremental source provenance and schema checks for CGEL Chapter 3 pp. 187–194."""
import json
import unittest
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
START, END = 344, 413
REPORT = "sources/cambridge/chapter_03/PHASE_B_PP187_194_REPORT.md"


class Cambridge187194(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads((ROOT / "grammar/rules/other.json").read_text(encoding="utf-8"))
        cls.rules = [rule for rule in cls.catalog
                     if rule["id"].startswith("OTH-") and START <= int(rule["id"][4:]) <= END]
        cls.ledger = json.loads((ROOT / "grammar/coverage/cgel_ledger.json").read_text(encoding="utf-8"))["pages"]
        cls.schema = json.loads((ROOT / "grammar/schema.json").read_text(encoding="utf-8"))
        cls.validator = Draft202012Validator(cls.schema)

    def test_record_ids_unique_and_contiguous(self):
        self.assertEqual([rule["id"] for rule in self.rules],
                         [f"OTH-{n:03d}" for n in range(START, END + 1)])
        self.assertEqual(len(self.rules), 70)
        self.assertEqual(len({rule["id"] for rule in self.catalog}), len(self.catalog))

    def test_precise_page_ledger_and_audit(self):
        self.assertTrue((ROOT / REPORT).is_file())
        pages = {p for rule in self.rules for src in rule["sources"] for p in src["pages"]}
        self.assertEqual(pages, set(range(187, 195)))
        for page in range(187, 195):
            row = self.ledger[page - 1]
            self.assertEqual((row["page"], row["chapter"], row["status"]), (page, 3, "extracted"))
            self.assertEqual(row["evidence"], REPORT)
        chapter = [row for row in self.ledger if row["chapter"] == 3]
        counts = Counter(row["status"] for row in chapter)
        self.assertGreaterEqual(counts["extracted"], 121)
        self.assertEqual(counts["skipped_with_reason"], 3)
        self.assertLessEqual(counts["unprocessed"], 18)

    def test_schema_and_original_examples(self):
        self.assertEqual(Counter(r["rule_type"] for r in self.rules),
                         {"classification": 57, "descriptive_generalization": 12, "constraint": 1})
        for rule in self.rules:
            self.assertFalse(list(self.validator.iter_errors(rule)), rule["id"])
            self.assertEqual(rule["domain"], "other")
            self.assertEqual(rule["status"], "NEEDS_REVIEW")
            self.assertGreaterEqual(len(rule["examples"]["correct"]), 2)
            self.assertTrue(rule["exceptions"])
            self.assertTrue(all(e["origin"] == "ai_authored"
                                for group in rule["examples"].values() for e in group))
            self.assertTrue(all(src["chapter"] == 3 for src in rule["sources"]))
            for src in rule["sources"]:
                self.assertTrue(set(src["pages"]) <= set(range(187, 195)))
                self.assertEqual(src["pdf_pages"], [p + 20 for p in src["pages"]])
            self.assertTrue(all(m["relation"] == "unverified" for m in rule["burton_roberts_mapping"]))

    def test_constraint_is_not_an_enabled_runtime_detector(self):
        r = next(rule for rule in self.rules if rule["id"] == "OTH-377")
        self.assertEqual(r["rule_type"], "constraint")
        self.assertEqual(r["sources"][0]["pages"], [191])
        self.assertEqual(r["diagnostic"]["detector"], "spec_only")
        self.assertGreaterEqual(len(r["examples"]["correct"]), 2)
        self.assertGreaterEqual(len(r["examples"]["incorrect"]), 2)
        self.assertGreaterEqual(len(r["diagnostic"]["minimal_pairs"]), 2)
        guards = r["diagnostic"]["false_positive_guards"]
        self.assertTrue(any("Tell me when" in s for s in guards))
        self.assertTrue(any("If the price will" in s for s in guards))
        self.assertTrue(any("If you will" in s for s in guards))
        self.assertIsNone(next(rule for rule in self.rules if rule["id"] == "OTH-378")["diagnostic"])

    def test_chapter_coverage_is_not_misrepresented(self):
        report = (ROOT / REPORT).read_text(encoding="utf-8")
        self.assertIn("New production detectors: 0", report)
        self.assertIn("1,628 unprocessed", report)
        self.assertIn("195–202", report)
        self.assertIn("further restrictions", report)
