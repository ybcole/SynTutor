"""Semantic validation for SynTutor linguistic reference cases.

Valid metadata does not prove linguistic correctness or reviewer authenticity.
"""

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator


SCHEMA_PATH = Path(__file__).with_name("schema_v1.json")
SCHEMA = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

Draft202012Validator.check_schema(SCHEMA)
STRUCTURAL_VALIDATOR = Draft202012Validator(SCHEMA)

STATUSES = {"draft", "source_reviewed", "expert_adjudicated"}

DIMENSIONS = {
    "acceptability",
    "diagnostics",
    "trees",
    "corrections",
    "explanations",
}

ACCEPTABILITY = {
    "acceptable",
    "unacceptable",
    "context_dependent",
    "undetermined",
}


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def validate_case(case):
    errors = []

    if not isinstance(case, dict):
        return ["Case must be an object"]

    schema_errors = sorted(
        STRUCTURAL_VALIDATOR.iter_errors(case),
        key=lambda error: (
            tuple(str(part) for part in error.absolute_path),
            error.message,
        ),
    )

    if schema_errors:
        return [
            "Schema: "
            + (".".join(map(str, error.absolute_path)) or "<root>")
            + ": "
            + error.message
            for error in schema_errors
        ]

    for field in ("id", "sentence", "phenomenon", "variety"):
        if not nonempty(case.get(field)):
            errors.append(f"{field}: required nonempty string")

    if case.get("schema_version") != "1.0":
        errors.append("Unsupported schema_version")

    reference = case.get("reference")

    if not isinstance(reference, dict):
        errors.append("reference must be an object")
        reference = {}

    if reference.get("acceptability") not in ACCEPTABILITY:
        errors.append("Invalid reference acceptability")

    for field in (
        "diagnostics",
        "trees",
        "acceptable_repairs",
        "explanation_requirements",
    ):
        value = reference.get(field, [])

        if not isinstance(value, list):
            errors.append(f"reference.{field} must be an array")
            continue

        if field in ("diagnostics", "trees"):
            if any(not isinstance(item, dict) for item in value):
                errors.append(f"reference.{field} must contain objects")
        else:
            if any(not nonempty(item) for item in value):
                errors.append(f"reference.{field} must contain strings")

    sentence = case.get("sentence", "")
    diagnostics = reference.get("diagnostics", [])

    if isinstance(sentence, str) and isinstance(diagnostics, list):
        for index, item in enumerate(diagnostics):
            if not isinstance(item, dict):
                continue

            span = item.get("char_span")

            if span is None:
                continue

            valid = (
                isinstance(span, list)
                and len(span) == 2
                and all(type(n) is int for n in span)
                and 0 <= span[0] <= span[1] <= len(sentence)
            )

            if not valid:
                errors.append(
                    f"diagnostics[{index}]: invalid character span"
                )

    review = case.get("review")

    if not isinstance(review, dict):
        return errors + ["review must be an object"]

    status = review.get("status")

    if not isinstance(status, str) or status not in STATUSES:
        errors.append("Invalid review status")
        return errors

    dimensions = review.get("reviewed_dimensions")

    if not isinstance(dimensions, list):
        errors.append("reviewed_dimensions must be an array")
        return errors

    if not all(
        isinstance(d, str) and d in DIMENSIONS
        for d in dimensions
    ):
        errors.append("Invalid or duplicate reviewed dimensions")
        return errors

    if len(dimensions) != len(set(dimensions)):
        errors.append("Invalid or duplicate reviewed dimensions")

    if status == "draft":
        if dimensions:
            errors.append("Draft cannot have certified dimensions")
        return errors

    if not dimensions:
        errors.append("Reviewed case requires reviewed dimensions")

    checks = review.get("source_checks", [])

    if not isinstance(checks, list) or not checks:
        errors.append("Source review evidence is required")
    else:
        for index, check in enumerate(checks):
            if not isinstance(check, dict) or not (
                nonempty(check.get("citation"))
                and nonempty(check.get("reviewer_id"))
                and check.get("verified") is True
            ):
                errors.append(
                    f"source_checks[{index}]: incomplete evidence"
                )

    if status == "expert_adjudicated":
        reviews = review.get("independent_reviews", [])

        if not isinstance(reviews, list):
            reviews = []
            errors.append("independent_reviews must be an array")

        for dimension in dimensions:
            approvers = {
                item.get("reviewer_id")
                for item in reviews
                if isinstance(item, dict)
                and nonempty(item.get("reviewer_id"))
                and item.get("decision") == "approve"
                and isinstance(item.get("approved_dimensions"), list)
                and dimension in item["approved_dimensions"]
            }

            if len(approvers) < 2:
                errors.append(
                    f"{dimension}: requires two distinct expert approvals"
                )

        adjudication = review.get("adjudication")

        if not isinstance(adjudication, dict) or not (
            adjudication.get("decision") == "accepted"
            and nonempty(adjudication.get("adjudicator_id"))
        ):
            errors.append("Expert adjudication record is required")

    return errors


def validate_jsonl(path):
    errors = []
    seen = set()

    for number, line in enumerate(
        Path(path).read_text(encoding="utf-8").splitlines(), 1
    ):
        if not line.strip():
            continue

        try:
            case = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"Line {number}: invalid JSON: {exc.msg}")
            continue

        if isinstance(case, dict):
            case_id = case.get("id")
            if isinstance(case_id, str):
                if case_id in seen:
                    errors.append(f"Line {number}: duplicate ID {case_id}")
                seen.add(case_id)

        for error in validate_case(case):
            errors.append(f"Line {number}: {error}")

    return errors


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python validate.py <reference.jsonl>")
        sys.exit(2)

    problems = validate_jsonl(sys.argv[1])

    if problems:
        for problem in problems:
            print("FAIL:", problem)
        sys.exit(1)

    print("PASS: reference records satisfy semantic checks")
