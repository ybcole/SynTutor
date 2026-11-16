"""Existential there and non-finite relatives (Ch2 pp.26–27; Ch9; Ch10 p.242).

The expletive is a subject NP whose only terminal is *there*. Locative *there*
must not receive that subject NP analysis. Non-finite relatives keep a covert
C2 operator and an object gap.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api import build_payload, model_status


def _models_ready():
    return bool(model_status().get('ready'))


def walk(node):
    yield node
    for child in node.get('children', []):
        yield from walk(child)


@unittest.skipUnless(_models_ready(), 'parser models not installed')
class ExistentialThereTest(unittest.TestCase):
    def projected(self, text):
        payload = build_payload(text)
        self.assertEqual(payload['summary'].get('verdict'), 'grammatical', text)
        self.assertEqual(payload['br_analysis'].get('status'), 'normalized', text)
        return payload

    def subject_np(self, root):
        for child in root.get('children', []):
            if child.get('label') == 'NP':
                return child
        self.fail('no subject NP')

    def test_existential_there_is_an_np_subject(self):
        for text in [
            'There are many reasons to celebrate.',
            'There is a small park near the station.',
            'There were three cats in the garden.',
            'There seems to be a problem.',
            'There is a book to read.',
        ]:
            with self.subTest(text=text):
                payload = self.projected(text)
                root = payload['br_analysis']['tree']['root']
                subject = self.subject_np(root)
                words = [n['word'] for n in walk(subject) if n.get('word')]
                self.assertEqual(words, ['There'])
                self.assertEqual(payload['parse']['text'], text)

    def test_locative_there_is_not_an_expletive_subject(self):
        for text in ['The book is there.', 'The keys are there.', 'She stayed there.']:
            with self.subTest(text=text):
                payload = self.projected(text)
                root = payload['br_analysis']['tree']['root']
                subject = self.subject_np(root)
                words = [n['word'] for n in walk(subject) if n.get('word')]
                self.assertNotEqual(words, ['there'])
                self.assertNotEqual(words, ['There'])

    def test_existential_agreement_errors_are_rejected(self):
        for text in ['There is many reasons.', 'There are a reason.']:
            with self.subTest(text=text):
                payload = build_payload(text)
                self.assertEqual(payload['summary'].get('verdict'), 'ungrammatical')

    def test_nonfinite_relative_has_covert_operator_and_gap(self):
        payload = self.projected('There are many reasons to celebrate.')
        root = payload['br_analysis']['tree']['root']
        labels = [n.get('label') for n in walk(root)]
        gaps = [n for n in walk(root) if n.get('gap')]
        self.assertIn('C2', labels)
        self.assertTrue(gaps)

    def test_expletive_subject_explanation_is_not_the_generic_subject_text(self):
        payload = self.projected('There are many reasons to celebrate.')
        texts = [d.get('text') or '' for d in payload['node_details'].values()]
        self.assertTrue(any('expletive subject' in text and 'does not name'
                            in text for text in texts))


if __name__ == '__main__':
    unittest.main()
