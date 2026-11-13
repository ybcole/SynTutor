import os
import unittest

from cgel_since_probe import probe_ever_since
from parse_engine import NodeBuilder, analyze, parse_parse_string


class SinceProbeTests(unittest.TestCase):
    def test_present_continuation_is_required(self):
        sentence = "Mina knew him ever since childhood."
        tree = NodeBuilder().build(parse_parse_string(
            "(S (NP (NNP Mina)) (VP (VBD knew) (NP (PRP him)) "
            "(PP (RB ever) (IN since) (NP (NN childhood)))) (. .))"
        ), 7)
        for context, expected in [(True, ["OTH-098"]), (False, [])]:
            with self.subTest(context=context):
                rows = probe_ever_since(sentence, tree, variety="standard_english",
                                        present_continuation_confirmed=context)["candidates"]
                self.assertEqual([row["rule_id"] for row in rows], expected)

    @unittest.skipUnless(os.environ.get("CGEL_REQUIRE_PARSER") == "1", "configured parser required")
    def test_configured_since(self):
        for sentence, context, target in [
            ("Mina knew him ever since childhood.", True, True),
            ("The museum stood there ever since the district was founded.", True, True),
            ("Mina knew him ever since childhood.", False, False),
            ("Mina has known him ever since childhood.", True, False),
            ("By then, Mina had known him ever since childhood.", False, False),
            ("Mina knew him since they worked together.", True, False),
            ("Mina knew him last year.", True, False),
        ]:
            with self.subTest(sentence=sentence, context=context):
                analysis = analyze(sentence)
                rows = probe_ever_since(sentence, analysis["root"], variety="standard_english",
                                        present_continuation_confirmed=context)["candidates"]
                found = [row["rule_id"] for row in rows]
                print(f"Cambridge ever since {sentence!r}: {found}; target={target}; parse={analysis['parse_string']}")
                self.assertIn(found, ([], ["OTH-098"]) if target else ([],))
