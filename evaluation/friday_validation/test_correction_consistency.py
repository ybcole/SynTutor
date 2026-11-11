
import unittest
from test_tree_structure import analyze


class TestCorrectionConsistency(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.original = analyze("These book are heavy.")
        cls.repaired = analyze("These books are heavy.")
        cls.alternative = analyze("This book is heavy.")

    def test_primary_correction(self):
        """The selected correction is grammatically coherent."""
        correction = self.original["summary"].get(
            "corrected_sentence"
        )
        self.assertEqual(
            correction,
            "These books are heavy.",
        )

    def test_repairs_have_no_legacy_errors(self):
        """Both coherent interpretations should be accepted."""
        for result in (
            self.repaired,
            self.alternative,
        ):
            self.assertEqual(
                result["summary"]["constraints_fired"],
                [],
            )

    def test_advice_coordinates_with_selected_repair(self):
        """
        Advice must not unconditionally recommend a change
        that conflicts with the selected final correction.
        """
        details = self.original.get("node_details") or {}

        agreement_advice = [
            str(detail.get("text") or "").lower()
            for detail in details.values()
            if detail.get("constraint")
            == "C-SUBJECT-AGREEMENT"
        ]

        self.assertTrue(
            agreement_advice,
            "Expected an agreement diagnostic.",
        )

        for advice in agreement_advice:
            if "use 'is'" in advice:
                self.assertIn(
                    "this book is heavy",
                    advice,
                    "The explanation recommends 'is', "
                    "but does not explain the coherent "
                    "singular alternative to the selected "
                    "plural correction.",
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
