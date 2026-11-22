"""Parser-backed controls for local grammar evidence and repair safety."""
import unittest
from itertools import product
from unittest.mock import patch

import analysis_api
import corrections
from parse_engine import analyze, load_models
from webapp import app


class RealWorldNlpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        load_models()
        cls.client = app.test_client()

    def parse(self, text, **options):
        response = self.client.post('/api/parse', json={'text': text, **options})
        self.assertEqual(response.status_code, 200, response.json)
        payload = response.json
        source = payload['parse']['sentences'][options.get('sentence_index', 0)]
        self.assertEqual(payload['parse']['text'], source['text'])
        for token in payload['parse']['tokens']:
            self.assertEqual(text.strip()[token['start']:token['end']], token['t'])
        for item in payload['unified_findings']['findings']:
            start, end = item['span']
            self.assertLess(start, end)
            self.assertLessEqual(end, len(payload['parse']['tokens']))
            self.assertIn(item['legacy_node_id'], payload['nodes'])
        tree = payload['br_analysis']
        if tree.get('working_tree'):
            self.assertIsNone(tree['tree'])
            self.assertEqual(tree['working_tree']['source']['evidence_status'], 'UNCERTAIN')
        self.assertFalse(payload['learner_explanation']['whole_sentence_certified'])
        return payload

    @staticmethod
    def constraints(payload):
        return set(payload['summary']['constraints_fired'])

    def test_be_with_past_only_forms(self):
        for subject, be, past, target in [('I', 'am', 'ate', 'an apple'),
                                          ('Mira', 'is', 'wrote', 'a letter'),
                                          ('We', 'are', 'saw', 'a fox')]:
            with self.subTest(subject=subject, past=past):
                text = f'{subject} {be} {past} {target} yesterday.'
                payload = self.parse(text)
                self.assertIn('C-BE-PAST', self.constraints(payload))
                self.assertIsNone(payload['br_analysis']['tree'])
                rows = [row for row in payload['unified_findings']['findings']
                        if row['rule_id'] == 'C-BE-PAST']
                self.assertEqual(len(rows), 1)
                self.assertIn('past participle', rows[0]['violation'])
                self.assertIn(past, rows[0]['violation'])
                if subject == 'I':
                    self.assertEqual(payload['summary']['corrected_sentence'],
                                     'I ate an apple yesterday.')
        for text in ['The apple was eaten yesterday.', 'The apple was cut yesterday.',
                     'I am eating an apple.', 'The last thing I did was eat an apple.',
                     'The apple is gone.', 'Is the apple being eaten?']:
            with self.subTest(text=text):
                result = self.parse(text)
                self.assertNotIn('C-BE-PAST', self.constraints(result))
                self.assertIsNone(result['summary'].get('correction'))

    def test_nonlocal_be_diagnostics_withhold_tense_or_voice_rewrite(self):
        for text in ['I am not ate an apple yesterday.', 'Am I ate an apple yesterday?',
                     'He will be saw by everyone.', 'The apple was ate yesterday.']:
            with self.subTest(text=text):
                result = self.parse(text)
                self.assertIn('C-BE-PAST', self.constraints(result))
                self.assertNotIn('C-RUNON', self.constraints(result))
                self.assertIsNone(result['summary'].get('correction'))
                self.assertIsNone(result['br_analysis']['tree'])

    def test_contraction_and_clause_completeness_are_independent(self):
        result = self.parse('First sentence. If you dont know.', sentence_index=1)
        self.assertEqual(self.constraints(result), {'C-CONTRACTION', 'C-FRAGMENT'})
        self.assertIsNone(result['summary'].get('correction'))
        self.assertIn('(RB do) (RB nt)', result['parse']['parse_string'])
        self.assertTrue(result['br_analysis']['working_tree'])
        spelling = next(row for row in result['unified_findings']['findings']
                        if row['rule_id'] == 'C-CONTRACTION')
        self.assertEqual(spelling['span'], [2, 4])
        self.assertIn('‘know’ is the lexical verb', spelling['violation'])
        self.assertIn('in conversation', next(row['violation'] for row in
                      result['unified_findings']['findings'] if row['rule_id'] == 'C-FRAGMENT'))
        for text, expected in [
            ("If you don't know.", {'C-FRAGMENT'}),
            ('If you don’t know, ask Naomi.', set()),
            ('When you know, tell me.', set()),
            ('A cant is a kind of slope.', set()),
            ("He ain't coming.", set()),
            ('We demand that he know the truth.', set()),
            ('Do not touch the glass.', set()),
        ]:
            with self.subTest(text=text):
                self.assertEqual(self.constraints(self.parse(text)), expected)
        for source, repair in [
            ('Naomi doesnt know the answer.', "Naomi doesn't know the answer."),
            ('They didnt arrive.', "They didn't arrive."),
            ('If you dont know, ask Naomi.', "If you don't know, ask Naomi."),
            ('I cant swim.', "I can't swim."),
        ]:
            with self.subTest(source=source):
                self.assertEqual(self.parse(source)['summary']['corrected_sentence'], repair)
        informal = self.parse('He aint coming.')
        self.assertEqual(self.constraints(informal), {'C-CONTRACTION'})
        finding = informal['unified_findings']['findings'][0]
        self.assertIn("ain't", finding['suggested_fix'])
        homograph = self.parse('A cant is a kind of slope.')
        self.assertIsNone(homograph['br_analysis']['tree'])
        self.assertIsNone(homograph['summary'].get('correction'))

    def test_names_technical_words_and_orthographic_pairs(self):
        for text in ["Naomi's MacBook connects to OpenAI.",
                     'José-Luis and Amihan work at DLSU-D in Dasmariñas.',
                     'X Æ A-12 arrived.', 'iPhone sales increased.',
                     'They use epifluorescence microscopy.', 'We measured qudit coherence.',
                     'CRISPR-Cas9 cuts DNA.', 'She rides a unicycle.',
                     'An umbrella is useful.', 'Naomi said, “Go!”',
                     'My favorite color is rose.', 'The shade is cream.']:
            with self.subTest(text=text):
                result = self.parse(text)
                self.assertFalse(self.constraints(result))
                self.assertIsNone(result['summary'].get('correction'))
        self.assertIn('C-ARTICLE-MISMATCH', self.constraints(self.parse('She rides an unicycle.')))
        self.assertIn('C-ARTICLE', self.constraints(self.parse('She bought apple.')))
        self.assertEqual(self.parse('They recieved it yesterday.')['summary']['corrected_sentence'],
                         'They received it yesterday.')
        words = self.client.post('/api/words', json={'words': ['OpenAI', 'Dasmariñas', 'qudit', 42]})
        self.assertEqual(words.status_code, 200)
        self.assertTrue(all(row['suggestion'] is None for row in words.json['results']))

    def test_auxiliary_checks_respect_phrase_boundaries_and_voice(self):
        for text in [
            'They are doing their job as well as they can, waiting for relief.',
            'She does her homework, listening to music.',
            'She can, when necessary, do her homework alone.',
            'She is commonly known as a writer.',
            'She is describing the sculpture.',
            'The last thing I did was read a book.',
        ]:
            with self.subTest(text=text):
                payload = self.parse(text)
                self.assertNotIn('C-AUX-FORM', self.constraints(payload))
                self.assertIsNone(payload['summary'].get('correction'))

        for text, correction, wanted, evidence, detail in [
            ('She is commonly know as a writer.', None, 'know', ['is'], 'past participle'),
            ('The parcels are usually deliver by Naomi.', 'The parcels are usually delivered by Naomi.',
             'deliver', ['are', 'by'], 'past participle'),
            ('The child is play outside.', None, 'play', ['is'], 'progressive'),
            ('She can not working today.', 'She can not work today.',
             'working', ['can'], 'plain form'),
        ]:
            with self.subTest(text=text):
                payload = self.parse(text)
                finding = next(f for f in payload['learner_analysis']['findings']
                               if f['constraint'] == 'C-AUX-FORM')
                tokens = {token['i']: token['t'] for token in payload['parse']['tokens']}
                self.assertEqual([tokens[i] for i in finding['target_token_ids']], [wanted])
                self.assertEqual([tokens[i] for i in finding['related_token_ids']], evidence)
                self.assertIn(detail, finding['text'])
                self.assertEqual(payload['summary'].get('corrected_sentence'), correction)

    def test_existential_quantified_agreement_highlights_the_witness(self):
        for text in [
            'There are plenty of books.', 'There is plenty of water.',
            'There are a lot of apples.', 'There is a lot of milk.',
            'There is a box of shells.', 'There are plenty.',
        ]:
            with self.subTest(text=text):
                payload = self.parse(text)
                self.assertNotIn('C-EXISTENTIAL', self.constraints(payload))
                self.assertIsNone(payload['summary'].get('correction'))
        for text, fix, verb, head in [
            ('There is plenty of books.', 'There are plenty of books.', 'is', 'books'),
            ('There are lots of water.', 'There is lots of water.', 'are', 'water'),
            ('There were a box of shells.', 'There was a box of shells.', 'were', 'box'),
        ]:
            with self.subTest(text=text):
                payload = self.parse(text)
                finding = next(f for f in payload['learner_analysis']['findings']
                               if f['constraint'] == 'C-EXISTENTIAL')
                tokens = {token['i']: token['t'] for token in payload['parse']['tokens']}
                self.assertEqual([tokens[i] for i in finding['target_token_ids']], [verb])
                self.assertIn(head, [tokens[i] for i in finding['related_token_ids']])
                self.assertIn(head, finding['text'])
                self.assertEqual(payload['summary'].get('corrected_sentence'), fix)

    def test_bare_noun_and_little_readings_preserve_meaning(self):
        for text in [
            'They bought little red houses.', 'There is little milk.',
            'She plays handball.', 'The referee called a handball.',
            'Summer is hot.', 'It was a summer of rain.',
            'They took immediate action.', 'They took an unusual action.',
        ]:
            with self.subTest(text=text):
                payload = self.parse(text)
                self.assertFalse(self.constraints(payload))
                self.assertIsNone(payload['summary'].get('correction'))
        self.assertIn('C-ARTICLE', self.constraints(self.parse('She bought bicycle.')))
        self.assertEqual(self.parse('There are much books.')['summary']['corrected_sentence'],
                         'There are many books.')
        self.assertNotIn('C-COUNT-MASS', self.constraints(self.parse('They like little changes.')))

    def test_stranded_recipient_retains_direct_object_and_linked_gap(self):
        for text, receiver, direct_object in [
            ('Who will Alex give the package to?', 'Who', 'package'),
            ('Who did Naomi send the photograph to?', 'Who', 'photograph'),
        ]:
            with self.subTest(text=text):
                payload = self.parse(text)
                self.assertEqual(payload['br_analysis']['status'], 'normalized', payload['br_analysis'])
                root = payload['br_analysis']['tree']['root']

                def flatten(node):
                    yield node
                    for child in node.get('children', ()):
                        yield from flatten(child)

                predicate = next(node for node in flatten(root) if node.get('label') == 'VP'
                                 and node['children'][0].get('label') == 'V')
                head, obj, recipient = predicate['children']
                self.assertIn('ditrans', head['features'])
                self.assertEqual((obj['label'], recipient['label']), ('NP', 'PP'))
                self.assertIn(direct_object, [node.get('word') for node in flatten(obj)])
                prep, gap = recipient['children']
                self.assertEqual(prep['children'][0]['word'], 'to')
                self.assertTrue(gap['children'][0]['gap'])
                wh = root['children'][0]
                self.assertEqual(wh['children'][0]['word'], receiver)
                self.assertEqual(wh['index'], gap['children'][0]['index'])
                self.assertIsNone(payload['summary'].get('correction'))

    def test_request_boundaries_and_model_failure_have_no_verdict(self):
        for body, expected in [({'text': '  '}, 422), ({'text': '🙂?!'}, 422),
                               ({'text': '今天下雨。'}, 422),
                               ({'text': 'a' * 12001}, 400), ({'text': 42}, 400),
                               ({'text': 'a' * 250001}, 413)]:
            with self.subTest(expected=expected, length=len(str(body))):
                with patch.object(analysis_api, 'analyze') as parser:
                    response = self.client.post('/api/parse', json=body)
                    self.assertEqual(response.status_code, expected)
                    self.assertNotIn('summary', response.json)
                    parser.assert_not_called()
        with patch('webapp.build_payload', side_effect=RuntimeError('parser unavailable')), \
                patch('webapp.health_payload', return_value={'error': 'model unavailable'}):
            response = self.client.post('/api/parse', json={'text': 'She sings.'})
            self.assertEqual(response.status_code, 503)
            self.assertNotIn('summary', response.json)
        self.assertEqual(self.client.post('/api/words', json=['word']).status_code, 400)

    def test_generated_whitespace_and_unicode_inputs_keep_aligned_evidence(self):
        for name, spaces, ending in product(('Naomi', 'José', 'X Æ A-12'),
                                            (' ', ' \n '), ('.', '?!')):
            text = f'{name}{spaces}called{ending}'
            with self.subTest(text=text):
                result = self.parse(text)
                self.assertEqual(result['parse']['text'], text)
                self.assertIsNone(result['summary'].get('correction'))

    def test_correction_prose_cannot_edit_same_word_outside_the_evidence_span(self):
        text = 'She read the book.'
        tokens = analyze(text)['tokens']
        detail = {'status': 'error', 'span': [0, 1], 'surface': 'She',
                  'constraint': 'test', 'remediation': {'suggested_fix': "Change 'book' to 'letter'."}}
        self.assertIsNone(corrections.assemble(text, {'n': detail}, tokens, validate=lambda _: True))
        self.assertFalse(analysis_api._validate_correction('She read. He are late.'))


if __name__ == '__main__':
    unittest.main()
