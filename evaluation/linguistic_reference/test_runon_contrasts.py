"""Provisional run-on and auxiliary-inversion regressions.

Expectations are draft linguistic judgments, not expert-adjudicated
gold annotations. Tests target the isolated SynTutor API.
"""

import json
import unittest
from urllib.request import Request, urlopen

API_URL = "http://127.0.0.1:8001/api/parse"


def rules_for(sentence):
    request = Request(
        API_URL,
        data=json.dumps({"text": sentence}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=120) as response:
        data = json.load(response)

    return (data.get("summary") or {}).get(
        "constraints_fired"
    ) or []


class RunonContrastTests(unittest.TestCase):

    def test_fused_sentence_detected(self):
        rules = rules_for("She sings he dances.")
        self.assertIn("C-RUNON", rules)

    def test_coordination_not_runon(self):
        rules = rules_for("She sings and he dances.")
        self.assertNotIn("C-RUNON", rules)

    def test_valid_modal_question_not_runon(self):
        rules = rules_for("Can she sing?")
        self.assertNotIn("C-RUNON", rules)

    def test_malformed_modal_question_not_runon(self):
        rules = rules_for("Can she sings?")
        self.assertNotIn(
            "C-RUNON", rules,
            "Modal-complement error misattributed to run-on",
        )

    def test_malformed_do_question_not_runon(self):
        rules = rules_for("Does she runs?")
        self.assertNotIn(
            "C-RUNON", rules,
            "Auxiliary-complement error misattributed to run-on",
        )


if __name__ == "__main__":
    unittest.main()
