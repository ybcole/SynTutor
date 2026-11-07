"""Source-backed schema extensions; citations/review receipt are in sources/."""
import copy
import json
from pathlib import Path
import unittest
from jsonschema import Draft202012Validator, ValidationError
from burton_roberts import canonicalize_gold_record, validate_canonical_tree, build_canonical_analysis

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = Draft202012Validator(json.loads((ROOT / 'docs/canonical-burton-roberts-tree.schema.json').read_text()))


def source(chapter, ident):
    data = json.loads((ROOT / f'web/content/book/ch{chapter:02d}.trees.json').read_text())
    return next(row for row in data['trees'] if row['id'] == ident), data


def canonical(chapter, ident):
    row, data = source(chapter, ident)
    result = canonicalize_gold_record(row, data)
    if result['status'] != 'normalized': raise AssertionError(result)
    SCHEMA.validate(result['tree'])
    return result['tree']


def walk(node):
    yield node
    for child in node.get('children', []): yield from walk(child)


class SourceExtensionTests(unittest.TestCase):
    def test_empty_determiner_is_zero_word_not_gap(self):
        tree = canonical(7, 'ch7-10a')
        empty = next(node for node in walk(tree['root']) if node.get('empty'))
        self.assertEqual((empty['label'], empty['empty_role']), ('DET', 'determiner'))
        self.assertEqual(empty['token_span'], [0, 0])
        self.assertNotIn('word', empty); self.assertNotIn('gap', empty)
        self.assertEqual([token['text'] for token in tree['tokens']], ['essays'])

    def test_empty_complementiser_preserves_source_anomaly_flag(self):
        tree = canonical(9, 'ch9-26')
        self.assertEqual(tree['source']['evidence_status'], 'IMG_ANOMALY')
        self.assertTrue(any(node.get('empty_role') == 'complementiser' for node in walk(tree['root'])))
        self.assertTrue(any(node.get('features') == ['intens', 'pres'] for node in walk(tree['root'])))

    def test_ellipsis_marker_preserves_E_without_an_invented_word(self):
        tree = canonical(5, 'ch5-46')
        node = next(node for node in walk(tree['root']) if node.get('empty_role') == 'ellipsis')
        self.assertEqual(node['label'], 'E'); self.assertNotIn('word', node)
        self.assertEqual(node['token_span'][0], node['token_span'][1])

    def test_unlabelled_wh_triangle_is_not_guessed_to_be_NP(self):
        tree = canonical(9, 'ch9-d1a')
        node = next(node for node in walk(tree['root']) if node.get('unlabelled'))
        self.assertNotIn('label', node)
        self.assertEqual(node['words'], ['which', 'books'])
        invalid = copy.deepcopy(tree)
        invalid['root'] = next(node for node in walk(invalid['root']) if node.get('unlabelled'))
        self.assertFalse(validate_canonical_tree(invalid)['valid'])

    def test_legacy_envelope_remains_supported(self):
        tree = canonical(2, 'ch2-33'); tree['schema_version'] = '1.0.0'
        SCHEMA.validate(tree)
        self.assertTrue(validate_canonical_tree(tree)['valid'])

    def test_new_empty_nodes_cannot_claim_legacy_schema_version(self):
        tree = canonical(7, 'ch7-10a'); tree['schema_version'] = '1.0.0'
        with self.assertRaises(ValidationError): SCHEMA.validate(tree)
        self.assertFalse(validate_canonical_tree(tree)['valid'])

    def test_invalid_empty_role_overt_span_and_future_category_are_rejected(self):
        for change in [{'empty_role': 'ellipsis'}, {'token_span': [0, 1]}, {'label': 'NP'}]:
            tree = canonical(7, 'ch7-10a')
            empty = next(node for node in walk(tree['root']) if node.get('empty'))
            empty.update(change)
            self.assertFalse(validate_canonical_tree(tree)['valid'])
        tree = canonical(7, 'ch7-10a'); tree['convention_profile'] = {'chapter': 4, 'version': 'V4', 'profile_id': 'V4'}
        tree['source']['chapter'] = 4
        self.assertTrue(any('not introduced' in error for error in validate_canonical_tree(tree)['errors']))

    def test_possessive_and_curly_apostrophe_alignment(self):
        record, data = source(7, 'ch7-12')
        record['sentence'] = 'John’s father'
        result = canonicalize_gold_record(record, data)
        self.assertEqual(result['status'], 'normalized', result.get('errors'))
        self.assertEqual([token['char_span'] for token in result['tree']['tokens']], [[0, 4], [4, 6], [7, 13]])
        SCHEMA.validate(result['tree'])

    def test_alignment_does_not_match_inside_an_unrelated_word(self):
        row = {'id': 'false-substring', 'sentence': 'theory', 'status': 'IMG', 'tree': {'label': 'NP', 'children': [{'word': 'he'}]}}
        self.assertEqual(canonicalize_gold_record(row, {'chapter': 2})['status'], 'unresolved')

    def test_text_licensed_alternative_has_tree_and_retains_its_basis(self):
        tree = canonical(9, 'ch9-d3a')
        self.assertTrue(any(node.get('label') == 'AP' for node in walk(tree['root'])))
        alternative = tree['accepted_alternatives'][0]
        self.assertTrue(any(node.get('label') == 'PP' for node in walk(alternative['root'])))
        self.assertIn('not a separately printed diagram', alternative['rationale'])
        self.assertTrue(any('TXT' in note for note in tree['notes']))

    def test_introductory_Sentence_label_is_retained_as_printed(self):
        tree = canonical(2, 'ch2-2')
        self.assertEqual(tree['root']['label'], 'Sentence')
        self.assertEqual(tree['source']['printed_page'], 24)

    def test_full_importer_corpus_matches_schema_except_nonlinguistic_schematics(self):
        unresolved = []; total = 0
        for chapter in range(1, 11):
            data = json.loads((ROOT / f'web/content/book/ch{chapter:02d}.trees.json').read_text())
            for record in data['trees']:
                total += 1
                result = canonicalize_gold_record(record, data)
                if result['status'] == 'normalized': SCHEMA.validate(result['tree'])
                else: unresolved.append(record['id'])
        self.assertEqual(total, 252)
        self.assertEqual(set(unresolved), {'ch1-ex1', 'ch2-35'})
