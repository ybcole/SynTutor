"""Regression checks for literal preservation in learner-facing explanations.

Run: python -m unittest -v server.test_plain_literal_preservation
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plain import apply_plain_language, plain_text


class PlainLiteralPreservationTests(unittest.TestCase):
    def test_double_quoted_source_keeps_family_words(self):
        result = plain_text(
            'The sentence "Her sister loves her daughter." contains a noun phrase.'
        )
        self.assertEqual(
            result,
            'The sentence "Her sister loves her daughter." contains a noun group.'
        )

    def test_single_quoted_source_with_contraction_is_preserved(self):
        original = "The example 'My sister doesn't like this clause.' shows a noun phrase."
        result = plain_text(original)
        self.assertIn("'My sister doesn't like this clause.'", result)
        self.assertIn("noun group", result)

    def test_curly_quote_and_internal_whitespace_are_preserved(self):
        quoted = "“My  sister isn’t here.”"
        result = plain_text("The sentence " + quoted + " contains a noun phrase.")
        self.assertIn(quoted, result)
        self.assertIn("noun group", result)

    def test_technical_sister_daughter_terms_are_contextual(self):
        self.assertEqual(
            plain_text("The sister node relates to the daughter node."),
            "The sibling node relates to the child node."
        )
        self.assertEqual(
            plain_text("Her sister called her daughter."),
            "Her sister called her daughter."
        )

    def test_apply_plain_language_preserves_literal_across_fields(self):
        example = "Her sister likes her daughter."
        details = {
            "n1": {
                "status": "error",
                "role": "sister node",
                "text": 'The noun phrase "' + example + '" has a head noun.',
                "remediation": {
                    "suggested_fix": 'Keep "' + example + '" unchanged.'
                },
                "findings": [{
                    "status": "error",
                    "role": "daughter node",
                    "text": "The example '" + example + "' contains a noun phrase.",
                    "remediation": {"violation": "Do not alter '" + example + "'."}
                }]
            }
        }
        summary = {"explanation": ""}
        apply_plain_language(details, summary)
        self.assertIn('"' + example + '"', details["n1"]["text"])
        self.assertIn('"' + example + '"', summary["explanation"])
        self.assertIn('"' + example + '"', details["n1"]["remediation"]["suggested_fix"])
        self.assertIn("'" + example + "'", details["n1"]["findings"][0]["text"])
        self.assertIn("'" + example + "'", details["n1"]["findings"][0]["remediation"]["violation"])
        self.assertEqual(details["n1"]["role"], "sibling node")
        self.assertEqual(details["n1"]["findings"][0]["role"], "child node")


if __name__ == "__main__":
    unittest.main()
