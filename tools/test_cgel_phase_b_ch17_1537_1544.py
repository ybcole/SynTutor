"""Source and exception regressions for Chapter 17 pp. 1537–1544."""
import json
import unittest
from pathlib import Path

from tools.cgel_batch_gate import check_batch

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "sources/cambridge/chapter_17/PP1537_1544_AUDIT.json"


class Chapter17FragmentBatch(unittest.TestCase):
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
            list(range(1537, 1545)),
        )
        self.assertEqual(check_batch(self.manifest), [])

    def test_dialect_and_casual_omissions_are_descriptive(self):
        for concept in (
            "Dialectal denial with stressed postauxiliary so",
            "Casual ellipsis of a clause-initial subject",
            "Initial omission in casual closed interrogatives",
        ):
            with self.subTest(concept=concept):
                self.assertIsNone(self.by_concept[concept]["diagnostic"])

    def test_additive_so_and_stranding_guards(self):
        guards = {
            "Polarity of additive inverted so": "The alarm was broken, so Lee couldn't hear it.",
            "Stranding restriction in interrogative fragments with determiners": "Which cabin are we staying in?",
        }
        for concept, example in guards.items():
            with self.subTest(concept=concept):
                rule = self.by_concept[concept]
                self.assertEqual(rule["diagnostic"]["detector"], "spec_only")
                self.assertIn(example, rule["diagnostic"]["false_positive_guards"])
