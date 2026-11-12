"""Source and exception regressions for Chapter 17 pp. 1505–1512."""
import json
import unittest
from pathlib import Path

from tools.cgel_batch_gate import check_batch

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "sources/cambridge/chapter_17/PP1505_1512_AUDIT.json"


class Chapter17DemonstrativeBatch(unittest.TestCase):
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
            list(range(1505, 1513)),
        )
        self.assertEqual(check_batch(self.manifest), [])

    def test_animate_identification_and_informal_usage(self):
        for concept in (
            "Animate identification with independent demonstratives",
            "Informal false-definite this",
            "Informal degree that without an antecedent",
        ):
            with self.subTest(concept=concept):
                rule = self.by_concept[concept]
                self.assertIsNone(rule["diagnostic"])
                self.assertFalse(rule["examples"]["incorrect"])

    def test_placement_and_countability_guards(self):
        guards_by_concept = {
            "Spatial agreement inside a demonstrative NP":
                "Put this envelope over there.",
            "Nondeictic that as a fused definite determiner-head":
                "This path is shorter than that over there.",
            "Countability in fused that and pro-nominal one":
                "This drill is lighter than the one in the shed.",
            "Immediate cardinal or no before bare pro-nominal ones":
                "We found no loose ones.",
        }
        for concept, guard in guards_by_concept.items():
            with self.subTest(concept=concept):
                rule = self.by_concept[concept]
                self.assertEqual(rule["diagnostic"]["detector"], "spec_only")
                self.assertIn(guard, rule["diagnostic"]["false_positive_guards"])
