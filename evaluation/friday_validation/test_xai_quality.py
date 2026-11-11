
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


class TestPronounXAI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        analysis = helpers.analyze("She can sing.")
        tree = analysis["br_analysis"]["tree"]

        pronoun = tree["root"]["children"][0]["children"][0]
        word = pronoun["children"][0]

        cls.pronoun_explanation = explain(
            tree, pronoun["id"]
        )
        cls.word_explanation = explain(
            tree, word["id"]
        )

    def test_pronoun_explains_grammatical_function(self):
        """The pronoun explanation should teach its role."""
        text = self.pronoun_explanation["text"].lower()

        self.assertIn("pronoun", text)
        self.assertIn("subject", text)

    def test_word_explanation_is_contextual(self):
        """The terminal explanation should avoid circularity."""
        text = self.word_explanation["text"].lower()

        self.assertIn(
            "subject",
            text,
            "The explanation does not identify the "
            "pronoun's grammatical function.",
        )

        self.assertNotIn(
            'part of “she”',
            text,
            "The explanation describes She as part "
            "of itself.",
        )


    def test_word_explanation_avoids_circularity(self):
        """A word should not be explained as part of itself."""
        text = self.word_explanation["text"].lower()

        self.assertNotIn(
            'part of “she”',
            text,
            "The explanation incorrectly describes "
            "'She' as part of itself.",
        )


class TestAgreementXAI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        analysis = helpers.analyze("The boys runs.")
        tree = analysis["br_analysis"]["tree"]

        verb = tree["root"]["children"][1]["children"][0]

        cls.summary = analysis["summary"]
        cls.explanation = explain(tree, verb["id"])

    def test_legacy_detects_agreement_error(self):
        self.assertIn(
            "C-SUBJECT-AGREEMENT",
            self.summary["constraints_fired"],
        )

    def test_explains_subject_verb_conflict(self):
        """The explanation should identify the agreement problem."""
        text = self.explanation["text"].lower()

        self.assertIn(
            "boys",
            text,
            "The explanation does not identify the subject.",
        )
        self.assertIn(
            "plural",
            text,
            "The explanation does not explain subject number.",
        )

    def test_explains_correct_verb_form(self):
        """The explanation should provide the appropriate form."""
        import re

        text = self.explanation["text"].lower()

        self.assertRegex(
            text,
            r"\brun\b",
            "The explanation does not identify the "
            "appropriate verb form 'run'.",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
