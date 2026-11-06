"""Validate canonical B-R payloads against the versioned JSON Schema."""
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator

from br_tree import _atoms, _source_yield, load_reference_records, normalize_candidate


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "grammar" / "br_tree.schema.json").read_text(encoding="utf-8"))
VALIDATOR = Draft202012Validator(SCHEMA)


class BrTreeSchemaTests(unittest.TestCase):
    def test_schema_is_well_formed(self):
        Draft202012Validator.check_schema(SCHEMA)

    def test_unresolved_payload_matches_schema(self):
        result = normalize_candidate({}, None, "A sentence without a supported mapping.", "V10", [])
        self.assertEqual(result["status"], "unresolved")
        self.assertEqual(list(VALIDATOR.iter_errors(result)), [])

    def test_all_accepted_sentence_aligned_img_fixtures_match_schema(self):
        checked = 0
        rejected = []
        for record in load_reference_records():
            if record.get("status") != "IMG" or record.get("correct") is False:
                continue
            sentence = record.get("sentence")
            version = record.get("_convention_version")
            tree = record.get("tree")
            if not isinstance(sentence, str) or not version or not isinstance(tree, dict):
                continue
            if _source_yield(tree) != _atoms(sentence):
                continue
            result = normalize_candidate({}, None, sentence, version, [record])
            if result.get("status") != "normalized":
                continue
            checked += 1
            errors = list(VALIDATOR.iter_errors(result))
            if errors:
                rejected.append({
                    "tree_id": record.get("id"),
                    "errors": [error.message for error in errors[:4]],
                })
        self.assertGreater(checked, 0)
        self.assertEqual(rejected, [], f"Normalized fixtures do not match schema: {rejected[:10]}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
