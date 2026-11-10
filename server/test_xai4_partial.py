"""XAI-4 candidate-vs-approved checks; synthetic approval fixture is NOT production.
English-only contrastive positives, negative controls, exceptions, ambiguity,
simultaneous issues, source-gate forgery, unresolved tree, and API parity.
"""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from jsonschema import Draft202012Validator

from xai4_partial import (ROOT, tokenize, inspect, evaluate_xai4,
                          load_manifest, eligible, overlap_groups)
from explanations import explain_request
from tree_evaluation import evaluate_request
from test_builder_evaluation import tree

CANDIDATES, AUDIT = load_manifest()
SCHEMA = json.loads((ROOT / "grammar/xai4_candidates.schema.json").read_text())
FAMILIES = {r["family"]: r for r in CANDIDATES["rules"]}


def signal(family, sentence):
    return [x["signal"] for x in inspect(family, tokenize(sentence))]


class XAI4PartialTests(unittest.TestCase):
    def test_contract_catalog_is_strict_english_and_all_disabled(self):
        Draft202012Validator.check_schema(SCHEMA)
        Draft202012Validator(SCHEMA).validate(CANDIDATES)
        self.assertEqual(len(FAMILIES), 4)
        self.assertEqual(CANDIDATES["runtime_enabled_rule_ids"], [])
        self.assertTrue(all(x["runtime_status"] == "disabled" for x in CANDIDATES["rules"]))
        self.assertTrue(all(x["review"]["independent_human_review"] is False for x in CANDIDATES["rules"]))
        self.assertTrue(all(not eligible(x, AUDIT, CANDIDATES) for x in CANDIDATES["rules"]))

    def test_perfect_had_forms_and_lexical_exception(self):
        family = "perfect_auxiliary_participle"
        for good in ["She had eaten.", "She had gone home.", "They have walked home.", "She has read it."]:
            with self.subTest(sentence=good):
                self.assertIn("SATISFIED", signal(family, good))
        for bad in ["She had went home.", "She has ate.", "They have saw it."]:
            with self.subTest(sentence=bad):
                self.assertIn("VIOLATED", signal(family, bad))
        for lexical in ["She had breakfast.", "I have a dog.", "The students have books."]:
            self.assertEqual(signal(family, lexical), [])
        self.assertEqual(signal(family, "She'd gone home."), ["AMBIGUOUS"])

    def test_modal_plain_verb_vs_nonmodal_can(self):
        family = "modal_plain_form"
        self.assertEqual(signal(family, "She can go."), ["SATISFIED"])
        self.assertEqual(signal(family, "She can goes."), ["VIOLATED"])
        self.assertEqual(signal(family, "They must has gone."), ["VIOLATED"])
        self.assertEqual(signal(family, "She might have gone."), ["SATISFIED"])
        self.assertEqual(signal(family, "A tin can fell."), [])
        self.assertEqual(signal(family, "May I ask a question?"), [])

    def test_progressive_vs_copular_passive_exception(self):
        family = "progressive_auxiliary_gerund_participle"
        self.assertEqual(signal(family, "She is singing."), ["SATISFIED"])
        self.assertEqual(signal(family, "She is sing."), ["VIOLATED"])
        self.assertEqual(signal(family, "She is happy."), [])
        self.assertEqual(signal(family, "The door is closed."), ["AMBIGUOUS"])
        self.assertEqual(signal(family, "She is being careful."), ["SATISFIED"])

    def test_temporal_context_always_ambiguous(self):
        family = "present_perfect_time_adjunct"
        self.assertEqual(signal(family, "We've already discussed it yesterday."), ["AMBIGUOUS"])
        self.assertEqual(signal(family, "She has eaten today."), [])
        self.assertEqual(signal(family, "She has gone yesterday."), ["AMBIGUOUS"])

    def test_all_unapproved_candidate_signals_are_sealed_from_public(self):
        for text in ["She had went home.", "She has eaten.", "She can goes.",
                     "She is sing.", "She can has went home."]:
            result = evaluate_xai4(text)
            self.assertEqual(result["enabled_rule_ids"], [])
            self.assertEqual(result["findings"], [])
            self.assertEqual(result["dependencies"], [])
            self.assertEqual(result["groups"], [])
            self.assertFalse(result["global_verdict"]["whole_sentence_certified"])
            self.assertEqual(result["global_verdict"]["status"], "NOT_EVALUATED")
            self.assertNotIn("VIOLATED", {x["status"] for x in result["evaluations"]})
            self.assertNotIn("SATISFIED", {x["status"] for x in result["evaluations"]})
            self.assertNotIn('"signal"', json.dumps(result))
            self.assertNotIn("wrong", json.dumps(result).lower())

    def test_can_evaluate_raw_sentence_without_valid_br_tree(self):
        result = evaluate_xai4("She had went.", analysis_status="unresolved")
        self.assertEqual(result["analysis_status"], "unresolved")
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["token_index_basis"], "XAI4_RAW_SOURCE_TOKENS_NOT_BR_NODES")
        match = next(x for x in result["evaluations"] if x["rule_id"] == "CGEL4-PERF-COMPLEMENT")
        self.assertEqual(match["status"], "BLOCKED")
        self.assertEqual(match["evidence"][0]["char_span"], [4, 12])

    def test_dialect_quotes_and_experiential_excepted(self):
        quoted = evaluate_xai4('Someone said "She had went home."')
        self.assertEqual(quoted["findings"], [])
        self.assertTrue(any(x["status"] == "AMBIGUOUS" for x in quoted["evaluations"]))
        special = evaluate_xai4("We've already discussed it yesterday.")
        self.assertTrue(any(x["rule_id"] == "CGEL4-PERF-TIME-CONTEXT" and
                            x["status"] == "AMBIGUOUS" for x in special["evaluations"]))
        self.assertEqual(special["findings"], [])

    def test_production_source_audit_disallows_runtime_flip(self):
        rule = deepcopy(FAMILIES["perfect_auxiliary_participle"])
        manifest = deepcopy(CANDIDATES)
        manifest["runtime_enabled_rule_ids"] = [rule["id"]]
        rule["runtime_status"] = "enabled"
        rule["may_issue_verified_error"] = True
        rule["review"].update(status="HUMAN_APPROVED",independent_human_review=True,
               reviewed_by="synthetic-only",reviewed_on="2026-11-10",
               exception_review_completed=True,held_out_adjudication_completed=True,
               test_status="passed")
        self.assertFalse(eligible(rule,AUDIT,manifest))  # source claims still unapproved

    def test_approved_synthetic_fixture_can_group_overlapping_violations(self):
        manifest, audit = deepcopy(CANDIDATES), deepcopy(AUDIT)
        modal = next(r for r in manifest["rules"] if r["family"] == "modal_plain_form")
        modal["crosswalk_id"] = "TEST-CW-MODAL"
        modal["source_claim_ids"].append("BR3-AUX-HEADS-VP")
        audit["crosswalks"].append(dict(id="TEST-CW-MODAL",
             cgel_claim_id="CGEL-MODAL-PLAIN", br_claim_id="BR3-AUX-HEADS-VP",
             review_status="independently_approved", relation="terminology_differs",
             may_change_br_tree_labels=False))
        for rule in manifest["rules"]:
            if rule["family"] not in {"modal_plain_form", "perfect_auxiliary_participle"}:
                continue
            manifest["runtime_enabled_rule_ids"].append(rule["id"])
            rule["runtime_status"] = "enabled"
            rule["may_issue_verified_error"] = True
            rule["review"].update(status="HUMAN_APPROVED",independent_human_review=True,
                 reviewed_by="synthetic-unit-test",reviewed_on="2026-11-10",
                 exception_review_completed=True,held_out_adjudication_completed=True,test_status="passed")
        for claim in audit["claims"]:
            if claim["id"] in {s for r in manifest["rules"] if r["id"] in manifest["runtime_enabled_rule_ids"]
                               for s in r["source_claim_ids"]}:
                claim["review"].update(independent_human_review=True,approval="human_approved")
                claim["runtime"].update(constraint_enabled=True,may_issue_grammatical_verdict=True)
        for cw in audit["crosswalks"]:
            if cw["id"] == "CW-PERF-PARTICIPLE":
                cw["review_status"] = "independently_approved"
        # This explicit fixture is never copied into grammar/ production files.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "grammar/xai_pre").mkdir(parents=True)
            (root / "grammar/xai4_candidates.json").write_text(json.dumps(manifest))
            (root / "grammar/xai_pre/source_audit.json").write_text(json.dumps(audit))
            result = evaluate_xai4("She can has went home.", root=root)
        self.assertEqual(len(result["findings"]), 2)
        self.assertEqual({x["rule_id"] for x in result["findings"]},
                         {"CGEL4-PERF-COMPLEMENT", "CGEL4-MODAL-PLAIN"})
        self.assertEqual(len(result["dependencies"]), 1)
        self.assertEqual(result["groups"][0]["coupling"], "interacting")
        self.assertEqual(result["global_verdict"]["status"], "PARTIALLY_EVALUATED")
        self.assertFalse(result["global_verdict"]["whole_sentence_certified"])

    def test_token_offsets_and_contraction_are_from_original(self):
        text = "  We've  already discussed it yesterday."
        tokens = tokenize(text)
        for item in tokens:
            self.assertEqual(text[slice(*item["char_span"])], item["text"])
        match = next(x for x in inspect("present_perfect_time_adjunct",tokens))
        self.assertEqual(text[slice(*match["char_span"])].strip(),
                         "We've  already discussed it yesterday")

    def test_duplicate_ids_and_invalid_catalog_fail_closed(self):
        bad = deepcopy(CANDIDATES)
        bad["rules"].append(deepcopy(bad["rules"][0]))
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root/"grammar/xai_pre").mkdir(parents=True)
            (root/"grammar/xai4_candidates.json").write_text(json.dumps(bad))
            (root/"grammar/xai_pre/source_audit.json").write_text(json.dumps(AUDIT))
            result = evaluate_xai4("She had went home.",root=root)
        self.assertEqual(result["status"], "not_evaluated")
        self.assertEqual(result["findings"], [])
        self.assertEqual(result["diagnostics"][0]["code"], "SOURCE_REGISTRY_UNAVAILABLE")

    def test_client_cannot_supply_rule_or_reviewer_authority(self):
        t = tree("br-02")
        for payload in [
                {"tree":t,"runtime_enabled_rule_ids":["CGEL4-PERF-COMPLEMENT"]},
                {"tree":t,"xai4_rules":CANDIDATES["rules"]},
                {"tree":t,"independent_human_review":True}]:
            with self.assertRaises(ValueError):
                explain_request(payload)
            with self.assertRaises(ValueError):
                evaluate_request(payload)

    def test_shared_builder_and_explain_sidecars(self):
        t = tree("br-02")
        a = explain_request({"tree":t})
        b = evaluate_request({"tree":t})
        self.assertEqual(a["xai4_partial_evaluation"], b["xai4_partial_evaluation"])
        self.assertEqual(a["xai4_partial_evaluation"],b["explanation_evidence"]["xai4_partial_evaluation"])
        self.assertEqual(b["grammaticality"]["status"], "unresolved")
        self.assertEqual(a["channels"]["remediation"], [])
        self.assertEqual(b["xai4_partial_evaluation"]["enabled_rule_ids"], [])

    def test_unsupported_empty_or_invalid_input_is_not_a_pass(self):
        self.assertEqual(evaluate_xai4(None)["status"], "not_evaluated")
        self.assertEqual(evaluate_xai4("")["findings"], [])
        with self.assertRaises(ValueError):
            evaluate_xai4("word " * 5000)
        with self.assertRaises(ValueError):
            evaluate_xai4("She had gone.", variety=" ")
        self.assertEqual(inspect("invented_family",tokenize("She had went")), [])

    def test_independent_groups_dont_misstate_causality(self):
        findings=[
         {"id":"a","affected_token_ids":["t1","t2"]},
         {"id":"b","affected_token_ids":["t4","t5"]},
         {"id":"c","affected_token_ids":["t2","t3"]}]
        deps, groups=overlap_groups(findings)
        self.assertEqual(deps,[{"from":"a","to":"c","kind":"OVERLAPS_SPAN"}])
        self.assertEqual([x["coupling"] for x in groups],["interacting","independent"])


if __name__ == "__main__":
    unittest.main()
