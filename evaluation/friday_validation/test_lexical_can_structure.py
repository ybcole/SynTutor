
import unittest
from test_tree_structure import analyze


class TestLexicalCanStructure(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.singular = analyze("She cans the peaches.")
        cls.plural = analyze("They can the peaches.")

    def test_singular_lexical_can_normalized(self):
        """The existing supported lexical-verb construction."""
        self.assertEqual(
            self.singular["br_analysis"]["status"],
            "normalized",
        )

    def test_plural_lexical_can_normalized(self):
        """A lexical verb must not be rejected as an auxiliary."""
        self.assertEqual(
            self.plural["br_analysis"]["status"],
            "normalized",
            "The normalizer fails to handle plural-subject "
            "lexical 'can' in a transitive construction.",
        )

    def test_no_false_agreement_diagnostics(self):
        """Neither acceptable lexical construction needs repair."""
        for result in (self.singular, self.plural):
            self.assertEqual(
                result["summary"]["constraints_fired"],
                [],
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
