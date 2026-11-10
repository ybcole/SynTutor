"""Regression gate for source-cited Cambridge Chapter 3 printed pp. 179–186."""
from collections import Counter
from pathlib import Path
import json
import unittest

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
START, END = 287, 343
REPORT = "sources/cambridge/chapter_03/PHASE_B_PP179_186_REPORT.md"


class Cambridge179186(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads((ROOT / "grammar/rules/other.json").read_text(encoding="utf-8"))
        cls.rules = [
            r for r in cls.catalog
            if r["id"].startswith("OTH-") and START <= int(r["id"][4:]) <= END
        ]
        cls.ledger = json.loads((ROOT / "grammar/coverage/cgel_ledger.json").read_text(encoding="utf-8"))["pages"]
        cls.validator = Draft202012Validator(
            json.loads((ROOT / "grammar/schema.json").read_text(encoding="utf-8"))
        )

    def test_ids_and_count(self):
        self.assertEqual(
            [rule["id"] for rule in self.rules],
            [f"OTH-{num:03d}" for num in range(START, END + 1)]
        )
        self.assertEqual(len({rule["id"] for rule in self.catalog}), len(self.catalog))
        self.assertEqual(len(self.rules), 57)

    def test_page_ledger_and_sources(self):
        self.assertTrue((ROOT / REPORT).is_file())
        cited = {p for rule in self.rules for source in rule["sources"] for p in source["pages"]}
        self.assertEqual(cited, set(range(179, 187)))
        for page in range(179, 187):
            item = self.ledger[page - 1]
            self.assertEqual((item["page"], item["chapter"], item["status"]), (page, 3, "extracted"))
            self.assertEqual(item["evidence"], REPORT)
        chapter = [item for item in self.ledger if item["chapter"] == 3]
        counts = Counter(item["status"] for item in chapter)
        self.assertGreaterEqual(counts["extracted"], 113)
        self.assertEqual(counts["skipped_with_reason"], 3)
        self.assertLessEqual(counts["unprocessed"], 26)

    def test_schema_original_examples_and_no_runtime_claims(self):
        self.assertEqual(
            Counter(r["rule_type"] for r in self.rules),
            {"classification": 42, "descriptive_generalization": 15}
        )
        for rule in self.rules:
            self.assertFalse(list(self.validator.iter_errors(rule)), rule["id"])
            self.assertEqual(rule["status"], "NEEDS_REVIEW")
            self.assertEqual(rule["domain"], "other")
            self.assertIsNone(rule["diagnostic"])
            self.assertIsNone(rule["violation"])
            self.assertTrue(rule["exceptions"])
            self.assertEqual(len(rule["examples"]["correct"]), 2)
            self.assertEqual(rule["examples"]["incorrect"], [])
            self.assertTrue(all(ex["origin"] == "ai_authored" for ex in rule["examples"]["correct"]))
            for source in rule["sources"]:
                self.assertEqual(source["chapter"], 3)
                self.assertTrue(set(source["pages"]) <= set(range(179, 187)))
                self.assertEqual(source["pdf_pages"], [p + 20 for p in source["pages"]])
            self.assertTrue(all(
                mapping["relation"] == "unverified" for mapping in rule["burton_roberts_mapping"]
            ))

    def test_all_source_notes_present_without_claiming_full_chapter(self):
        audit = (ROOT / REPORT).read_text(encoding="utf-8")
        self.assertIn("New production detectors: 0", audit)
        for p in range(179, 187):
            self.assertIn(str(p), audit)
        self.assertIn("incomplete", audit.lower())
