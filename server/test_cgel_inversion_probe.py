import os
import re
import unittest

from cgel_inversion_probe import probe_fronted_inversion, probe_inversion
from parse_engine import NodeBuilder, analyze, parse_parse_string


CASES = [
    ("She can swim?", "(S (NP (PRP She)) (VP (MD can) (VP (VB swim))) (. ?))", "polar", ["CLS-103"]),
    ("She can swim?", "(S (NP (PRP She)) (VP (MD can) (VP (VB swim))) (. ?))", None, []),
    ("Can she swim?", "(SQ (MD Can) (NP (PRP she)) (VP (VB swim)) (. ?))", "polar", []),
    ("Where she can swim?", "(SBARQ (WHADVP (WRB Where)) (S (NP (PRP she)) (VP (MD can) (VP (VB swim)))) (. ?))", "non_subject_wh", ["CLS-104"]),
    ("Who called?", "(SBARQ (WHNP (WP Who)) (SQ (VP (VBD called))) (. ?))", "subject_wh", []),
    ("What did she do?", "(SBARQ (WHNP (WP What)) (SQ (VBD did) (NP (PRP she)) (VP (VB do))) (. ?))", "non_subject_wh", []),
    ("I wonder where she went.", "(S (NP (PRP I)) (VP (VBP wonder) (SBAR (WHADVP (WRB where)) (S (NP (PRP she)) (VP (VBD went))))) (. .))", None, []),
]


class InversionTests(unittest.TestCase):
    def check_case(self, sentence, tree, kind, expected):
        result = probe_inversion(sentence, tree, variety="standard_english", question_kind=kind)
        self.assertEqual([c["rule_id"] for c in result["candidates"]], expected)
        if expected:
            self.assertFalse(result["production_enabled"])
            self.assertIsNone(result["candidates"][0]["edit_hint"])

    def test_source_scope_and_question_structure(self):
        for sentence, parse, kind, expected in CASES:
            with self.subTest(sentence=sentence, kind=kind):
                tree = NodeBuilder().build(parse_parse_string(parse), len(re.findall(r"\([^()]+\)", parse)))
                self.check_case(sentence, tree, kind, expected)

    @unittest.skipUnless(os.environ.get("CGEL_REQUIRE_PARSER") == "1", "configured parser required")
    def test_configured_parser(self):
        for sentence, _, kind, expected in CASES:
            with self.subTest(sentence=sentence, kind=kind):
                self.check_case(sentence, analyze(sentence)["root"], kind, expected)


FRONTED_CASES = [
    ("Never she complained.", "(S (ADVP (RB Never)) (NP (PRP she)) (VP (VBD complained)) (. .))",
     True, ["CLS-106"]),
    ("Only then she understood.", "(S (ADVP (RB Only) (RB then)) (NP (PRP she)) (VP (VBD understood)) (. .))",
     True, ["CLS-107"]),
    ("Never she complained.", "(S (ADVP (RB Never)) (NP (PRP she)) (VP (VBD complained)) (. .))",
     False, []),
    ("Never did she complain.", "(S (ADVP (RB Never)) (VBD did) (NP (PRP she)) (VP (VB complain)) (. .))",
     True, []),
    ("Only Maya complained.", "(S (NP (RB Only) (NNP Maya)) (VP (VBD complained)) (. .))",
     True, []),
    ("Not long afterwards she left.", "(S (ADVP (RB Not) (RB long) (RB afterwards)) (NP (PRP she)) (VP (VBD left)) (. .))",
     True, []),
]


class FrontedInversionTests(unittest.TestCase):
    def check_case(self, sentence, tree, scope, expected):
        result = probe_fronted_inversion(sentence, tree, variety="standard_english", clause_scope_confirmed=scope)
        self.assertEqual([row["rule_id"] for row in result["candidates"]], expected)
        self.assertFalse(result["production_enabled"])

    def test_fronted_adjunct_scope(self):
        for sentence, parse, scope, expected in FRONTED_CASES:
            with self.subTest(sentence=sentence, scope=scope):
                tree = NodeBuilder().build(parse_parse_string(parse), len(re.findall(r"\([^()]+\)", parse)))
                self.check_case(sentence, tree, scope, expected)

    @unittest.skipUnless(os.environ.get("CGEL_REQUIRE_PARSER") == "1", "configured parser required")
    def test_configured_fronted_controls(self):
        for sentence, _, scope, expected in FRONTED_CASES:
            with self.subTest(sentence=sentence, scope=scope):
                result = probe_fronted_inversion(sentence, analyze(sentence)["root"],
                                                 variety="standard_english", clause_scope_confirmed=scope)
                observed = [row["rule_id"] for row in result["candidates"]]
                self.assertTrue(not observed or observed == expected)
                print(f"fronted inversion {sentence!r} scope={scope}: {observed} (expected {expected})")
