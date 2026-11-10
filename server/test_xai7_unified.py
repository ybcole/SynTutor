"""XAI-7: cross-mode shared evidence and relation-localization acceptance.

These are deterministic English-only UI evidence contracts, not human
approval of any unreviewed Cambridge rule or learner correction.
"""
from __future__ import annotations

from copy import deepcopy
import json
import unittest

from jsonschema import Draft202012Validator

from explanations import explain_request, explain_analysis
from tree_evaluation import evaluate_request
from quiz_bank import explain_quiz_request, load_quiz_bank
from xai7_unified import VERSION, assemble
from xai_composer import compose_explanations
from xai_facts import build_fact_graph
from test_builder_evaluation import tree
from test_explanations import registry
from xai6_naturalizer import ROOT

SCHEMA = json.loads((ROOT/"grammar/xai7_unified.schema.json").read_text())
VALIDATOR = Draft202012Validator(SCHEMA)


def selection(record="br-03", kind="word"):
    t = tree(record)
    graph = build_fact_graph({"status":"normalized","tree":t})
    selected = next(n for n in graph["nodes"] if n["kind"] == kind)
    return t, selected["node_id"]


class XAI7UnifiedTests(unittest.TestCase):
    def test_schema_is_strict(self):
        Draft202012Validator.check_schema(SCHEMA)
        self.assertFalse(SCHEMA["additionalProperties"])
        self.assertEqual(VERSION,"xai7-evidence-1.0.0")

    def test_single_word_selected_parent_and_sibling_are_observed_not_functions(self):
        t, ident=selection()
        response=explain_request({"tree":t,"node_id":ident})
        ui=response["xai7_unified"]
        VALIDATOR.validate(ui)
        self.assertEqual(ui["mode"],"tree")
        self.assertEqual(ui["tree_status"],"observed")
        self.assertEqual(ui["selected_node_id"],ident)
        self.assertTrue(any(x["reason"]=="selected" and x["node_id"]==ident
                            for x in ui["focus"]))
        self.assertTrue(any(x["reason"]=="parent" for x in ui["focus"]))
        self.assertTrue(all(x["relation_authority"]=="witnessed_tree_position"
                            for x in ui["focus"]))
        self.assertEqual(ui["verified_issues"],[])
        self.assertEqual(ui["claim_boundary"],
                         "observations_do_not_create_new_functions_or_grammar_verdicts")
        self.assertFalse(ui["whole_sentence_certified"])

    def test_original_graph_and_contextual_output_unchanged(self):
        t,ident=selection()
        result=explain_request({"tree":t,"node_id":ident})
        graph=result["fact_graph"]
        original=build_fact_graph({"status":"normalized","tree":t},node_id=ident)
        self.assertEqual(graph,original)
        self.assertEqual(result["contextual_explanations"],
                         compose_explanations(original,node_id=ident))
        self.assertEqual(result["xai6_naturalization"]["status"],"disabled")

    def test_all_modes_use_unchanged_common_top_level(self):
        t,ident=selection()
        generator=explain_request({"tree":t,"node_id":ident})
        builder=evaluate_request({"tree":t})
        canonical=explain_request({"tree":t})
        self.assertEqual(builder["explanation_evidence"],canonical)
        self.assertEqual(builder["xai7_unified"],canonical["xai7_unified"])
        self.assertEqual(generator["xai7_unified"]["selected_node_id"],ident)
        self.assertEqual(builder["xai7_unified"]["selected_node_id"],None)
        self.assertEqual(generator["xai4_partial_evaluation"]["findings"],[])
        VALIDATOR.validate(builder["xai7_unified"])

    def test_no_user_can_inject_an_approved_relation_into_http_evidence(self):
        t,_=selection()
        for key in ("xai7_unified","approved_governor","source_approval","reviewer","xai4_findings"):
            with self.subTest(key=key),self.assertRaises(ValueError):
                explain_request({"tree":t,key:True})
            with self.subTest(key=key),self.assertRaises(ValueError):
                evaluate_request({"tree":t,key:True})

    def test_known_feature_rows_keep_exact_source_labels(self):
        t=tree("br-03")
        g=build_fact_graph({"status":"normalized","tree":t})
        featured=[n for n in g["nodes"] if n.get("features")]
        self.assertTrue(featured)
        ident=featured[0]["node_id"]
        result=explain_request({"tree":t,"node_id":ident})
        items=result["xai7_unified"]["feature_rows"]
        self.assertEqual([r["feature"] for r in items],featured[0]["features"])
        self.assertTrue(all(r["status"]=="observed_label_not_a_verified_function"
                            for r in items))
        VALIDATOR.validate(result["xai7_unified"])

    def test_no_selection_means_no_invented_context(self):
        t,_=selection()
        response=explain_request({"tree":t})
        ui=response["xai7_unified"]
        self.assertIsNone(ui["selected_node_id"])
        self.assertEqual(ui["focus"],[])
        self.assertEqual(ui["feature_rows"],[])
        self.assertEqual(ui["verified_issues"],[])

    def test_provisional_tree_preserves_uncertainty(self):
        t, ident=selection()
        t["source"]["evidence_status"]="UNCERTAIN"
        result=explain_analysis({"status":"working","tree":t},node_id=ident)
        self.assertEqual(result["xai7_unified"]["tree_status"],"provisional")
        self.assertEqual(result["xai7_unified"]["contextual_status"],"provisional")
        self.assertEqual(result["xai7_unified"]["verified_issues"],[])
        VALIDATOR.validate(result["xai7_unified"])

    def test_unresolved_tree_returns_no_fictitious_nodes(self):
        res=explain_request({"tree":None})
        ui=res["xai7_unified"]
        VALIDATOR.validate(ui)
        self.assertEqual(ui["tree_status"],"unavailable")
        self.assertEqual(ui["focus"],[])
        self.assertIsNone(ui["selected_node_id"])
        self.assertEqual(ui["citations"],[])

    def test_source_verified_structural_citations_show_actual_pages(self):
        t=tree("br-02")
        result=explain_analysis({"status":"normalized","tree":t},registry=registry())
        ui=result["xai7_unified"]
        VALIDATOR.validate(ui)
        for citation in ui["citations"]:
            self.assertIsInstance(citation["printed_page"],int)
            self.assertGreater(citation["printed_page"],0)
            self.assertIn(citation["book"],{"B-R","Cambridge"})
        self.assertNotIn("invented_page_url",ui)

    def test_fake_extra_source_cannot_create_book_link(self):
        t,ident=selection()
        t["source"]["unreviewed_pdf_url"]="https://example.com/fake.pdf#page=100"
        with self.assertRaises(ValueError):
            explain_request({"tree":t,"node_id":ident})

    def test_quiz_feedback_uses_same_schema_without_fake_tree(self):
        bank=load_quiz_bank()
        item=bank["items"][0]
        result=explain_quiz_request({
            "quiz_item_id":item["item_id"],
            "quiz_item_version":item["content_version"],
            "answer_id":item["answer"],
        })
        ui=result["xai7_unified"]
        VALIDATOR.validate(ui)
        self.assertEqual(ui["mode"],"quiz")
        self.assertEqual(ui["tree_status"],"unavailable")
        self.assertEqual(ui["focus"],[])
        self.assertIsNone(ui["analysis_id"])
        self.assertEqual(ui["book_status"],result["status"])
        self.assertFalse(ui["whole_sentence_certified"])

    def test_quiz_unapproved_book_claim_is_not_human_verified(self):
        bank=load_quiz_bank()
        item=deepcopy(bank["items"][0])
        item["review_status"]="PENDING"
        from explanations import explain_quiz_response
        result=explain_quiz_response(item,item["answer"],bank.get("sources",[]))
        self.assertEqual(result["status"],"NO_BOOK_BASIS")
        self.assertEqual(result["xai7_unified"]["citations"],[])
        VALIDATOR.validate(result["xai7_unified"])

    def test_quiz_answer_tree_can_be_explained_like_generator(self):
        bank=load_quiz_bank()
        sample=next((item for item in bank["items"] if item.get("answer_tree")),None)
        if sample is None:self.skipTest("No released quiz answer-tree fixture")
        ident=sample["answer_tree"]["root"]["id"]
        res=explain_request({"tree":sample["answer_tree"],"node_id":ident})
        VALIDATOR.validate(res["xai7_unified"])
        self.assertEqual(res["xai7_unified"]["selected_node_id"],ident)

    def test_correction_preview_uses_new_tree_not_original(self):
        a=tree("br-02")
        b=tree("br-03")
        orig=explain_request({"tree":a,"node_id":a["root"]["id"]})["xai7_unified"]
        new=explain_request({"tree":b,"node_id":b["root"]["id"]})["xai7_unified"]
        self.assertNotEqual(orig["analysis_id"],new["analysis_id"])
        self.assertNotEqual(orig["selected_node_id"],new["selected_node_id"])
        self.assertEqual(new["verified_issues"],[])
        VALIDATOR.validate(new)

    def test_cannot_infer_grammatical_relation_from_unapproved_xai4(self):
        t,ident=selection()
        result=explain_request({"tree":t,"node_id":ident})
        self.assertEqual(result["xai4_partial_evaluation"]["enabled_rule_ids"],[])
        ui=result["xai7_unified"]
        self.assertFalse(any(x["relation_authority"]=="approved_rule" for x in ui["focus"]))
        self.assertEqual(ui["verified_issues"],[])

    def test_simulated_approved_rule_highlights_only_attested_tree_nodes(self):
        t,ident=selection()
        res=explain_request({"tree":t,"node_id":ident})
        graph=res["fact_graph"]
        parent=graph["target"]["parent_id"]
        if parent is None:self.skipTest("Selected node has no parent")
        simulation=deepcopy(res)
        simulation["xai5_localization"]={"diagnoses":[{
            "finding_id":"synthetic-only","rule_id":"TEST-NOT-PRODUCTION",
            "governor_location":{"node_id":parent,"ancestor_node_ids":[]},
            "target_location":{"node_id":ident,"ancestor_node_ids":[parent]},
            "char_span":[0,1],
        }]}
        ui=assemble(simulation)
        VALIDATOR.validate(ui)
        self.assertEqual(len(ui["verified_issues"]),1)
        self.assertTrue(any(r["reason"]=="approved_governor" and r["node_id"]==parent
                            for r in ui["focus"]))
        self.assertEqual(ui["verified_issues"][0]["status"],"verified_local_violation")
        self.assertFalse(ui["whole_sentence_certified"])
        # This direct fabricated sidecar is confined to synthetic test input.
        original=assemble(res)
        self.assertEqual(original["verified_issues"],[])

    def test_selected_word_and_ancestor_witness_exact_node_ids(self):
        t,ident=selection("br-03","word")
        res=explain_request({"tree":t,"node_id":ident})
        graph=res["fact_graph"]
        ui=res["xai7_unified"]
        ids={n["node_id"] for n in graph["nodes"]}
        self.assertTrue(set(r["node_id"] for r in ui["focus"]).issubset(ids))
        self.assertEqual(ui["focus"][0]["node_id"],ident)
        for focus in ui["focus"]:
            self.assertNotIn("Benepar",focus["relation_authority"])

    def test_book_source_conflict_retains_distinct_status(self):
        t=tree("br-02")
        reg=registry()
        if not reg["templates"]:self.skipTest("No source templates in fixture")
        conflicting=deepcopy(reg["templates"][0])
        conflicting["id"]="synthetic-conflict"
        conflicting["text"]="Completely different synthetic wording."
        reg["templates"].append(conflicting)
        output=explain_analysis({"status":"normalized","tree":t},registry=reg)
        self.assertIn(output["xai7_unified"]["book_status"],
                      {"SOURCE_CONFLICT","EXPLAINED","NO_BOOK_BASIS"})
        self.assertFalse(output["xai7_unified"]["whole_sentence_certified"])

    def test_english_only_learning_tree_examples_all_validate(self):
        course=json.loads((ROOT/"web/content/lessons/course.json").read_text())
        count=0
        for lesson in course["lessons"]:
            t=lesson.get("worked_example",{}).get("tree")
            if not isinstance(t,dict):continue
            with self.subTest(lesson=lesson["lesson_id"]):
                g=build_fact_graph({"status":"normalized","tree":t})
                for node in g["nodes"][:3]:
                    evidence=explain_request({"tree":t,"node_id":node["node_id"]})
                    VALIDATOR.validate(evidence["xai7_unified"])
                    self.assertEqual(evidence["xai7_unified"]["language_policy"],"ENGLISH_ONLY")
                    self.assertFalse(evidence["xai7_unified"]["whole_sentence_certified"])
                    count+=1
        self.assertGreaterEqual(count,25)

    def test_book_tree_sampled_gold_is_proof_preserving(self):
        from burton_roberts import canonicalize_gold_record
        count=0
        for path in sorted((ROOT/"web/content/book").glob("ch*.trees.json")):
            data=json.loads(path.read_text())
            for row in data.get("trees",[]):
                analysis=canonicalize_gold_record(row,data)
                if analysis["status"]!="normalized":continue
                root=analysis["tree"]["root"]["id"]
                evidence=explain_analysis(analysis,node_id=root)
                VALIDATOR.validate(evidence["xai7_unified"])
                self.assertEqual(evidence["xai7_unified"]["selected_node_id"],root)
                count+=1
                break
        self.assertGreaterEqual(count,8)

    def test_invalid_mode_rejected(self):
        with self.assertRaises(ValueError):assemble({},mode="unknown")
        with self.assertRaises(ValueError):assemble(None)
        with self.assertRaises(ValueError):assemble({},mode=None)


if __name__=="__main__":
    unittest.main()
