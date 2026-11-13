import os
import unittest

from cgel_imperative_probe import probe_imperative, probe_negative_imperative
from parse_engine import NodeBuilder, analyze, parse_parse_string


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

    @unittest.skipUnless(os.environ.get("CGEL_REQUIRE_PARSER") == "1", "configured parser required")
    def test_configured_parser_respects_confirmed_intent(self):
        sentence = "Everybody brings a pencil."
        tree = analyze(sentence)["root"]
        for intent, count in [(False, 0), (True, 1)]:
            result = probe_imperative(sentence, tree, variety="standard_english", directive_confirmed=intent)
            self.assertEqual(len(result["candidates"]), count)
        edit = result["candidates"][0]["edit_hint"]
        start, end = edit["char_span"]
        repaired = sentence[:start] + edit["replacement"] + sentence[end:]
        self.assertEqual(repaired, "Everybody bring a pencil.")
        recheck = probe_imperative(repaired, analyze(repaired)["root"],
                                   variety="standard_english", directive_confirmed=True)
        self.assertEqual(recheck["candidates"], [])


NEGATIVE_CASES = [
    ("Be not late.", "(S (VP (VB Be) (RB not) (ADJP (JJ late))) (. .))", True, "Do not be late."),
    ("Not be late!", "(S (VP (RB Not) (VP (VB be) (ADJP (JJ late)))) (. !))", True, "Do not be late!"),
    ("Be not late.", "(S (VP (VB Be) (RB not) (ADJP (JJ late))) (. .))", False, None),
    ("Do not be late.", "(S (VP (VBP Do) (RB not) (VP (VB be) (ADJP (JJ late)))) (. .))", True, None),
    ("She is not late.", "(S (NP (PRP She)) (VP (VBZ is) (RB not) (ADJP (JJ late))) (. .))", False, None),
]


class NegativeImperativeTests(unittest.TestCase):
    def check(self, sentence, tree, context, expected, *, configured=False):
        result = probe_negative_imperative(
            sentence, tree, variety="standard_english", ordinary_verbal_directive_confirmed=context
        )
        if configured:
            print(f"Negative imperative {sentence!r} context={context}: {len(result['candidates'])} candidate(s)")
        if expected is None or configured and not result["candidates"]:
            self.assertEqual(result["candidates"], [])
            return
        candidate, = result["candidates"]
        self.assertEqual(candidate["rule_id"], "CLS-102")
        self.assertEqual(candidate["supporting_rule_ids"], ["CLS-131"])
        edit = candidate["edit_hint"]
        start, end = edit["char_span"]
        repaired = sentence[:start] + edit["replacement"] + sentence[end:]
        self.assertEqual(repaired, expected)
        if configured:
            recheck = probe_negative_imperative(
                repaired, analyze(repaired)["root"], variety="standard_english",
                ordinary_verbal_directive_confirmed=True
            )
            self.assertEqual(recheck["candidates"], [])

    def test_negative_imperative_fixtures(self):
        for sentence, parse, context, expected in NEGATIVE_CASES:
            with self.subTest(sentence=sentence, context=context):
                tree = NodeBuilder().build(parse_parse_string(parse), len(sentence.rstrip(".!").split()) + 1)
                self.check(sentence, tree, context, expected)

    @unittest.skipUnless(os.environ.get("CGEL_REQUIRE_PARSER") == "1", "configured parser required")
    def test_configured_negative_imperatives(self):
        for sentence, _, context, expected in NEGATIVE_CASES:
            with self.subTest(sentence=sentence, context=context):
                self.check(sentence, analyze(sentence)["root"], context, expected, configured=True)
