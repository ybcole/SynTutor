import os
import unittest

from cgel_since_probe import probe_completed_past_perfect, probe_ever_since
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


class CompletedPastPerfectTests(unittest.TestCase):
    def test_closed_time_and_context(self):
        sentence = "I have visited the director yesterday."
        tree = NodeBuilder().build(parse_parse_string(
            "(S (NP (PRP I)) (VP (VBP have) (VP (VBN visited) (NP (DT the) (NN director)) "
            "(NP (NN yesterday)))) (. .))"
        ), 7)
        for context, expected in [(True, ["OTH-102"]), (False, [])]:
            result = probe_completed_past_perfect(sentence, tree, variety="standard_english",
                                                  single_event_confirmed=context)
            self.assertEqual([row["rule_id"] for row in result["candidates"]], expected)

    @unittest.skipUnless(os.environ.get("CGEL_REQUIRE_PARSER") == "1", "configured parser required")
    def test_configured_completed_past(self):
        for sentence, context, target in [
            ("I have visited the director yesterday.", True, True),
            ("They have finished the assignment two minutes ago.", True, True),
            ("I visited the director yesterday.", True, False),
            ("I have visited the director recently.", True, False),
            ("We have already discussed it yesterday.", True, False),
            ("I have read the report that arrived yesterday.", True, False),
            ("I have visited the director yesterday.", False, False),
        ]:
            with self.subTest(sentence=sentence, context=context):
                analysis = analyze(sentence)
                result = probe_completed_past_perfect(
                    sentence, analysis["root"], variety="standard_english", single_event_confirmed=context
                )
                found = [row["rule_id"] for row in result["candidates"]]
                print(f"Cambridge completed past {sentence!r}: {found}; target={target}; parse={analysis['parse_string']}")
                self.assertIn(found, ([], ["OTH-102"]) if target else ([],))
