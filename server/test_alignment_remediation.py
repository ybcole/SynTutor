"""Production-path controls for the 26-sentence reliability remediation."""
import unittest

from analysis_api import build_payload
from parse_engine import load_models


class AlignmentRemediationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        load_models()

    def test_scoped_edits_and_highlights(self):
        examples = (
            ('He met really tall a woman.', 'He met a really tall woman.', 'C-ARTICLE-ORDER', 'a'),
            ('I wonder where did they find it.', 'I wonder where they found it.', 'C-INDIRECT-Q-ORDER', 'did'),
            ('Do the children can swim?', 'Can the children swim?', 'C-DO-MODAL', 'Do'),
            ('The window was broke by the storm.', 'The window was broken by the storm.', 'C-BE-PAST', 'broke'),
            ('They made her to laugh.', 'They made her laugh.', 'C-CAUSATIVE-TO', 'to'),
            ('The vase which we bought it was expensive.', 'The vase which we bought was expensive.',
             'C-RESUMPTIVE-RELATIVE', 'it'),
            ('Each of these books belong here.', 'Each of these books belongs here.',
             'C-SUBJ-AGREE-XP', 'belong'),
            ('He drives carefully very.', 'He drives very carefully.', 'C-DEGREE-ORDER', 'very'),
        )
        for text, corrected, code, target in examples:
            with self.subTest(text=text):
                payload = build_payload(text)
                summary = payload['summary']
                self.assertEqual(summary['verdict'], 'ungrammatical')
                self.assertEqual(summary.get('corrected_sentence'), corrected)
                self.assertTrue(summary['correction']['validation_scope']['reparsed'])
                self.assertFalse(summary['correction']['validation_scope']['independent_meaning_verification'])
                local = [f for f in payload['learner_analysis']['findings'] if f['constraint'] == code]
                self.assertEqual(len(local), 1)
                self.assertFalse(local[0]['book_verified'])
                self.assertEqual([text[s:e] for s, e in local[0]['target_char_spans']], [target])
                self.assertTrue(local[0]['related_token_ids'])
                self.assertTrue(any(node['error'] for node in payload['learner_analysis']['nodes'].values()))
                if code == 'C-SUBJ-AGREE-XP':
                    finding = next(f for f in payload['unified_findings']['findings'] if f['rule_id'] == code)
                    self.assertIsNone(finding['alternative_fix'])
                    self.assertRegex(finding['violation'], r"'Each' controls singular (?:agreement|match)")
                    self.assertIn("not the noun inside the following 'of' phrase", finding['violation'])

    def test_grammatical_neighbors(self):
        for text in (
            'Both her friends arrived.',
            'I wonder where they did find it.',
            'Can the children swim?',
            'The window was broken by the storm.',
            'She was made to wait.',
            'They made her laugh.',
            'The vase which we bought was expensive.',
            'Each of these books belongs here.',
            'He drives very carefully.',
            'She put the keys on the shelf.',
        ):
            with self.subTest(text=text):
                result = build_payload(text)
                self.assertEqual(result['summary']['verdict'], 'grammatical')
                self.assertIsNone(result['summary'].get('correction'))
        # Literary degree inversion is grammatical even if the advisory model
        # abstains; the deterministic order rule must not diagnose or repair it.
        inversion = build_payload('He met so tall a woman.')
        self.assertNotEqual(inversion['summary']['verdict'], 'ungrammatical')
        self.assertNotIn('C-ARTICLE-ORDER', inversion['summary']['constraints_fired'])
        self.assertIsNone(inversion['summary'].get('correction'))

    def test_no_invented_context_or_contradictory_roles(self):
        named = build_payload('Alex scratched herself.')
        self.assertNotIn('C-REFLEXIVE-ANTECEDENT', named['summary']['constraints_fired'])
        self.assertTrue(named['summary']['contextual_notes'])
        self.assertIsNone(named['summary'].get('correction'))

        placement = build_payload('She put the keys.')
        self.assertIn('C-PLACEMENT-COMPLEMENT', placement['summary']['constraints_fired'])
        self.assertIn('location', placement['learner_analysis']['findings'][0]['text'])
        self.assertIsNone(placement['summary'].get('correction'))

        selected = build_payload('They made her to laugh.')
        self.assertFalse(any(r['kind'] == 'pronoun_case' and not r['matches']
                             for r in selected['learner_analysis']['relationships']))
        self.assertNotEqual(selected['br_analysis']['status'], 'normalized')

        uncertain = build_payload('Which gift did you wonder whether he bought?')
        self.assertEqual(uncertain['summary']['verdict'], 'unverified')
        self.assertNotIn('is grammatical', uncertain['summary']['explanation'])
        self.assertIsNone(uncertain['br_analysis']['tree'])
        self.assertIsNone(uncertain['summary'].get('correction'))
