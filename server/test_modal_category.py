"""Category gating for legacy modal diagnostics; no parser required here."""
import unittest
import ruleset


def leaves(*pairs):
    return [{'id': str(i), 'type': tag, 'surface': word}
            for i, (tag, word) in enumerate(pairs)]


class ModalCategoryTests(unittest.TestCase):
    def constraints(self, *pairs):
        return {f['constraint'] for f in ruleset._check_basic(None, [], leaves(*pairs))}

    def test_nonmodal_homographs_do_not_license_modal_checks(self):
        for tag, word in [('NN', 'can'), ('NN', 'will'), ('NNP', 'May'),
                          ('VB', 'can'), ('VBP', 'can'), ('NN', 'must')]:
            for following in [('VBZ', 'rusts'), ('IN', 'of'), ('JJ', 'able'),
                              ('TO', 'to'), ('MD', 'will')]:
                with self.subTest(tag=tag, word=word, following=following):
                    found = self.constraints((tag, word), following)
                    self.assertFalse(any(c.startswith('C-MODAL-') for c in found), found)

    def test_genuine_modal_diagnostics_are_retained(self):
        for following, expected in [(('VBZ', 'goes'), 'C-MODAL-VERB-FORM'),
                                     (('IN', 'of'), 'C-MODAL-OF'),
                                     (('JJ', 'able'), 'C-MODAL-ABLE'),
                                     (('TO', 'to'), 'C-MODAL-TO'),
                                     (('MD', 'will'), 'C-MODAL-STACK')]:
            with self.subTest(expected=expected):
                self.assertIn(expected, self.constraints(('MD', 'could'), following))

    def test_modal_may_select_lexical_can(self):
        self.assertNotIn('C-MODAL-STACK', self.constraints(('MD', 'may'), ('VB', 'can')))
        self.assertFalse(self.constraints(('MD', 'can'), ('VB', 'swim')))


if __name__ == '__main__':
    unittest.main()
