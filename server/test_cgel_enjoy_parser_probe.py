import re
import unittest

from cgel_enjoy_parser_probe import probe_enjoy_parser
from parse_engine import NodeBuilder, parse_parse_string


def probe(sentence, parse, variety="standard_english"):
    leaf_count = len(re.findall(r"\([^()]+\)", parse))
    tree = NodeBuilder().build(parse_parse_string(parse), leaf_count)
    return probe_enjoy_parser(sentence, tree, variety=variety)


DIRECT = "(S (NP (PRP She)) (VP (VBZ enjoys) (S (VP (TO to) (VP (VB swim))))) (. .))"


class EnjoyParserProbeTests(unittest.TestCase):
    def test_one_relation_and_exact_edit(self):
        result = probe("She enjoys to swim.", DIRECT)
        candidate, = result["candidates"]
        self.assertFalse(result["production_enabled"])
        self.assertEqual(candidate["rule_id"], "COMP-062")
        self.assertEqual(candidate["source_pages"], [221])
        self.assertEqual(candidate["relation"]["governor_char_span"], [4, 10])
        self.assertEqual(candidate["relation"]["dependent_char_span"], [14, 18])
        self.assertEqual(candidate["edit_hint"]["char_span"], [11, 18])
        self.assertEqual(candidate["edit_hint"]["replacement"], "swimming")

    def test_licensed_and_ambiguous_complements_are_guarded(self):
        for sentence, vp in [
            ("She enjoys the pool.", "(VBZ enjoys) (NP (DT the) (NN pool))"),
            ("She enjoys swimming.", "(VBZ enjoys) (S (VP (VBG swimming)))"),
            ("She likes to swim.", "(VBZ likes) (S (VP (TO to) (VP (VB swim))))"),
            ("She enjoys to swim and dive.", "(VBZ enjoys) (S (VP (TO to) (VP (VB swim) (CC and) (VB dive))))"),
            ("She enjoys to glorp.", "(VBZ enjoys) (S (VP (TO to) (VP (VB glorp))))"),
        ]:
            with self.subTest(sentence=sentence):
                tree = f"(S (NP (PRP She)) (VP {vp}) (. .))"
                self.assertEqual(probe(sentence, tree)["candidates"], [])

    def test_variety_and_token_alignment(self):
        self.assertEqual(probe("She enjoys to swim.", DIRECT, variety=None)["candidates"], [])
        self.assertEqual(probe("She enjoys to dive.", DIRECT)["blocked"], ["parser_token_alignment_unavailable"])
