"""Stress regressions for explanation coverage and B-R fallback trees.

These tests exercise the learner-facing symptoms reported in the manual
stress test: red words without a "What's wrong" record, unlabelled triangles
for modal/to sequences, and whole-sentence triangles for wh-questions.
"""

import importlib
import sys
import unittest

from api import build_payload
from explanations import explain_analysis
from learner_explanations import compose_learner_explanation


def setUpModule():
    """Undo dependency stubs left by another test module.

    ``test_api_contract`` installs stub ``parse_engine``, ``matrix``,
    ``detector`` and related modules in ``sys.modules`` while importing ``api``.
    In a grouped CI run that leaves ``api.analyze``/``api.evaluate`` as None for
    later modules, so restore the real modules before exercising payloads.
    """
    import api
    if callable(getattr(api, "analyze", None)) and callable(getattr(api, "evaluate", None)):
        return
    for name in ("parse_engine", "matrix", "detector", "licensing",
                 "corrector", "corrections", "plain"):
        sys.modules.pop(name, None)
    importlib.invalidate_caches()
    importlib.reload(api)


def _walk(node):
    yield node
    for child in node.get("children") or []:
        yield from _walk(child)


def _error_details(payload):
    return {key: detail for key, detail in (payload.get("node_details") or {}).items()
            if isinstance(detail, dict) and detail.get("status") == "error"}


class ExplanationCoverageTests(unittest.TestCase):
    def test_every_error_word_has_a_canonical_binding(self):
        payload = build_payload("These child are tired.")
        details = _error_details(payload)
        self.assertTrue(details)
        for detail in details.values():
            self.assertTrue(detail.get("canonical_node_ids"),
                            f"{detail.get('constraint')} has no canonical node")
        determiner = next(detail for detail in details.values()
                          if detail.get("constraint") == "C-DETERMINER-AGREEMENT")
        spans = determiner["canonical_binding"]["token_spans"]
        self.assertIn([0, 1], spans)
        self.assertIn([1, 2], spans)

    def test_participle_error_word_is_bound(self):
        payload = build_payload("I seen him yesterday and he don't care.")
        detail = next(detail for detail in _error_details(payload).values()
                      if detail.get("constraint") == "C-VBN-SIMPLE-PAST")
        self.assertIn([1, 2], detail["canonical_binding"]["token_spans"])

    def test_modal_to_sequence_is_labelled_not_triangulated(self):
        payload = build_payload(
            "The researchers might to have been examining the evidence when the committee unexpectedly arrived.")
        analysis = payload["br_analysis"]
        self.assertEqual(analysis["status"], "normalized")
        labels = [node.get("label") for node in _walk(analysis["tree"]["root"])]
        self.assertIn("MOD", labels)
        self.assertIn("AUX", labels)
        unlabelled = [node for node in _walk(analysis["tree"]["root"])
                      if node.get("triangle") and not node.get("label")]
        self.assertFalse(unlabelled)

    def test_wh_question_keeps_a_labelled_tree(self):
        payload = build_payload(
            "Who did the administrator say that submitted the application before the deadline?")
        analysis = payload["br_analysis"]
        self.assertEqual(analysis["status"], "normalized")
        self.assertTrue(analysis.get("tree"))
        self.assertTrue(analysis.get("display_labels"))
        root = analysis["tree"]["root"]
        self.assertFalse(root.get("triangle"))
        self.assertGreater(len(list(_walk(root))), 8)

    def test_locative_pp_expands_with_nested_pp(self):
        payload = build_payload(
            "The list of items are on the table beside the folder reviews.")
        analysis = payload["br_analysis"]
        self.assertEqual(analysis["status"], "normalized")
        pp_nodes = [node for node in _walk(analysis["tree"]["root"])
                    if node.get("label") == "PP"]
        self.assertGreaterEqual(len(pp_nodes), 2)
        self.assertTrue(all(not node.get("triangle") for node in pp_nodes))

    def test_word_explanations_are_specific_and_not_self_referential(self):
        cases = [
            ("Who did the administrator say that submitted the application before the deadline?",
             "who", "wh-phrase"),
            ("He gave to charity all the money she had left him.", "he", "pronoun"),
        ]
        for sentence, word, expected in cases:
            with self.subTest(word=word):
                payload = build_payload(sentence)
                graph = explain_analysis({
                    **payload["br_analysis"], "sentence": sentence})["fact_graph"]
                by_id = {node["node_id"]: node for node in graph["nodes"]}
                word_node = next(node for node in graph["nodes"]
                                 if node["kind"] == "word"
                                 and node["surface"].lower() == word)
                text = compose_learner_explanation(
                    graph, node_id=word_node["node_id"])["text"]
                self.assertIn(expected, text.lower())
                for node in graph["nodes"]:
                    node_text = compose_learner_explanation(
                        graph, node_id=node["node_id"])["text"]
                    surface = str(node.get("surface") or "").strip()
                    self.assertNotIn(f"larger expression “{surface}”", node_text)
                    if surface:
                        self.assertNotIn(f"is part of “{surface}”", node_text)
                        self.assertNotIn("this position identifies", node_text)
                    parent = by_id.get(node.get("parent_id"))
                    if parent and (node["kind"] == "word"
                                   or node.get("label") in {"pronoun", "C2", "C1"}):
                        parent_text = compose_learner_explanation(
                            graph, node_id=parent["node_id"])["text"]
                        self.assertNotEqual(node_text, parent_text)

    def test_correction_reports_its_impact(self):
        payload = build_payload("A apple are on the table.")
        impact = payload["summary"]["correction"]["impact"]
        self.assertTrue(impact["whole_sentence_clean"])
        self.assertEqual(impact["resolved_count"], 2)
        self.assertEqual(impact["remaining_count"], 0)
        self.assertEqual(impact["introduced_count"], 0)


if __name__ == "__main__":
    unittest.main()
