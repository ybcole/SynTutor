import os
import unittest

from cgel_lexical_number_probe import probe_lexical_number
from parse_engine import NodeBuilder, analyze, parse_parse_string


CASES = [
    ("Cattle is outside.", "(NNS Cattle)", "VBZ is", "outside", False, [("PHR-062", "are")]),
    ("The police was outside.", "(DT The) (NNS police)", "VBD was", "outside", False, [("PHR-062", "were")]),
    ("The news are encouraging.", "(DT The) (NN news)", "VBP are", "encouraging", False, [("PHR-065", "is")]),
    ("Shingles are painful.", "(NNS Shingles)", "VBP are", "painful", True, [("PHR-065", "is")]),
    ("Shingles are painful.", "(NNS Shingles)", "VBP are", "painful", False, []),
    ("The police officer is outside.", "(DT The) (NN police) (NN officer)", "VBZ is", "outside", False, []),
    ("The news is encouraging.", "(DT The) (NN news)", "VBZ is", "encouraging", False, []),
    ("The shingles are loose.", "(DT The) (NNS shingles)", "VBP are", "loose", False, []),
]


class LexicalNumberTests(unittest.TestCase):
    def check_case(self, sentence, tree, disease, expected):
        result = probe_lexical_number(sentence, tree, variety="standard_english", disease_confirmed=disease)
        found = [(row["rule_id"], row["expected_verb"]) for row in result["candidates"]]
        self.assertEqual(found, expected)
        self.assertFalse(result["production_enabled"])

    def test_lexical_number_fixtures(self):
        for sentence, np, verb, adjective, disease, expected in CASES:
            with self.subTest(sentence=sentence, disease=disease):
                parse = f"(S (NP {np}) (VP ({verb}) (ADJP (JJ {adjective}))) (. .))"
                tree = NodeBuilder().build(parse_parse_string(parse), len(sentence.split()) + 1)
                self.check_case(sentence, tree, disease, expected)

    @unittest.skipUnless(os.environ.get("CGEL_REQUIRE_PARSER") == "1", "configured parser required")
    def test_configured_lexical_number(self):
        for sentence, _, _, _, disease, expected in CASES:
            with self.subTest(sentence=sentence, disease=disease):
                self.check_case(sentence, analyze(sentence)["root"], disease, expected)
