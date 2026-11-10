"""Learner-first explanation acceptance: one contextual English paragraph per node.

Source approvals remain enforced by the separate XAI channels, and an unapproved
Cambridge check cannot appear in the learner text as a categorical error claim.
"""
from __future__ import annotations
from copy import deepcopy
import json
import re
import unittest
from jsonschema import Draft202012Validator
from learner_explanations import compose_learner_explanation, VERSION
from explanations import explain_request
from tree_evaluation import evaluate_request
from xai_facts import build_fact_graph
from test_builder_evaluation import tree
from xai4_partial import evaluate_xai4, ROOT

SCHEMA=json.loads((ROOT/"grammar/learner_explanation.schema.json").read_text())
VALIDATE=Draft202012Validator(SCHEMA)
FORBIDDEN=("B-R structural analysis","Tree rule references","book evidence",
           "Cambridge grammar checks","approval","fact atom","data-xai",
           "source-reviewed", "token interval","unlicensed","XAI-",
           "Benepar","printed page", "not a grammaticality judgment")


def find_word(t, word):
    graph=build_fact_graph({"status":"normalized","tree":t})
    return graph,next(x["node_id"] for x in graph["nodes"] if x["kind"]=="word"
                      and x["surface"].lower()==word.lower())


class LearnerExplanationTests(unittest.TestCase):
    def test_schema_and_invalid_state_stay_safe(self):
        Draft202012Validator.check_schema(SCHEMA)
        self.assertFalse(SCHEMA["additionalProperties"])
        missing=compose_learner_explanation(None)
        VALIDATE.validate(missing)
        self.assertEqual(missing["status"],"unavailable")
        self.assertFalse(missing["whole_sentence_certified"])
        self.assertEqual(missing["source_claim_ids"],[])
        self.assertNotIn("book",missing["text"].lower())

    def test_all_source_works_are_short_and_not_audit_reports(self):
        lesson=json.loads((ROOT/"web/content/lessons/course.json").read_text())
        n=0
        for row in lesson["lessons"]:
            t=row.get("worked_example",{}).get("tree")
            if not isinstance(t,dict): continue
            g=build_fact_graph({"status":"normalized","tree":t})
            for node in g["nodes"]:
                out=compose_learner_explanation(g,node_id=node["node_id"])
                with self.subTest(lesson=row["lesson_id"],node=node["node_id"]):
                    VALIDATE.validate(out)
                    self.assertEqual(out["language_policy"],"ENGLISH_ONLY")
                    self.assertEqual(out["schema_version"],VERSION)
                    self.assertFalse(out["whole_sentence_certified"])
                    self.assertEqual(out["source_claim_ids"],[])
                    self.assertEqual(out["text"].count("\n"),0)
                    self.assertLess(len(out["text"]),750)
                    self.assertTrue(all(phrase.lower() not in out["text"].lower()
                                        for phrase in FORBIDDEN),out["text"])
                n+=1
        self.assertGreaterEqual(n,68)  # All 68 nodes across the ten source lesson trees

    def test_is_explains_actual_ongoing_action_not_span(self):
        g,ident=find_word(tree("br-06"),"is")
        text=compose_learner_explanation(g,node_id=ident)["text"]
        self.assertIn("form of the verb “be”",text)
        self.assertIn("inspecting",text)
        self.assertIn("activity in progress",text)
        self.assertNotIn("drawn",text)
        self.assertNotIn("span",text)

    def test_are_is_an_explained_present_tense_auxiliary(self):
        t=tree("br-06")
        t["sentence"]="They are inspecting the bridge"
        t["tokens"]=[{"index":i,"text":m.group(),"char_span":[m.start(),m.end()]}
                     for i,m in enumerate(re.finditer(r"\S+",t["sentence"]))]
        t["root"]["children"][0]["words"]=["They"]
        t["root"]["children"][1]["children"][0]["children"][0]["word"]="are"
        g,ident=find_word(t,"are")
        text=compose_learner_explanation(g,node_id=ident)["text"]
        self.assertIn("“are”",text)
        self.assertIn("present-tense",text)
        self.assertIn("inspecting",text)
        self.assertNotIn("B-R",text)
        self.assertNotIn("source",text.lower())
        self.assertEqual(len(text.split(".")),3)

    def test_noun_phrase_and_verb_phrase_have_distinct_sentence_meanings(self):
        t=tree("br-04")
        graph=build_fact_graph({"status":"normalized","tree":t})
        np=next(n for n in graph["nodes"] if n["label"]=="NP")
        vp=next(n for n in graph["nodes"] if n["label"]=="VP")
        a=compose_learner_explanation(graph,node_id=np["node_id"])["text"]
        b=compose_learner_explanation(graph,node_id=vp["node_id"])["text"]
        self.assertIn("Nora",a)
        self.assertIn("inspected",a)
        self.assertIn("verb phrase",b)
        self.assertIn("Nora",b)
        self.assertNotEqual(a,b)

    def test_root_sentence_provides_one_summary_before_selection(self):
        graph=build_fact_graph({"status":"normalized","tree":tree("br-02")})
        out=compose_learner_explanation(graph)
        VALIDATE.validate(out)
        self.assertIsNone(out["selected_node_id"])
        self.assertIn("The robins",out["text"])
        self.assertIn("sing",out["text"])
        self.assertLess(len(out["text"]),320)

    def test_cheerful_and_very_are_different_not_a_dictionary_dump(self):
        t=tree("br-03")
        graph=build_fact_graph({"status":"normalized","tree":t})
        words={n["surface"]:n["node_id"] for n in graph["nodes"] if n["kind"]=="word"}
        a=compose_learner_explanation(graph,node_id=words["very"])["text"]
        b=compose_learner_explanation(graph,node_id=words["cheerful"])["text"]
        self.assertNotEqual(a,b)
        self.assertIn("emphasis",a)
        self.assertIn("quality",b)
        self.assertIn("very cheerful",b)

    def test_unspoken_positions_are_not_reported_as_grammar_errors(self):
        from burton_roberts import canonicalize_gold_record
        count=0
        for path in sorted((ROOT/"web/content/book").glob("ch*.trees.json")):
            data=json.loads(path.read_text())
            for row in data.get("trees",[]):
                item=canonicalize_gold_record(row,data)
                if item.get("status")!="normalized":continue
                graph=build_fact_graph(item)
                for node in graph["nodes"]:
                    if node["kind"] not in {"gap","empty","elided_terminal"}:continue
                    out=compose_learner_explanation(graph,node_id=node["node_id"])
                    VALIDATE.validate(out)
                    self.assertIn("omitted part",out["text"])
                    self.assertNotIn("wrong",out["text"])
                    count+=1
            if count>=5:break
        self.assertGreater(count,0)

    def test_provisional_is_honest_and_not_a_certified_rule(self):
        t=tree("br-03")
        g=build_fact_graph({"status":"working","tree":t})
        ident=next(n["node_id"] for n in g["nodes"] if n["kind"]=="word")
        out=compose_learner_explanation(g,node_id=ident)
        VALIDATE.validate(out)
        self.assertEqual(out["status"],"provisional")
        self.assertTrue(out["text"].startswith("In this possible reading"))
        self.assertEqual(out["source_claim_ids"],[])

    def test_approved_source_metadata_cannot_rewrite_student_paragraph(self):
        t=tree("br-03")
        original=explain_request({"tree":t})
        forged=deepcopy(t)
        forged["source"]["review_status"]="HUMAN_APPROVED"
        forged["source"]["printed_page"]=999
        revised=explain_request({"tree":forged})
        self.assertEqual(original["learner_explanation"]["text"],
                         revised["learner_explanation"]["text"])
        self.assertEqual(original["learner_explanation"]["source_claim_ids"],[])

    def test_full_original_xai_channels_stay_available_to_tests(self):
        t=tree("br-04")
        e=explain_request({"tree":t})
        VALIDATE.validate(e["learner_explanation"])
        self.assertIn("contextual_explanations",e)
        self.assertIn("fact_graph",e)
        self.assertIn("xai4_partial_evaluation",e)
        self.assertIn("xai7_unified",e)
        self.assertEqual(e["xai4_partial_evaluation"]["enabled_rule_ids"],[])
        self.assertFalse(e["learner_explanation"]["whole_sentence_certified"])

    def test_builder_shares_exact_same_learner_copy(self):
        t=tree("br-04")
        a=explain_request({"tree":t})
        b=evaluate_request({"tree":t})
        self.assertEqual(b["explanation_evidence"],a)
        self.assertEqual(b["learner_explanation"],a["learner_explanation"])

    def test_minimal_pair_does_not_keep_stale_sentence_copy(self):
        a=tree("br-03")
        b=tree("br-04")
        one=explain_request({"tree":a})["learner_explanation"]
        two=explain_request({"tree":b})["learner_explanation"]
        self.assertNotEqual(one["analysis_id"],two["analysis_id"])
        self.assertNotEqual(one["text"],two["text"])

    def test_legacy_unreviewed_perfect_rule_cannot_say_wrong(self):
        out=evaluate_xai4("She had went home.")
        self.assertFalse(out["findings"])
        self.assertEqual(out["enabled_rule_ids"],[])
        text=compose_learner_explanation(None)["text"]
        self.assertNotIn("incorrect",text.lower())
        self.assertNotIn("book",text.lower())


if __name__ == "__main__":
    unittest.main()
