import json
import unittest
from pathlib import Path

from ruleset import RULEBOOK

ROOT = Path(__file__).resolve().parents[1]


class LegacyDispositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(
            (ROOT / "docs/planning/legacy_rule_disposition.json").read_text(encoding="utf-8"))

    def test_every_legacy_rule_is_accounted_for(self):
        ids = {row["rule_id"] for row in self.data["rules"]}
        self.assertEqual(ids, set(RULEBOOK))

    def test_dispositions_are_proposed_not_final(self):
        self.assertEqual(self.data["counts"]["total"], len(RULEBOOK))
        self.assertEqual(self.data["counts"]["port_candidate"], 62)
        self.assertEqual(self.data["counts"]["keep_legacy_diagnostic"], 50)
        self.assertTrue(all(row["status"] == "proposed_needs_review"
                            for row in self.data["rules"]))
        self.assertFalse(self.data["policy"]["production_without_review"])
        self.assertFalse(self.data["policy"]["delete_without_parity"])


if __name__ == "__main__":
    unittest.main()
