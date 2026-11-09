"""Model-free tests for the experimental B-R construction chart.

The chart yields candidates only, never authoritative linguistic verdicts.
"""
import unittest
from server.br_native_chart import generate_br_chart_candidates


def tagged(*parts):
    return [{"text": word, "parser_tag": tag} for word, tag in parts]


def labels(node):
    return [node.get("label")] + [
        tag for child in node.get("children", [])
        for tag in labels(child)
    ]


class NativeChartTests(unittest.TestCase):
    def test_generates_unseen_simple_intransitive_sentence(self):
        data = tagged(("Max", "NNP"), ("sleeps", "VBZ"))
        outcome = generate_br_chart_candidates(data)
        self.assertEqual(outcome["status"], "candidate")
        self.assertFalse(outcome["may_certify_grammaticality"])
        tree = outcome["candidates"][0]["root"]
        self.assertEqual(tree["label"], "S")
        subject, predicate = tree["children"]
        self.assertEqual(subject["children"][0]["label"], "name")
        self.assertEqual(predicate["children"][0]["features"], ["intrans", "pres"])

    def test_generates_nominal_with_article_and_transitive_frame(self):
        data = tagged(("The", "DT"), ("robots", "NNS"), ("admire", "VBP"),
                      ("Max", "NNP"))
        output = generate_br_chart_candidates(data)
        self.assertEqual(output["status"], "candidate")
        root = output["candidates"][0]["root"]
        self.assertEqual([c["label"] for c in root["children"]], ["NP", "VP"])
        self.assertEqual(root["children"][0]["children"][0]["label"], "DET")
        self.assertIn("trans", root["children"][1]["children"][0]["features"])
        self.assertEqual(root["children"][1]["children"][1]["label"], "NP")

    def test_bare_plural_uses_empty_determiner_without_hallucinating_word(self):
        output = generate_br_chart_candidates(tagged(("Robots", "NNS"), ("sleep", "VBP")))
        self.assertEqual(output["status"], "candidate")
        empty_det = output["candidates"][0]["root"]["children"][0]["children"][0]
        self.assertEqual(empty_det, {"label": "DET", "children": []})

    def test_vp_adjunct_is_nested_and_deictic_is_p_only(self):
        output = generate_br_chart_candidates(tagged(("Max", "NNP"),
            ("sleeps", "VBZ"), ("now", "RB")))
        self.assertEqual(output["status"], "candidate")
        predicate = output["candidates"][0]["root"]["children"][1]
        self.assertEqual([c["label"] for c in predicate["children"]], ["VP", "PP"])
        self.assertEqual(predicate["children"][1]["children"][0]["label"], "P")
        self.assertNotIn("ADVP", labels(predicate))

    def test_pp_adjunct_uses_np_determiner_hierarchy(self):
        output = generate_br_chart_candidates(tagged(("Max", "NNP"), ("walks", "VBZ"),
            ("near", "IN"), ("the", "DT"), ("river", "NN")))
        self.assertEqual(output["status"], "candidate")
        vp, pp = output["candidates"][0]["root"]["children"][1]["children"]
        self.assertEqual(vp["label"], "VP")
        self.assertEqual([c["label"] for c in pp["children"]], ["P", "NP"])

    def test_unlicensed_frame_fails_closed(self):
        result = generate_br_chart_candidates(tagged(("Max", "NNP"), ("sleeps", "VBZ"),
                                                     ("the", "DT"), ("rabbit", "NN")))
        self.assertEqual(result["status"], "unresolved")
        self.assertEqual(result["candidates"], [])
        self.assertFalse(result["may_certify_grammaticality"])

    def test_unknown_verb_fails_closed(self):
        result = generate_br_chart_candidates(tagged(("Max", "NNP"), ("teleports", "VBZ")))
        self.assertEqual(result["status"], "unresolved")
        self.assertFalse(result["may_certify_grammaticality"])

    def test_bounded_input_and_invalid_tokens_fail_closed(self):
        self.assertEqual(generate_br_chart_candidates([])["status"], "unresolved")
        self.assertEqual(generate_br_chart_candidates([{"text": "x"}]*25)["status"], "unresolved")
        self.assertEqual(generate_br_chart_candidates([{"text": ""}])["status"], "unresolved")


if __name__ == "__main__":
    unittest.main()
