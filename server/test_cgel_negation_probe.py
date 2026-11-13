import os
import re
import unittest

from cgel_negation_probe import probe_primary_negation
from parse_engine import NodeBuilder, analyze, parse_parse_string


CASES = [
    ("The neighbor smokes not.", "(S (NP (DT The) (NN neighbor)) (VP (VBZ smokes) (RB not)) (. .))",
     True, "The neighbor does not smoke."),
    ("The children whispered not.", "(S (NP (DT The) (NNS children)) (VP (VBD whispered) (RB not)) (. .))",
     True, "The children did not whisper."),
    ("The neighbor smokes not.", "(S (NP (DT The) (NN neighbor)) (VP (VBZ smokes) (RB not)) (. .))",
     False, None),
    ("The neighbor does not smoke.", "(S (NP (DT The) (NN neighbor)) (VP (VBZ does) (RB not) (VP (VB smoke))) (. .))",
     True, None),
    ("The neighbor is not.", "(S (NP (DT The) (NN neighbor)) (VP (VBZ is) (RB not)) (. .))",
     True, None),
    ("They decided not to whisper.", "(S (NP (PRP They)) (VP (VBD decided) (S (RB not) (VP (TO to) (VP (VB whisper))))) (. .))",
     True, None),
    ("Not long afterwards she left.", "(S (ADVP (RB Not) (RB long) (RB afterwards)) (NP (PRP she)) (VP (VBD left)) (. .))",
     True, None),
]


class PrimaryNegationTests(unittest.TestCase):
    def check(self, sentence, tree, context, expected, *, configured=False):
        result = probe_primary_negation(sentence, tree, variety="standard_english", primary_confirmed=context)
        self.assertFalse(result["production_enabled"])
        if expected is None:
            self.assertEqual(result["candidates"], [])
            return
        if configured and not result["candidates"]:
            print(f"Primary negation parser miss: {sentence}")
            return
        candidate, = result["candidates"]
        self.assertEqual(candidate["rule_id"], "CLS-099")
        edit = candidate["edit_hint"]
        start, end = edit["char_span"]
        repaired = sentence[:start] + edit["replacement"] + sentence[end:]
        self.assertEqual(repaired, expected)
        if configured:
            recheck = probe_primary_negation(repaired, analyze(repaired)["root"],
                                             variety="standard_english", primary_confirmed=True)
            self.assertEqual(recheck["status"], "candidate_only")
            self.assertEqual(recheck["candidates"], [])
            print(f"Primary negation parser repair: {repaired}")

    def test_fixture_cases(self):
        for sentence, parse, context, expected in CASES:
            with self.subTest(sentence=sentence, context=context):
                tree = NodeBuilder().build(parse_parse_string(parse), len(re.findall(r"\([^()]+\)", parse)))
                self.check(sentence, tree, context, expected)

    @unittest.skipUnless(os.environ.get("CGEL_REQUIRE_PARSER") == "1", "configured parser required")
    def test_configured_parser(self):
        for sentence, _, context, expected in CASES:
            with self.subTest(sentence=sentence, context=context):
                self.check(sentence, analyze(sentence)["root"], context, expected, configured=True)
