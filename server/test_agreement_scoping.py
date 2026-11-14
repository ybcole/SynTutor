"""Agreement rules must inspect the clause predicate, not embedded verbs.

Regression for: "I and he saw the three thieves stealing the car whom was
parked on the wrong side". The main predicate is past-tense "saw"; "was" is the
predicate of the relative clause and agrees with "the car". The coordinated-
subject rule must not compare the main subject with the relative-clause verb.
"""

import unittest

from api import build_payload


def _errors(sentence):
    payload = build_payload(sentence)
    return [
        (detail.get("constraint"), str(detail.get("surface") or ""))
        for detail in (payload.get("node_details") or {}).values()
        if detail.get("status") == "error"
    ]


class AgreementScopingTests(unittest.TestCase):
    def test_relative_verb_is_not_the_coordinated_subject_predicate(self):
        errors = _errors(
            "I and he saw the three thieves stealing the car whom was parked "
            "on the wrong side")
        self.assertNotIn(("C-COORD-SUBJ-AGREE", "was"), errors)
        # The relative pronoun is wrong for the inanimate antecedent, but the
        # relative-clause verb is not compared with the main subject.
        self.assertIn(("C-RELATIVE-PRONOUN", "whom"), errors)
        self.assertEqual(
            sorted(constraint for constraint, _ in errors),
            ["C-RELATIVE-PRONOUN", "C-TERMINAL-PUNCT"])

    def test_coordinated_subject_rule_still_catches_main_verb(self):
        self.assertIn(("C-COORD-SUBJ-AGREE", "was"),
                      _errors("I and he was late."))
        self.assertIn(("C-COORD-SUBJ-AGREE", "sees"),
                      _errors("I and he sees the thieves."))
        self.assertNotIn(("C-COORD-SUBJ-AGREE", "was"),
                         _errors("I and he saw the man who was late."))

    def test_correlative_rule_ignores_embedded_verbs(self):
        self.assertNotIn(("C-CORRELATIVE-AGREE", "was"),
                         _errors("Neither the teacher nor I saw the man who was late."))
        self.assertIn(("C-CORRELATIVE-AGREE", "is"),
                      _errors("Neither the teacher nor I is late."))

    def test_number_of_rule_ignores_relative_verbs(self):
        self.assertNotIn(
            ("C-NUMBER-AGREE", "were"),
            _errors("The number of students who were late surprised me."))
        self.assertNotIn(
            ("C-NUMBER-AGREE", "were"),
            _errors("The number of students who were late is growing."))
        self.assertIn(
            ("C-NUMBER-AGREE", "are"),
            _errors("The number of students are growing."))
        self.assertIn(
            ("C-NUMBER-AGREE", "were"),
            _errors("The number of students were late."))


if __name__ == "__main__":
    unittest.main()
