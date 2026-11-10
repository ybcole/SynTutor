"""XAI-5 acceptance: immutable revision trees, source gates and interacting errors.

All tests use English. The synthetic approval fixture is local to this unit
test and DOES NOT constitute independent review of Cambridge grammar claims.
"""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from jsonschema import Draft202012Validator

from xai4_partial import ROOT, load_manifest, evaluate_xai4, tokenize
from xai5_repair import (VERSION, _digest, _token_alignment, _attach_token,
                         localize_xai4, recheck_revisions, repair_request)
from xai_facts import build_fact_graph
from explanations import explain_request
from tree_evaluation import evaluate_request
from test_builder_evaluation import tree
from test_cambridge_evaluator import CambridgeEvaluatorTests

REPAIR_SCHEMA = json.loads((ROOT / "grammar/xai5_repair.schema.json").read_text())
LOCATION_SCHEMA = json.loads((ROOT / "grammar/xai5_localization.schema.json").read_text())
VALIDATE_REPAIR = Draft202012Validator(REPAIR_SCHEMA)
VALIDATE_LOCATION = Draft202012Validator(LOCATION_SCHEMA)


def unresolved(text):
    return {"status": "unresolved", "tree": None,
            "sentence": text, "reparse_status": "unavailable_or_failed"}


def synthetic_source(root):
    """A fabricated approved-rule registry for detector-lineage *tests only*."""
    catalog, audit = load_manifest()
    catalog, audit = deepcopy(catalog), deepcopy(audit)
    modal = next(r for r in catalog["rules"] if r["family"] == "modal_plain_form")
    modal["crosswalk_id"] = "TEST-CW-MODAL"
    modal["source_claim_ids"].append("BR3-AUX-HEADS-VP")
    audit["crosswalks"].append({
        "id": "TEST-CW-MODAL", "cgel_claim_id": "CGEL-MODAL-PLAIN",
        "br_claim_id": "BR3-AUX-HEADS-VP",
        "review_status": "independently_approved", "relation": "terminology_differs",
        "may_change_br_tree_labels": False,
    })
    for rule in catalog["rules"]:
        if rule["family"] not in {"modal_plain_form", "perfect_auxiliary_participle"}:
            continue
        catalog["runtime_enabled_rule_ids"].append(rule["id"])
        rule["runtime_status"] = "enabled"
        rule["may_issue_verified_error"] = True
        rule["review"].update({
            "status": "HUMAN_APPROVED", "independent_human_review": True,
            "reviewed_by": "SYNTHETIC-TEST-ONLY", "reviewed_on": "2026-11-10",
            "exception_review_completed": True,
            "held_out_adjudication_completed": True,
            "test_status": "passed", "approved_varieties": ["Standard English"],
        })
    affected = set()
    for rule in catalog["rules"]:
        if rule["id"] in catalog["runtime_enabled_rule_ids"]:
            affected.update(rule["source_claim_ids"])
    for claim in audit["claims"]:
        if claim["id"] in affected:
            claim["review"].update(approval="human_approved", independent_human_review=True)
            claim["runtime"].update(constraint_enabled=True,
                                     may_issue_grammatical_verdict=True)
    for crosswalk in audit["crosswalks"]:
        if crosswalk["id"] == "CW-PERF-PARTICIPLE":
            crosswalk["review_status"] = "independently_approved"
    (root / "grammar/xai_pre").mkdir(parents=True)
    (root / "grammar/xai4_candidates.json").write_text(json.dumps(catalog))
    (root / "grammar/xai_pre/source_audit.json").write_text(json.dumps(audit))


