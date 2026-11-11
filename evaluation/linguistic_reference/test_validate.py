"""Independent tests for the LREF annotation validator."""

import json
import tempfile
import unittest
from pathlib import Path

from evaluation.linguistic_reference.validate import (
    validate_case,
    validate_jsonl,
)


def draft_case():
    return {
        "schema_version": "1.0",
        "id": "LREF-001",
        "sentence": "The boy runs.",
        "phenomenon": "subject_verb_agreement",
        "variety": "standard_english",
        "reference": {
            "acceptability": "acceptable",
            "diagnostics": [],
            "trees": [],
            "acceptable_repairs": [],
            "explanation_requirements": [],
        },
        "review": {
            "status": "draft",
            "reviewed_dimensions": [],
        },
    }


class TestLREFValidator(unittest.TestCase):

    def test_valid_draft(self):
        self.assertEqual(validate_case(draft_case()), [])

    def test_draft_cannot_claim_certification(self):
        case = draft_case()
        case["review"]["reviewed_dimensions"] = ["acceptability"]
        self.assertTrue(validate_case(case))

    def test_source_review_requires_evidence(self):
        case = draft_case()
        case["review"]["status"] = "source_reviewed"
        case["review"]["reviewed_dimensions"] = ["acceptability"]
        self.assertTrue(validate_case(case))

    def test_expert_status_requires_approvals(self):
        case = draft_case()
        case["review"]["status"] = "expert_adjudicated"
        case["review"]["reviewed_dimensions"] = ["acceptability"]
        self.assertTrue(validate_case(case))

    def test_out_of_bounds_span(self):
        case = draft_case()
        case["reference"]["diagnostics"] = [
            {"char_span": [0, 1000]}
        ]
        self.assertTrue(validate_case(case))

    def test_boolean_span_rejected(self):
        case = draft_case()
        case["reference"]["diagnostics"] = [
            {"char_span": [True, 4]}
        ]
        self.assertTrue(validate_case(case))

    def test_duplicate_ids(self):
        case = draft_case()

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cases.jsonl"
            path.write_text(
                json.dumps(case) + "\n" +
                json.dumps(case) + "\n",
                encoding="utf-8",
            )

            errors = validate_jsonl(path)
            self.assertTrue(
                any("duplicate ID" in e for e in errors)
            )

    def test_malformed_status_fails_safely(self):
        case = draft_case()
        case["review"]["status"] = []

        errors = validate_case(case)
        self.assertTrue(errors)

    def test_malformed_dimensions_fail_safely(self):
        case = draft_case()
        case["review"]["reviewed_dimensions"] = [
            {"invalid": "dimension"}
        ]

        errors = validate_case(case)
        self.assertTrue(errors)


    def test_unknown_top_level_field_rejected(self):
        case = draft_case()
        case["unexpected_field"] = "invalid"

        errors = validate_case(case)

        self.assertTrue(
            any("Additional properties" in error for error in errors),
            errors,
        )

    def test_unknown_reference_field_rejected(self):
        case = draft_case()
        case["reference"]["unexpected_field"] = "invalid"

        errors = validate_case(case)

        self.assertTrue(
            any("Additional properties" in error for error in errors),
            errors,
        )


if __name__ == "__main__":
    unittest.main()
