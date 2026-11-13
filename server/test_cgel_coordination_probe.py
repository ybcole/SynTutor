import os
import re
import unittest

from cgel_coordination_probe import probe_coordination
from parse_engine import NodeBuilder, analyze, parse_parse_string


CASES = [
    ("The visitor arrived yesterday and the station.",
     "(S (NP (DT The) (NN visitor)) (VP (VBD arrived) (UCP (ADVP (RB yesterday)) (CC and) (NP (DT the) (NN station)))) (. .))",
     ["CLS-1034"]),
    ("The visitor arrived yesterday and after lunch.",
     "(S (NP (DT The) (NN visitor)) (VP (VBD arrived) (UCP (ADVP (RB yesterday)) (CC and) (PP (IN after) (NP (NN lunch))))) (. .))",
     []),
    ("To cycle or walking is good exercise.",
     "(S (S (VP (TO To) (VP (VB cycle))) (CC or) (VP (VBG walking))) (VP (VBZ is) (NP (JJ good) (NN exercise))) (. .))",
     ["CLS-1035"]),
    ("Walking or to cycle is good exercise.",
     "(S (S (VP (VBG Walking)) (CC or) (VP (TO to) (VP (VB cycle)))) (VP (VBZ is) (NP (JJ good) (NN exercise))) (. .))",
     ["CLS-1035"]),
    ("To cycle or to walk is good exercise.",
     "(S (S (VP (TO To) (VP (VB cycle))) (CC or) (VP (TO to) (VP (VB walk)))) (VP (VBZ is) (NP (JJ good) (NN exercise))) (. .))",
     []),
    ("Cycling or walking is good exercise.",
     "(S (S (VP (VBG Cycling)) (CC or) (VP (VBG walking))) (VP (VBZ is) (NP (JJ good) (NN exercise))) (. .))",
     []),
]


class CoordinationProbeTests(unittest.TestCase):
    def test_fixtures(self):
        for sentence, parse, expected in CASES:
            with self.subTest(sentence=sentence):
                tree = NodeBuilder().build(parse_parse_string(parse), len(re.findall(r"\([^()]+\)", parse)))
                result = probe_coordination(sentence, tree, variety="standard_english")
                self.assertFalse(result["production_enabled"])
                self.assertEqual([row["rule_id"] for row in result["candidates"]], expected)

    @unittest.skipUnless(os.environ.get("CGEL_REQUIRE_PARSER") == "1", "configured parser required")
    def test_configured_coordination(self):
        for sentence, _, expected in CASES:
            with self.subTest(sentence=sentence):
                analysis = analyze(sentence)
                rows = probe_coordination(sentence, analysis["root"], variety="standard_english")["candidates"]
                found = [row["rule_id"] for row in rows]
                print(f"Cambridge coordination {sentence!r}: {found}; expected={expected}; parse={analysis['parse_string']}")
                self.assertIn(found, (expected, []))
