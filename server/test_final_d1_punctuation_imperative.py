"""Regression tests for terminal punctuation and supported imperatives.

Terminal punctuation is removed from the phrase-marker projection only; the
sentence string, parser tokens and offsets remain untouched.  Imperatives use
the existing NP-gap subject convention; negative do-support and 'please' remain
unresolved until a source figure establishes their node labels.

Run:  python test_final_d1_punctuation_imperative.py
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api import build_payload, model_status


def _models_ready():
    return bool(model_status().get('ready'))


@unittest.skipUnless(_models_ready(), 'parser models not installed')
class PunctuationAndImperativeTest(unittest.TestCase):
    def payload(self, text):
        return build_payload(text)

    def assert_normalized(self, text):
        payload = self.payload(text)
        self.assertEqual(payload['summary'].get('verdict'), 'grammatical', text)
        self.assertEqual(payload['br_analysis'].get('status'), 'normalized', text)
        return payload

    def test_terminal_punctuation_is_not_a_phrase_marker_node(self):
        for text, mark in [
            ('The cat sleeps.', '.'),
            ('Where are the keys?', '?'),
            ('Close the door!', '!'),
        ]:
            with self.subTest(text=text):
                payload = self.assert_normalized(text)
                self.assertEqual(payload['parse']['text'], text)
                self.assertTrue(any(t.get('t') == mark for t in payload['parse']['tokens']))
                # No POS/punctuation node leaks into the canonical tree.
                def labels(node):
                    yield node.get('label')
                    for child in node.get('children', []):
                        yield from labels(child)
                self.assertNotIn(mark, {label for label in labels(
                    payload['br_analysis']['tree']['root']) if label})

    def test_supported_imperatives(self):
        for text in [
            'Close the door.',
            'Open the window.',
            'Bring me the book.',
            'Sit down.',
            'Do my laundry for me.',
        ]:
            with self.subTest(text=text):
                payload = self.assert_normalized(text)
                self.assertTrue(payload['parse']['text'].endswith('.'))

    def test_negative_do_support_stays_unresolved_pending_source(self):
        payload = self.payload('Do not touch the paintings.')
        self.assertEqual(payload['br_analysis'].get('status'), 'unresolved')
        self.assertTrue(any('TENSE' in d.get('message', '')
                            for d in payload['br_analysis'].get('diagnostics', [])))

    def test_please_imperative_stays_unresolved_pending_source(self):
        payload = self.payload('Please close the door.')
        self.assertEqual(payload['br_analysis'].get('status'), 'unresolved')


if __name__ == '__main__':
    unittest.main()
