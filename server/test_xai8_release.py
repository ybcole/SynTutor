"""XAI-8 independent evidence, false-positive traps, safety gates and rollout.

These are *engineering* contracts, not an expert-adjudicated grammar benchmark.
Do not fake human accuracy numbers or enable the unreviewed Cambridge rules.
"""
from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

from jsonschema import Draft202012Validator

from xai8_release import (
    ROOT, POLICY_PATH, SCHEMA_PATH, QUALITY_METRICS,
    OptInAggregateTelemetry, evaluate_release, load_policy,
)
from xai4_partial import evaluate_xai4
from xai5_repair import recheck_revisions
from explanations import explain_request
from tree_evaluation import evaluate_request
from test_builder_evaluation import tree
from xai_facts import build_fact_graph
from xai_composer import compose_explanations
from learner_explanations import compose_learner_explanation

PATH=ROOT/"scripts/audit_xai8_release.py"
spec=importlib.util.spec_from_file_location("audit_xai8_release",PATH)
audit=importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class XAI8ReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.probes=audit.validate_probes()
        cls.report=audit.benchmark()
        cls.policy=load_policy()

    def test_policy_and_probes_validate_strict_schema(self):
        for name,data in [("evaluation/xai8_release_policy.schema.json",self.policy),
                          ("evaluation/xai8_safety_probes.schema.json",self.probes)]:
            schema=json.loads((ROOT/name).read_text())
            Draft202012Validator.check_schema(schema)
            self.assertFalse(schema["additionalProperties"])
            Draft202012Validator(schema).validate(data)

    def test_zero_real_human_gold_cases_never_invented(self):
        self.assertEqual(self.probes["independent_expert_case_count"],0)
        self.assertEqual(self.report["independent_expert_cases"],0)
        self.assertEqual(self.policy["expert_gates"]["adjudicated_case_count"],0)
        for metric in QUALITY_METRICS:
            self.assertIsNone(self.report[metric],metric)

    def test_fifty_three_new_unseen_english_probes_twelve_families(self):
        self.assertEqual(self.report["probe_count"],53)
        self.assertEqual(self.report["probe_family_count"],12)
        self.assertEqual(self.report["xai0_text_overlap_count"],0)
        self.assertEqual(self.report["xai0_development_case_count"],116)
        self.assertTrue(all(r["expected_status"]=="NOT_ADJUDICATED"
                            and r["language"]=="en"
                            and r["expected_grammaticality"] is None
                            for r in self.probes["cases"]))

    def test_required_safety_categories_present(self):
        names=set(self.report["probe_family_counts"])
        self.assertEqual(names,{
            "pronouns_and_roles","perfect_and_lexical_have",
            "interacting_errors","temporal_context",
            "attachment_ambiguity","dialect_and_register",
            "quotation_and_attribution","ellipsis_and_fragments",
            "stylistic_and_marked","multiple_sentence_and_failure",
            "minimal_pairs","prompt_and_injection",
        })

    def test_real_dev_corpus_cannot_be_repurposed_as_gold(self):
        bad=deepcopy(self.probes)
        bad["cases"][0]["text"]=json.loads(
            (ROOT/"evaluation/xai0_development_cases.json").read_text()
        )["cases"][0]["text"]
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"tampered.json"
            p.write_text(json.dumps(bad))
            with self.assertRaisesRegex(ValueError,"disjoint"):
                audit.validate_probes(p)

    def test_reject_forged_gold_labels_before_metrics(self):
        bad=deepcopy(self.probes)
        bad["cases"][0]["expected_status"]="GRAMMATICAL"
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"tampered.json"
            p.write_text(json.dumps(bad))
            from jsonschema import ValidationError
            with self.assertRaises(ValidationError): audit.validate_probes(p)

    def test_developer_probe_duplicates_rejected(self):
        bad=deepcopy(self.probes)
        bad["cases"][-1]["text"]=bad["cases"][0]["text"]
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"tampered.json"
            p.write_text(json.dumps(bad))
            with self.assertRaisesRegex(ValueError,"Duplicate"):audit.validate_probes(p)

    def test_source_tree_node_coverage_and_exact_proof_atoms(self):
        self.assertGreaterEqual(self.report["source_tree_nodes"],100)
        self.assertEqual(self.report["source_node_paragraph_coverage"],1.0)
        self.assertEqual(self.report["source_fact_proof_completeness"],1.0)
        self.assertGreater(self.report["source_fact_proof_total"],100)
        self.assertEqual(self.report["source_lesson_tree_count"],10)
        self.assertGreaterEqual(self.report["source_book_tree_count"],10)

    def test_technical_release_checks_pass_but_production_remains_on_hold(self):
        dec=self.report["release"]
        self.assertEqual(dec["technical_acceptance"],"PASS",self.report["evaluation_failures"])
        self.assertEqual(dec["expert_quality_acceptance"],"NOT_MEASURED")
        self.assertEqual(dec["release_decision"],"HOLD")
        self.assertFalse(dec["new_diagnostic_rollout_permitted"])
        self.assertEqual(dec["live_canary_percent"],0)
        self.assertIn("INDEPENDENT_EXPERT_AND_LEARNER_QUALITY_REVIEW_MISSING",dec["reasons"])

    def test_zero_unsupported_book_claim_and_no_grammar_pass(self):
        self.assertEqual(self.report["unsupported_book_verified_claim_count"],0)
        self.assertEqual(self.report["probe_verified_grammar_finding_count"],0)
        self.assertEqual(self.report["whole_sentence_certifications"],0)
        self.assertEqual(self.report["evaluation_failure_count"],0)
        self.assertEqual(self.report["runtime_enabled_cambridge_rule_count"],0)

    def test_zero_model_cost_and_model_production_off(self):
        self.assertGreater(self.report["model_request_checks"],0)
        self.assertEqual(self.report["model_provider_calls"],0)
        self.assertFalse(self.report["production_ai_model_enabled"])
        self.assertFalse(self.policy["new_diagnostic_rollout_enabled"])
        self.assertTrue(self.policy["rollback"]["kill_switch"])
        self.assertEqual(self.policy["rollback"]["canary_percent"],0)

    def test_latency_population_and_no_semantic_inference(self):
        values=self.report["timings_ms"]
        self.assertGreaterEqual(values["probe_evaluation_p95"],0)
        self.assertGreaterEqual(values["node_composition_p95"],0)
        self.assertIsNone(self.report["learner_comprehension_gain"])
        self.assertIsNone(self.report["blind_readability_preference"])
        self.assertIsNone(self.report["repair_validity"])

    def test_private_sentence_not_in_release_report(self):
        text=json.dumps(self.report)
        for row in self.probes["cases"]:
            self.assertNotIn(row["text"],text)
        self.assertEqual(self.report["raw_text_telemetry_events"],0)

    def test_not_even_an_expert_claim_can_bypass_kill_switch(self):
        clone=deepcopy(self.report)
        clone["independent_expert_cases"]=300
        for metric in QUALITY_METRICS:
            clone[metric]=0.99
        decision=evaluate_release(clone)
        self.assertEqual(decision["release_decision"],"HOLD")
        self.assertFalse(decision["new_diagnostic_rollout_permitted"])

    def test_evaluation_report_spoofed_cannot_enable_production(self):
        clone=deepcopy(self.report)
        clone["unsupported_book_verified_claim_count"]=1
        dec=evaluate_release(clone)
        self.assertEqual(dec["technical_acceptance"],"FAIL")
        self.assertIn("UNSUPPORTED_BOOK_CLAIMS",dec["reasons"])

    def test_omitted_or_corrupted_report_fails_closed(self):
        with self.assertRaises(ValueError):evaluate_release(None)
        clone=deepcopy(self.report)
        clone["schema_version"]="xai8-spoofed"
        self.assertEqual(evaluate_release(clone)["release_decision"],"HOLD")
        self.assertEqual(evaluate_release(clone)["technical_acceptance"],"FAIL")

    def test_missing_grounding_witness_disables_technical_pass(self):
        for key in ["source_fact_proof_completeness","source_node_paragraph_coverage"]:
            bad=deepcopy(self.report)
            bad[key]=0.5
            self.assertEqual(evaluate_release(bad)["technical_acceptance"],"FAIL")

    def test_absent_real_review_and_fake_reviewer_flags_not_approved(self):
        policy=deepcopy(self.policy)
        policy["expert_gates"]["reviewers"]=["SYNTHETIC-ONLY","ANOTHER-FAKE"]
        policy["expert_gates"]["adjudicated_case_count"]=999
        policy["expert_gates"]["independent_linguist_count"]=2
        policy["expert_gates"]["quality_metrics_available"]=True
        dec=evaluate_release(self.report,policy)
        self.assertEqual(dec["release_decision"],"HOLD")

    def test_telemetry_defaults_to_opt_out_and_storage_empty(self):
        telemetry=OptInAggregateTelemetry()
        self.assertFalse(telemetry.record(opted_in=False,mode="generator",
                                         outcome="observed",latency_ms=42))
        self.assertFalse(telemetry.record(opted_in=True,mode="builder",
                                         outcome="observed",latency_ms=42))
        self.assertEqual(telemetry.snapshot()["status"],"suppressed")
        self.assertIsNone(telemetry.snapshot()["count"])

    def test_opt_in_telemetry_only_discloses_anonymous_minimum_batch(self):
        policy=deepcopy(self.policy)
        policy["telemetry"]["enabled"]=True
        telemetry=OptInAggregateTelemetry(policy)
        for i in range(19):
            self.assertTrue(telemetry.record(opted_in=True,mode="quizzes",
                                             outcome="observed",latency_ms=200))
        self.assertEqual(telemetry.snapshot()["status"],"suppressed")
        self.assertTrue(telemetry.record(opted_in=True,mode="quizzes",
                                         outcome="observed",latency_ms=2000))
        snapshot=telemetry.snapshot()
        self.assertEqual(snapshot["status"],"aggregate_only")
        self.assertEqual(snapshot["count"],20)
        self.assertTrue(all(set(r)=={"mode","outcome","latency_bucket","count"}
                            for r in snapshot["counts"]))
        self.assertNotIn("sentence",json.dumps(snapshot))
        self.assertNotIn("user",json.dumps(snapshot))

    def test_telemetry_rejects_unstructured_identity_or_user_text(self):
        policy=deepcopy(self.policy)
        policy["telemetry"]["enabled"]=True
        telemetry=OptInAggregateTelemetry(policy)
        for kwargs in ({"text":"my private sentence"},
                       {"user_id":"secret"},
                       {"ip_address":"127.0.0.1"}):
            with self.subTest(kwargs=kwargs),self.assertRaises(TypeError):
                telemetry.record(opted_in=True,mode="builder",
                                 outcome="observed",latency_ms=30,**kwargs)
        self.assertFalse(telemetry.record(opted_in=True,mode="evil",
                                          outcome="observed",latency_ms=30))
        self.assertFalse(telemetry.record(opted_in=True,mode="builder",
                                          outcome="observed",latency_ms=-1))

    def test_quoted_bad_grammar_still_not_a_runtime_verified_error(self):
        for sentence in [
            '"She can goes" is a quotation.',
            'She had breakfast.',
            "We've already discussed it yesterday.",
            'They ain\\'t coming today.',
            'The boy said "I has went home".',
        ]:
            with self.subTest(text=sentence):
                verdict=evaluate_xai4(sentence)
                self.assertEqual(verdict["findings"],[])
                self.assertEqual(verdict["enabled_rule_ids"],[])
                self.assertFalse(verdict["global_verdict"]["whole_sentence_certified"])

    def test_multi_error_unreviewed_raw_signals_not_real_diagnoses(self):
        for sentence in [
            "She have went to the store yesterday.",
            "The boys is carrying a boxes.",
            "They can has went already.",
        ]:
            with self.subTest(text=sentence):
                result=evaluate_xai4(sentence)
                self.assertEqual(result["findings"],[])
                self.assertNotEqual(result["status"],"partially_evaluated")
                self.assertFalse(result["global_verdict"]["whole_sentence_certified"])

    def test_generator_builder_source_and_learner_parity_unmodified(self):
        t=tree("br-04")
        e=explain_request({"tree":t})
        b=evaluate_request({"tree":t})
        self.assertEqual(b["explanation_evidence"],e)
        self.assertEqual(b["learner_explanation"],e["learner_explanation"])
        self.assertEqual(e["learner_explanation"]["source_claim_ids"],[])
        self.assertEqual(e["xai4_partial_evaluation"]["findings"],[])
        self.assertFalse(e["learner_explanation"]["whole_sentence_certified"])

    def test_minimal_pair_does_not_return_stale_paragraph(self):
        a=tree("br-03")
        b=tree("br-04")
        ea=explain_request({"tree":a})["learner_explanation"]
        eb=explain_request({"tree":b})["learner_explanation"]
        self.assertNotEqual(ea["analysis_id"],eb["analysis_id"])
        self.assertNotEqual(ea["text"],eb["text"])

    def test_revision_recheck_never_certifies_meaning_or_whole_sentence(self):
        result=recheck_revisions({"text":"She had went home.",
             "candidates":[{"text":"She had gone home."}]},
            analyzer=lambda text:{"status":"unresolved","tree":None,"sentence":text})
        self.assertEqual(result["original_finding_ids"],[])
        self.assertFalse(result["whole_sentence_certified"])
        self.assertFalse(result["revisions"][0]["whole_sentence_certified"])
        self.assertEqual(result["revisions"][0]["meaning_status"],"not_assessed")

    def test_both_rollback_and_opt_in_collection_are_locked_off(self):
        self.assertEqual(self.policy["stage"],"HOLD_INTERNAL_ONLY")
        self.assertTrue(self.policy["rollback"]["kill_switch"])
        self.assertEqual(self.policy["rollback"]["canary_percent"],0)
        self.assertFalse(self.policy["telemetry"]["enabled"])
        self.assertFalse(self.policy["telemetry"]["raw_sentence_collection_allowed"])
        self.assertTrue(self.policy["telemetry"]["explicit_opt_in_required"])


if __name__=="__main__":
    unittest.main()
