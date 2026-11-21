"""Live parser checks for rule witnesses and learner-facing node evidence."""
import unittest

from analysis_api import build_payload
from findings import supported_findings
from parse_engine import analyze


class LearnerAnalysisTest(unittest.TestCase):
    def inspect(self, text, **kwargs):
        payload = build_payload(text, **kwargs)
        return payload, payload['learner_analysis']

    @staticmethod
    def words(payload):
        envelope = payload['br_analysis'].get('tree') or payload['br_analysis']['working_tree']

        def visit(node):
            if 'word' in node:
                yield node['word'], node['id']
            for child in node.get('children', []):
                yield from visit(child)

        return list(visit(envelope['root']))

    def test_agreement_targets_finite_verb_and_uses_actual_subject(self):
        payload, view = self.inspect('The boy with the bags walk.')
        finding, = view['findings']
        self.assertEqual(finding['target_token_ids'], [5])
        self.assertEqual(finding['related_token_ids'], [1])
        self.assertFalse(finding['book_verified'])
        words = dict(self.words(payload))
        self.assertIn('singular noun', view['nodes'][words['boy']]['text'])
        self.assertTrue(view['nodes'][words['boy']]['related'])
        self.assertFalse(view['nodes'][words['boy']]['error'])
        self.assertFalse(view['nodes'][words['bags']]['findings'])
        self.assertTrue(view['nodes'][words['walk']]['error'])
        self.assertEqual(view['revision']['text'], 'The boy with the bags walks.')

    def test_independent_findings_survive_a_working_tree(self):
        payload, view = self.inspect('If you dont know, the boys walks.')
        self.assertEqual(view['tree_status'], 'provisional')
        self.assertIsNone(payload['br_analysis']['tree'])
        self.assertEqual({row['constraint'] for row in view['findings']},
                         {'C-CONTRACTION', 'C-SUBJECT-AGREEMENT'})
        words = dict(self.words(payload))
        self.assertEqual(len(view['nodes'][words['walks']]['findings']), 1)
        self.assertEqual(len(view['nodes'][words['know']]['findings']), 1)
        self.assertIn('provisional', view['nodes'][words['walks']]['text'])
        self.assertIn("don't", view['revision']['text'])

    def test_agreement_mutations_and_exceptions(self):
        for name in ('Naomi', 'Mira'):
            for tail, error in [('walks to class every day.', False), ('walk to class every day.', True)]:
                with self.subTest(name=name, tail=tail):
                    _, view = self.inspect(f'{name} {tail}')
                    self.assertEqual(any(r['lesson'] == 'agreement' for r in view['findings']), error)
        for text in ('The boys walk.', 'Naomi and Lee walk.', 'If I were taller, I would play.',
                     'Three eggs is plenty.', 'What we need is more time.', 'The deer are here.', 'Naomi, walk.'):
            with self.subTest(text=text):
                _, view = self.inspect(text)
                self.assertFalse(any(r['lesson'] == 'agreement' for r in view['findings']))

    def test_two_distinct_errors_and_determiner_number_control(self):
        _, view = self.inspect('These child are tired.')
        self.assertEqual({row['lesson'] for row in view['findings']}, {'determiner', 'agreement'})
        self.assertEqual({i for row in view['findings'] for i in row['target_token_ids']}, {0, 2})
        self.assertEqual(view['revision']['text'], 'These children are tired.')
        _, view = self.inspect('These children are tired.')
        self.assertFalse(view['findings'])

    def test_auxiliaries_have_distinct_target_and_evidence(self):
        for text, other, bad in [('She can goes home.', 'can', 'goes'),
                                 ('The girls has went to school.', 'has', 'went')]:
            with self.subTest(text=text):
                payload, view = self.inspect(text)
                finding = next(row for row in view['findings'] if row['lesson'] == 'auxiliary')
                tokens = payload['parse']['tokens']
                self.assertEqual([tokens[i]['t'] for i in finding['target_token_ids']], [bad])
                self.assertEqual([tokens[i]['t'] for i in finding['related_token_ids']], [other])
        for text in ('She can cut it.', 'She has gone home.', 'She cut it yesterday.',
                     'She has been walking.', 'The notice was printed yesterday.'):
            with self.subTest(text=text):
                _, view = self.inspect(text)
                self.assertFalse(any(row['lesson'] == 'auxiliary' for row in view['findings']))

    def test_article_and_pronoun_case_controls(self):
        for text, code in [('An dog barks.', 'C-ARTICLE-MISMATCH'),
                           ('Me saw him.', 'C-PRONOUN-CASE')]:
            with self.subTest(text=text):
                _, view = self.inspect(text)
                self.assertIn(code, {row['constraint'] for row in view['findings']})
        for text in ('An hour passed.', 'A university opened.', 'An herb grew.',
                     'I saw him.', 'It is me.'):
            with self.subTest(text=text):
                _, view = self.inspect(text)
                self.assertFalse(set(row['constraint'] for row in view['findings'])
                                 & {'C-ARTICLE-MISMATCH', 'C-PRONOUN-CASE'})

    def test_subject_object_and_modifier_context(self):
        payload, view = self.inspect('The careful student read the book on the bus.')
        phrases = {record['text'] for record in view['nodes'].values()}
        self.assertTrue(any('subject of “read”' in text for text in phrases))
        self.assertTrue(any('direct object of “read”' in text for text in phrases))
        self.assertTrue(any('preposition “on”' in text and 'complement' in text for text in phrases))
        self.assertIn('predicate', view['sentence_text'])
        self.assertEqual(payload['explanation_evidence']['xai4_partial_evaluation']['enabled_rule_ids'], [])

    def test_unicode_sentence_offsets_and_repeated_word_identity(self):
        payload, view = self.inspect('😊 We waited. The boys walks beside the boys.', sentence_index=1)
        matching = [node for word, node in self.words(payload) if word == 'boys']
        self.assertEqual(len(matching), 2)
        self.assertTrue(view['nodes'][matching[0]]['related'])
        self.assertFalse(view['nodes'][matching[1]]['related'])
        self.assertFalse(view['nodes'][matching[1]]['error'])
        self.assertTrue(view['findings'])

    def test_partial_repair_retains_unresolved_word(self):
        payload, view = self.inspect('Ths cat sleepps.')
        revision = view['revision']
        self.assertEqual(revision['text'], 'Ths cat sleeps.')
        self.assertFalse(revision['impact']['whole_sentence_clean'])
        self.assertEqual(revision['impact']['unresolved_tokens'], [{'token_id': 0, 'surface': 'Ths'}])
        self.assertEqual(payload['parse']['text'], 'Ths cat sleepps.')
        _, view = self.inspect('The cat sleepps.')
        self.assertTrue(view['revision']['impact']['whole_sentence_clean'])

    def test_rule_name_alone_is_insufficient(self):
        analysis = analyze('The boys walk.')
        verb = next(item for item in analysis['nodes'].values() if item['surface'] == 'walk' and not item.get('children'))
        fabricated = {verb['id']: {'id': verb['id'], 'span': verb['span'], 'status': 'error',
                                  'constraint': 'C-SUBJECT-AGREEMENT', 'text': 'Invented contradiction'}}
        self.assertFalse(supported_findings(analysis, fabricated)[0])
        _, view = self.inspect('They demolished.')
        self.assertEqual(view['tree_status'], 'provisional')
        self.assertFalse(view['findings'])

    def test_generalized_evidence_propagation_across_rule_families(self):
        """Every corroborated rule family propagates into learner_analysis with
        real token targets, while grammatical controls emit zero findings."""
        cases = [
            ('She bought apple.', 'C-ARTICLE'),
            ('She gave me an advice.', 'C-UNCOUNTABLE'),
            ('She bought five book yesterday.', 'C-QUANT-PLURAL'),
            ('He drank many water.', 'C-QUANTIFIER'),
            ('Some my jobs are in jeopardy.', 'C-DET-STACK'),
            ('The two childs played outside.', 'C-NOUN-FORM'),
            ('He always brang bad marks home.', 'C-VERB-FORM'),
            ('He runs quick.', 'C-ADJ-ADV'),
            ('She is more taller than him.', 'C-COMPARATIVE-DOUBLE'),
            ('She must to leave now.', 'C-MODAL-TO'),
            ('They should of called earlier.', 'C-MODAL-OF'),
            ('Himself solved the puzzle.', 'C-REFLEXIVE-SUBJECT'),
            ('Sandra has ever planned to get a job.', 'C-NPI-LICENSING'),
            ('No man has revealed at least five forks.', 'C-SUPERLATIVE-QUANT'),
            ('She arrived the station.', 'C-INTRANSITIVE-OBJECT'),
            ('The boy was vanished.', 'C-INTRANSITIVE-PASSIVE'),
            ('What could Jessica sell these spotlights before noticing?', 'C-ADJUNCT-ISLAND'),
            ('Whose did you see car?', 'C-LEFT-BRANCH-ISLAND'),
            ('The meeting starts in Monday.', 'C-TIME-PLACE-PREP'),
            ('The boys was here yesterday.', 'C-SUBJECT-AGREEMENT'),
            ('Naomi and Lee walks to class.', 'C-SUBJECT-AGREEMENT'),
            ('She bought a books.', 'C-DETERMINER-AGREEMENT'),
            ('I went home, she stayed there.', 'C-COMMA-SPLICE'),
        ]
        for sentence, expected_code in cases:
            with self.subTest(ungrammatical=sentence, expected=expected_code):
                payload, view = self.inspect(sentence)
                codes = {row['constraint'] for row in view['findings']}
                self.assertIn(expected_code, codes, f'Missing {expected_code} in learner_analysis for {sentence!r}; got {codes}')
                for row in view['findings']:
                    self.assertTrue(row['text'].strip())
                    self.assertFalse(row['book_verified'])
                    # Non-erroneous related tokens must never collide with target tokens
                    self.assertFalse(set(row['target_token_ids']) & set(row['related_token_ids']))

        # Negative / grammatical controls across those exact families
        controls = [
            'She bought an apple.',
            'She gave me some advice.',
            'She bought five books yesterday.',
            'He drank much water.',
            'Some of my jobs are safe.',
            'The two children played outside.',
            'He always brought good books home.',
            'He runs quickly.',
            'She is taller than him.',
            'She must leave now.',
            'They should have called earlier.',
            'He solved the puzzle himself.',
            'Has Sandra ever planned to get a job?',
            'No man has revealed more than five forks.',
            'She arrived at the station.',
            'The boy vanished.',
            'Whose car did you see?',
            'The meeting starts on Monday.',
            'The boys were here yesterday.',
            'Naomi and Lee walk to class.',
            'She bought a few books.',
            'I went home, and she stayed there.',
        ]
        for sentence in controls:
            with self.subTest(grammatical_control=sentence):
                _, view = self.inspect(sentence)
                self.assertEqual(view['findings'], [], f'False finding on {sentence!r}: {view["findings"]}')

    def test_brang_nonstandard_irregular_repaired_to_brought(self):
        payload, view = self.inspect('He always brang bad marks home.')
        self.assertIn('C-VERB-FORM', {r['constraint'] for r in view['findings']})
        self.assertEqual(view['revision']['text'], 'He always brought bad marks home.')
        self.assertTrue(view['revision']['impact']['whole_sentence_clean'])

    def test_system_wide_word_phrase_clause_explanations_avoid_shallow_boilerplate(self):
        """Word, phrase, and clause nodes across supported B-R categories produce
        sentence-specific grammatical explanations rather than shallow slot text."""
        sentences = [
            'The careful student has read the book on the bus.',
            'Yesterday, Naomi and Lee quickly walked to the library.',
            'The window was broken by the storm, and the students noticed that it was cold.',
            'The book which she read was very interesting.',
        ]
        shallow_marker = 'position in '
        covered_labels = set()
        for sent in sentences:
            payload, view = self.inspect(sent)
            self.assertEqual(view['tree_status'], 'canonical', f'Expected canonical tree for {sent!r}')
            fg = payload['explanation_evidence']['fact_graph']
            for node in fg['nodes']:
                lbl = node.get('label')
                info = view['nodes'][node['node_id']]
                txt = info['text']
                self.assertTrue(txt.strip(), f'Empty explanation on {lbl} ({node.get("surface")})')
                if lbl in {'S', "S'", 'S-bar', 'S″', 'S-dbar', 'NP', 'NOM', 'VP', 'PP', 'AP', 'AdvP',
                           'N', 'V', 'A', 'Adv', 'P', 'ART', 'MOD', 'PERF', 'PASS', 'name', 'pronoun', 'C1', 'C2'}:
                    covered_labels.add(lbl)
                    self.assertNotIn(shallow_marker, txt, f'Shallow boilerplate on {lbl} in {sent!r}: {txt!r}')
                    self.assertNotIn('expresses what happens', txt, f'Generic VP text on {lbl}: {txt!r}')
        # Confirm broad B-R node category coverage was actually exercised
        self.assertTrue({'S', 'NP', 'NOM', 'VP', 'PP', 'AP', 'AdvP', 'N', 'V', 'A', 'Adv', 'P', 'ART', 'PERF', 'PASS', 'name', 'pronoun'} <= covered_labels,
                        f'Missing expected labels; covered={sorted(covered_labels)}')

    def test_provisional_word_nodes_keep_uncertainty_with_morphological_evidence(self):
        payload, view = self.inspect('If you dont know, the boys walks.')
        self.assertEqual(view['tree_status'], 'provisional')
        words = dict(self.words(payload))
        walks_info = view['nodes'][words['walks']]
        self.assertIn('provisional', walks_info['text'].lower())
        self.assertIn('verb', walks_info['text'].lower())
        self.assertTrue(walks_info['error'])
        boys_info = view['nodes'][words['boys']]
        self.assertTrue(boys_info['related'])
        self.assertFalse(boys_info['error'])


if __name__ == '__main__':
    unittest.main()
