"""Regression tests for syntax-generator false positives and false negatives.

These run the real parser + rule matrix, so they are skipped when the spaCy /
Benepar models are not installed.

Run:  python test_false_positive_regressions.py
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api import build_payload, model_status


def _models_ready():
    status = model_status()
    return bool(status.get('ready'))


@unittest.skipUnless(_models_ready(), 'parser models not installed')
class FalsePositiveRegressionTest(unittest.TestCase):
    def verdict(self, text):
        return build_payload(text)['summary'].get('verdict')

    def test_reported_copula_plus_plural_event_noun_is_rejected(self):
        self.assertEqual(self.verdict('The boys are walks.'), 'ungrammatical')

    def test_copula_with_legitimate_person_noun_complement_is_accepted(self):
        self.assertEqual(self.verdict('The boys are cooks.'), 'grammatical')

    def test_demonstrative_plus_event_noun_is_accepted(self):
        self.assertEqual(self.verdict('These are walks.'), 'grammatical')

    def test_mass_noun_object_does_not_need_an_article(self):
        self.assertEqual(self.verdict('Her younger sister studies medicine.'), 'grammatical')

    def test_singular_s_subject_takes_singular_verb(self):
        self.assertEqual(self.verdict('Mathematics is difficult but rewarding.'), 'grammatical')

    def test_singular_news_subject(self):
        self.assertEqual(self.verdict('The news surprised everyone.'), 'grammatical')

    def test_have_subject_aux_inversion_keeps_participle(self):
        self.assertEqual(self.verdict('Never have I seen such a beautiful sunset.'), 'grammatical')

    def test_adverb_inside_is_licensed(self):
        self.assertEqual(self.verdict('If it rains, we will stay inside.'), 'grammatical')


if __name__ == '__main__':
    unittest.main()
