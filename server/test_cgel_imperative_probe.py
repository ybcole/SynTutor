import unittest

from cgel_imperative_probe import probe_imperative
from parse_engine import NodeBuilder, parse_parse_string


class ImperativeProbeTests(unittest.TestCase):
    def test_identical_words_depend_on_directive_intent(self):
        sentence = "Everybody brings a pencil."
        tree = NodeBuilder().build(parse_parse_string(
            "(S (NP (NN Everybody)) (VP (VBZ brings) (NP (DT a) (NN pencil))) (. .))"
        ), 5)
        for intent in (False, None):
            self.assertEqual(probe_imperative(
                sentence, tree, variety="standard_english", directive_confirmed=intent
            )["candidates"], [])
        candidate, = probe_imperative(
            sentence, tree, variety="standard_english", directive_confirmed=True
        )["candidates"]
        self.assertEqual(candidate["rule_id"], "CLS-130")
        self.assertEqual(candidate["edit_hint"]["char_span"], [10, 16])
        self.assertEqual(candidate["edit_hint"]["replacement"], "bring")

    def test_plain_form_and_coordination(self):
        for sentence, vp, count in [
            ("Everybody bring pencils.", "(VB bring) (NP (NNS pencils))", 4),
            ("Everybody brings and shares pencils.", "(VBZ brings) (CC and) (VBZ shares) (NP (NNS pencils))", 6),
        ]:
            tree = NodeBuilder().build(parse_parse_string(
                f"(S (NP (NN Everybody)) (VP {vp}) (. .))"
            ), count)
            self.assertEqual(probe_imperative(
                sentence, tree, variety="standard_english", directive_confirmed=True
            )["candidates"], [])
