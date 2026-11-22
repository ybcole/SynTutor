import csv
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from run_h02_grounding_comparator import exact_mcnemar, holm_adjust, pair_groups, run_ungrounded, write_review
from run_reference_specified import compare


def node(label, *children):
    return {'label': label, 'children': [
        {'word': child} if isinstance(child, str) else child for child in children
    ]}


class ReferenceSpecifiedTests(unittest.TestCase):
    gold = node('S', {'label': 'NP', 'triangle': True, 'words': ['these', 'old', 'maps']},
                node('VP', node('V', 'tore')))

    def test_ignores_only_unmatched_strict_interiors(self):
        pred = node('S', node('NP', 'these', node('NOM', 'old', 'maps')), node('VP', 'tore'))
        result = compare(self.gold, pred)
        self.assertFalse(result['full_exact'])
        self.assertTrue(result['specified_exact'])
        self.assertEqual(result['ignored'], [{'span': (1, 3, 'NOM'), 'count': 1,
                                              'reference_triangle': (0, 3)}])

    def test_wrong_category_at_triangle_boundary_and_crossing_attachment_fail(self):
        for pred, expected in (
            (node('S', node('PP', 'these', 'old', 'maps'), node('VP', 'tore')), (0, 3, 'PP')),
            (node('S', node('NP', 'these', 'old'), node('VP', 'maps', 'tore')), (2, 4, 'VP')),
        ):
            with self.subTest(pred=pred):
                result = compare(self.gold, pred)
                self.assertFalse(result['specified_exact'])
                self.assertIn(expected, result['predicted_only'])
                self.assertIn((0, 3, 'NP'), result['gold_only'])

    def test_failure_retains_the_gold_denominator(self):
        for pred in (None, node('S', 'These', 'new', 'maps', 'tore')):
            result = compare(self.gold, pred)
            self.assertEqual(result['gold'], 3)
            self.assertEqual(result['matched'], 0)
            self.assertEqual(result['ignored'], [])


class ComparatorTests(unittest.TestCase):
    def test_exact_and_adjusted_p_values(self):
        self.assertEqual(exact_mcnemar(12, 1)['p_value'], 0.00341797)
        self.assertEqual(exact_mcnemar(2, 2)['p_value'], 1)
        self.assertEqual(holm_adjust({'first': .01, 'second': .03, 'third': .04}),
                         {'first': .03, 'second': .06, 'third': .06})

    def test_rejects_incomplete_or_repeated_minimal_pairs(self):
        good = {'item_id': 'family:2:grammatical', 'gold_label': 'grammatical', 'sentence': 'We walk.'}
        bad = {'item_id': 'family:2:ungrammatical', 'gold_label': 'ungrammatical', 'sentence': 'We walks.'}
        self.assertEqual(len(pair_groups([good, bad])), 1)
        with self.assertRaises(ValueError):
            pair_groups([good])
        with self.assertRaises(ValueError):
            pair_groups([good, good, bad])

    def test_unavailable_detector_does_not_issue_a_grammar_error(self):
        view = {'parse': {'text': 'We walk.', 'tokens': []}, 'summary': {}}
        with patch('run_h02_grounding_comparator.detector.classify', return_value=None):
            result = run_ungrounded('We walk.', view)
        self.assertEqual(result['verdict'], 'unverified')
        self.assertEqual(result['findings'], [])

    def test_neural_control_does_not_reuse_grounded_feedback(self):
        view = {
            'parse': {'text': 'We walk.', 'tokens': []},
            'summary': {'detector': {'available': True, 'acceptable': True},
                        'verdict': 'ungrammatical', 'corrected_sentence': 'We walks.'},
            'learner_analysis': {'findings': [{'constraint': 'C-SUBJECT-AGREEMENT'}]},
        }
        with patch('run_h02_grounding_comparator.corrector.sweep') as sweep:
            result = run_ungrounded('We walk.', view)
        sweep.assert_not_called()
        self.assertEqual(result['verdict'], 'grammatical')
        self.assertIsNone(result['corrected_sentence'])
        self.assertEqual(result['findings'], [])

    def test_review_intake_preserves_identical_and_unavailable_rows_with_blank_ratings(self):
        a = ('available', 'grammatical', '', 'Main clause.')
        b = ('available', 'unverified', '', '')
        missing = ('unavailable', '', '', '')
        with TemporaryDirectory() as output:
            directory = Path(output)
            summary = write_review(directory, [('First.', a, b), ('Second.', a, a), ('Third.', missing, missing)])
            key_path = directory / 'BLINDED_KEY_SEALED.json'
            self.assertEqual(key_path.stat().st_mode & 0o777, 0o600)
            key = json.loads(key_path.read_text())
            with Path(summary['path']).open(newline='') as source:
                records = list(csv.DictReader(source))
        self.assertEqual(summary['n_total_pairs'], 3)
        self.assertEqual(summary['n_identical_pairs'], 2)
        self.assertEqual(summary['n_both_available'], 2)
        self.assertEqual(len({row['pair_id'] for row in key}), 3)
        self.assertEqual({row['pair_id'] for row in records}, {row['pair_id'] for row in key})
        first = next(row for row in records if row['source_sentence'] == 'First.')
        first_key = next(row for row in key if row['pair_id'] == first['pair_id'])
        grounded_arm = next(arm for arm in ('X', 'Y') if first_key[arm] == 'grounded')
        self.assertEqual(first[f'{grounded_arm}_verdict'], 'grammatical')
        self.assertTrue(all(not value for row in records for field, value in row.items()
                            if field.endswith('_rating') or field == 'notes'))


if __name__ == '__main__':
    unittest.main()
