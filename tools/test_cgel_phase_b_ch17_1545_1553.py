"""Source and exception regressions for Chapter 17 pp. 1545–1553."""
import json
import unittest
from pathlib import Path

from tools.cgel_batch_gate import check_batch

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "sources/cambridge/chapter_17/PP1545_1553_AUDIT.json"


class Chapter17SpatialBatch(unittest.TestCase):
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
            list(range(1545, 1554)),
        )
        self.assertEqual(check_batch(self.manifest), [])

    def test_spatial_preferences_remain_descriptive(self):
        for concept in (
            "Anaphoric here and there",
            "Perspective-dependent choice between come and go",
            "Here and there as motion goals",
        ):
            with self.subTest(concept=concept):
                self.assertIsNone(self.by_concept[concept]["diagnostic"])

    def test_else_preserves_disjunction_and_post_head_use(self):
        rule = self.by_concept["Post-head else and implicit comparison"]
        self.assertEqual(rule["diagnostic"]["detector"], "spec_only")
        self.assertIn(
            "Ask for another key, or else call the caretaker.",
            rule["diagnostic"]["false_positive_guards"],
        )
        self.assertIn("Who else can help?", rule["diagnostic"]["false_positive_guards"])
