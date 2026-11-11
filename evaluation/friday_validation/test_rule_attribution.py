
import unittest
import test_tree_structure as helpers


class TestModalRuleAttribution(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.singular = helpers.analyze("She cans sing.")
        cls.plural = helpers.analyze("They cans sing.")

    def test_singular_modal_inflection_detected(self):
        """Modal inflection must not depend on subject number."""
        rules = self.singular["summary"]["constraints_fired"]

        self.assertTrue(
            rules,
            "The system misses the invalid modal "
            "form in 'She cans sing.'",
        )

    def test_plural_modal_not_misclassified_as_agreement(self):
        """An inflected central modal is not an agreement error."""
        rules = self.plural["summary"]["constraints_fired"]

        self.assertNotIn(
            "C-SUBJECT-AGREEMENT",
            rules,
            "The system misclassifies modal inflection "
            "as subject-verb agreement.",
        )

    def test_plural_correction(self):
        """The existing minimal correction is appropriate."""
        correction = self.plural["summary"]["corrected_sentence"]

        self.assertEqual(
            correction,
            "They can sing.",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
