"""Provisional positive attribution tests for auxiliary inversion."""

import json
import unittest
from urllib.request import Request, urlopen

API_URL = "http://127.0.0.1:8001/api/parse"

AUXILIARY_FORM_RULES = {
    "C-AUX-FORM",
    "C-MODAL-VERB-FORM",
}


def rules_for(sentence):
    request = Request(
        API_URL,
        data=json.dumps({"text": sentence}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urlopen(request, timeout=120) as response:
        data = json.load(response)

    return set(
        (data.get("summary") or {}).get("constraints_fired") or []
    )


class AuxiliaryInversionPositiveTests(unittest.TestCase):

    def test_modal_question_form_error_detected(self):
        rules = rules_for("Can she sings?")

        self.assertTrue(
            rules & AUXILIARY_FORM_RULES,
            f"Expected auxiliary-form diagnosis; got {sorted(rules)}",
        )

    def test_do_support_form_error_detected(self):
        rules = rules_for("Does she runs?")

        self.assertTrue(
            rules & AUXILIARY_FORM_RULES,
            f"Expected auxiliary-form diagnosis; got {sorted(rules)}",
        )


if __name__ == "__main__":
    unittest.main()
