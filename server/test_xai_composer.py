"""XAI-3 contextual composer acceptance: real course/book trees and blind fixtures.

All examples are English. These tests establish sentence-specific *observations*,
not instructor adjudication of functions or grammaticality.
"""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator

from burton_roberts import canonicalize_gold_record, validate_canonical_tree
from explanations import explain_analysis, explain_request
from tree_evaluation import evaluate_request
from xai_composer import compose_explanations
from xai_facts import build_fact_graph
from xai_planner import plan_nodes
from test_builder_evaluation import tree

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "grammar/xai_composer.schema.json").read_text())
VALIDATOR = Draft202012Validator(SCHEMA)


def content(t, node_id=None, status="normalized"):
    return compose_explanations(build_fact_graph({"tree": t, "status": status}), node_id=node_id)


class XAI3ComposerTests(unittest.TestCase):
    def test_schema_and_all_ten_worked_examples_cover_every_node(self):
        Draft202012Validator.check_schema(SCHEMA)
        course = json.loads((ROOT / "web/content/lessons/course.json").read_text())
        self.assertFalse(SCHEMA["additionalProperties"])
        for lesson in course["lessons"]:
            t = lesson.get("worked_example", {}).get("tree")
            if t is None:
                continue
            with self.subTest(lesson=lesson["lesson_id"]):
                graph = build_fact_graph({"tree": t, "status": "normalized"})
                result = compose_explanations(graph)
                VALIDATOR.validate(result)
                self.assertEqual(result["status"], "observed")
                self.assertEqual(len(result["items"]), len(graph["nodes"]))
                self.assertEqual({row["node_id"] for row in result["items"]},
                                 {row["node_id"] for row in graph["nodes"]})
                for row in result["items"]:
                    self.assertTrue(row["short"] and row["deep"])
                    self.assertEqual(row["source_ids"], [])
                    self.assertEqual(row["claim_status"], "STRUCTURAL_OBSERVATION_ONLY")
                    self.assertEqual(row["function_status"], "unknown_unlicensed")

    def test_unseen_minimal_pair_updates_exact_lexical_context_without_cache(self):
        first = tree("br-02")
        other = deepcopy(first)
        other["sentence"] = "The swans swim"
        other["tokens"][1].update(text="swans", char_span=[4, 9])
        other["tokens"][2].update(text="swim", char_span=[10, 14])
        other["root"]["children"][0]["words"] = ["The", "swans"]
        other["root"]["children"][1]["words"] = ["swim"]
        self.assertTrue(validate_canonical_tree(other)["valid"])
        a = content(first)
        b = content(other)
        self.assertNotEqual(a["analysis_id"], b["analysis_id"])
        self.assertIn("robins", a["items"][0]["short"])
        self.assertIn("swans", b["items"][0]["short"])
        self.assertIn("swim", b["items"][0]["short"])
        self.assertNotIn("robins", b["items"][0]["short"])
        self.assertNotIn("sing", b["items"][0]["short"])

    def test_parent_and_child_explanations_differ_and_name_daughters(self):
        t = tree("br-02")
        rows = {row["node_id"]: row for row in content(t)["items"]}
        root = t["root"]
        np, vp = root["children"]
        self.assertIn("At the root", rows[root["id"]]["short"])
        self.assertIn("NP", rows[root["id"]]["short"])
        self.assertIn("VP", rows[root["id"]]["short"])
        self.assertIn("first immediate child", rows[np["id"]]["short"])
        self.assertIn("second immediate child", rows[vp["id"]]["short"])
        self.assertIn("S", rows[np["id"]]["short"])
        self.assertNotEqual(rows[root["id"]]["short"], rows[np["id"]]["short"])

    def test_word_terminal_has_its_own_sentence_specific_record(self):
        t = tree("br-03")
        graph = build_fact_graph({"status": "normalized", "tree": t})
        word = next(n for n in graph["nodes"] if n["kind"] == "word" and n["surface"] == "cheerful")
        response = content(t, word["node_id"])
        self.assertEqual(len(response["items"]), 1)
        self.assertEqual(response["selected_node_id"], word["node_id"])
        self.assertIn("word “cheerful”", response["items"][0]["short"])
        self.assertIn("A “cheerful”", response["items"][0]["short"])
        self.assertNotIn("is the subject", response["items"][0]["short"])
        self.assertIn("parent", response["items"][0]["deep"])

    def test_exact_source_spacing_and_punctuation_not_normalized_away(self):
        t = tree("br-02")
        t["sentence"] = "The  robins sing"
        t["tokens"][1]["char_span"] = [5, 11]
        t["tokens"][2]["char_span"] = [12, 16]
        self.assertTrue(validate_canonical_tree(t)["valid"])
        root = content(t)["items"][0]
        self.assertIn("The  robins sing", root["short"])
        self.assertIn("The  robins sing", root["deep"])

    def test_opaque_triangle_no_unsupported_internal_word_categories(self):
        t = tree("br-02")
        rows = content(t)["items"]
        tri = [x for x in rows if x["target_kind"] == "triangle"]
        self.assertEqual(len(tri), 2)
        self.assertIn("opaque span", tri[0]["short"])
        self.assertIn("no verified internal category nodes", tri[0]["deep"])
        self.assertFalse(any(x["target_kind"] == "word" for x in rows))

    def test_provisional_unlabelled_tree_displays_uncertainty(self):
        t = tree("br-02")
        t["source"]["evidence_status"] = "UNCERTAIN"
        t["root"]["children"][0].pop("label")
        t["root"]["children"][0]["unlabelled"] = True
        self.assertTrue(validate_canonical_tree(t)["valid"])
        graph = build_fact_graph({"status": "working", "tree": t})
        result = compose_explanations(graph)
        VALIDATOR.validate(result)
        self.assertEqual(result["status"], "provisional")
        self.assertIn("unlabelled triangle", result["items"][1]["short"])
        self.assertTrue(all(x["uncertainty"] == "provisional" for x in result["items"]))
        self.assertTrue(all("subject" not in x["short"].lower() for x in result["items"]))

    def test_gaps_are_not_blame_or_invented_antecedent(self):
        result = content(tree("br-09"))
        gaps = [i for i in result["items"] if i["target_kind"] == "gap"]
        self.assertTrue(gaps)
        for gap in gaps:
            self.assertIn("no spoken word", gap["short"])
            self.assertIsNone(gap["token_span"])
            self.assertNotIn("wrong", gap["short"].lower())
            self.assertNotIn("antecedent is", gap["deep"].lower())

    def test_alternatives_are_not_silently_fused(self):
        t = tree("br-02")
        alt = deepcopy(t["root"])
        alt["children"][1]["label"] = "NP"
        t["accepted_alternatives"] = [{"analysis_id": "test-alternative", "root": alt,
                                        "acceptance": "ACCEPTED",
                                        "rationale": "Unapproved synthetic comparison"}]
        self.assertTrue(validate_canonical_tree(t)["valid"])
        result = content(t)
        self.assertIn("separately recorded alternative", result["items"][0]["deep"])
        self.assertIn("VP", result["items"][0]["short"])
        self.assertNotIn("NP “sing”", result["items"][0]["short"])

    def test_proof_ids_are_actual_atoms_with_matching_tree_paths(self):
        t = tree("br-03")
        graph = build_fact_graph({"tree": t, "status": "normalized"})
        atoms = {a["fact_id"]: a for a in graph["atoms"]}
        output = compose_explanations(graph)
        for row in output["items"]:
            self.assertEqual({p["fact_id"] for p in row["proof"]},
                             set(row["evidence_atom_ids"]))
            for p in row["proof"]:
                self.assertEqual(p["predicate"], atoms[p["fact_id"]]["predicate"])
                self.assertEqual(p["proof_path"], atoms[p["fact_id"]]["proof_path"])
        self.assertTrue(any(len(x["proof"]) > 1 for x in output["items"]))

    def test_missing_proof_and_forged_head_are_rejected(self):
        graph = build_fact_graph({"tree": tree("br-02"), "status": "normalized"})
        wrong = deepcopy(graph)
        wrong["atoms"] = [a for a in wrong["atoms"]
                          if not (a["predicate"] == "node_kind" and a["subject_node_id"] == wrong["nodes"][0]["node_id"])]
        with self.assertRaisesRegex(ValueError, "proof"):
            compose_explanations(wrong)
        wrong = deepcopy(graph)
        wrong["nodes"][1]["function"] = "subject"
        with self.assertRaisesRegex(ValueError, "unlicensed"):
            compose_explanations(wrong)

    def test_untrusted_review_metadata_cannot_create_source_or_role_prose(self):
        t = tree("br-02")
        baseline = content(t)
        t["source"].update(review_status="HUMAN_APPROVED",
                           printed_page=200, book="Burton-Roberts, Analysing Sentences")
        result = content(t)
        self.assertEqual(result, baseline)
        self.assertTrue(all(not x["source_ids"] for x in result["items"]))

    def test_shared_explain_evaluate_and_per_node_api(self):
        t = tree("br-03")
        ordinary = explain_request({"tree": t})
        evaled = evaluate_request({"tree": t})
        self.assertEqual(ordinary["contextual_explanations"], evaled["contextual_explanations"])
        self.assertEqual(ordinary["contextual_explanations"],
                         evaled["explanation_evidence"]["contextual_explanations"])
        self.assertEqual(evaled["grammaticality"]["status"], "unresolved")
        word = next(x for x in ordinary["contextual_explanations"]["items"]
                    if x["target_kind"] == "word")
        selected = explain_request({"tree": t, "node_id": word["node_id"]})
        self.assertEqual(selected["contextual_explanations"]["items"], [word])
        self.assertEqual(ordinary["channels"]["remediation"], [])

    def test_unresolved_no_tree_does_not_invent_prose(self):
        result = compose_explanations(build_fact_graph({"status": "unresolved"}))
        VALIDATOR.validate(result)
        self.assertEqual(result["status"], "unavailable")
        self.assertEqual(result["items"], [])
        response = explain_request({"tree": None})
        self.assertIsNone(response["contextual_explanations"])

    def test_gold_chapters_exercise_nonlesson_tree_shapes(self):
        sampled = 0
        categories = set()
        for path in sorted((ROOT / "web/content/book").glob("ch*.trees.json")):
            data = json.loads(path.read_text())
            successful = 0
            for record in data.get("trees", []):
                canonical = canonicalize_gold_record(record, data)
                if canonical["status"] != "normalized":
                    continue
                with self.subTest(path=path.name, item=record.get("id")):
                    graph = build_fact_graph(canonical)
                    result = compose_explanations(graph)
                    VALIDATOR.validate(result)
                    self.assertEqual(len(result["items"]), len(graph["nodes"]))
                    categories.update(n["label"] for n in graph["nodes"] if n["label"])
                sampled += 1
                successful += 1
                if successful == 4:
                    break
        self.assertGreaterEqual(sampled, 32)
        self.assertTrue({"S", "NP", "VP", "V", "N", "PP", "AP"}.issubset(categories), categories)


if __name__ == "__main__":
    unittest.main()
