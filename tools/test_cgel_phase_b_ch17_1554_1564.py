"""Source and exception regressions for Chapter 17 pp. 1554–1564."""
import json
import unittest
from pathlib import Path

from tools.cgel_batch_gate import check_batch

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "sources/cambridge/chapter_17/PP1554_1564_AUDIT.json"


class Chapter17TemporalBatch(unittest.TestCase):
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
            list(range(1554, 1565)),
        )
        self.assertEqual(check_batch(self.manifest), [])

    def test_chapter_page_accounting(self):
        ledger = json.loads(
            (ROOT / "grammar/coverage/cgel_ledger.json").read_text(encoding="utf-8")
        )
        pages = [row for row in ledger["pages"] if row["chapter"] == 17]
        self.assertEqual([row["page"] for row in pages], list(range(1449, 1565)))
        self.assertEqual(
            [row["page"] for row in pages if row["status"] == "skipped_with_reason"],
            [1449, 1450],
        )
        self.assertTrue(all(row["status"] == "extracted" for row in pages[2:]))

    def test_spatial_and_temporal_preferences_have_no_diagnostic(self):
        for concept in (
            "Intrinsic and observer-based spatial orientation",
            "Weekday names and near-day reference",
            "Shifted temporal deixis in free indirect style",
        ):
            with self.subTest(concept=concept):
                self.assertIsNone(self.by_concept[concept]["diagnostic"])
