"""Schema checks for the approved B-R envelope and Cambridge rule checks."""
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
BR_SCHEMA = json.loads(
    (ROOT / "docs" / "canonical-burton-roberts-tree.schema.json").read_text(encoding="utf-8")
)
RULE_SCHEMA = json.loads(
    (ROOT / "grammar" / "schema.json").read_text(encoding="utf-8")
)


class GrammarSchemaTests(unittest.TestCase):
    def test_approved_m1_burton_roberts_schema_is_well_formed(self):
        Draft202012Validator.check_schema(BR_SCHEMA)

    def test_cambridge_rule_schema_is_well_formed(self):
        Draft202012Validator.check_schema(RULE_SCHEMA)

    def test_machine_readable_runtime_check_is_schema_valid(self):
        rule = {
            "id": "TEST-001",
            "domain": "other",
            "concept": "test-only rule",
            "rule_type": "constraint",
            "scope": "sentence",
            "condition": "A configured token sequence appears in the sentence.",
            "violation": "The configured token sequence is present.",
            "exceptions": [],
            "examples": {
                "correct": [
                    {"text": "A permitted example.", "origin": "ai_authored"},
                    {"text": "Another permitted example.", "origin": "ai_authored"},
                ],
                "incorrect": [
                    {"text": "A test-only violation.", "origin": "ai_authored"},
                    {"text": "Another test-only violation.", "origin": "ai_authored"},
                ],
            },
            "sources": [{
                "book": "Cambridge Grammar", "chapter": 1, "pages": [51],
            }],
            "burton_roberts_mapping": [{
                "br_concept": "test-only mapping", "relation": "compatible",
            }],
            "status": "APPROVED",
            "runtime_check": {
                "kind": "forbidden_token_sequences",
                "forbidden_sequences": [["very", "unique"]],
                "exception_sequences": [["not", "very", "unique"]],
            },
        }
        errors = list(Draft202012Validator(RULE_SCHEMA).iter_errors(rule))
        self.assertEqual(errors, [], [error.message for error in errors])

    def test_unsupported_runtime_check_kind_is_rejected_by_schema(self):
        rule = {
            "id": "TEST-002",
            "domain": "other",
            "concept": "test-only rule",
            "rule_type": "constraint",
            "scope": "sentence",
            "condition": "A configured token sequence appears in the sentence.",
            "violation": "The configured token sequence is present.",
            "exceptions": [],
            "examples": {
                "correct": [
                    {"text": "A permitted example.", "origin": "ai_authored"},
                    {"text": "Another permitted example.", "origin": "ai_authored"},
                ],
                "incorrect": [
                    {"text": "A test-only violation.", "origin": "ai_authored"},
                    {"text": "Another test-only violation.", "origin": "ai_authored"},
                ],
            },
            "sources": [{
                "book": "Cambridge Grammar", "chapter": 1, "pages": [51],
            }],
            "burton_roberts_mapping": [{
                "br_concept": "test-only mapping", "relation": "compatible",
            }],
            "status": "APPROVED",
            "runtime_check": {
                "kind": "interpret-natural-language-condition",
                "forbidden_sequences": [["very", "unique"]],
            },
        }
        errors = list(Draft202012Validator(RULE_SCHEMA).iter_errors(rule))
        self.assertTrue(errors)


if __name__ == "__main__":
    unittest.main(verbosity=2)
