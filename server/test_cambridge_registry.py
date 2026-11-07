"""Tests for the explicit, fail-closed Cambridge runtime rule registry."""
import json
from pathlib import Path
import tempfile
import unittest

from cambridge_registry import load_runtime_registry


class CambridgeRegistryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "grammar" / "rules").mkdir(parents=True)
        (self.root / "grammar" / "runtime_registry.json").write_text(
            json.dumps({"registry_version": 1, "enabled_rules": []}), encoding="utf-8"
        )

    def tearDown(self):
        self.temp.cleanup()

    def add_rule(self, mapping_relation="compatible"):
        rule = {
            "id": "TEST-001",
            "rule_type": "constraint",
            "status": "APPROVED",
            "sources": [{"book": "Cambridge Grammar", "pages": [51]}],
            "burton_roberts_mapping": [{"relation": mapping_relation}],
            "runtime_check": {
                "kind": "forbidden_token_sequences",
                "forbidden_sequences": [["very", "unique"]],
                "exception_sequences": [["not", "very", "unique"]],
            },
        }
        (self.root / "grammar" / "rules" / "test.json").write_text(
            json.dumps([rule]), encoding="utf-8"
        )
        registry_entry = {
            "rule_id": "TEST-001",
            "independent_review": True,
            "reviewed_by": "reviewer",
            "reviewed_on": "2026-11-07",
            "crosswalk_status": "compatible",
            "test_status": "passed",
            "runtime_status": "enabled",
        }
        (self.root / "grammar" / "runtime_registry.json").write_text(
            json.dumps({"registry_version": 1, "enabled_rules": [registry_entry]}),
            encoding="utf-8",
        )

    def test_empty_allow_list_enables_no_rules(self):
        result = load_runtime_registry(self.root)
        self.assertEqual(result["active_rules"], [])
        self.assertEqual(result["active_rule_ids"], [])

    def test_unverified_crosswalk_blocks_extracted_approved_rule(self):
        self.add_rule("unverified")
        result = load_runtime_registry(self.root)
        self.assertEqual(result["active_rules"], [])
        self.assertEqual(result["diagnostics"][0]["code"], "RULE_NOT_RUNTIME_ELIGIBLE")
        self.assertIn("unresolved B-R crosswalk", result["diagnostics"][0]["message"])

    def test_rule_without_a_machine_readable_runtime_check_is_blocked(self):
        self.add_rule("compatible")
        path = self.root / "grammar" / "rules" / "test.json"
        rule = json.loads(path.read_text(encoding="utf-8"))[0]
        rule.pop("runtime_check")
        path.write_text(json.dumps([rule]), encoding="utf-8")
        result = load_runtime_registry(self.root)
        self.assertEqual(result["active_rules"], [])
        self.assertIn("deterministic runtime_check is missing",
                      result["diagnostics"][0]["message"])

    def test_fully_reviewed_allow_list_entry_is_eligible(self):
        self.add_rule("compatible")
        result = load_runtime_registry(self.root)
        self.assertEqual(result["active_rule_ids"], ["TEST-001"])
        self.assertEqual(result["active_rules"][0]["runtime_check"]["kind"],
                         "forbidden_token_sequences")


if __name__ == "__main__":
    unittest.main(verbosity=2)
