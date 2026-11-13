import os
import re
import unittest

from cgel_inversion_probe import probe_inversion
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
