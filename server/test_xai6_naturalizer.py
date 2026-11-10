"""XAI-6 optional LLM-naturalization acceptance and adversarial evidence tests.

No external AI service is called. Fake model/reviewer metadata is strictly local
to tests and NEVER represents a human-reviewed blind quality study.
"""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from jsonschema import Draft202012Validator

from explanations import explain_request
from tree_evaluation import evaluate_request
from xai_composer import compose_explanations
from xai_facts import build_fact_graph
from xai6_naturalizer import (
    ROOT, BoundedNaturalizerCache, allowed_variants, load_policy,
    naturalize, promotion_eligible, verify_candidate,
)
from test_builder_evaluation import tree

POLICY = load_policy()
POLICY_SCHEMA = json.loads((ROOT / "grammar/xai6_policy.schema.json").read_text())
CANDIDATE_SCHEMA = json.loads((ROOT / "grammar/xai6_candidate.schema.json").read_text())
RESULT_SCHEMA = json.loads((ROOT / "grammar/xai6_result.schema.json").read_text())
CHECK = Draft202012Validator(RESULT_SCHEMA)


def target(t=None):
    t = t or tree("br-03")
    graph = build_fact_graph({"status": "normalized", "tree": t})
    word = next(n for n in graph["nodes"] if n["kind"] == "word")
    item = compose_explanations(graph, node_id=word["node_id"])
    return graph, item, word["node_id"]


def synthetic_enabled():
    """Synthetic sign-off metadata ONLY inside test process, never production."""
    p = deepcopy(POLICY)
    p["release_status"] = "APPROVED_FOR_LIMITED_ROLLOUT"
    p["model_enabled"] = True
    p["human_evaluation_fixture_count"] = 20
    p["enablement"].update({
        "independent_human_blind_comparison": True,
        "factual_fidelity_at_least_baseline": True,
        "readability_gain_demonstrated": True,
        "no_material_increase_in_false_claims": True,
        "reviewed_by": "SYNTHETIC-TEST-ONLY",
        "reviewed_on": "2026-11-10",
        "review_report": "synthetic://not-a-human-review",
    })
    p["contract"]["model_transport_enabled"] = True
    p["contract"]["model_id"] = "synthetic-no-network"
    return p


def choose(packet, *, timeout_ms, max_output_tokens):
    assert timeout_ms <= 1500 and max_output_tokens <= 300
    return {
        "candidate": {
            "schema_version": "xai6-candidate-1.0.0",
            "language_policy": "ENGLISH_ONLY",
            "analysis_id": packet["analysis_id"],
            "node_id": packet["node_id"],
            "reading_level": packet["reading_level"],
            "paragraphs": [
                {"level": para["level"], "text": para["allowed_texts"][-1],
                 "supported_fact_ids": para["supported_fact_ids"], "source_ids": []}
                for para in packet["paragraphs"]
            ],
        },
        "usage": {"input_tokens": 80, "output_tokens": 100, "cost_usd": 0.001},
    }


