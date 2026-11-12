"""Source and exception regressions for Chapter 17 pp. 1521–1528."""
import json
import unittest
from pathlib import Path

from tools.cgel_batch_gate import check_batch

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "sources/cambridge/chapter_17/PP1521_1528_AUDIT.json"


class Chapter17EllipsisBatch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((ROOT / MANIFEST).read_text(encoding="utf-8"))
        phrases = json.loads(
            (ROOT / "grammar/rules/phrases.json").read_text(encoding="utf-8")
        )
        added = set(cls.manifest["added_rule_ids"])
        cls.by_concept = {rule["concept"]: rule for rule in phrases if rule["id"] in added}

    def test_source_audit(self):
        self.assertEqual(
            [entry["page"] for entry in self.manifest["page_checks"]],
            list(range(1521, 1529)),
        )
        self.assertEqual(check_batch(self.manifest), [])

    def test_marginal_and_informal_forms_are_descriptive(self):
        for concept in (
            "Voice mismatch in auxiliary ellipsis",
            "Dialect variation in stranded being and having",
            "Licensing environments for reduced to-infinitivals",
        ):
            with self.subTest(concept=concept):
                rule = self.by_concept[concept]
                self.assertIsNone(rule["diagnostic"])
                self.assertFalse(rule["examples"]["incorrect"])

    def test_distinct_antecedent_and_remainder_guards(self):
        guards = {
            "Antecedent head restriction on reduction-driven do": "Nina should have called, but her brother did.",
            "Full-complement omission with lexical verbs": "I can grade the second set even if I can't the first.",
        }
        for concept, example in guards.items():
            with self.subTest(concept=concept):
                rule = self.by_concept[concept]
                self.assertEqual(rule["diagnostic"]["detector"], "spec_only")
                self.assertIn(example, rule["diagnostic"]["false_positive_guards"])
