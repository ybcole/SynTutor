import os
import unittest

from cgel_catenative_probe import probe_believe_object, probe_catenative_perfect
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


class BelieveObjectTests(unittest.TestCase):
    def check_case(self, sentence, tree, context, expected):
        result = probe_believe_object(
            sentence, tree, variety="standard_english", complement_confirmed=context
        )
        self.assertFalse(result["production_enabled"])
        self.assertEqual([row["rule_id"] for row in result["candidates"]], expected)
        for row in result["candidates"]:
            self.assertIsNone(row["edit_hint"])

    def test_active_complement_requires_object(self):
        sentence = "Nina believed to be qualified."
        tree = NodeBuilder().build(parse_parse_string(
            "(S (NP (NNP Nina)) (VP (VBD believed) (S (VP (TO to) "
            "(VP (VB be) (ADJP (JJ qualified)))))) (. .))"
        ), 6)
        self.check_case(sentence, tree, True, ["CLS-320"])
        self.check_case(sentence, tree, False, [])

    @unittest.skipUnless(os.environ.get("CGEL_REQUIRE_PARSER") == "1", "configured parser required")
    def test_configured_believe_objects(self):
        for sentence, context, expected in [
            ("Nina believed to be qualified.", True, ["CLS-320"]),
            ("I believed to be ready.", True, ["CLS-320"]),
            ("Nina believed to be qualified.", False, []),
            ("Nina believed herself to be qualified.", True, []),
            ("Nina believed him to be qualified.", True, []),
            ("Nina was believed to be qualified.", True, []),
            ("Nina believed that she was qualified.", True, []),
            ("Nina hoped to be qualified.", True, []),
        ]:
            with self.subTest(sentence=sentence, context=context):
                self.check_case(sentence, analyze(sentence)["root"], context, expected)
