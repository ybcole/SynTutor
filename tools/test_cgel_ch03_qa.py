"""Independent reproducible structural QA for the extracted Cambridge Chapter 3 records.

No test asserts linguistic truth or owner review from merely having a source citation.
"""
import json
import unittest
from pathlib import Path

from tools.audit_cgel_ch03 import (
    ROOT, CORPUS, audit, build_candidate_corpus, load_all_rules, normalize_guard, source_pages
)


class ChapterThreeQATests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.summary, cls.errors, cls.expected_corpus = audit()
        cls.rules = load_all_rules()
        cls.by_id = {r["id"]: r for r in cls.rules}

    def test_automated_qa_gate_and_chapter_inventory(self):
        self.assertEqual(self.errors, [])
        self.assertTrue(self.summary["automated_gate_passed"])
        self.assertEqual(self.summary["source_pages"], 142)
        self.assertEqual(self.summary["extracted_pages"], 139)
        self.assertEqual(self.summary["contents_only_skips"], 3)
        self.assertEqual(self.summary["unprocessed_chapter_pages"], 0)
        self.assertGreaterEqual(self.summary["catalog_total"], 887)
        self.assertGreaterEqual(self.summary["ch03_rules"], 695)

    def test_candidate_corpus_is_derived_not_invented(self):
        actual = json.loads((ROOT / CORPUS).read_text(encoding="utf-8"))
        self.assertEqual(actual, self.expected_corpus)
        self.assertEqual(actual["language_policy"], "ENGLISH_ONLY")
        self.assertEqual(actual["runtime_status"], "not_enabled")
        self.assertEqual(actual["measurement_status"], "not_evaluated")
        self.assertGreaterEqual(actual["total_cases"], 277)
        self.assertGreaterEqual(len(actual["diagnostic_rule_ids"]), 35)
        self.assertTrue(all(c["rule_id"] in self.by_id for c in actual["cases"]))
        self.assertTrue(all(c["source_pages"] == source_pages(self.by_id[c["rule_id"]])
                            for c in actual["cases"]))
        ids = [c["id"] for c in actual["cases"]]
        self.assertEqual(len(ids), len(set(ids)))

    def test_candidates_are_not_mistaken_for_measured_performance(self):
        corpus = self.expected_corpus
        self.assertEqual(corpus["authority"], "SOURCE_EXTRACTED_CANDIDATES_NOT_GOLD_ADJUDICATED")
        self.assertIn("article_determiner", corpus["families_below_full_10_10_gate"])
        self.assertGreater(corpus["families_below_full_10_10_gate"]["article_determiner"]["error_needed"], 0)
        for item in corpus["cases"]:
            self.assertTrue(item["sentence"])
            if item["kind"] == "error":
                self.assertTrue(item["expected_correction"])
                self.assertNotEqual(item["sentence"], item["expected_correction"])
            else:
                self.assertEqual(item["kind"], "valid")
                self.assertIsNone(item["expected_correction"])

    def test_scope_annotation_stripping_is_non_destructive(self):
        self.assertEqual(normalize_guard("The door opened. [contextual example]"),
                         ("The door opened.", "contextual example"))
        self.assertEqual(normalize_guard("They called [the office] later."),
                         ("They called [the office] later.", None))
        self.assertEqual(normalize_guard("Might I enter?"), ("Might I enter?", None))

    def test_legacy_split_pdf_locators_normalized_without_status_change(self):
        for rid in ("AGR-002", "MORPH-004", "MORPH-005", "MORPH-006"):
            rule = self.by_id[rid]
            self.assertEqual(rule["status"], "APPROVED")
            ref = [s for s in rule["sources"]
                   if s.get("chapter") == 3 and s.get("pages") == [75]]
            self.assertEqual(len(ref), 1)
            self.assertEqual(ref[0]["pdf_pages"], [95])
            self.assertIn("Full-volume source locator normalized", rule["review_notes"])
        self.assertEqual(set(self.summary["legacy_diagnostic_blockers"]),
                         {"AGR-002", "MORPH-004", "MORPH-005", "MORPH-006"})
        self.assertEqual(self.summary["runtime_eligible_claimed"], 0)

    def test_duplicate_semantic_checks_linked_not_double_counted(self):
        a = self.by_id["CLS-119"]
        b = self.by_id["OTH-453"]
        self.assertIn(b["id"], a["related_rules"])
        self.assertIn(a["id"], b["related_rules"])
        self.assertEqual(a["rule_type"], b["rule_type"])
        self.assertEqual(a["diagnostic"]["detector"], "spec_only")
        self.assertEqual(b["diagnostic"]["detector"], "spec_only")
        self.assertIn("COMP-030", self.by_id["CLS-100"]["related_rules"])
        self.assertIn("CLS-100", self.by_id["COMP-030"]["related_rules"])

    def test_audit_detects_source_mutation_without_papering_over_it(self):
        original = self.by_id["OTH-453"]
        changed = dict(original)
        changed["diagnostic"] = dict(original["diagnostic"])
        changed["diagnostic"]["minimal_pairs"] = ["not a valid minimal pair"]
        subset = [changed]
        with self.assertRaises(ValueError):
            build_candidate_corpus(subset)
        self.assertEqual(original["diagnostic"]["detector"], "spec_only")
