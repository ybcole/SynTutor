"""XAI-2 node/word/edge/span fact contract: gold and adversarial English trees."""
import copy
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator
from burton_roberts import validate_canonical_tree
from xai_facts import build_fact_graph
from explanations import explain_analysis, explain_request
from test_builder_evaluation import tree

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "grammar/xai_facts.schema.json").read_text())
VALIDATOR = Draft202012Validator(SCHEMA)


def analysis(t, status="normalized"):
    return {"status": status, "tree": t}


class XAI2FactTests(unittest.TestCase):
    def test_schema_valid_on_all_reviewed_lesson_trees(self):
        course = json.loads((ROOT / "web/content/lessons/course.json").read_text())
        self.assertEqual(SCHEMA["additionalProperties"], False)
        Draft202012Validator.check_schema(SCHEMA)
        count = 0
        for lesson in course["lessons"]:
            t = lesson.get("worked_example", {}).get("tree")
            if not t:
                continue
            with self.subTest(lesson=lesson["lesson_id"]):
                graph = build_fact_graph(analysis(t))
                VALIDATOR.validate(graph)
                self.assertEqual(graph["status"], "observed")
                self.assertTrue(graph["nodes"])
                self.assertEqual(graph["nodes"][0]["path"], "root")
                self.assertEqual(len(graph["token_index"]), len(t["tokens"]))
                self.assertEqual(len({n["node_id"] for n in graph["nodes"]}),
                                 len(graph["nodes"]))
                self.assertTrue(all(n["function"] is None and n["head_node_id"] is None
                                    for n in graph["nodes"]))
                self.assertTrue(all(a["source_rule_ids"] == [] for a in graph["atoms"]))
                count += 1
        self.assertGreaterEqual(count, 10)

    def test_exact_spans_and_opaque_triangles(self):
        t = tree("br-02")
        graph = build_fact_graph(analysis(t), t["root"]["children"][0]["id"])
        root, subject, predicate = graph["nodes"]
        self.assertEqual(root["surface"], "The robins sing")
        self.assertEqual(root["child_ids"], [subject["node_id"], predicate["node_id"]])
        self.assertEqual(subject["sibling_ids"], [predicate["node_id"]])
        self.assertEqual(subject["token_span"], [0, 2])
        self.assertEqual(graph["target"], subject)
        self.assertTrue(graph["token_index"][0]["opaque"])
        self.assertEqual(graph["token_index"][0]["smallest_node_id"], subject["node_id"])
        self.assertIsNone(graph["token_index"][0]["lexical_ancestor_id"])
        self.assertEqual(graph["observed_shapes"][0]["shape"], "S > NP VP")
        self.assertEqual(graph["observed_shapes"][0]["licensed_functions"], [])

    def test_preserves_original_spacing_and_stable_ids(self):
        t = tree("br-02")
        t["sentence"] = "The  robins sing"
        t["tokens"][1]["char_span"] = [5, 11]
        t["tokens"][2]["char_span"] = [12, 16]
        # The first token ends at position 3; the second begins at position 5.
        t["tokens"][1]["char_span"] = [5, 11]
        self.assertTrue(validate_canonical_tree(t)["valid"])
        a = build_fact_graph(analysis(t))
        b = build_fact_graph(analysis(copy.deepcopy(t)))
        self.assertEqual(a, b)
        self.assertEqual(a["nodes"][0]["surface"], "The  robins sing")
        self.assertEqual(a["nodes"][1]["surface"], "The  robins")

    def test_real_lexical_ancestors_are_not_promoted_to_heads(self):
        t = tree("br-03")
        graph = build_fact_graph(analysis(t))
        self.assertTrue(any(n["kind"] == "word" for n in graph["nodes"]))
        self.assertTrue(any(n["label"] in {"V", "N", "P", "A"}
                            for n in graph["nodes"]))
        self.assertTrue(any(item["lexical_ancestor_id"] is not None
                            for item in graph["token_index"]))
        self.assertTrue(all(n["head_status"] == "unknown_unlicensed"
                            for n in graph["nodes"]))

    def test_unlabelled_working_triangle_is_opaque_and_provisional(self):
        t = tree("br-02")
        t["source"]["evidence_status"] = "UNCERTAIN"
        t["root"]["children"][0].pop("label")
        t["root"]["children"][0]["unlabelled"] = True
        self.assertTrue(validate_canonical_tree(t)["valid"])
        graph = build_fact_graph(analysis(t, "working"))
        self.assertEqual(graph["status"], "provisional")
        self.assertIsNone(graph["nodes"][1]["label"])
        self.assertTrue(graph["token_index"][0]["opaque"])
        self.assertTrue(all(a["uncertainty"] == "provisional" for a in graph["atoms"]))
        self.assertEqual(graph["observed_shapes"], [])

    def test_gaps_without_anchors_have_no_invented_token_spans(self):
        t = tree("br-09")
        graph = build_fact_graph(analysis(t))
        gaps = [n for n in graph["nodes"] if n["kind"] == "gap"]
        self.assertGreaterEqual(len(gaps), 1)
        self.assertTrue(all(n["surface"] == "" and n["token_span"] is None
                            and n["char_span"] is None for n in gaps))
        self.assertEqual(graph["movement_links"], [])
        self.assertTrue(all(n["function_status"] == "unknown_unlicensed" for n in gaps))

    def test_alternatives_never_merge_into_primary_tree(self):
        t = tree("br-02")
        alternate_root = copy.deepcopy(t["root"])
        alternate_root["children"][1]["label"] = "NP"
        t["accepted_alternatives"] = [{
            "analysis_id": "synthetic-alternative",
            "root": alternate_root,
            "acceptance": "ACCEPTED",
            "rationale": "Synthetic unit fixture, not an approved linguistic analysis",
        }]
        self.assertTrue(validate_canonical_tree(t)["valid"])
        graph = build_fact_graph(analysis(t))
        VALIDATOR.validate(graph)
        self.assertEqual(len(graph["alternatives"]), 1)
        self.assertEqual(graph["observed_shapes"][0]["shape"], "S > NP VP")
        self.assertEqual(graph["alternatives"][0]["observed_shapes"], [])
        self.assertEqual(graph["alternatives"][0]["status"],
                         "conditional_alternative_not_merged")

    def test_untrusted_source_flags_do_not_authorize_roles(self):
        t = tree("br-02")
        t["source"]["review_status"] = "HUMAN_APPROVED"
        t["source"]["printed_page"] = 29
        graph = build_fact_graph(analysis(t))
        self.assertTrue(all(n["function"] is None for n in graph["nodes"]))
        self.assertTrue(all(n["head_node_id"] is None for n in graph["nodes"]))
        self.assertTrue(all(a["source_rule_ids"] == [] for a in graph["atoms"]))

    def test_invalid_tree_and_missing_target_rejected(self):
        t = tree("br-02")
        t["tokens"][0]["text"] = "FAKE"
        with self.assertRaises(ValueError):
            build_fact_graph(analysis(t))
        with self.assertRaisesRegex(ValueError, "node_id"):
            build_fact_graph(analysis(tree("br-02")), "absent")
        with self.assertRaises(ValueError):
            build_fact_graph(analysis(tree("br-02")), {"bad": "node"})

    def test_shared_transport_and_evaluation_do_not_change_verdict(self):
        t = tree("br-02")
        graph = build_fact_graph(analysis(t))
        explanation = explain_analysis(analysis(t))
        request = explain_request({"tree": t})
        self.assertEqual(explanation["fact_graph"], graph)
        self.assertEqual(request["fact_graph"], graph)
        self.assertEqual(explanation["channels"]["grammatical"], [])
        self.assertEqual(explanation["channels"]["remediation"], [])
        from tree_evaluation import evaluate_request
        evaluated = evaluate_request({"tree": t})
        self.assertEqual(evaluated["fact_graph"], graph)
        self.assertEqual(evaluated["grammaticality"]["status"], "unresolved")
        self.assertEqual(evaluated["explanation_evidence"]["fact_graph"], graph)

    def test_unresolved_has_no_fabricated_structure(self):
        graph = build_fact_graph({"status": "unresolved", "tree": None})
        VALIDATOR.validate(graph)
        self.assertEqual(graph["status"], "unavailable")
        self.assertEqual(graph["nodes"], [])
        self.assertEqual(graph["atoms"], [])
        self.assertIsNone(explain_request({"tree": None})["fact_graph"])


if __name__ == "__main__":
    unittest.main()