class XAI5RepairTests(unittest.TestCase):
    def test_repair_and_localization_json_schemas_are_valid(self):
        Draft202012Validator.check_schema(REPAIR_SCHEMA)
        Draft202012Validator.check_schema(LOCATION_SCHEMA)
        self.assertFalse(REPAIR_SCHEMA["additionalProperties"])
        self.assertFalse(LOCATION_SCHEMA["additionalProperties"])

    def test_production_no_approved_finding_and_no_auto_fix(self):
        original = "She had went home."
        xai = evaluate_xai4(original)
        locations = localize_xai4(xai, analysis=unresolved(original), sentence=original)
        VALIDATE_LOCATION.validate(locations)
        self.assertEqual(locations["diagnoses"], [])
        self.assertEqual(locations["auto_repair_suggestions"], [])
        self.assertEqual(locations["tree_status"], "unavailable")
        self.assertEqual(locations["enabled_rule_ids"], [])
        self.assertFalse(locations["whole_sentence_certified"])
        self.assertTrue(any(o["status"] == "BLOCKED" for o in locations["observations"]))
        self.assertTrue(all(o["authority"] == "UNAPPROVED_CANDIDATE"
                            for o in locations["observations"]))

    def test_production_manual_revision_does_not_claim_verified_repair(self):
        original = "She had went home."
        revised = "She had gone home."
        session = recheck_revisions(
            {"text": original, "candidates": [{"text": revised}]}, analyzer=unresolved)
        VALIDATE_REPAIR.validate(session)
        self.assertEqual(session["original"]["text"], original)
        self.assertEqual(session["revisions"][0]["snapshot"]["text"], revised)
        self.assertEqual(session["original_finding_ids"], [])
        self.assertEqual(session["revisions"][0]["original_finding_lineage"], [])
        self.assertEqual(session["auto_suggestions"], [])
        self.assertEqual(session["diagnostic_rule_count"], 0)
        self.assertFalse(session["whole_sentence_certified"])
        self.assertEqual(session["global_verdict"], "NOT_CERTIFIED")

    def test_exact_span_and_proof_for_opaque_tree(self):
        t = CambridgeEvaluatorTests.analysis("She had went home")
        xai = evaluate_xai4("She had went home")
        locations = localize_xai4(xai, analysis=t, sentence="She had went home")
        VALIDATE_LOCATION.validate(locations)
        self.assertEqual(locations["tree_status"], "observed")
        hit = next(o for o in locations["observations"]
                   if o["rule_id"] == "CGEL4-PERF-COMPLEMENT")
        self.assertEqual(hit["governor_text"], "had")
        self.assertEqual(hit["target_text"], "went")
        self.assertEqual(hit["governor_location"]["status"], "opaque_triangle")
        self.assertEqual(hit["target_location"]["status"], "opaque_triangle")
        self.assertEqual(hit["governor_location"]["node_id"], "vp")
        self.assertTrue(hit["target_location"]["proof_atom_ids"])
        self.assertEqual(hit["tree_relationship_status"],
                         "position_only_no_licensed_function")
        self.assertEqual(locations["diagnoses"], [])

    def test_actual_word_nodes_preferred_over_covering_phrase(self):
        t = tree("br-03")
        graph = build_fact_graph({"status": "normalized", "tree": t})
        original = t["sentence"]
        word = next(token for token in tokenize(original) if token["text"] == "cheerful")
        localized = _attach_token(graph, word)
        self.assertEqual(localized["status"], "exact_word")
        self.assertTrue(localized["ancestor_node_ids"])
        self.assertTrue(localized["proof_atom_ids"])
        self.assertIn(localized["node_id"], {n["node_id"] for n in graph["nodes"]
                                           if n["kind"] == "word"})

    def test_mismatched_tree_text_does_not_invent_node_mapping(self):
        t = tree("br-02")
        original = "She had went home"
        out = localize_xai4(evaluate_xai4(original),
                            analysis={"status": "normalized", "tree": t},
                            sentence=original)
        self.assertEqual(out["tree_status"], "unavailable")
        self.assertTrue(all(o["target_location"]["node_id"] is None
                            for o in out["observations"]))

    def test_repeated_words_token_ids_remain_distinct(self):
        text = "She had went and had went."
        xai = evaluate_xai4(text)
        loc = localize_xai4(xai, sentence=text)
        ids = [o["target_token_id"] for o in loc["observations"]
               if o["rule_id"] == "CGEL4-PERF-COMPLEMENT"]
        self.assertEqual(len(ids), 2)
        self.assertEqual(len(set(ids)), 2)
        self.assertEqual(loc["original_hash"], _digest(text))

    def test_token_replacement_alignment_is_source_anchored(self):
        original = "She had went home."
        revised = "She had gone home."
        edits, mapping, formatting = _token_alignment(original, revised)
        self.assertEqual(len(edits), 1)
        self.assertEqual(edits[0]["original_char_span"], [8,12])
        self.assertEqual(edits[0]["original_text"], "went")
        self.assertEqual(edits[0]["replacement_text"], "gone")
        self.assertEqual(edits[0]["original_token_ids"], ["t2"])
        self.assertEqual(mapping["t0"], "t0")
        self.assertFalse(formatting)

    def test_original_source_not_mutated_across_alternatives(self):
        payload = {"text": "She had went.", "candidates": [
            {"text": "She had gone."}, {"text": "She went."},
            {"text": "She had eaten."}]}
        saved = deepcopy(payload)
        session = recheck_revisions(payload, analyzer=unresolved)
        VALIDATE_REPAIR.validate(session)
        self.assertEqual(payload, saved)
        self.assertEqual(session["original"]["text"], saved["text"])
        self.assertEqual(len(session["revisions"]), 3)
        self.assertEqual([r["parent_version_id"] for r in session["revisions"]],
                         ["u0","u0","u0"])
        self.assertEqual(len({r["snapshot"]["text_hash"] for r in session["revisions"]}),3)

    def test_staged_revisions_reference_their_actual_parents(self):
        payload = {"text":"She had went home.", "candidates":[
            {"text":"She has went home."},
            {"text":"She has gone home.","parent_version_id":"v1"}]}
        session = recheck_revisions(payload,analyzer=unresolved)
        self.assertEqual(session["revisions"][1]["parent_version_id"],"v1")
        self.assertEqual(session["revisions"][1]["step_edits"][0]["original_text"],"went")
        self.assertEqual(session["revisions"][1]["edits_from_original"][0]["original_text"],"had")
        self.assertEqual(session["revisions"][1]["edits_from_original"][1]["original_text"],"went")

    def test_every_revision_reparsed_not_reused(self):
        visited = []
        def parser(text):
            visited.append(text)
            return unresolved(text)
        data = recheck_revisions({"text":"She had went.", "candidates":[
            {"text":"She had gone."},
            {"text":"She ate."},
            {"text":"She had eaten."}]},analyzer=parser)
        self.assertEqual(visited, ["She had went.","She had gone.","She ate.","She had eaten."])
        self.assertTrue(all(x["snapshot"]["reparse_status"] == "unavailable_or_failed"
                            for x in data["revisions"]))

    def test_parser_exception_is_explicitly_unresolved(self):
        def broken(_):
            raise RuntimeError("parser unavailable")
        result = recheck_revisions({"text":"She had went.",
                                   "candidates":[{"text":"She had gone."}]},
                                  analyzer=broken)
        VALIDATE_REPAIR.validate(result)
        self.assertEqual(result["original"]["reparse_status"],"unavailable_or_failed")
        self.assertEqual(result["revisions"][0]["snapshot"]["tree_id"],None)
        self.assertFalse(result["whole_sentence_certified"])

    def test_no_source_approval_can_be_sent_via_request(self):
        original = {"text":"She had went.","candidates":[],
                    "runtime_enabled_rule_ids":["CGEL4-PERF-COMPLEMENT"]}
        with self.assertRaises(ValueError):
            repair_request(original)
        for key in ("source_claim_ids","approved","registry","analyzer","root"):
            with self.assertRaises(ValueError,key):
                repair_request({"text":"She had went.",key:True})

    def test_invalid_revision_and_forward_parent_fail_closed(self):
        base={"text":"She had went."}
        cases=[
            {"candidates":[{"text":"She had went."}]},
            {"candidates":[{"text":" "}]},
            {"candidates":[{"text":"She had gone.","parent_version_id":"v1"}]},
            {"candidates":[{"text":"She had gone.","parent_version_id":"v2"}]},
            {"candidates":[{"text":"She had gone."}]*5},
            {"candidates":"She had gone."},
            {"chapter":True},
            {"variety":""},
            {"candidates":[{"text":"She had gone.","source_ids":["fake"]}]},
        ]
        for extra in cases:
            with self.subTest(extra=extra), self.assertRaises(ValueError):
                recheck_revisions({**base, **extra},analyzer=unresolved)

    def test_source_whitespace_only_revision_is_never_grammar_pass(self):
        data=recheck_revisions({"text":"She had gone.", "candidates":[
            {"text":"She  had gone."}]},analyzer=unresolved)
        line=data["revisions"][0]
        self.assertTrue(line["formatting_only_change"])
        self.assertEqual(line["edits_from_original"], [])
        self.assertEqual(line["original_finding_lineage"], [])
        self.assertFalse(line["whole_sentence_certified"])

    def test_nonword_contraction_punctuation_and_offsets_survive(self):
        original="We've already discussed it yesterday."
        revision="We've already discussed it today."
        result=recheck_revisions({"text":original,"candidates":[{"text":revision}]},
                                 analyzer=unresolved)
        VALIDATE_REPAIR.validate(result)
        old=result["original"]["tokens"]
        self.assertEqual(old[0]["text"],"We've")
        self.assertEqual(result["revisions"][0]["edits_from_original"][0]["original_text"],"yesterday")
        for token in old:
            a,b=token["char_span"]
            self.assertEqual(original[a:b],token["text"])
        self.assertEqual(result["diagnostic_rule_count"],0)

    def test_had_breakfast_is_neither_accused_nor_corrected(self):
        data=recheck_revisions({"text":"She had breakfast.","candidates":[
            {"text":"She ate breakfast."}]},analyzer=unresolved)
        self.assertEqual(data["original_localization"]["diagnoses"],[])
        self.assertEqual(data["original_finding_ids"],[])
        self.assertEqual(data["auto_suggestions"],[])

    def test_synthetic_approved_two_errors_staged_recheck(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            synthetic_source(root)
            session=recheck_revisions({"text":"She can has went home.",
                    "variety":"Standard English",
                    "candidates":[
                        {"text":"She can have went home."},
                        {"text":"She can have gone home.","parent_version_id":"v1"}]},
                    analyzer=unresolved,root=root)
        VALIDATE_REPAIR.validate(session)
        self.assertEqual(len(session["original_finding_ids"]),2)
        self.assertEqual(session["original_localization"]["groups"][0]["coupling"],"interacting")
        first=session["revisions"][0]
        second=session["revisions"][1]
        out1={x["rule_id"]:x["outcome"] for x in first["original_finding_lineage"]}
        out2={x["rule_id"]:x["outcome"] for x in second["original_finding_lineage"]}
        self.assertEqual(out1["CGEL4-MODAL-PLAIN"],"resolved_by_satisfaction")
        self.assertEqual(out1["CGEL4-PERF-COMPLEMENT"],"persists")
        self.assertEqual(out2["CGEL4-MODAL-PLAIN"],"resolved_by_satisfaction")
        self.assertEqual(out2["CGEL4-PERF-COMPLEMENT"],"resolved_by_satisfaction")
        self.assertEqual(second["parent_finding_lineage"][0]["original_finding_id"],"f1")
        self.assertTrue(all(not c["whole_sentence_certified"] for c in session["revisions"]))

    def test_synthetic_no_applicability_is_not_satisfaction(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);synthetic_source(root)
            result=recheck_revisions({"text":"She had went.",
                     "variety":"Standard English",
                     "candidates":[{"text":"She had breakfast."}]},
                     analyzer=unresolved,root=root)
        self.assertEqual(result["revisions"][0]["original_finding_lineage"][0]["outcome"],
                         "no_longer_applicable_after_rewrite")
        self.assertFalse(result["whole_sentence_certified"])

    def test_synthetic_new_finding_origin_unproven_not_fabricated(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);synthetic_source(root)
            result=recheck_revisions({"text":"She can have gone.",
                     "variety":"Standard English",
                     "candidates":[{"text":"She can has gone."}]},
                     analyzer=unresolved,root=root)
        fresh=result["revisions"][0]["new_findings"]
        self.assertTrue(fresh)
        self.assertTrue(all(x["origin"]=="unknown" and not x["causal_evidence_ids"]
                            for x in fresh))
        self.assertFalse(result["whole_sentence_certified"])

    def test_generator_builder_shared_source_safe_localization(self):
        t=tree("br-02")
        from_explain=explain_request({"tree":t})
        from_evaluate=evaluate_request({"tree":t})
        first=from_explain["xai5_localization"]
        VALIDATE_LOCATION.validate(first)
        self.assertEqual(first,from_evaluate["xai5_localization"])
        self.assertEqual(first,from_evaluate["explanation_evidence"]["xai5_localization"])
        self.assertEqual(first["auto_repair_suggestions"],[])
        self.assertEqual(from_evaluate["grammaticality"]["status"],"unresolved")

    def test_no_client_can_supply_book_authority_via_explanation_endpoint(self):
        t=tree("br-02")
        for key in ("reviewed_by","xai5_localization","source_ids"):
            with self.assertRaises(ValueError):
                explain_request({"tree":t,key:"human-approved"})
            with self.assertRaises(ValueError):
                evaluate_request({"tree":t,key:"human-approved"})

    def test_invalid_analysis_and_bad_graph_fail_closed(self):
        sentence="She had went home."
        bad={"status":"normalized","tree":{"sentence":sentence,"root":{}}}
        localized=localize_xai4(evaluate_xai4(sentence),analysis=bad,sentence=sentence)
        self.assertEqual(localized["tree_status"],"unavailable")
        VALIDATE_LOCATION.validate(localized)


if __name__ == "__main__":
    unittest.main()
