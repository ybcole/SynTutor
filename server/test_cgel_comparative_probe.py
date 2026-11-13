import os
import re
import unittest

from cgel_comparative_probe import probe_comparative_gap
from parse_engine import NodeBuilder, analyze, parse_parse_string


class ComparativeGapTests(unittest.TestCase):
    def test_fixture_degree_modifier_and_adjunct(self):
        for lower, text, expected in [
            ("(ADJP (RB very) (JJ wide))", "very wide", ["CLS-1119"]),
            ("(ADJP (JJ wide))", "wide", []),
            ("(ADJP (JJ wide)) (ADVP (RB today))", "wide today", []),
        ]:
            with self.subTest(text=text):
                parse = ("(S (NP (PRP It)) (VP (VBZ is) (ADJP (RB as) (JJ deep) "
                         f"(SBAR (IN as) (S (NP (PRP it)) (VP (VBZ is) {lower}))))) (. .))")
                tree = NodeBuilder().build(parse_parse_string(parse), len(re.findall(r"\([^()]+\)", parse)))
                rows = probe_comparative_gap(f"It is as deep as it is {text}.", tree,
                                             variety="standard_english")["candidates"]
                self.assertEqual([row["rule_id"] for row in rows], expected)

    @unittest.skipUnless(os.environ.get("CGEL_REQUIRE_PARSER") == "1", "configured parser required")
    def test_configured_comparatives(self):
        for sentence, target in [
            ("The shelf is as deep as it is very wide.", True),
            ("The arch is taller than it is quite wide.", True),
            ("The shelf is as deep as it is wide.", False),
            ("The shelf is as deep as it was yesterday.", False),
            ("The arch is taller than two meters.", False),
            ("As it is very wide, the shelf is useful.", False),
        ]:
            with self.subTest(sentence=sentence):
                analysis = analyze(sentence)
                rows = probe_comparative_gap(sentence, analysis["root"],
                                             variety="standard_english")["candidates"]
                found = [row["rule_id"] for row in rows]
                self.assertEqual(found, ["CLS-1119"] if target else [])
                print(f"Cambridge comparative gap {sentence!r}: {found}; target={target}; parse={analysis['parse_string']}")
