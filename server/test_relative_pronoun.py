"""Relative pronoun choice (who / whom / which) and its scoping.

Regression for "the car whom was parked": an inanimate antecedent takes
"which"/"that", and a subject-gap relative pronoun that is "whom" is the wrong
case. Pronoun-case rules must not read a pronoun inside a relative clause as a
prepositional object.
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


def _payload(sentence):
    return build_payload(sentence)


class RelativePronounTests(unittest.TestCase):
    def test_inanimate_antecedent_rejects_who_and_whom(self):
        self.assertIn(("C-RELATIVE-PRONOUN", "whom"),
                      _errors("The car whom was parked outside belongs to me."))
        self.assertIn(("C-RELATIVE-PRONOUN", "who"),
                      _errors("The car who was parked outside belongs to me."))
        self.assertNotIn(
            ("C-RELATIVE-PRONOUN", "which"),
            _errors("The car which was parked outside belongs to me."))

    def test_human_antecedent_choice_and_subject_case(self):
        self.assertIn(("C-RELATIVE-PRONOUN", "which"),
                      _errors("The man which saw me was late."))
        self.assertIn(("C-RELATIVE-PRONOUN", "whom"),
                      _errors("The man whom was late saw me."))
        self.assertNotIn(("C-RELATIVE-PRONOUN", "whom"),
                         _errors("The man whom I saw was late."))
        self.assertIn(("C-RELATIVE-PRONOUN", "which"),
                      _errors("The teacher which I met was kind."))

    def test_inanimate_pronoun_fix_is_executable(self):
        correction = _payload(
            "The car whom was parked outside belongs to me."
        )["summary"].get("correction") or {}
        self.assertEqual(correction.get("corrected_sentence"),
                         "The car which was parked outside belongs to me.")

    def test_relative_clause_is_not_a_prepositional_object(self):
        errors = _errors("The students from several departments whom I met were late.")
        self.assertNotIn("C-PRONOUN-CASE",
                         [constraint for constraint, _ in errors])
        self.assertNotIn("C-RELATIVE-PRONOUN",
                         [constraint for constraint, _ in errors])
        # The real prepositional-object error still fires.
        self.assertIn("C-PREP-PRON-CASE",
                      [constraint for constraint, _ in _errors("The gift is for I.")])

    def test_collective_antecedent_accepts_which(self):
        self.assertNotIn(
            ("C-RELATIVE-PRONOUN", "which"),
            _errors("The committee which met yesterday approved the plan."))
        self.assertIn(
            ("C-RELATIVE-PRONOUN", "whom"),
            _errors("The committee whom met yesterday approved the plan."))


if __name__ == "__main__":
    unittest.main()
