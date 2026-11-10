"""Source, guard and page-ledger regressions for Cambridge Chapter 3 pp. 195–202."""
import json
import unittest
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
START, END = 414, 483
REPORT = "sources/cambridge/chapter_03/PHASE_B_PP195_202_REPORT.md"
SPEC_ONLY = {"OTH-439", "OTH-453", "OTH-458"}


class Cambridge195202(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads((ROOT / "grammar/rules/other.json").read_text(encoding="utf-8"))
        cls.rules = [
            r for r in cls.catalog
            if r["id"].startswith("OTH-") and START <= int(r["id"][4:]) <= END
        ]
        cls.by_id = {r["id"]: r for r in cls.rules}
        cls.ledger = json.loads((ROOT / "grammar/coverage/cgel_ledger.json").read_text(encoding="utf-8"))["pages"]
        cls.validator = Draft202012Validator(
            json.loads((ROOT / "grammar/schema.json").read_text(encoding="utf-8"))
        )

    def test_unique_contiguous_rule_ids(self):
        self.assertEqual([r["id"] for r in self.rules],
                         [f"OTH-{n:03d}" for n in range(START, END + 1)])
        self.assertEqual(len(self.rules), 70)
        self.assertEqual(len({r["id"] for r in self.catalog}), len(self.catalog))

    def test_every_page_cited_and_extraction_recorded(self):
        self.assertTrue((ROOT / REPORT).is_file())
        citations = {p for r in self.rules for source in r["sources"] for p in source["pages"]}
        self.assertEqual(citations, set(range(195, 203)))
        for page in range(195, 203):
            row = self.ledger[page - 1]
            self.assertEqual((row["page"], row["chapter"], row["status"]),
                             (page, 3, "extracted"))
            self.assertEqual(row["evidence"], REPORT)
        counts = Counter(row["status"] for row in self.ledger if row["chapter"] == 3)
        # Monotonic check: future page ranges may increase extracted and decrease unprocessed.
        self.assertGreaterEqual(counts["extracted"], 129)
        self.assertEqual(counts["skipped_with_reason"], 3)
        self.assertLessEqual(counts["unprocessed"], 10)

    def test_schema_citations_and_original_english_examples(self):
        self.assertEqual(Counter(r["rule_type"] for r in self.rules), {
            "classification": 54,
            "descriptive_generalization": 10,
            "constraint": 3,
            "variety_restricted": 2,
            "stylistic_or_prescriptive": 1,
        })
        for r in self.rules:
            self.assertFalse(list(self.validator.iter_errors(r)), r["id"])
            self.assertEqual(r["domain"], "other")
            self.assertEqual(r["status"], "NEEDS_REVIEW")
            self.assertGreaterEqual(len(r["examples"]["correct"]), 2)
            self.assertTrue(r["exceptions"], r["id"])
            self.assertTrue(all(ex["origin"] == "ai_authored"
                                for group in r["examples"].values() for ex in group), r["id"])
            self.assertTrue(all(m["relation"] == "unverified" for m in r["burton_roberts_mapping"]))
            for src in r["sources"]:
                self.assertEqual(src["chapter"], 3)
                self.assertTrue(set(src["pages"]) <= set(range(195, 203)))
                self.assertEqual(src["pdf_pages"], [p + 20 for p in src["pages"]])

    def test_constraints_specification_only_and_minimal_pair_repairs(self):
        constraints = {r["id"] for r in self.rules if r["rule_type"] == "constraint"}
        self.assertEqual(constraints, SPEC_ONLY)
        for rid in SPEC_ONLY:
            r = self.by_id[rid]
            self.assertEqual(r["diagnostic"]["detector"], "spec_only")
            self.assertGreaterEqual(len(r["examples"]["correct"]), 2)
            self.assertGreaterEqual(len(r["examples"]["incorrect"]), 2)
            self.assertGreaterEqual(len(r["diagnostic"]["false_positive_guards"]), 5)
            pairs = r["diagnostic"]["minimal_pairs"]
            self.assertEqual(len(pairs), 2)
            for pair, wrong in zip(pairs, r["examples"]["incorrect"]):
                left, sep, right = pair.partition(" ||| ")
                self.assertTrue(sep)
                self.assertEqual(left, wrong["text"])
                self.assertTrue(right.strip())
            self.assertEqual(r["diagnostic"]["variety_scope"], "standard_english")
        self.assertTrue(any("could have" in s for s in
                            self.by_id["OTH-439"]["diagnostic"]["false_positive_guards"]))
        self.assertTrue(any("shop is open" in s for s in
                            self.by_id["OTH-453"]["diagnostic"]["false_positive_guards"]))
        self.assertTrue(any("I hope" in s for s in
                            self.by_id["OTH-458"]["diagnostic"]["false_positive_guards"]))

    def test_dialect_and_prescriptive_cases_are_not_error_detectors(self):
        for rid in ("OTH-419", "OTH-479", "OTH-482"):
            r = self.by_id[rid]
            self.assertNotEqual(r["rule_type"], "constraint")
            self.assertIsNone(r["diagnostic"])
            self.assertEqual(r["examples"]["incorrect"], [])
        for rid in ("OTH-479", "OTH-482"):
            self.assertEqual(self.by_id[rid]["rule_type"], "variety_restricted")
            self.assertIn("Dialect B", self.by_id[rid]["variety"])

    def test_coverage_report_and_unprocessed_next_range(self):
        report = (ROOT / REPORT).read_text(encoding="utf-8")
        self.assertIn("New runtime detectors: **0**", report)
        self.assertIn("printed p. 202 ends *mid-explanation*", report)
        self.assertIn("203–210", report)
        coverage = (ROOT / "COVERAGE.md").read_text(encoding="utf-8")
        self.assertIn("**769 rules**", coverage)
        self.assertIn("203–212", coverage)
