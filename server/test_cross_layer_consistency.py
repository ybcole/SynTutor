"""Cross-layer linguistic consistency, licensing, and explainability tests."""
import unittest

from analysis_api import build_payload


def _iter_tree(node):
    if not node:
        return
    yield node
    for child in node.get('children', []):
        yield from _iter_tree(child)


class CrossLayerLinguisticConsistencyTest(unittest.TestCase):
    def inspect(self, text):
        payload = build_payload(text)
        return payload, payload['learner_analysis']

    def assertGlobalInvariants(self, sentence, payload, view):
        for finding in view['findings']:
            self.assertFalse(
                set(finding['target_token_ids']) & set(finding['related_token_ids']),
                f'Target/related collision in {sentence!r}: {finding}',
            )
        tree = payload['br_analysis'].get('tree') or payload['br_analysis'].get('working_tree')
        labels_by_id = {n['id']: n.get('label') for n in _iter_tree(tree['root'])} if tree else {}
        for nid, nd in view['nodes'].items():
            text = nd.get('text', '')
            self.assertNotIn('It functions and serves as', text, f'Malformed prose on {nid} in {sentence!r}')
            if labels_by_id.get(nid) in {'N', 'NP', 'NOM'}:
                self.assertNotIn(
                    'predicative adjective complement', text,
                    f'Category/function contradiction on {nid} ({labels_by_id.get(nid)}) in {sentence!r}: {text}',
                )
            if nd.get('lesson'):
                self.assertTrue(nd['lesson']['route'].startswith('#lesson/'))

    def test_reported_sentence_i_am_scares_tomorrow(self):
        payload, view = self.inspect('I am scares tomorrow.')
        self.assertGlobalInvariants('I am scares tomorrow.', payload, view)
        self.assertEqual(view['verdict'], 'ungrammatical')
        codes = {row['constraint'] for row in view['findings']}
        self.assertIn('C-COPULA', codes)
        cop = next(row for row in view['findings'] if row['constraint'] == 'C-COPULA')
        self.assertEqual(cop['target_token_ids'], [2])
        self.assertEqual(cop['related_token_ids'], [0, 1])
        self.assertEqual(cop['lesson'], 'predicative')
        # Ambiguous intended meaning (scared vs scary vs scaring) -> must not silently guess
        self.assertIsNone(view.get('revision'))
        # No fabricated PP / empty P for temporal adjunct 'tomorrow'
        tree = payload['br_analysis']['tree']['root']
        labels = [n.get('label') for n in _iter_tree(tree)]
        self.assertNotIn('PP', labels)
        self.assertNotIn('P', labels)
        # 'scares' must not be described as a confirmed plural noun or predicative adjective complement
        scares_nodes = [
            view['nodes'][n['id']] for n in _iter_tree(tree)
            if n.get('word') == 'scares' or (n.get('label') == 'N' and any(c.get('word') == 'scares' for c in n.get('children', [])))
        ]
        self.assertTrue(scares_nodes)
        for nd in scares_nodes:
            self.assertNotIn('is a plural noun', nd['text'])
            self.assertNotIn('predicative adjective complement', nd['text'])
            self.assertTrue(nd['error'])
        # 'I' and 'am' carry related=True (non-erroneous) and qualified local agreement
        for w in ('I', 'am'):
            wn = next(view['nodes'][n['id']] for n in _iter_tree(tree) if n.get('word') == w)
            self.assertFalse(wn['error'])
            self.assertTrue(wn['related'])
            self.assertTrue(any('does not establish that the rest of the sentence is grammatical' in r for r in wn['relationships']))
        # Root S and outer VP must not leak unqualified local agreement
        self.assertEqual(view['nodes']['sg-root']['relationships'], [])
        # 'tomorrow' is explained as a temporal adjunct with adjunct lesson
        tom_word = next(view['nodes'][n['id']] for n in _iter_tree(tree) if n.get('word') == 'tomorrow')
        self.assertIn('temporal adverbial modifier', tom_word['text'])
        self.assertEqual(tom_word['lesson']['route'], '#lesson/br-05/concepts')

    def test_copular_predicative_number_mismatch_and_controls(self):
        for bad in ('I am teachers.', 'He is doctors.', 'She is students.'):
            with self.subTest(ungrammatical=bad):
                payload, view = self.inspect(bad)
                self.assertGlobalInvariants(bad, payload, view)
                self.assertEqual(view['verdict'], 'ungrammatical')
                cop = next((r for r in view['findings'] if r['constraint'] == 'C-COPULA'), None)
                self.assertIsNotNone(cop)
                self.assertEqual(cop['target_token_ids'], [2])
                self.assertEqual(cop['related_token_ids'], [0, 1])
                self.assertEqual(cop['lesson'], 'predicative')
                self.assertIsNone(view.get('revision'))

        controls = [
            'I am scared tomorrow.',
            'I am happy tomorrow.',
            'I am a teacher.',
            'They are teachers.',
            'We are students.',
            'Those are scares.',
            'I am friends with her.',
            'The problem is delays.',
            'The noise scares them.',
            'I am leaving tomorrow.',
        ]
        for good in controls:
            with self.subTest(grammatical=good):
                payload, view = self.inspect(good)
                self.assertGlobalInvariants(good, payload, view)
                self.assertEqual(view['findings'], [], f'Unexpected finding on {good!r}: {view["findings"]}')
                self.assertEqual(view['verdict'], 'grammatical')

    def test_those_are_scares_compatible_role_and_licensed_ellipsis(self):
        payload, view = self.inspect('Those are scares.')
        self.assertGlobalInvariants('Those are scares.', payload, view)
        tree = payload['br_analysis']['tree']['root']
        scares_node = next(view['nodes'][n['id']] for n in _iter_tree(tree) if n.get('word') == 'scares')
        self.assertIn('plural noun', scares_node['text'])
        self.assertIn('predicative complement of “are”', scares_node['text'])
        self.assertNotIn('adjective', scares_node['text'])
        # Elided noun after 'Those' must name its licensor 'Those'
        elided_nodes = [n for n in _iter_tree(tree) if n.get('label') == 'E']
        self.assertTrue(elided_nodes)
        elided_text = view['nodes'][elided_nodes[0]['id']]['text']
        self.assertIn('“Those”', elided_text)
        self.assertIn('licensed', elided_text)

    def test_auxiliary_be_plus_finite_verb_and_valid_irregulars(self):
        payload, view = self.inspect('She is sleeps today.')
        self.assertGlobalInvariants('She is sleeps today.', payload, view)
        self.assertEqual(view['verdict'], 'ungrammatical')
        aux = next((r for r in view['findings'] if r['constraint'] == 'C-AUX-FORM'), None)
        self.assertIsNotNone(aux)
        self.assertEqual(aux['target_token_ids'], [2])
        self.assertEqual(aux['related_token_ids'], [1])
        self.assertEqual(view['revision']['text'], 'She is sleeping today.')
        self.assertTrue(view['revision']['impact']['whole_sentence_clean'])

        for valid in ('She has gone home.', 'The notice was printed yesterday.', 'She cut it yesterday.'):
            with self.subTest(valid_irregular=valid):
                p, v = self.inspect(valid)
                self.assertGlobalInvariants(valid, p, v)
                self.assertEqual(v['findings'], [])

    def test_temporal_adjuncts_avoid_fabricated_pp_and_mixed_coord_stays_clean(self):
        for s in ('She leaves tomorrow.', 'She hardly slept last night.', 'They arrived yesterday.'):
            with self.subTest(temporal=s):
                payload, view = self.inspect(s)
                self.assertGlobalInvariants(s, payload, view)
                self.assertEqual(view['findings'], [])
                tree = payload['br_analysis']['tree']['root']
                labels = [n.get('label') for n in _iter_tree(tree)]
                self.assertNotIn('PP', labels)
                self.assertNotIn('P', labels)
                # Zero-determiner DET slot must not claim an omitted spoken article
                empty_dets = [n for n in _iter_tree(tree) if n.get('label') == 'DET' and not n.get('children')]
                for det in empty_dets:
                    self.assertIn('no spoken article is omitted', view['nodes'][det['id']]['text'])

        # Mixed temporal coordination ('tomorrow or on Friday') stays grammatical
        payload, view = self.inspect('She will arrive tomorrow or on Friday.')
        self.assertGlobalInvariants('She will arrive tomorrow or on Friday.', payload, view)
        self.assertEqual(view['findings'], [])

    def test_multiple_errors_and_ambiguous_ellipsis_qualification(self):
        payload, view = self.inspect("I seen him yesterday and he don't care.")
        self.assertGlobalInvariants("I seen him yesterday and he don't care.", payload, view)
        self.assertGreaterEqual(len(view['findings']), 2)
        self.assertEqual(view['verdict'], 'ungrammatical')

        # Ambiguous bare transitive ellipsis remains provisional without fabricated findings
        p2, v2 = self.inspect('They demolished.')
        self.assertGlobalInvariants('They demolished.', p2, v2)
        self.assertEqual(v2['findings'], [])
        self.assertEqual(v2['tree_status'], 'provisional')
        self.assertIn('reliable syntax tree', v2['sentence_text'])

    def test_lexical_uncertainty_and_determiner_controls(self):
        # 1-3. Canonical determiner / demonstrative / possessive controls
        det_controls = [
            ('The cat sleeps.', 'ART', 'The'),
            ('This cat sleeps.', 'DEM', 'This'),
            ('His cat sleeps.', 'POSS', 'His'),
        ]
        for sentence, expected_label, expected_word in det_controls:
            with self.subTest(control=sentence):
                payload, view = self.inspect(sentence)
                self.assertGlobalInvariants(sentence, payload, view)
                self.assertEqual(payload['br_analysis']['status'], 'normalized')
                self.assertEqual(view['tree_status'], 'canonical')
                self.assertEqual(view['findings'], [])
                self.assertIsNone(payload['summary'].get('unresolved_tokens'))
                root = payload['br_analysis']['tree']['root']
                labels = [n.get('label') for n in _iter_tree(root)]
                self.assertIn('DET', labels)
                self.assertIn(expected_label, labels)

        # 4-5. Uncertain determiner-slot tokens ('Ths cat sleeps.', 'Ths boys walk.')
        uncertain_cases = [
            ('Ths cat sleeps.', 'cat', 'sleeps', ('“The”', '“This”')),
            ('Ths boys walk.', 'boys', 'walk', ('“The”', '“These”', '“Those”')),
        ]
        for sentence, noun, verb, expected_readings in uncertain_cases:
            with self.subTest(uncertain=sentence):
                payload, view = self.inspect(sentence)
                self.assertGlobalInvariants(sentence, payload, view)
                # Must not promote 'Ths' into a verified canonical DET -> POSS tree
                self.assertEqual(payload['br_analysis']['status'], 'unresolved')
                self.assertIsNone(payload['br_analysis']['tree'])
                self.assertIsNotNone(payload['br_analysis']['working_tree'])
                self.assertEqual(view['tree_status'], 'provisional')
                self.assertEqual(payload['summary']['unresolved_tokens'], [{'token_id': 0, 'surface': 'Ths'}])
                self.assertEqual(view['unresolved_tokens'], [{'token_id': 0, 'surface': 'Ths'}])
                self.assertEqual(view['consistency']['unresolved_tokens'], ['Ths'])
                w_root = payload['br_analysis']['working_tree']['root']
                w_labels = [n.get('label') for n in _iter_tree(w_root)]
                self.assertNotIn('POSS', w_labels)
                self.assertNotIn('DET', w_labels)
                # Valid local subject-verb agreement is preserved and qualified
                self.assertTrue(any(r['matches'] and r['kind'] == 'subject_verb_agreement' for r in view['relationships']))
                self.assertIn('provisional analysis', view['sentence_text'].lower())
                self.assertIn('“Ths”', view['sentence_text'])
                self.assertIn('uncertain', view['sentence_text'].lower())
                self.assertIn(f'“{noun}”', view['sentence_text'])
                self.assertIn(f'“{verb}”', view['sentence_text'])
                self.assertIn('agrees with its subject', view['sentence_text'])
                for reading in expected_readings:
                    self.assertIn(reading, view['sentence_text'])
                # Node explanation for 'Ths' communicates uncertainty and never claims possessive
                for nd in view['nodes'].values():
                    self.assertNotIn('possessive word', nd['text'].lower())
                    self.assertNotIn('possessive position', nd['text'].lower())
                ths_node = view['nodes']['sg-root-0-0']
                self.assertIn('uncertain', ths_node['text'].lower())
                for reading in expected_readings:
                    self.assertIn(reading, ths_node['text'])
                self.assertEqual(ths_node.get('lesson', {}).get('route'), '#lesson/br-07/concepts')

        # 6. Clear transposed determiner typo ('Teh cat sleeps.')
        payload, view = self.inspect('Teh cat sleeps.')
        self.assertGlobalInvariants('Teh cat sleeps.', payload, view)
        self.assertEqual(payload['br_analysis']['status'], 'unresolved')
        self.assertEqual(view['tree_status'], 'provisional')
        self.assertEqual(payload['summary']['unresolved_tokens'], [{'token_id': 0, 'surface': 'Teh'}])
        self.assertTrue(any(f['constraint'] == 'C-SPELLING' and '“the”' in f['text'] for f in view['findings']))
        for nd in view['nodes'].values():
            self.assertNotIn('“Teh” is a noun', nd['text'])

        # 7-8. Proper-name controls ('Tsh arrived yesterday.', 'Ana sleeps.')
        for prop in ('Tsh arrived yesterday.', 'Ana sleeps.'):
            with self.subTest(proper_name=prop):
                payload, view = self.inspect(prop)
                self.assertGlobalInvariants(prop, payload, view)
                self.assertEqual(payload['br_analysis']['status'], 'normalized')
                self.assertEqual(view['tree_status'], 'canonical')
                self.assertEqual(view['findings'], [])
                self.assertIsNone(payload['summary'].get('unresolved_tokens'))
                self.assertIsNone(view.get('revision'))
                root = payload['br_analysis']['tree']['root']
                labels = [n.get('label') for n in _iter_tree(root)]
                self.assertIn('name', labels)


if __name__ == '__main__':
    unittest.main()
