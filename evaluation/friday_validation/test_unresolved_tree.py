
import unittest
import test_tree_structure as helpers


class TestUnresolvedTree(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.data = helpers.analyze("She can sings.")
        cls.summary = cls.data.get("summary") or {}
        cls.br = cls.data.get("br_analysis") or {}
        cls.cambridge = cls.data.get("cambridge_evaluation") or {}

    def test_legacy_detects_modal_error(self):
        self.assertIn(
            "C-MODAL-VERB-FORM",
            self.summary.get("constraints_fired", []),
        )

    def test_correction_candidate(self):
        self.assertEqual(
            self.summary.get("corrected_sentence"),
            "She can sing.",
        )

    def test_canonical_tree_unresolved(self):
        self.assertEqual(
            self.br.get("status"),
            "unresolved",
        )

    def test_cambridge_not_evaluated(self):
        self.assertEqual(
            self.cambridge.get("status"),
            "not_evaluated",
        )

    def test_not_book_verified(self):
        self.assertIs(
            self.summary.get("book_verified"),
            False,
        )

    def test_legacy_and_canonical_are_distinct(self):
        self.assertEqual(
            self.summary.get("verdict"),
            "ungrammatical",
        )
        self.assertNotEqual(
            self.br.get("status"),
            "normalized",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
