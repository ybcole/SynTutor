"""Dependency-free regression tests for diagnostic authority reconciliation."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'server'))
from diagnostic_authority import reconcile_summary  # noqa: E402


class DiagnosticAuthorityTests(unittest.TestCase):
    def test_model_rejection_never_certifies_grammaticality(self):
        original = {
            'verdict': 'unverified', 'valid': True,
            'explanation': "'They can the peaches .' is grammatical: every word is used in an allowed way.",
            'constraints_fired': [], 'unverified': [], 'checker_errors': [],
            'detector': {'available': True, 'acceptable': False, 'acceptable_prob': 0.1413},
            'detector_note': 'CoLA rejected this sentence',
        }
        actual = reconcile_summary(original, canonical_status='unresolved')
        self.assertEqual(actual['verdict'], 'unverified')
        self.assertEqual(actual['diagnostic_assessment']['status'], 'unverified')
        self.assertTrue(actual['diagnostic_assessment']['model_disagreement'])
        self.assertNotIn('is grammatical:', actual['explanation'])
        self.assertIn('model flagged', actual['explanation'])
        self.assertIn('canonical syntax analysis is unresolved', actual['explanation'])
        self.assertEqual(actual['detector_note'], original['detector_note'])
        self.assertEqual(original['explanation'], "'They can the peaches .' is grammatical: every word is used in an allowed way.")

    def test_no_supported_error_is_not_certification(self):
        result = reconcile_summary({'verdict': 'grammatical', 'valid': True, 'constraints_fired': [],
                                    'explanation': 'Every word is allowed.'}, canonical_status='normalized')
        self.assertEqual(result['verdict'], 'grammatical')  # backwards compatibility
        self.assertEqual(result['diagnostic_assessment']['status'], 'no_supported_error')
        self.assertFalse(result['diagnostic_assessment']['independently_verified'])
        self.assertIn('does not independently verify', result['explanation'])
        self.assertFalse(result['book_verified'])

    def test_rule_diagnosis_is_not_silenced_by_acceptability_model(self):
        original = {'verdict': 'ungrammatical', 'constraints_fired': ['C-SUBJECT-AGREEMENT'],
                    'violations': ['n4'], 'explanation': "The boys and 'runs' do not match.",
                    'detector': {'available': True, 'acceptable': True}}
        result = reconcile_summary(original, canonical_status='unresolved')
        self.assertEqual(result['verdict'], 'ungrammatical')
        self.assertEqual(result['explanation'], original['explanation'])
        self.assertEqual(result['diagnostic_assessment']['status'], 'rule_reported_violation')
        self.assertFalse(result['diagnostic_assessment']['independently_verified'])

    def test_rule_only_unverified_retains_uncertainty(self):
        result = reconcile_summary({'verdict': 'unverified', 'constraints_fired': [],
                                    'unverified': ['n4:1.12'], 'checker_errors': [],
                                    'explanation': 'Old generic explanation'})
        self.assertEqual(result['diagnostic_assessment']['acceptability_signal'], 'unavailable')
        self.assertIn('checks remain unresolved', result['explanation'])
        self.assertNotIn('grammatical:', result['explanation'])

    def test_model_acceptance_does_not_override_rule_uncertainty(self):
        result = reconcile_summary({'verdict': 'unverified', 'constraints_fired': [],
                                    'detector': {'available': True, 'acceptable': True},
                                    'unverified': ['n2']}, canonical_status='normalized')
        self.assertEqual(result['diagnostic_assessment']['status'], 'unverified')
        self.assertEqual(result['verdict'], 'unverified')

    def test_contradictory_summary_fails_closed(self):
        result = reconcile_summary({'verdict': 'grammatical',
                                    'constraints_fired': ['C-RUNON'],
                                    'explanation': 'Fully grammatical.'})
        self.assertEqual(result['verdict'], 'unverified')
        self.assertEqual(result['diagnostic_assessment']['status'], 'unverified')

    def test_missing_state_fails_closed(self):
        result = reconcile_summary({}, canonical_status='unresolved')
        self.assertEqual(result['verdict'], 'unverified')
        self.assertFalse(result['book_verified'])

    def test_unverified_without_model_rejection_does_not_make_claim(self):
        result = reconcile_summary({'verdict': 'unverified', 'valid': True,
                                    'explanation': 'is grammatical:',
                                    'detector': {'available': False, 'acceptable': False}}, canonical_status='normalized')
        self.assertNotIn('is grammatical:', result['explanation'])
        self.assertEqual(result['diagnostic_assessment']['acceptability_signal'], 'unavailable')


if __name__ == '__main__':
    unittest.main()
