
import unittest
from test_tree_structure import analyze


class TestDiagnosticContract(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.clean = analyze("She can sing.")
        cls.missed = analyze("She cans sing.")
        cls.detected = analyze("The boys runs.")

    def test_legacy_fields_remain_compatible(self):
        """Existing consumers must retain legacy fields."""
        summary = self.clean["summary"]

        self.assertEqual(
            summary["verdict"], "grammatical"
        )
        self.assertIs(
            summary["book_verified"], False
        )
        self.assertEqual(
            summary["verdict_authority"],
            "legacy_diagnostic",
        )

    def test_no_error_detected_is_not_certification(self):
        """No diagnostic is not proof of correctness."""
        summary = self.clean["summary"]

        self.assertEqual(
            summary.get("diagnostic_status"),
            "no_supported_error_detected",
        )
        self.assertIs(
            summary.get("grammaticality_certified"),
            False,
        )

    def test_missed_error_preserves_uncertainty(self):
        """Structural uncertainty must remain visible."""
        summary = self.missed["summary"]
        br = self.missed["br_analysis"]

        self.assertEqual(
            summary["constraints_fired"], []
        )
        self.assertEqual(
            br["status"], "unresolved"
        )
        self.assertEqual(
            summary.get("diagnostic_status"),
            "no_supported_error_detected",
        )
        self.assertIs(
            summary.get("grammaticality_certified"),
            False,
        )

    def test_detected_violation_preserves_authority(self):
        """Legacy findings must not become book certification."""
        summary = self.detected["summary"]

        self.assertIn(
            "C-SUBJECT-AGREEMENT",
            summary["constraints_fired"],
        )
        self.assertEqual(
            summary.get("diagnostic_status"),
            "supported_violation_detected",
        )
        self.assertIs(
            summary.get("grammaticality_certified"),
            False,
        )
        self.assertIs(
            summary["book_verified"], False
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
