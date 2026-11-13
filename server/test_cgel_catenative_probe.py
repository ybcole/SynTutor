import os
import unittest

from cgel_catenative_probe import probe_catenative_perfect
from parse_engine import NodeBuilder, analyze, parse_parse_string


class CatenativePerfectTests(unittest.TestCase):
    def test_confirmed_bound_reading(self):
        sentence = "She began to have read it."
        tree = NodeBuilder().build(parse_parse_string(
            "(S (NP (PRP She)) (VP (VBD began) (S (VP (TO to) "
            "(VP (VB have) (VP (VBN read) (NP (PRP it))))))) (. .))"
        ), 7)
        for context, expected in [(True, ["OTH-182"]), (False, [])]:
            rows = probe_catenative_perfect(sentence, tree, variety="standard_english",
                                           bound_reading_confirmed=context)["candidates"]
            self.assertEqual([row["rule_id"] for row in rows], expected)

    @unittest.skipUnless(os.environ.get("CGEL_REQUIRE_PARSER") == "1", "configured parser required")
    def test_configured_catenatives(self):
        for sentence, context, target in [
            ("She began to have read the manuscript.", True, True),
            ("The tutor made the class have completed the exercise.", True, True),
            ("She began to have read the manuscript.", False, False),
            ("She seemed to have read the manuscript.", True, False),
            ("They expected her to have finished the exercise.", True, False),
            ("She began to have doubts.", True, False),
            ("The tutor made the class complete the exercise.", True, False),
        ]:
            with self.subTest(sentence=sentence, context=context):
                analysis = analyze(sentence)
                rows = probe_catenative_perfect(sentence, analysis["root"], variety="standard_english",
                                               bound_reading_confirmed=context)["candidates"]
                found = [row["rule_id"] for row in rows]
                print(f"Cambridge catenative perfect {sentence!r}: {found}; target={target}; parse={analysis['parse_string']}")
                self.assertIn(found, ([], ["OTH-182"]) if target else ([],))
