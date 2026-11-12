"""Source and exception regressions for Chapter 17 pp. 1529–1536."""
import json
import unittest
from pathlib import Path

from tools.cgel_batch_gate import check_batch

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "sources/cambridge/chapter_17/PP1529_1536_AUDIT.json"


class Chapter17ProFormBatch(unittest.TestCase):
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
            list(range(1529, 1537)),
        )
        self.assertEqual(check_batch(self.manifest), [])

    def test_preference_does_not_enable_a_diagnostic(self):
        for concept in (
            "Dialect differences in finite complement omission",
            "Chaining and crossed anaphoric links",
            "Antecedent differences with do so",
        ):
            with self.subTest(concept=concept):
                self.assertIsNone(self.by_concept[concept]["diagnostic"])

    def test_do_so_contrast_and_antecedent_guards(self):
        guards = {
            "Auxiliary-headed antecedent exclusion for do so": "Mira has packed the bag, and Theo has done so too.",
            "Contrastive objects and do so": "I checked the latch and did so carefully.",
            "Do so in comparisons": "I closed the hatch. As I did so, the warning light went out.",
        }
        for concept, example in guards.items():
            with self.subTest(concept=concept):
                rule = self.by_concept[concept]
                self.assertEqual(rule["diagnostic"]["detector"], "spec_only")
                self.assertIn(example, rule["diagnostic"]["false_positive_guards"])
