"""Regression tests for FINAL-D1 non-finite clause subjects.

Covers CONVENTIONS.md V8 (clauses as subject sit under NP) and V10 (non-finite
clauses, covert subjects, [-tense]), plus the V4 complex-transitive object
predicative that Benepar wraps in a verbless S node.

Run:  python test_final_d1_nonfinite_subject.py
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api import build_payload, model_status


def _models_ready():
    return bool(model_status().get('ready'))


@unittest.skipUnless(_models_ready(), 'parser models not installed')
class NonFiniteSubjectProjectionTest(unittest.TestCase):
    def canonical(self, text):
        payload = build_payload(text)
        analysis = payload.get('br_analysis') or {}
        return payload, analysis

    def assert_projected(self, text):
        payload, analysis = self.canonical(text)
        self.assertEqual(payload['summary'].get('verdict'), 'grammatical', text)
        self.assertEqual(analysis.get('status'), 'normalized', text)
        root = (analysis.get('tree') or {}).get('root')

        def triangles(node):
            return (1 if node.get('triangle') else 0) + sum(
                triangles(child) for child in node.get('children', []))

        self.assertEqual(triangles(root), 0, text)

    def test_reported_gerund_subject(self):
        self.assert_projected('Running every morning keeps him healthy.')

    def test_additional_gerund_subjects(self):
        for sentence in [
            'Reading books makes me happy.',
            'Swimming in the sea keeps us fit.',
            'Walking to work keeps her healthy.',
        ]:
            with self.subTest(sentence=sentence):
                self.assert_projected(sentence)

    def test_infinitive_subjects(self):
        for sentence in [
            'To learn a language requires patience.',
            'To finish the task took two hours.',
            'To travel alone can be dangerous.',
        ]:
            with self.subTest(sentence=sentence):
                self.assert_projected(sentence)

    def test_ordinary_np_subject_is_not_misread_as_a_clause(self):
        self.assert_projected('Running water keeps him healthy.')

    def test_case_error_in_object_predicative_subject(self):
        payload, _ = self.canonical('Running every morning keeps he healthy.')
        self.assertEqual(payload['summary'].get('verdict'), 'ungrammatical')

    def test_clause_subject_is_singular_for_agreement(self):
        for sentence in [
            'Running every morning keep him healthy.',
            'To learn languages require patience.',
        ]:
            with self.subTest(sentence=sentence):
                payload, _ = self.canonical(sentence)
                self.assertEqual(payload['summary'].get('verdict'), 'ungrammatical')


if __name__ == '__main__':
    unittest.main()
