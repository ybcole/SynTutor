"""Tests for the fail-closed Cambridge runtime evaluator.

The pattern matcher tested here is an execution primitive, not an enabled
Cambridge grammatical rule. Production rule execution remains empty until
specific records pass independent review, B-R crosswalk and test gates.
"""
import json
from pathlib import Path
import tempfile
import unittest

from cambridge_evaluator import evaluate_cambridge
from cambridge_registry import load_runtime_registry


class CambridgeEvaluatorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "grammar" / "rules").mkdir(parents=True)
        (self.root / "grammar" / "runtime_registry.json").write_text(
            json.dumps({"registry_version": 1, "enabled_rules": []}),
            encoding="utf-8",
        )

    def tearDown(self):
        self.temp.cleanup()

    def add_allowlisted_rule(self, mapping="compatible"):
        rule = {
            "id": "TEST-001",
            "domain": "other",
            "concept": "test-only token sequence check",
            "rule_type": "constraint",
            "scope": "sentence",
            "condition": "A test-only token sequence is present in the input sentence.",
            "violation": "A configured test-only token sequence is present.",
            "exceptions": [],
            "examples": {"correct": [], "incorrect": []},
            "sources": [{"book": "Cambridge Grammar", "chapter": 1, "pages": [51]}],
            "burton_roberts_mapping": [{
                "br_concept": "test-only pattern check", "relation": mapping,
            }],
            "status": "APPROVED",
            "runtime_check": {
                "kind": "forbidden_token_sequences",
                "forbidden_sequences": [["very", "unique"]],
                "exception_sequences": [["not", "very", "unique"]],
            },
        }
        (self.root / "grammar" / "rules" / "test.json").write_text(
            json.dumps([rule]), encoding="utf-8",
        )
        entry = {
            "rule_id": "TEST-001",
            "independent_review": True,
            "reviewed_by": "synthetic-test-reviewer",
            "reviewed_on": "2026-11-07",
            "crosswalk_status": "compatible",
            "test_status": "passed",
            "runtime_status": "enabled",
        }
        (self.root / "grammar" / "runtime_registry.json").write_text(
            json.dumps({"registry_version": 1, "enabled_rules": [entry]}),
            encoding="utf-8",
        )

    @staticmethod
    def analysis(sentence):
        return {
            "status": "normalized",
            "tree": {
                "schema_version": "1.0.0",
                "sentence": sentence,
                "root": {"id": "root", "label": "S", "children": []},
            },
        }

    def test_no_allowlisted_rules_produces_no_cambridge_verdict(self):
        registry = load_runtime_registry(self.root)
        result = evaluate_cambridge(self.analysis("The students laugh."), registry)
        self.assertEqual(result["status"], "no_runtime_rules")
        self.assertEqual(result["evaluated_rule_ids"], [])
        self.assertEqual(result["findings"], [])
        self.assertEqual(result["diagnostics"][-1]["code"], "NO_RUNTIME_ENABLED_RULES")

    def test_unresolved_b_r_analysis_skips_cambridge_evaluation(self):
        result = evaluate_cambridge(
            {"status": "unresolved", "tree": None},
            {"active_rules": [{"rule_id": "TEST-001"}]},
        )
        self.assertEqual(result["status"], "not_evaluated")
        self.assertEqual(result["diagnostics"][0]["code"], "BR_ANALYSIS_UNRESOLVED")

    def test_pattern_primitive_handles_positive_negative_and_exception_cases(self):
        self.add_allowlisted_rule()
        registry = load_runtime_registry(self.root)

        positive = evaluate_cambridge(self.analysis("The item is very unique."), registry)
        self.assertEqual(positive["status"], "evaluated")
        self.assertEqual(positive["evaluated_rule_ids"], ["TEST-001"])
        self.assertEqual(positive["findings"][0]["rule_id"], "TEST-001")

        negative = evaluate_cambridge(self.analysis("The item is quite rare."), registry)
        self.assertEqual(negative["status"], "evaluated")
        self.assertEqual(negative["findings"], [])
        self.assertEqual(negative["evaluations"][0]["status"], "passed")

        exception = evaluate_cambridge(self.analysis("It is not very unique."), registry)
        self.assertEqual(exception["status"], "evaluated")
        self.assertEqual(exception["findings"], [])
        self.assertEqual(exception["evaluations"][0]["status"], "exception")

    def test_unverified_crosswalk_never_reaches_the_evaluator(self):
        self.add_allowlisted_rule(mapping="unverified")
        registry = load_runtime_registry(self.root)
        self.assertEqual(registry["active_rules"], [])
        result = evaluate_cambridge(self.analysis("The item is very unique."), registry)
        self.assertEqual(result["status"], "no_runtime_rules")
        self.assertEqual(result["findings"], [])

    def test_non_constraint_runtime_entries_cannot_create_error_findings(self):
        result = evaluate_cambridge(
            self.analysis("The item is very unique."),
            {"active_rules": [{
                "rule_id": "TEST-CLASSIFY", "rule_type": "classification",
                "runtime_check": {
                    "kind": "forbidden_token_sequences",
                    "forbidden_sequences": [["very", "unique"]],
                },
            }]},
        )
        self.assertEqual(result["status"], "no_implemented_rules")
        self.assertEqual(result["findings"], [])
        self.assertEqual(result["diagnostics"][0]["code"], "NON_CONSTRAINT_RULE_BLOCKED")


if __name__ == "__main__":
    unittest.main(verbosity=2)
