"""Independent QA: real Generator diagnostic authority and explanation checks.

Uses installed NLP models. No production database or external account.
Expected failures are defects or unresolved contract requirements,
not environment failures.
"""
import re
import unittest

from api import build_payload


class GeneratorAuthorityContract(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.clean = build_payload("The birds sing.")
        cls.agreement = build_payload("These book are heavy.")
        cls.modal = build_payload("Can she swims?")

    def test_modal_error_is_not_explained_as_run_on(self):
        explanation = self.modal["summary"].get("explanation", "")
        self.assertNotRegex(
            explanation.lower(),
            r"two full parts|without punctuation or a conjunction|run.on",
            "A modal-complement error must not be explained as a run-on."
        )

    def test_uncertified_sentence_avoids_categorical_assurance(self):
        summary = self.clean["summary"]
        xai = self.clean["xai4_partial_evaluation"]
        certified = xai["global_verdict"].get(
            "whole_sentence_certified", False
        )
        book_verified = summary.get("book_verified", False)

        if not certified and not book_verified:
            explanation = summary.get("explanation", "")
            self.assertNotRegex(
                explanation.lower(),
                r"\bis grammatical\b|every word is used in an allowed way",
                "Uncertified analysis must not assert complete correctness."
            )

    def test_agreement_correction_is_the_expected_candidate(self):
        self.assertEqual(
            self.agreement["summary"].get("corrected_sentence"),
            "These books are heavy."
        )
        self.assertEqual(
            self.agreement["summary"].get("verdict"),
            "ungrammatical"
        )

    def test_tree_normalization_does_not_certify_grammar(self):
        result = self.clean
        self.assertEqual(result["br_analysis"]["status"], "normalized")
        self.assertFalse(
            result["xai4_partial_evaluation"]["global_verdict"][
                "whole_sentence_certified"
            ]
        )


if __name__ == "__main__":
    unittest.main()
