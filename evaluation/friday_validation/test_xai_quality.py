
import json
import unittest
from urllib.request import Request, urlopen

import test_tree_structure as helpers

API_URL = "http://127.0.0.1:8001/api/explain"


def explain(tree, node_id):
    request = Request(
        API_URL,
        data=json.dumps({
            "tree": tree,
            "node_id": node_id,
        }).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urlopen(request, timeout=30) as response:
        return json.load(response)["learner_explanation"]


class TestModalXAI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        analysis = helpers.analyze("She can sing.")
        tree = analysis["br_analysis"]["tree"]

        # Select the MOD node exactly as the frontend does.
        modal = tree["root"]["children"][1]["children"][0]

        cls.explanation = explain(tree, modal["id"])
        cls.modal_id = modal["id"]

    def test_correct_node_selected(self):
        self.assertEqual(
            self.explanation["selected_node_id"],
            self.modal_id,
        )

    def test_identifies_modal_auxiliary(self):
        text = self.explanation["text"].lower()

        self.assertIn("modal", text)
        self.assertIn("can", text)

    def test_does_not_claim_full_certification(self):
        self.assertIs(
            self.explanation["whole_sentence_certified"],
            False,
        )

    def test_explains_required_verb_form(self):
        """Educational requirement from B-R Chapter 6."""
        text = self.explanation["text"].lower()

        acceptable_terms = (
            "plain form",
            "base form",
            "bare form",
            "stem form",
            "non-finite form",
            "uninflected form",
        )

        self.assertTrue(
            any(term in text for term in acceptable_terms),
            "The modal explanation does not identify "
            "the required form of the following verb.",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
