"""Real spaCy/Benepar + shared API regressions for modal category gating."""
import unittest
from unittest.mock import patch
import api


class ModalCategoryRuntimeTests(unittest.TestCase):
    def test_lexical_homographs_have_no_modal_diagnosis_or_repair(self):
        cases = [('The can rusts.', 'can', 'NN'),
                 ('The will matters.', 'will', 'NN'),
                 ('May rains often.', 'May', 'NNP'),
                 ('They want to can peaches.', 'can', 'VB'),
                 ('The can to the left rusts.', 'can', 'NN'),
                 ('She cans the peaches.', 'cans', 'VBZ'),
                 ('They canned peaches.', 'canned', 'VBD'),
                 ('They are canning peaches.', 'canning', 'VBG')]
        with patch.object(api, 'classify', return_value=None):
            for sentence, word, tag in cases:
                with self.subTest(sentence=sentence):
                    payload = api.build_payload(sentence)
                    self.assertIn(f'({tag} {word})', payload['parse']['parse_string'])
                    summary = payload['summary']
                    self.assertFalse(summary['checker_errors'])
                    self.assertFalse(any(c.startswith('C-MODAL-') or c == 'C-TO-BASE'
                                         for c in summary['constraints_fired']), summary)
                    self.assertNotEqual(summary['verdict'], 'ungrammatical', summary)
                    self.assertNotIn('correction', summary)
                    self.assertNotIn('After the modal', summary['explanation'])
                    self.assertFalse(any(d.get('status') == 'error'
                                         and str(d.get('constraint', '')).startswith('C-MODAL-')
                                         for d in payload['node_details'].values()))
                    self.assertFalse(payload['summary']['book_verified'])

    def test_valid_modal_plain_form_controls(self):
        with patch.object(api, 'classify', return_value=None):
            for sentence in ['She can swim.', 'They could leave.', 'He will work.',
                             'Can she swim?', 'They can and will work.', 'They cannot swim.']:
                with self.subTest(sentence=sentence):
                    payload = api.build_payload(sentence)
                    self.assertFalse(payload['summary']['constraints_fired'])
                    self.assertFalse(payload['summary']['checker_errors'])
                    self.assertNotIn('correction', payload['summary'])

    def test_modal_errors_still_produce_matching_diagnostics(self):
        cases = [('She can goes.', 'C-MODAL-VERB-FORM'),
                 ('They could of left.', 'C-MODAL-OF'),
                 ('They can able to swim.', 'C-MODAL-ABLE'),
                 ('They can to preserve peaches.', 'C-MODAL-TO'),
                 ('They will can swim.', 'C-MODAL-STACK'),
                 ('They want to can swim.', 'C-TO-BASE')]
        with patch.object(api, 'classify', return_value=None):
            for sentence, constraint in cases:
                with self.subTest(sentence=sentence):
                    payload = api.build_payload(sentence)
                    self.assertIn(constraint, payload['summary']['constraints_fired'])
                    self.assertEqual(payload['summary']['verdict'], 'ungrammatical')
                    self.assertFalse(payload['summary']['checker_errors'])


if __name__ == '__main__':
    unittest.main()
