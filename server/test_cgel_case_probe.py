import os
import unittest

from cgel_case_probe import probe_pronoun_case
from parse_engine import NodeBuilder, analyze, parse_parse_string


CASES = [
    ("Him greeted us.", ["subject"]),
    ("They greeted she.", ["direct_object"]),
    ("Him thanked she.", ["subject", "direct_object"]),
    ("He greeted us.", []),
    ("They greeted her.", []),
]


class CaseProbeTests(unittest.TestCase):
    def test_simple_active_roles(self):
        for sentence, expected in CASES:
            with self.subTest(sentence=sentence):
                subject, verb, obj = sentence.rstrip(".").split()
                parse = f"(S (NP (PRP {subject})) (VP (VBD {verb}) (NP (PRP {obj}))) (. .))"
                tree = NodeBuilder().build(parse_parse_string(parse), 4)
                rows = probe_pronoun_case(sentence, tree, variety="standard_english")["candidates"]
                self.assertEqual([row["relation"]["kind"] for row in rows], expected)
                for row in rows:
                    support = row["supporting_sources"]
                    self.assertEqual(bool(support), row["relation"]["kind"] == "subject")

    @unittest.skipUnless(os.environ.get("CGEL_REQUIRE_PARSER") == "1", "configured parser required")
    def test_configured_case_probe(self):
        for sentence, expected in CASES + [
            ("It was her.", []), ("They waved to her.", []), ("He and I greeted her.", []),
            ("They thanked him and me.", []),
        ]:
            with self.subTest(sentence=sentence):
                analysis = analyze(sentence)
                rows = probe_pronoun_case(sentence, analysis["root"], variety="standard_english")["candidates"]
                found = [row["relation"]["kind"] for row in rows]
                print(f"Cambridge case {sentence!r}: {found}; expected={expected}; parse={analysis['parse_string']}")
                self.assertEqual(found, [role for role in expected if role in found])
