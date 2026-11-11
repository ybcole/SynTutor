"""Structural validation tests for provisional LREF reference trees."""

import copy
import json
import unittest
from pathlib import Path

from evaluation.linguistic_reference.validate import validate_case


DATASET = Path(__file__).with_name("pilot_draft.jsonl")


def load_case(case_id):
    for line in DATASET.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue

        case = json.loads(line)

        if case["id"] == case_id:
            return copy.deepcopy(case)

    raise ValueError(f"Case not found: {case_id}")


class TreeValidationTests(unittest.TestCase):

    def test_valid_draft_tree(self):
        case = load_case("SVA-001")

        self.assertEqual(
            validate_case(case),
            [],
        )

    def test_child_outside_parent_rejected(self):
        case = load_case("SVA-001")

        root = case["reference"]["trees"][0]["root"]
        clause = root["children"][0]
        vp = clause["children"][1]

        # VP extends beyond the clause boundary.
        vp["char_span"] = [8, 13]

        self.assertTrue(
            validate_case(case),
            "Child span outside parent was accepted",
        )

    def test_leaf_surface_mismatch_rejected(self):
        case = load_case("SVA-001")

        root = case["reference"]["trees"][0]["root"]
        clause = root["children"][0]
        np = clause["children"][0]
        noun = np["children"][1]

        # Original sentence contains "boy", not "cat".
        noun["surface"] = "cat"

        self.assertTrue(
            validate_case(case),
            "Incorrect leaf surface was accepted",
        )

    def test_invalid_relation_endpoint_rejected(self):
        case = load_case("SVA-001")

        tree = case["reference"]["trees"][0]
        relation = tree["relations"][0]

        # This is not the span of the annotated noun head.
        relation["subject_head_span"] = [0, 3]

        self.assertTrue(
            validate_case(case),
            "Relation pointing to the determiner was accepted",
        )


if __name__ == "__main__":
    unittest.main()