class XAI6NaturalizerTests(unittest.TestCase):
    def test_policy_and_candidate_result_schemas(self):
        for schema in [POLICY_SCHEMA, CANDIDATE_SCHEMA, RESULT_SCHEMA]:
            Draft202012Validator.check_schema(schema)
            self.assertFalse(schema["additionalProperties"])
        Draft202012Validator(POLICY_SCHEMA).validate(POLICY)
        self.assertFalse(POLICY["model_enabled"])
        self.assertEqual(POLICY["language_policy"], "ENGLISH_ONLY")
        self.assertEqual(POLICY["human_evaluation_fixture_count"], 0)
        self.assertFalse(promotion_eligible(POLICY))

    def test_default_release_never_calls_model_and_preserves_xai3(self):
        graph, context, node = target()
        calls = []
        def provider(*args, **kwargs):
            calls.append(args)
            raise AssertionError("model should not be called")
        result = naturalize(graph,context,node_id=node,provider=provider)
        CHECK.validate(result)
        self.assertEqual(result["status"],"disabled")
        self.assertEqual(result["reason_code"],"INDEPENDENT_BLIND_REVIEW_PENDING")
        self.assertEqual(result["provider_calls"],0)
        self.assertEqual(calls,[])
        self.assertEqual(result["paragraphs"][0]["text"],context["items"][0]["short"])
        self.assertEqual(result["paragraphs"][1]["text"],context["items"][0]["deep"])
        self.assertEqual(result["source_ids"],[])
        self.assertFalse(result["whole_sentence_certified"])

    def test_no_selected_node_or_unresolved_tree_uses_no_model(self):
        graph,_,node=target()
        whole=compose_explanations(graph)
        missing=naturalize(graph,whole,node_id=None,policy=synthetic_enabled(),provider=choose)
        CHECK.validate(missing)
        self.assertEqual(missing["status"],"unavailable")
        self.assertEqual(missing["reason_code"],"NO_SELECTED_NODE")
        self.assertEqual(missing["paragraphs"],[])
        unresolved=naturalize(None,None,node_id=node)
        CHECK.validate(unresolved)
        self.assertEqual(unresolved["status"],"unavailable")

    def test_every_review_gate_is_individually_required(self):
        base=synthetic_enabled()
        self.assertTrue(promotion_eligible(base))
        for key in base["enablement"]:
            if key in {"reviewed_by","reviewed_on","review_report"}:
                invalid=deepcopy(base);invalid["enablement"][key]=None
            else:
                invalid=deepcopy(base);invalid["enablement"][key]=False
            with self.subTest(approval=key):
                self.assertFalse(promotion_eligible(invalid))
        for key,value in [("model_enabled",False),("release_status","DISABLED_PENDING_BLIND_REVIEW"),
                          ("human_evaluation_fixture_count",19)]:
            invalid=deepcopy(base);invalid[key]=value
            self.assertFalse(promotion_eligible(invalid))

    def test_model_production_transport_is_not_configured(self):
        self.assertIsNone(POLICY["contract"]["model_id"])
        self.assertFalse(POLICY["contract"]["model_transport_enabled"])
        self.assertEqual(POLICY["contract"]["max_provider_calls"],1)
        graph,context,node=target()
        missing=naturalize(graph,context,node_id=node,policy=synthetic_enabled())
        CHECK.validate(missing)
        self.assertEqual(missing["status"],"fallback")
        self.assertEqual(missing["reason_code"],"MODEL_TRANSPORT_UNAVAILABLE")

    def test_only_bounded_paraphrase_choice_is_accepted(self):
        graph,context,node=target()
        packet=[]
        def callback(payload, **kwargs):
            packet.append(payload)
            return choose(payload,**kwargs)
        result=naturalize(graph,context,node_id=node,provider=callback,
                          policy=synthetic_enabled(),cache=BoundedNaturalizerCache())
        CHECK.validate(result)
        self.assertEqual(result["status"],"accepted")
        self.assertEqual(result["reason_code"],"NATURALIZATION_ACCEPTED")
        self.assertEqual(result["provider_calls"],1)
        self.assertEqual(result["cache_status"],"miss")
        self.assertEqual(len(packet),1)
        self.assertEqual({a["fact_id"] for a in packet[0]["facts"]},
                         set(context["items"][0]["evidence_atom_ids"]))
        self.assertEqual(packet[0]["claim_status"],"STRUCTURAL_OBSERVATION_ONLY")
        self.assertEqual(packet[0]["paragraphs"][0]["source_ids"],[])
        self.assertNotEqual(result["paragraphs"][0]["text"],context["items"][0]["short"])

    def test_outside_quotes_never_modifies_source_literal(self):
        original='The overt word “the tree shows is drawn” is drawn within V “is drawn”.'
        variants=allowed_variants(original)
        self.assertTrue(any(v!=original for v in variants))
        for variant in variants:
            self.assertIn('“the tree shows is drawn”',variant)
            self.assertIn('V “is drawn”',variant)
        self.assertEqual(allowed_variants("No safe phrase to replace."),
                         ["No safe phrase to replace."])

    def test_provider_cannot_assert_subject_or_source_page(self):
        graph,context,node=target()
        def forged(packet,**kwargs):
            answer=choose(packet,**kwargs)
            answer["candidate"]["paragraphs"][0]["text"] += " This is the subject (Cambridge p. 123)."
            return answer
        out=naturalize(graph,context,node_id=node,provider=forged,
                       policy=synthetic_enabled(),cache=BoundedNaturalizerCache())
        self.assertEqual(out["status"],"fallback")
        self.assertEqual(out["reason_code"],"MODEL_RESPONSE_REJECTED")
        self.assertEqual(out["paragraphs"][0]["text"],context["items"][0]["short"])

    def test_provider_cannot_rewrite_quote_or_presuppose_wrongness(self):
        graph,context,node=target()
        for extra in [' You should correct this sentence.', ' It is always ungrammatical.']:
            def mutate(packet,**kwargs):
                answer=choose(packet,**kwargs)
                answer["candidate"]["paragraphs"][0]["text"] += extra
                return answer
            with self.subTest(extra=extra):
                out=naturalize(graph,context,node_id=node,provider=mutate,
                               policy=synthetic_enabled(),cache=BoundedNaturalizerCache())
                self.assertEqual(out["status"],"fallback")

    def test_forged_fact_id_and_dropped_proof_rejected(self):
        graph,context,node=target()
        for change in ("extra","drop"):
            def mutate(packet,**kwargs):
                value=choose(packet,**kwargs)
                facts=value["candidate"]["paragraphs"][0]["supported_fact_ids"]
                if change=="extra":facts.append("f99999")
                else:facts.pop()
                return value
            with self.subTest(change=change):
                out=naturalize(graph,context,node_id=node,provider=mutate,
                               policy=synthetic_enabled(),cache=BoundedNaturalizerCache())
                self.assertEqual(out["status"],"fallback")

    def test_invented_citation_is_rejected(self):
        graph,context,node=target()
        def candidate(packet,**kwargs):
            value=choose(packet,**kwargs)
            value["candidate"]["paragraphs"][0]["source_ids"]=["fake-book-page"]
            return value
        result=naturalize(graph,context,node_id=node,provider=candidate,
                          policy=synthetic_enabled(),cache=BoundedNaturalizerCache())
        self.assertEqual(result["reason_code"],"MODEL_RESPONSE_REJECTED")

    def test_wrong_node_analysis_level_are_rejected(self):
        graph,context,node=target()
        for kind in ("node_id","analysis_id","reading_level"):
            def candidate(packet,**kwargs):
                result=choose(packet,**kwargs)
                result["candidate"][kind]={"node_id":"fake-node",
                   "analysis_id":"fake-tree","reading_level":"advanced"}[kind]
                return result
            with self.subTest(kind=kind):
                result=naturalize(graph,context,node_id=node,provider=candidate,
                                  policy=synthetic_enabled(),cache=BoundedNaturalizerCache())
                self.assertEqual(result["reason_code"],"MODEL_RESPONSE_REJECTED")

    def test_extra_paragraph_and_unexpected_property_rejected(self):
        graph,context,node=target()
        for kind in ("extra","rogue"):
            def candidate(packet,**kwargs):
                result=choose(packet,**kwargs)
                if kind=="extra":
                    result["candidate"]["paragraphs"].append(deepcopy(result["candidate"]["paragraphs"][0]))
                else:result["candidate"]["book_authority"]=True
                return result
            with self.subTest(kind=kind):
                out=naturalize(graph,context,node_id=node,provider=candidate,
                               policy=synthetic_enabled(),cache=BoundedNaturalizerCache())
                self.assertEqual(out["status"],"fallback")

    def test_provider_usage_cost_or_tokens_exceeds_ceiling(self):
        graph,context,node=target()
        for field,value in (("cost_usd",0.02),("output_tokens",999),
                            ("input_tokens",False),("cost_usd",-0.1)):
            def candidate(packet,**kwargs):
                output=choose(packet,**kwargs)
                output["usage"][field]=value
                return output
            with self.subTest(field=field,value=value):
                out=naturalize(graph,context,node_id=node,provider=candidate,
                               policy=synthetic_enabled(),cache=BoundedNaturalizerCache())
                self.assertEqual(out["reason_code"],"MODEL_RESPONSE_REJECTED")

    def test_absent_usage_is_rejected(self):
        graph,context,node=target()
        def bad(packet,**kwargs):
            return {"candidate":choose(packet,**kwargs)["candidate"]}
        out=naturalize(graph,context,node_id=node,provider=bad,
                       policy=synthetic_enabled(),cache=BoundedNaturalizerCache())
        self.assertEqual(out["status"],"fallback")

    def test_provider_exception_falls_back_once_without_user_text_log(self):
        graph,context,node=target()
        calls=[]
        def broken(packet,**kwargs):
            calls.append(1)
            raise RuntimeError("She ate sensitive private words")
        out=naturalize(graph,context,node_id=node,provider=broken,
                       policy=synthetic_enabled(),cache=BoundedNaturalizerCache())
        CHECK.validate(out)
        self.assertEqual(len(calls),1)
        self.assertEqual(out["reason_code"],"MODEL_REQUEST_FAILED")
        self.assertNotIn("sensitive",json.dumps(out))
        self.assertEqual(out["provider_calls"],1)

    def test_slow_response_is_discarded(self):
        graph,context,node=target()
        ticks=[100.0,102.0]
        with patch("xai6_naturalizer.time.monotonic",side_effect=lambda: ticks.pop(0)):
            out=naturalize(graph,context,node_id=node,provider=choose,
                           policy=synthetic_enabled(),cache=BoundedNaturalizerCache())
        self.assertEqual(out["reason_code"],"MODEL_DEADLINE_EXCEEDED")
        self.assertEqual(out["provider_elapsed_ms"],2000)
        self.assertEqual(out["status"],"fallback")

    def test_unchanged_model_text_returns_offline_baseline(self):
        graph,context,node=target()
        def unchanged(packet,**kwargs):
            res=choose(packet,**kwargs)
            for row,p in zip(res["candidate"]["paragraphs"],packet["paragraphs"]):
                row["text"]=p["text"]
            return res
        out=naturalize(graph,context,node_id=node,provider=unchanged,
                       policy=synthetic_enabled(),cache=BoundedNaturalizerCache())
        self.assertEqual(out["reason_code"],"MODEL_UNCHANGED_BASELINE")
        self.assertEqual(out["paragraphs"][0]["text"],context["items"][0]["short"])

    def test_cache_hit_avoids_second_model_call(self):
        graph,context,node=target()
        calls=[]
        def callback(packet,**kwargs):
            calls.append(1);return choose(packet,**kwargs)
        cache=BoundedNaturalizerCache()
        opts={"node_id":node,"policy":synthetic_enabled(),"cache":cache,
              "provider":callback,"variety":"Standard English"}
        first=naturalize(graph,context,**opts)
        second=naturalize(graph,context,**opts)
        self.assertEqual(first["status"],"accepted")
        self.assertEqual(second["reason_code"],"CACHE_HIT")
        self.assertEqual(second["provider_calls"],0)
        self.assertEqual(len(calls),1)
        self.assertEqual(len(cache),1)

    def test_cache_separates_variety_level_registry_and_rule_set(self):
        graph,context,node=target()
        cache=BoundedNaturalizerCache()
        calls=[]
        def callback(packet,**kwargs):
            calls.append(1);return choose(packet,**kwargs)
        common={"node_id":node,"policy":synthetic_enabled(),"cache":cache,"provider":callback}
        for kwargs in [
            {"variety":"American English","reading_level":"plain"},
            {"variety":"British English","reading_level":"plain"},
            {"variety":"British English","reading_level":"advanced"},
            {"variety":"British English","reading_level":"advanced","source_registry_version":"2"},
            {"variety":"British English","reading_level":"advanced","source_registry_version":"2","runtime_rule_set_version":"2"},
        ]:
            result=naturalize(graph,context,**common,**kwargs)
            self.assertEqual(result["status"],"accepted")
            self.assertEqual(result["cache_status"],"miss")
        self.assertEqual(len(calls),5)
        self.assertEqual(len(cache),5)

    def test_cache_size_is_bounded_and_copies_results(self):
        cache=BoundedNaturalizerCache(2)
        cache.put("a",{"paragraphs":[{"text":"first"}]})
        cache.put("b",{"paragraphs":[{"text":"second"}]})
        got=cache.get("a")
        got["paragraphs"][0]["text"]="malicious"
        self.assertEqual(cache.get("a")["paragraphs"][0]["text"],"first")
        cache.put("c",{"paragraphs":[]})
        self.assertIsNone(cache.get("b"))
        self.assertEqual(len(cache),2)
        with self.assertRaises(ValueError): BoundedNaturalizerCache(65)

    def test_input_over_prompt_ceiling_falls_back_without_model_call(self):
        graph,context,node=target()
        policy=synthetic_enabled()
        policy["contract"]["max_prompt_chars"]=10
        calls=[]
        def never(*a,**kw):
            calls.append(1); return choose(*a,**kw)
        out=naturalize(graph,context,node_id=node,provider=never,
                       policy=policy,cache=BoundedNaturalizerCache())
        self.assertEqual(out["reason_code"],"MODEL_BUDGET_EXCEEDED")
        self.assertEqual(calls,[])

    def test_malformed_policy_is_not_a_runtime_promotion(self):
        graph,context,node=target()
        p=synthetic_enabled()
        p["enablement"]["independent_human_blind_comparison"]="yes"
        output=naturalize(graph,context,node_id=node,policy=p,provider=choose)
        self.assertEqual(output["reason_code"],"INVALID_POLICY")
        self.assertFalse(output["model_enabled"])

    def test_forbidden_free_text_in_source_span_never_passes(self):
        graph,context,node=target()
        for issue in ("was", "subject", "<script>alert(1)</script>"):
            def candidate(packet,**kwargs):
                result=choose(packet,**kwargs)
                result["candidate"]["paragraphs"][0]["text"] += " " + issue
                return result
            with self.subTest(issue=issue):
                result=naturalize(graph,context,node_id=node,provider=candidate,
                                  policy=synthetic_enabled(),cache=BoundedNaturalizerCache())
                self.assertEqual(result["status"],"fallback")

    def test_full_source_metadata_forgery_not_promoted_to_book_claim(self):
        t=tree("br-03")
        t["source"].update(review_status="HUMAN_APPROVED",
                           printed_page=999, book="Cambridge")
        graph=build_fact_graph({"status":"normalized","tree":t})
        word=next(n["node_id"] for n in graph["nodes"] if n["kind"]=="word")
        context=compose_explanations(graph,node_id=word)
        result=naturalize(graph,context,node_id=word)
        self.assertEqual(result["status"],"disabled")
        self.assertEqual(result["source_ids"],[])
        self.assertEqual(result["claim_status"],"STRUCTURAL_OBSERVATION_ONLY")

    def test_illegal_untrusted_source_rule_list_rejected_by_canonical_schema(self):
        graph_tree=tree("br-03")
        graph_tree["source"]["source_rule_ids"]=["fake"]
        with self.assertRaises(ValueError):
            build_fact_graph({"status":"normalized","tree":graph_tree})

    def test_shared_explain_evaluate_generator_builder_fallback_parity(self):
        t=tree("br-03")
        graph=build_fact_graph({"status":"normalized","tree":t})
        word=next(n["node_id"] for n in graph["nodes"] if n["kind"]=="word")
        expl=explain_request({"tree":t,"node_id":word})
        evaluated=evaluate_request({"tree":t})
        expected=expl["xai6_naturalization"]
        CHECK.validate(expected)
        self.assertEqual(expected["status"],"disabled")
        self.assertEqual(expected["selected_node_id"],word)
        self.assertEqual(evaluated["xai6_naturalization"],evaluated["explanation_evidence"]["xai6_naturalization"])
        self.assertEqual(evaluated["xai6_naturalization"]["status"],"unavailable")
        self.assertFalse(evaluated["xai6_naturalization"]["whole_sentence_certified"])

    def test_unresolved_request_cannot_invent_naturalization(self):
        response=explain_request({"tree":None})
        self.assertIsNone(response["xai6_naturalization"])
        self.assertIsNone(response["contextual_explanations"])

    def test_different_reading_levels_do_not_relax_proof(self):
        graph,context,node=target()
        for level in ["plain","standard","advanced"]:
            with self.subTest(level=level):
                result=naturalize(graph,context,node_id=node,reading_level=level,
                                  policy=synthetic_enabled(),provider=choose,
                                  cache=BoundedNaturalizerCache())
                CHECK.validate(result)
                self.assertEqual(result["status"],"accepted")
                self.assertEqual(result["reading_level"],level)
        with self.assertRaises(ValueError):
            naturalize(graph,context,node_id=node,reading_level="Taglish")

    def test_no_client_supplied_policy_or_model_provider_route(self):
        t=tree("br-03")
        for field in ("model_enabled","naturalizer_policy","provider","reading_level",
                      "xai6_naturalization"):
            with self.subTest(field=field), self.assertRaises(ValueError):
                explain_request({"tree":t,field:True})
            with self.subTest(field=field), self.assertRaises(ValueError):
                evaluate_request({"tree":t,field:True})


if __name__ == "__main__":
    unittest.main()
