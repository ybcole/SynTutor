import os
import re
import unittest

from cgel_coordination_probe import probe_coordinated_determiner, probe_coordination
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


DETERMINER_CASES = [
    ("I packed these cup and saucer.", "(DT these) (NML (NN cup) (CC and) (NN saucer))", True),
    ("I packed two plate and bowl.", "(CD two) (NML (NN plate) (CC and) (NN bowl))", True),
    ("I packed this cup and saucer.", "(DT this) (NML (NN cup) (CC and) (NN saucer))", False),
    ("I packed these cups and saucers.", "(DT these) (NML (NNS cups) (CC and) (NNS saucers))", False),
    ("I packed this cup and that saucer.", "(NP (DT this) (NN cup)) (CC and) (NP (DT that) (NN saucer))", False),
]


class CoordinatedDeterminerTests(unittest.TestCase):
    def test_shared_determiner_and_np_coordination(self):
        for sentence, phrase, target in DETERMINER_CASES:
            with self.subTest(sentence=sentence):
                parse = f"(S (NP (PRP I)) (VP (VBD packed) (NP {phrase})) (. .))"
                tree = NodeBuilder().build(parse_parse_string(parse), len(re.findall(r"\([^()]+\)", parse)))
                rows = probe_coordinated_determiner(sentence, tree, variety="standard_english")["candidates"]
                self.assertEqual([row["rule_id"] for row in rows], ["CLS-1036"] if target else [])
                if target:
                    self.assertIsNone(rows[0]["edit_hint"])

    @unittest.skipUnless(os.environ.get("CGEL_REQUIRE_PARSER") == "1", "configured parser required")
    def test_configured_coordinated_determiner(self):
        for sentence, _, target in DETERMINER_CASES:
            with self.subTest(sentence=sentence):
                analysis = analyze(sentence)
                rows = probe_coordinated_determiner(
                    sentence, analysis["root"], variety="standard_english"
                )["candidates"]
                found = [row["rule_id"] for row in rows]
                self.assertIn(found, ([], ["CLS-1036"]) if target else ([],))
                print(f"Cambridge coordinated determiner {sentence!r}: {found}; target={target}; parse={analysis['parse_string']}")
