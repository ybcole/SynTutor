"""Contract tests: CoLA is an advisory signal, never a rule authority."""

import unittest

from detector import combine


class CoLAAdvisoryContractTests(unittest.TestCase):
    @staticmethod
    def matrix_summary(verdict="grammatical"):
        return {
            "verdict": verdict,
            "valid": verdict == "grammatical",
            "explanation": "Matrix explanation remains authoritative for rule findings.",
            "constraints_fired": [],
            "violations": [],
        }

    @staticmethod
    def detector_result(acceptable):
        return {
            "available": True,
            "model": "test-CoLA",
            "label": "acceptable" if acceptable else "unacceptable",
            "acceptable": acceptable,
            "acceptable_prob": 0.99 if acceptable else 0.01,
            "confidence": 0.99,
            "explanation": "Model acceptability signal only.",
        }

    def test_model_rejection_only_downgrades_clean_result_to_unverified(self):
        original = self.matrix_summary("grammatical")
        merged = combine(original, self.detector_result(False))

        self.assertEqual(merged["verdict"], "unverified")
        self.assertEqual(merged["constraints_fired"], [])
        self.assertEqual(merged["violations"], [])
        self.assertEqual(merged["explanation"], original["explanation"])
        self.assertIn("not condemned", merged["detector_note"])

    def test_model_cannot_overrule_a_rule_explained_violation(self):
        original = self.matrix_summary("ungrammatical")
        original["constraints_fired"] = ["LEGACY-001"]
        merged = combine(original, self.detector_result(True))

        self.assertEqual(merged["verdict"], "ungrammatical")
        self.assertEqual(merged["constraints_fired"], ["LEGACY-001"])
        self.assertEqual(merged["explanation"], original["explanation"])

    def test_model_acceptance_does_not_create_a_grammatical_rule_finding(self):
        original = self.matrix_summary("unverified")
        merged = combine(original, self.detector_result(True))

        self.assertEqual(merged["verdict"], "unverified")
        self.assertEqual(merged["constraints_fired"], [])
        self.assertEqual(merged["violations"], [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
