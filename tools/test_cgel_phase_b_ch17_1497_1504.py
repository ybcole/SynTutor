"""Source and exception regressions for Chapter 17 pp. 1497–1504."""
import json
import unittest
from pathlib import Path

from tools.cgel_batch_gate import check_batch

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "sources/cambridge/chapter_17/PP1497_1504_AUDIT.json"


class Chapter17ReciprocalBatch(unittest.TestCase):
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
            list(range(1497, 1505)),
        )
        self.assertEqual(check_batch(self.manifest), [])

    def test_compound_set_size_and_marginal_clefts_are_not_errors(self):
        for concept in (
            "Traditional set-size prescription for compound reciprocals",
            "Marginal reciprocals in it-clefts",
            "Nonreciprocal readings of split one",
        ):
            with self.subTest(concept=concept):
                rule = self.by_concept[concept]
                self.assertIsNone(rule["diagnostic"])
                self.assertFalse(rule["examples"]["incorrect"])

    def test_subject_and_antecedent_guards(self):
        guards_by_concept = {
            "Every plus singular noun as a reciprocal antecedent":
                "Everyone recognized one another.",
            "Subject restriction on verb-domain reciprocals":
                "The pilots arranged for each other to testify.",
            "Genitive antecedent exclusion in the mixed verb–noun reciprocal domain":
                "Their dislike for each other surprised the committee.",
            "Genitive exclusion with NP-internal emphatic reflexives":
                "We objected to Clara's directing the ceremony herself.",
        }
        for concept, guard in guards_by_concept.items():
            with self.subTest(concept=concept):
                rule = self.by_concept[concept]
                self.assertEqual(rule["diagnostic"]["detector"], "spec_only")
                self.assertIn(guard, rule["diagnostic"]["false_positive_guards"])
