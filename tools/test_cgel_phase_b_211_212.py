"""Final Cambridge Chapter 3 source-page and schema completion (not a runtime detector gate)."""
import json
import unittest
from collections import Counter
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
START, END = 570, 601
REPORT = "sources/cambridge/chapter_03/PHASE_B_PP211_212_REPORT.md"
AUDIT = "sources/cambridge/chapter_03/PHASE_B_SOURCE_COMPLETION_AUDIT.md"


class Cambridge211212(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads((ROOT / "grammar/rules/other.json").read_text(encoding="utf-8"))
        cls.rules = [r for r in cls.catalog
                     if r["id"].startswith("OTH-") and START <= int(r["id"][4:]) <= END]
        cls.by_id = {r["id"]: r for r in cls.rules}
        cls.pages = json.loads((ROOT / "grammar/coverage/cgel_ledger.json").read_text(encoding="utf-8"))["pages"]
        cls.validator = Draft202012Validator(
            json.loads((ROOT / "grammar/schema.json").read_text(encoding="utf-8")))

    def test_ids_unique_contiguous_and_source_cited(self):
        self.assertEqual([r["id"] for r in self.rules],
                         [f"OTH-{n:03d}" for n in range(START, END + 1)])
        self.assertEqual(len(self.rules), 32)
        self.assertEqual(len({r["id"] for r in self.catalog}), len(self.catalog))
        cited = {page for r in self.rules for s in r["sources"] for page in s["pages"]}
        self.assertEqual(cited, {211, 212})
        self.assertEqual(len([r for r in self.rules if r["sources"][0]["pages"] == [211]]), 17)
        self.assertEqual(len([r for r in self.rules if r["sources"][0]["pages"] == [212]]), 15)

    def test_schema_and_meaning_are_not_misreported_as_errors(self):
        self.assertEqual(Counter(r["rule_type"] for r in self.rules),
                         {"classification": 25, "descriptive_generalization": 6, "variety_restricted": 1})
        for rule in self.rules:
            self.assertFalse(list(self.validator.iter_errors(rule)), rule["id"])
            self.assertEqual(rule["domain"], "other")
            self.assertEqual(rule["status"], "NEEDS_REVIEW")
            self.assertIsNone(rule["diagnostic"])
            self.assertIsNone(rule["violation"])
            self.assertEqual(rule["examples"]["incorrect"], [])
            self.assertEqual(len(rule["examples"]["correct"]), 2)
            self.assertTrue(rule["exceptions"])
            self.assertTrue(all(e["origin"] == "ai_authored" for e in rule["examples"]["correct"]))
            self.assertTrue(all(m["relation"] == "unverified" for m in rule["burton_roberts_mapping"]))
            for source in rule["sources"]:
                self.assertEqual(source["chapter"], 3)
                self.assertEqual(source["pdf_pages"], [p + 20 for p in source["pages"]])
        self.assertIn("does not entail", self.by_id["OTH-592"]["concept"])
        self.assertIn("actually", self.by_id["OTH-593"]["statement"])
        self.assertIn("inference", self.by_id["OTH-595"]["statement"])

    def test_chapter_full_page_accounting_with_valid_evidence(self):
        chapter = [row for row in self.pages if row["chapter"] == 3]
        self.assertEqual(len(chapter), 142)
        self.assertEqual([row["page"] for row in chapter], list(range(71, 213)))
        self.assertEqual(Counter(row["status"] for row in chapter),
                         {"extracted": 139, "skipped_with_reason": 3})
        self.assertEqual([row["page"] for row in chapter
                          if row["status"] == "skipped_with_reason"], [71, 72, 73])
        for row in chapter:
            self.assertTrue(row["evidence"], str(row["page"]))
            self.assertTrue((ROOT / row["evidence"]).is_file(), str(row["page"]))
        for p in (211, 212):
            self.assertEqual(self.pages[p-1]["evidence"], REPORT)

    def test_completion_reports_distinguish_source_and_runtime(self):
        self.assertTrue((ROOT / REPORT).is_file())
        self.assertTrue((ROOT / AUDIT).is_file())
        audit = (ROOT / AUDIT).read_text(encoding="utf-8")
        self.assertIn("Independent linguistic QA", audit)
        self.assertIn("Phase C", audit)
        self.assertIn("Phase D", audit)
        self.assertIn("1,610 unprocessed", audit)
        coverage = (ROOT / "COVERAGE.md").read_text(encoding="utf-8")
        import re
        catalog_count = re.search(r"= \\*\\*(\\d+) rules\\*\\*", coverage)
        self.assertIsNotNone(catalog_count)
        self.assertGreaterEqual(int(catalog_count.group(1)), 887)
        self.assertIn("| 3. The verb | 142 | 139 | 0 | 3 | 0 |", coverage)
        self.assertIn("PHASE_B_PP211_212_REPORT.md", coverage)
        extracted = sum(row["status"] == "extracted" for row in self.pages)
        pending = sum(row["status"] == "unprocessed" for row in self.pages)
        self.assertIn(f"**{extracted} extracted**", coverage)
        self.assertIn(f"{pending} unprocessed", coverage)
