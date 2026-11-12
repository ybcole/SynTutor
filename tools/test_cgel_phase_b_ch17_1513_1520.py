"""Source and exception regressions for Chapter 17 pp. 1513–1520."""
import json
import unittest
from pathlib import Path

from tools.cgel_batch_gate import check_batch

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "sources/cambridge/chapter_17/PP1513_1520_AUDIT.json"


class Chapter17ReductionBatch(unittest.TestCase):
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
            list(range(1513, 1521)),
        )
        self.assertEqual(check_batch(self.manifest), [])

    def test_marginal_and_informal_forms_are_descriptive(self):
        for concept in (
            "Genitive determiners with pro-nominal one",
            "Informal and idiomatic a one",
            "Explicit partitives with pro-nominal one",
        ):
            with self.subTest(concept=concept):
                rule = self.by_concept[concept]
                self.assertIsNone(rule["diagnostic"])
                self.assertFalse(rule["examples"]["incorrect"])

    def test_complement_and_ellipsis_guards(self):
        guards_by_concept = {
            "Dependents of plural pro-nominal ones":
                "Ones with rubber grips were available.",
            "Content-clause complements of pro-nominal one":
                "They rejected the one that we submitted yesterday.",
            "Relational PP complements of pro-nominal one":
                "This proof of the lemma is shorter than the one of the theorem.",
            "Limits on contrasting complements after auxiliary stranding":
                "Have you invited Dana? No, but I have her brother.",
        }
        for concept, guard in guards_by_concept.items():
            with self.subTest(concept=concept):
                rule = self.by_concept[concept]
                self.assertEqual(rule["diagnostic"]["detector"], "spec_only")
                self.assertIn(guard, rule["diagnostic"]["false_positive_guards"])
