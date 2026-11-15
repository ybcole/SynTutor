"""Detection scoping regressions for complex sentences.

These cases were false positives on grammatical sentences or true positives
whose correction had no executable edit. The rule must inspect the clause or
phrase it owns, not a neighbour across a clause boundary.
"""

import unittest

from api import build_payload


def _constraints(sentence):
    payload = build_payload(sentence)
    return [
        detail.get("constraint")
        for detail in (payload.get("node_details") or {}).values()
        if detail.get("status") == "error"
    ]


class DetectionScopingTests(unittest.TestCase):
    def test_coordinated_and_participial_commas_are_not_splices(self):
        for sentence in (
            "They went to the market, bought some fruit, and returned home.",
            "The more you practice, the better you become.",
            "Having finished the report, she went home.",
        ):
            with self.subTest(sentence=sentence):
                self.assertNotIn("C-COMMA-SPLICE", _constraints(sentence))

    def test_coordination_and_apposition_are_not_determiner_stacks(self):
        for sentence in (
            "Both the committee and the staff approved the plan.",
            "Her idea — to rebuild the bridge — was expensive.",
        ):
            with self.subTest(sentence=sentence):
                self.assertNotIn("C-DET-STACK", _constraints(sentence))

    def test_comparative_subordinate_is_not_a_runon(self):
        self.assertNotIn(
            "C-RUNON", _constraints("The situation is far worse than we expected."))

    def test_bare_infinitive_small_clause_is_complete(self):
        self.assertNotIn(
            "C-TENSE-FINITE", _constraints("We heard the door close."))

    def test_two_item_coordination_needs_no_list_comma(self):
        self.assertNotIn(
            "C-COMMA-OMISSION",
            _constraints("She bought a university guide and an umbrella."))

    def test_preposition_is_not_a_gerund_or_infinitive_error(self):
        self.assertNotIn(
            "C-GERUND-INFIN",
            _constraints("The book that the teacher recommended to the students "
                         "who were preparing for the exam was out of print."))

    def test_relative_clause_is_not_an_indirect_question(self):
        self.assertNotIn(
            "C-INDIRECT-WH-INVERSION",
            _constraints("When the alarm rang, the students who were in the "
                         "laboratory left the building immediately."))

    def test_comparative_less_is_not_a_quantifier_error(self):
        self.assertNotIn(
            "C-QUANTIFIER", _constraints("He earns less than his colleague."))
        self.assertNotIn(
            "C-QUANTIFIER", _constraints("There is little water left in the bottle."))

    def test_true_positives_still_fire(self):
        self.assertIn("C-COMMA-SPLICE", _constraints("I came, I saw."))
        self.assertIn("C-RUNON", _constraints("I came I saw."))
        self.assertIn("C-INDIRECT-Q-ORDER",
                      _constraints("I wonder who did she call."))
        self.assertIn("C-GERUND-INFIN", _constraints("I enjoy to play tennis."))
        self.assertIn("C-COMMA-OMISSION",
                      _constraints("I bought apples oranges and pears."))

    def test_number_agreement_correction_is_executable(self):
        payload = build_payload("The number of students are increasing.")
        self.assertIn("C-NUMBER-AGREE",
                      [d.get("constraint") for d in (payload.get("node_details") or {}).values()
                       if d.get("status") == "error"])
        correction = (payload.get("summary") or {}).get("correction") or {}
        self.assertEqual(correction.get("corrected_sentence"),
                         "The number of students is increasing.")


if __name__ == "__main__":
    unittest.main()
