"""Draft linguistic authority regressions against SynTutor's API.

These are provisional linguistic expectations, not expert-adjudicated
benchmark results. Run against a recorded repository commit.
"""

import json
import unittest
from urllib.request import Request, urlopen

API_URL = "http://127.0.0.1:8001/api/parse"


def analyze(sentence):
    request = Request(
        API_URL,
        data=json.dumps({"text": sentence}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=120) as response:
        return json.load(response)


class LinguisticAuthorityTests(unittest.TestCase):

    def test_agreement_control(self):
        data = analyze("The boys runs.")
        rules = data["summary"]["constraints_fired"]

        self.assertIn("C-SUBJECT-AGREEMENT", rules)

    def test_modal_not_misattributed_to_agreement(self):
        data = analyze("They cans sing.")
        rules = data["summary"]["constraints_fired"]

        self.assertNotIn(
            "C-SUBJECT-AGREEMENT",
            rules,
            "Incorrectly classified modal inflection as "
            "ordinary subject-verb agreement",
        )

    def test_modal_inflection_detected(self):
        data = analyze("She cans sing.")
        rules = data["summary"]["constraints_fired"]

        self.assertTrue(
            any("MODAL" in rule for rule in rules),
            f"No modal-specific violation detected: {rules}",
        )

    def test_unverified_verdict_not_certified(self):
        data = analyze("They can the peaches.")
        summary = data["summary"]

        if summary["verdict"] == "unverified":
            explanation = summary.get("explanation") or ""

            self.assertNotIn(
                "is grammatical:",
                explanation.lower(),
                "Unverified analysis claims grammatical certainty",
            )


if __name__ == "__main__":
    unittest.main()
