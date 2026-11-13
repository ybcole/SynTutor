import os
import unittest

from cgel_tag_probe import probe_tag_auxiliary
from parse_engine import NodeBuilder, analyze, parse_parse_string


CASES = [
    ("She filed it, doesn't she?", "VBD filed", "(NP (PRP it))", "VBZ does", "did"),
    ("She filed it, didn't she?", "VBD filed", "(NP (PRP it))", "VBD did", None),
    ("She should stay, doesn't she?", "MD should", "(VP (VB stay))", "VBZ does", "should"),
    ("She should stay, shouldn't she?", "MD should", "(VP (VB stay))", "MD should", None),
]


class TagProbeTests(unittest.TestCase):
    def test_auxiliary_and_tense(self):
        for sentence, head, tail, tag, expected in CASES:
            with self.subTest(sentence=sentence):
                parse = f"(S (S (NP (PRP She)) (VP ({head}) {tail})) (, ,) ({tag}) (RB n't) (NP (PRP she)) (. ?))"
                tree = NodeBuilder().build(parse_parse_string(parse), 8)
                result = probe_tag_auxiliary(sentence, tree, variety="standard_english")
                self.assertEqual([c["expected_auxiliary"] for c in result["candidates"]], [expected] if expected else [])

    @unittest.skipUnless(os.environ.get("CGEL_REQUIRE_PARSER") == "1", "configured parser required")
    def test_configured_tags(self):
        for sentence, _, _, _, expected in CASES + [
            ("Stay here, won't you?", "", "", "", None),
            ("She filed it, right?", "", "", "", None),
            ("She filed it, did she?", "", "", "", None),
            ("She filed it, didn't they?", "", "", "", None),
        ]:
            with self.subTest(sentence=sentence):
                analysis = analyze(sentence)
                result = probe_tag_auxiliary(sentence, analysis["root"], variety="standard_english")
                found = [c["expected_auxiliary"] for c in result["candidates"]]
                self.assertIn(found, ([], [expected]) if expected else ([],))
                print(f"Cambridge tag {sentence!r}: {found}; expected={expected}; parse={analysis['parse_string']}")
