"""Incremental Cambridge Chapter 3 pp203–210 page, source, schema and semantics gates."""
import json
import unittest
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
START, END = 484, 569
REPORT = "sources/cambridge/chapter_03/PHASE_B_PP203_210_REPORT.md"
SCOPED = ("OTH-486", "OTH-487", "OTH-494", "OTH-495", "OTH-499", "OTH-500")
VARIETY = ("OTH-484", "OTH-517")
FUTURE_TENSE = ("OTH-550", "OTH-551", "OTH-552")


class Cambridge203210(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads((ROOT / "grammar/rules/other.json").read_text(encoding="utf-8"))
        cls.rules = [
            rule for rule in cls.catalog
            if rule["id"].startswith("OTH-") and START <= int(rule["id"][4:]) <= END
        ]
        cls.by_id = {rule["id"]: rule for rule in cls.rules}
        cls.ledger = json.loads((ROOT / "grammar/coverage/cgel_ledger.json").read_text(encoding="utf-8"))["pages"]
        cls.validator = Draft202012Validator(
            json.loads((ROOT / "grammar/schema.json").read_text(encoding="utf-8"))
        )

    def test_ids_are_unique_and_consecutive(self):
        self.assertEqual([r["id"] for r in self.rules],
                         [f"OTH-{n:03d}" for n in range(START, END + 1)])
        self.assertEqual(len(self.rules), 86)
        self.assertEqual(len({r["id"] for r in self.catalog}), len(self.catalog))

    def test_source_ledger_pages_and_page_evidence(self):
        self.assertTrue((ROOT / REPORT).is_file())
        cited = {p for r in self.rules for s in r["sources"] for p in s["pages"]}
        self.assertEqual(cited, set(range(203, 211)))
        for p in range(203, 211):
            row = self.ledger[p-1]
            self.assertEqual((row["page"], row["chapter"], row["status"]),
                             (p, 3, "extracted"))
            self.assertEqual(row["evidence"], REPORT)
        counts = Counter(row["status"] for row in self.ledger if row["chapter"] == 3)
        self.assertGreaterEqual(counts["extracted"], 137)
        self.assertEqual(counts["skipped_with_reason"], 3)
        self.assertLessEqual(counts["unprocessed"], 2)

    def test_schema_examples_and_scope_not_new_errors(self):
        self.assertEqual(Counter(r["rule_type"] for r in self.rules), {
            "classification": 75,
            "descriptive_generalization": 7,
            "variety_restricted": 2,
            "stylistic_or_prescriptive": 2,
        })
        for rule in self.rules:
            self.assertFalse(list(self.validator.iter_errors(rule)), rule["id"])
            self.assertEqual(rule["status"], "NEEDS_REVIEW")
            self.assertEqual(rule["domain"], "other")
            self.assertIsNone(rule["violation"])
            self.assertIsNone(rule["diagnostic"])
            self.assertEqual(len(rule["examples"]["correct"]), 2)
            self.assertEqual(rule["examples"]["incorrect"], [])
            self.assertTrue(rule["exceptions"])
            for group in rule["examples"].values():
                self.assertTrue(all(ex["origin"] == "ai_authored" for ex in group))
            self.assertTrue(all(m["relation"] == "unverified"
                                for m in rule["burton_roberts_mapping"]))
            for source in rule["sources"]:
                self.assertEqual(source["chapter"], 3)
                self.assertTrue(set(source["pages"]) <= set(range(203, 211)))
                self.assertEqual(source["pdf_pages"], [p + 20 for p in source["pages"]])

    def test_scope_dialect_and_future_analysis_are_not_prohibitions(self):
        for rid in SCOPED + FUTURE_TENSE:
            self.assertIsNone(self.by_id[rid]["diagnostic"])
            self.assertEqual(self.by_id[rid]["examples"]["incorrect"], [])
        for rid in VARIETY:
            self.assertEqual(self.by_id[rid]["rule_type"], "variety_restricted")
            self.assertTrue(self.by_id[rid].get("variety"))
        self.assertEqual(self.by_id["OTH-484"]["sources"][0]["pages"], [203])
        self.assertEqual(self.by_id["OTH-551"]["sources"][0]["pages"], [209])
        self.assertIn("be going", self.by_id["OTH-569"]["concept"].lower())

    def test_incomplete_chapter_report_is_honest(self):
        report = (ROOT / REPORT).read_text(encoding="utf-8")
        self.assertIn("No new detector specifications or runtime detectors", report)
        self.assertIn("2** unprocessed pages (**211–212**)", report)
        self.assertIn("855 records", report)
        coverage = (ROOT / "COVERAGE.md").read_text(encoding="utf-8")
        self.assertIn("**855 rules**", coverage)
        self.assertIn("**2 unprocessed (pp. 211–212)**", coverage)
