"""Regression tests for correction completeness vs. safety and proper-name protection."""
import sys
import unittest
from pathlib import Path

from analysis_api import build_payload
from spellcheck import known_word, strong_typo_candidate

EVAL_DIR = Path(__file__).resolve().parents[1] / 'docs' / 'audits' / 'technical_evaluation'
if str(EVAL_DIR) not in sys.path:
    sys.path.insert(0, str(EVAL_DIR))


class CorrectionCompletenessAndSafetyTest(unittest.TestCase):
    def test_ths_is_not_falsely_known_and_partial_repair_is_labeled_partial(self):
        self.assertFalse(known_word('Ths'))
        self.assertFalse(known_word('ths'))
        self.assertIsNone(strong_typo_candidate('Ths'))
        # Valid 3-letter words remain known
        for valid3 in ('the', 'has', 'was', 'his', 'its', 'yes', 'bus', 'gas', 'ads'):
            self.assertTrue(known_word(valid3), f'Expected {valid3!r} to remain known')

        payload = build_payload('Ths cat sleepps.')
        impact = payload['summary']['correction']['impact']
        rev = payload['learner_analysis']['revision']
        self.assertEqual(rev['text'], 'Ths cat sleeps.')
        self.assertFalse(impact['whole_sentence_clean'])
        self.assertEqual(impact['completeness'], 'partial')
        self.assertEqual(impact['unresolved_tokens'], [{'token_id': 0, 'surface': 'Ths'}])

    def test_complete_repair_is_labeled_complete(self):
        payload = build_payload('The cat sleepps.')
        impact = payload['summary']['correction']['impact']
        rev = payload['learner_analysis']['revision']
        self.assertEqual(rev['text'], 'The cat sleeps.')
        self.assertTrue(impact['whole_sentence_clean'])
        self.assertEqual(impact['completeness'], 'complete')
        self.assertFalse(impact.get('unresolved_tokens'))

    def test_repaired_contractions_are_marked_complete(self):
        for bad, good in (
            ('Naomi doesnt know the answer.', "Naomi doesn't know the answer."),
            ('They didnt arrive.', "They didn't arrive."),
        ):
            with self.subTest(sentence=bad):
                payload = build_payload(bad)
                self.assertEqual(payload['summary'].get('corrected_sentence'), good)
                impact = (payload['summary'].get('correction') or {}).get('impact') or {}
                self.assertTrue(impact.get('whole_sentence_clean'))
                self.assertEqual(impact.get('completeness'), 'complete')
                self.assertFalse(impact.get('unresolved_tokens'))

    def test_already_correct_sentences_are_never_silently_rewritten(self):
        for text in (
            'The cat sleeps.',
            'The students read books in the library.',
            'She arrived yesterday.',
            'I am scared tomorrow.',
        ):
            with self.subTest(grammatical=text):
                payload = build_payload(text)
                self.assertIsNone(payload['summary'].get('corrected_sentence'))
                self.assertIsNone(payload['learner_analysis'].get('revision'))
                self.assertEqual(payload['learner_analysis']['findings'], [])

    def test_capitalized_proper_names_and_short_tokens_are_protected(self):
        for text in (
            'Ana sleeps.',
            'Lee runs fast.',
            'Kim read a book.',
            'Kiyel arrived yesterday.',
            'Brang arrived in Manila.',
            'Tsh arrived yesterday.',
        ):
            with self.subTest(proper_name=text):
                payload = build_payload(text)
                self.assertIsNone(payload['summary'].get('corrected_sentence'))
                self.assertEqual(payload['learner_analysis']['findings'], [])

    def test_transposed_ambiguous_determiner_is_not_claimed_complete(self):
        payload = build_payload('Teh cat sleepps.')
        self.assertEqual(payload['summary']['verdict'], 'ungrammatical')
        self.assertNotEqual(payload['summary'].get('corrected_sentence'), 'A Teh cat sleeps.')
        unresolved = payload['summary'].get('unresolved_tokens') or []
        self.assertTrue(any(t['surface'] == 'Teh' for t in unresolved), unresolved)
        correction = payload['summary'].get('correction')
        if correction:
            impact = correction['impact']
            self.assertFalse(impact['whole_sentence_clean'])
            self.assertEqual(impact['completeness'], 'partial')
            self.assertTrue(any(t['surface'] == 'Teh' for t in impact.get('unresolved_tokens', [])))

        second = build_payload('Teh cat sleeps.')
        self.assertEqual(second['summary']['verdict'], 'ungrammatical')
        self.assertNotEqual(second['summary'].get('corrected_sentence'), 'A Teh cat sleeps.')
        self.assertTrue(any(f['constraint'] == 'C-SPELLING' for f in second['learner_analysis']['findings']))
        self.assertTrue(any(t['surface'] == 'Teh' for t in second['summary'].get('unresolved_tokens') or []))

    def test_multi_error_sentence_labels_partial_or_resolves_both_honestly(self):
        for text, expected_corr in (
            ('Ths boys walks.', 'Ths boys walk.'),
            ('Ths boys walks yesterday.', None),
        ):
            with self.subTest(sentence=text):
                payload = build_payload(text)
                correction = payload['summary'].get('correction')
                if expected_corr is not None:
                    self.assertIsNotNone(correction)
                    self.assertEqual(correction['corrected_sentence'], expected_corr)
                if correction:
                    impact = correction['impact']
                    self.assertFalse(impact['whole_sentence_clean'])
                    self.assertEqual(impact['completeness'], 'partial')
                    self.assertTrue(any(t['surface'] == 'Ths' for t in impact.get('unresolved_tokens', [])))

    def test_standalone_parse_exposes_unresolved_tokens_for_preview_consistency(self):
        for uncertain, surface in (
            ('Ths cat sleeps.', 'Ths'),
            ('Ths boys walk.', 'Ths'),
        ):
            with self.subTest(uncertain=uncertain):
                payload = build_payload(uncertain)
                unresolved = payload['summary'].get('unresolved_tokens') or []
                self.assertTrue(any(t['surface'] == surface for t in unresolved), unresolved)
        for clean in ('The cat sleeps.', 'The boys walk.', 'Tsh arrived yesterday.'):
            with self.subTest(clean=clean):
                payload = build_payload(clean)
                self.assertFalse(payload['summary'].get('unresolved_tokens'))

    def test_copular_finding_is_not_duplicated_in_learner_analysis(self):
        payload = build_payload('I am scares tomorrow.')
        findings = payload['learner_analysis']['findings']
        copula = [f for f in findings if f.get('constraint') == 'C-COPULA']
        self.assertEqual(len(copula), 1, findings)
        self.assertEqual(copula[0]['target_token_ids'], [2])
        self.assertEqual(copula[0]['related_token_ids'], [0, 1])

    def test_audit_distinguishes_morph_syntax_safety_from_spelling_completeness(self):
        from run_cycle7_evaluation import independent_check_correction
        from run_cycle8_evaluation import audit_correction_safety

        partial = audit_correction_safety(
            'Ths cat sleepps.', 'Ths cat sleeps.', ['C-LEXICON-MALFORMED'],
            independent_check_correction,
            whole_sentence_clean=False,
            unresolved_tokens=[{'token_id': 0, 'surface': 'Ths'}],
        )
        self.assertTrue(partial['independent_morph_syntax_clean'])
        self.assertFalse(partial['spelling_complete'])
        self.assertEqual(partial['correction_completeness'], 'partial_review_required')
        self.assertIn('Ths', partial['remaining_uncertain_tokens'])

        complete = audit_correction_safety(
            'The cat sleepps.', 'The cat sleeps.', ['C-LEXICON-MALFORMED'],
            independent_check_correction,
            whole_sentence_clean=True,
            unresolved_tokens=[],
        )
        self.assertTrue(complete['independent_morph_syntax_clean'])
        self.assertTrue(complete['spelling_complete'])
        self.assertEqual(complete['correction_completeness'], 'complete')
        self.assertEqual(complete['remaining_uncertain_tokens'], [])


if __name__ == '__main__':
    unittest.main()
