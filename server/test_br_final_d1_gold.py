import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class FinalD1GoldArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gold = json.loads(
            (ROOT / "evaluation/br_final_d1_gold.json").read_text(encoding="utf-8"))

    def test_twenty_entries_and_statuses(self):
        self.assertEqual(self.gold["counts"]["entries"], 20)
        self.assertEqual(len(self.gold["entries"]), 20)
        self.assertEqual(self.gold["counts"]["normalized"], 20)
        self.assertEqual(self.gold["counts"]["unresolved"], 0)

    def test_each_entry_has_complete_tree_or_explicit_unresolved(self):
        for entry in self.gold["entries"]:
            self.assertTrue(entry["text"])
            self.assertTrue(entry["profile_id"])
            if entry["status"] == "unresolved":
                self.assertIsNone(entry["tree"])
            else:
                self.assertIsInstance(entry["tree"], dict)
                self.assertIn("root", entry["tree"])
                self.assertIn("tokens", entry["tree"])

    def test_no_independent_review_claim(self):
        self.assertEqual(self.gold["status"], "AI_DRAFT_OWNER_WAIVER")
        self.assertIn("not independent", self.gold["provenance"])
        for entry in self.gold["entries"]:
            self.assertFalse(entry["independently_verified"])
            self.assertIn("owner_waiver", entry["verification_level"])


if __name__ == "__main__":
    unittest.main()
