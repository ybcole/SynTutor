
import unittest
from test_tree_structure import analyze


class TestQuestionModal(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.valid = analyze("Can she swim?")
        cls.invalid = analyze("Can she swims?")

    def test_valid_question_unflagged(self):
        """An acceptable modal question needs no diagnostic."""
        rules = self.valid["summary"]["constraints_fired"]
        self.assertEqual(rules, [])

    def test_invalid_question_detects_modal_form(self):
        """A modal requires the plain form of its following verb."""
        rules = self.invalid["summary"]["constraints_fired"]
        self.assertIn(
            "C-MODAL-VERB-FORM",
            rules,
            "The system fails to attribute the question's "
            "error to modal verb-form selection.",
        )

    def test_question_not_misclassified_as_runon(self):
        """One interrogative clause is not a run-on sentence."""
        rules = self.invalid["summary"]["constraints_fired"]
        self.assertNotIn(
            "C-RUNON",
            rules,
            "The system incorrectly diagnoses the "
            "question as a run-on sentence.",
        )

    def test_question_correction(self):
        """The correction should preserve interrogative syntax."""
        correction = self.invalid["summary"].get(
            "corrected_sentence"
        )
        self.assertEqual(correction, "Can she swim?")


if __name__ == "__main__":
    unittest.main(verbosity=2)
