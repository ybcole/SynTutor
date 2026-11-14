import unittest
from pathlib import Path

from burton_roberts import build_canonical_analysis
from cgel_candidate_xai import (bind_finding, build_benepar_index,
                                candidate_xai_for_sentence)
from cgel_phase_d import correct_selected_sentence
from explanations import explain_request
from parse_engine import analyze
from xai_facts import build_fact_graph

ROOT = Path(__file__).resolve().parents[1]


class CandidateTreeBindingTests(unittest.TestCase):
    def test_parser_tree_binding_for_spelling(self):
        sentence = "The guests paniced at the noise."
        result = candidate_xai_for_sentence(sentence, candidate_tree=analyze(sentence)["root"])
        self.assertEqual(result["status"], "candidate_only")
        self.assertEqual(result["tree_authority"], "benepar_candidate_parse")
        item = next(row for row in result["items"] if row["rule_id"] == "MORPH-109")
        self.assertEqual(item["tree_binding"]["status"], "mapped_span")
        self.assertTrue(item["tree_binding"]["affected_node_id"])
        self.assertIn("paniced", item["explanation"]["short"])
        self.assertIn("insert", item["explanation"]["short"])
        self.assertFalse(item["production_enabled"])

    def test_canonical_relation_binding(self):
        sentence = "The repair crew, arrived at dawn."
        analysis = build_canonical_analysis(analyze(sentence))
        result = candidate_xai_for_sentence(sentence, analysis=analysis)
        self.assertEqual(result["tree_authority"], "canonical_fact_graph")
        item = next(row for row in result["items"] if row["rule_id"] == "OTH-715")
        binding = item["tree_binding"]
        self.assertEqual(binding["status"], "mapped_relation")
        self.assertEqual(len(binding["relation_node_ids"]), 2)
        self.assertIn("noun phrase", item["explanation"]["short"])
        self.assertIn("verb phrase", item["explanation"]["short"])
        self.assertIn("clause", item["explanation"]["short"])

    def test_unresolved_canonical_falls_back_to_parser_tree(self):
        sentence = "The letter came from Washington, D.C.."
        analysis = build_canonical_analysis(analyze(sentence))
        result = candidate_xai_for_sentence(sentence, analysis=analysis)
        self.assertEqual(result["tree_authority"], "benepar_candidate_parse")
        item = next(row for row in result["items"] if row["rule_id"] == "OTH-764")
        self.assertEqual(item["tree_binding"]["status"], "mapped_span")
        self.assertIn("punctuation", item["explanation"]["short"])

    def test_node_filter_limits_items(self):
        sentence = "The repair crew, arrived at dawn."
        analysis = build_canonical_analysis(analyze(sentence))
        full = candidate_xai_for_sentence(sentence, analysis=analysis)
        node_id = full["items"][0]["tree_binding"]["affected_node_id"]
        filtered = candidate_xai_for_sentence(sentence, analysis=analysis, node_id=node_id)
        self.assertEqual(len(filtered["items"]), 1)
        missing = candidate_xai_for_sentence(sentence, analysis=analysis, node_id="not-a-node")
        self.assertEqual(missing["items"], [])
        graph = build_fact_graph(analysis)
        descendant = next(node["node_id"] for node in graph["nodes"]
                          if node_id in node.get("ancestor_ids", []))
        descendant_result = candidate_xai_for_sentence(
            sentence, analysis=analysis, node_id=descendant)
        self.assertEqual(len(descendant_result["items"]), 1)

    def test_finding_without_span_is_unmapped(self):
        sentence = "The guests arrived."
        index = build_benepar_index(analyze(sentence)["root"], sentence)
        binding = bind_finding(index, {
            "rule_id": "TEST-1", "relation": {"kind": "no_span"},
            "edit_hint": None, "learner_explanation": "No span.",
        })
        self.assertEqual(binding["status"], "unmapped")
        self.assertEqual(binding["reason"], "finding_has_no_char_span")


class CandidateXaiIntegrationTests(unittest.TestCase):
    def test_phase_d_findings_carry_bindings(self):
        result = correct_selected_sentence("The guests paniced at the noise.")
        finding = result["original"]["findings"][0]
        self.assertEqual(finding["tree_binding"]["status"], "mapped_span")
        self.assertIn("paniced", finding["candidate_explanation"]["short"])

    def test_explain_request_flag(self):
        sentence = "The guests paniced at the noise."
        tree = build_canonical_analysis(analyze(sentence))["tree"]
        enabled = explain_request({"tree": tree, "include_candidate_xai": True})
        self.assertEqual(enabled["candidate_xai"]["status"], "candidate_only")
        self.assertTrue(enabled["candidate_xai"]["items"])
        disabled = explain_request({"tree": tree})
        self.assertIsNone(disabled["candidate_xai"])
        with self.assertRaises(ValueError):
            explain_request({"tree": tree, "invented": True})



    def test_frontend_has_candidate_red_hook(self):
        main = (ROOT / "web/js/main.js").read_text(encoding="utf-8")
        css = (ROOT / "web/css/style.css").read_text(encoding="utf-8")
        self.assertIn("candidateIssue", main)
        self.assertIn("[data-candidate-issue]", css)
        self.assertIn("include_candidate_xai: true", main)

    def test_candidate_output_is_never_production(self):
        sentence = "The guests paniced at the noise."
        result = candidate_xai_for_sentence(sentence, candidate_tree=analyze(sentence)["root"])
        self.assertFalse(result["production_enabled"])
        self.assertFalse(result["whole_sentence_certified"])
        for item in result["items"]:
            self.assertFalse(item["production_enabled"])
            self.assertEqual(item["explanation"]["claim_status"],
                             "CANDIDATE_OBSERVATION_NOT_VERIFIED_ERROR")


if __name__ == "__main__":
    unittest.main()
