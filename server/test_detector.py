"""Contract tests: CoLA is an advisory signal, never a rule authority."""

import importlib.util
from pathlib import Path
import unittest

# Load the real detector module by path. test_api_contract installs temporary
# sys.modules stubs while importing api.py; that stub must not leak into this
# independent unit test.
_SPEC = importlib.util.spec_from_file_location(
    "_syntutor_detector_under_test", Path(__file__).with_name("detector.py")
)
_DETECTOR = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_DETECTOR)
combine = _DETECTOR.combine


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


class ModelSuggestionAuthorityTests(unittest.TestCase):
    def test_proposed_edit_does_not_create_error_or_change_verdict(self):
        import api
        import copy
        from unittest.mock import patch
        summary = {'valid': False, 'verdict': 'unverified', 'constraints_fired': []}
        details = {}
        original = copy.deepcopy(summary)
        leaf = {'id': 'word', 'type': 'VBP'}
        located = {'bad': 'go', 'good': 'goes', 'position': 0,
                   'corrected_text': 'She goes', 'cola_p': 0.99}
        # Exercise the production helper's complete advisory path without models.
        with patch.object(api, 'evaluate', return_value={'summary': {'valid': True}, 'details': {}}), \
             patch.object(api, 'analyze', return_value={'root': leaf, 'sentence': 'She goes'}), \
             patch.object(api, '_tree_leaves', return_value=[leaf]), \
             patch.object(api.corrector, 'morph_diff', return_value=('go', 'VBP', 'base', 'VBZ', 'third'), create=True), \
             patch.object(api.corrector, 'EXTENDED_TAG_LABEL', {}, create=True), \
             patch.object(api.corrector, 'template', return_value='Test suggestion', create=True):
            suggestion = api._apply_correction(located, leaf, details, summary, 'She go', {'acceptable_prob': 0.1})
        self.assertEqual(summary, original)
        self.assertEqual(details, {})
        self.assertIn('advisory', suggestion['method'])


if __name__ == "__main__":
    unittest.main(verbosity=2)
