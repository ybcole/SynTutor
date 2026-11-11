
import unittest
from test_tree_structure import analyze


class TestRunonControls(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.fused = analyze(
            "I like tea she likes coffee."
        )
        cls.joined = analyze(
            "I like tea, and she likes coffee."
        )
        cls.valid_question = analyze(
            "Can she swim?"
        )

    def test_genuine_fused_sentence_detected(self):
        rules = self.fused["summary"]["constraints_fired"]
        self.assertIn("C-RUNON", rules)

    def test_correctly_joined_clauses_not_flagged(self):
        rules = self.joined["summary"]["constraints_fired"]
        self.assertNotIn("C-RUNON", rules)

    def test_valid_question_not_flagged_as_runon(self):
        rules = self.valid_question["summary"]["constraints_fired"]
        self.assertNotIn("C-RUNON", rules)


if __name__ == "__main__":
    unittest.main(verbosity=2)
