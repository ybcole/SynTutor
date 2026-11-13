import os
import unittest

from cgel_imperative_probe import probe_imperative, probe_inclusive_lets, probe_negative_imperative
from cgel_imperative_probe import probe_reported_negative_directive
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


class InclusiveLetsTests(unittest.TestCase):
    def test_contraction_alignment(self):
        for marker in ["(VB let's)", "(VB let) (PRP 's)"]:
            with self.subTest(marker=marker):
                tree = NodeBuilder().build(parse_parse_string(
                    f"(S (NP (PRP We)) (VP {marker} (VP (VB wait))) (. .))"
                ), 4 if marker == "(VB let's)" else 5)
                candidate, = probe_inclusive_lets(
                    "We let's wait.", tree, variety="standard_english"
                )["candidates"]
                self.assertEqual(candidate["rule_id"], "CLS-268")
                self.assertEqual(candidate["relation"]["marker_char_span"], [3, 8])

    @unittest.skipUnless(os.environ.get("CGEL_REQUIRE_PARSER") == "1", "configured parser required")
    def test_configured_inclusive_lets(self):
        cases = [
            ("We let's wait here.", True),
            ("You let’s check the figures.", True),
            ("Let's wait here.", False),
            ("You, let's wait here.", False),
            ("You let us wait here.", False),
            ('She said, “Let’s wait here.”', False),
        ]
        for sentence, target in cases:
            with self.subTest(sentence=sentence):
                analysis = analyze(sentence)
                result = probe_inclusive_lets(sentence, analysis["root"], variety="standard_english")
                ids = [row["rule_id"] for row in result["candidates"]]
                self.assertIn(ids, ([], ["CLS-268"]) if target else ([],))
                print(f"Inclusive lets {sentence!r}: {ids}, target={target}, parse={analysis['parse_string']}")


class ReportedDirectiveTests(unittest.TestCase):
    def test_reported_negation_and_controls(self):
        cases = [
            ("Mina told us to do not touch it.", "(S (NP (NNP Mina)) (VP (VBD told) (NP (PRP us)) (S (VP (TO to) (VP (VB do) (RB not) (VP (VB touch) (NP (PRP it))))))) (. .))", "Mina told us not to touch it."),
            ("Mina told us not to touch it.", "(S (NP (NNP Mina)) (VP (VBD told) (NP (PRP us)) (S (RB not) (VP (TO to) (VP (VB touch) (NP (PRP it)))))) (. .))", None),
            ("Mina told us to do nothing.", "(S (NP (NNP Mina)) (VP (VBD told) (NP (PRP us)) (S (VP (TO to) (VP (VB do) (NP (NN nothing)))))) (. .))", None),
        ]
        for sentence, parse, expected in cases:
            with self.subTest(sentence=sentence):
                tree = NodeBuilder().build(parse_parse_string(parse), len(sentence.split()) + 1)
                result = probe_reported_negative_directive(sentence, tree, variety="standard_english")
                if expected is None:
                    self.assertEqual(result["candidates"], [])
                    continue
                candidate, = result["candidates"]
                self.assertEqual(candidate["rule_id"], "CLS-270")
                edit = candidate["edit_hint"]
                start, end = edit["char_span"]
                self.assertEqual(sentence[:start] + edit["replacement"] + sentence[end:], expected)

    @unittest.skipUnless(os.environ.get("CGEL_REQUIRE_PARSER") == "1", "configured parser required")
    def test_configured_reported_directives(self):
        cases = [
            ("Mina told us to do not touch it.", "Mina told us not to touch it."),
            ("Mina told us not to touch it.", None),
            ("Mina told us to do nothing.", None),
            ("Mina said that we did not touch it.", None),
            ('Mina said, “Do not touch it.”', None),
        ]
        for sentence, expected in cases:
            with self.subTest(sentence=sentence):
                result = probe_reported_negative_directive(
                    sentence, analyze(sentence)["root"], variety="standard_english"
                )
                candidates = result["candidates"]
                print(f"Reported directive {sentence!r}: {len(candidates)} candidate(s)")
                if expected is None:
                    self.assertEqual(candidates, [])
                elif candidates:
                    candidate, = candidates
                    edit = candidate["edit_hint"]
                    start, end = edit["char_span"]
                    repaired = sentence[:start] + edit["replacement"] + sentence[end:]
                    self.assertEqual(repaired, expected)
                    recheck = probe_reported_negative_directive(
                        repaired, analyze(repaired)["root"], variety="standard_english"
                    )
                    self.assertEqual(recheck["status"], "candidate_only")
                    self.assertEqual(recheck["candidates"], [])
