"""XAI-PRE contract tests: source scopes, original tokens and evolving repairs.

All grammar-error findings in fixtures are synthetic. No English diagnostic
is enabled, no book evidence is certified by this suite, and no model is needed.
Run: python -m unittest -v server.test_xai_preflight
"""
from __future__ import annotations

from copy import deepcopy
import unittest
from jsonschema import Draft202012Validator

from server.xai_preflight import (
    AUDIT_PATH, SCHEMA_PATH, FIXTURE_PATH,
    load_json, validate_source_audit, validate_diagnosis_repair_case,
)


class SourcePreflightTests(unittest.TestCase):
    def setUp(self):
        self.audit = load_json(AUDIT_PATH)
        self.fixtures = load_json(FIXTURE_PATH)
        self.cases = {row["id"]: row["envelope"]
                      for row in self.fixtures["cases"]}

    def test_source_gate_inventory_tracks_both_editions_and_limited_review(self):
        summary = validate_source_audit(self.audit)
        self.assertEqual(summary, {
            "books": 2, "chapters": 31, "source_passages": 13,
            "crosswalks": 3, "approved_runtime_constraints": 0,
        })
        self.assertEqual(self.audit["status"],
                         "targeted_source_checks_pending_independent_review")
        self.assertEqual(self.audit["books"][1]["physical_printing"],
                         "not_established")

    def test_past_time_exception_and_syncretism_are_explicit(self):
        claims = {row["id"]: row for row in self.audit["claims"]}
        self.assertEqual(claims["CGEL-PERF-EXPERIENTIAL-EXCEPTION"]
                         ["source"]["printed_pages"], [144])
        self.assertEqual(claims["CGEL-SYNCRETISM"]["source"]["printed_pages"], [76])
        self.assertTrue(all(not row["runtime"]["constraint_enabled"]
                            for row in claims.values()))
        self.assertTrue(all(not row["review"]["independent_human_review"]
                            for row in claims.values()))

    def test_crosswalk_records_terms_but_cannot_override_br_labels(self):
        crosswalks = self.audit["crosswalks"]
        self.assertEqual(sum(row["relation"] == "terminology_differs"
                             for row in crosswalks), 2)
        self.assertEqual(sum(row["relation"] == "unresolved"
                             for row in crosswalks), 1)
        self.assertTrue(all(row["may_change_br_tree_labels"] is False
                            for row in crosswalks))

    def test_source_audit_rejects_forged_certification(self):
        changed = deepcopy(self.audit)
        changed["claims"][0]["runtime"]["constraint_enabled"] = True
        with self.assertRaisesRegex(ValueError, "source review alone"):
            validate_source_audit(changed)

    def test_source_audit_rejects_wrong_chapter_page(self):
        changed = deepcopy(self.audit)
        next(row for row in changed["claims"] if row["id"] ==
             "CGEL-PERF-EXPERIENTIAL-EXCEPTION")["source"]["printed_pages"] = [700]
        with self.assertRaisesRegex(ValueError, "source page outside chapter"):
            validate_source_audit(changed)

    def test_source_audit_rejects_full_chapter_approval_from_topic_inventory(self):
        changed = deepcopy(self.audit)
        changed["chapters"][0]["coverage"] = "entire_book_approved"
        with self.assertRaisesRegex(ValueError, "full review"):
            validate_source_audit(changed)

    def test_contract_json_schema_is_valid_and_strict(self):
        Draft202012Validator.check_schema(load_json(SCHEMA_PATH))
        self.assertFalse(load_json(SCHEMA_PATH)["additionalProperties"])
        self.assertIn("tokens", load_json(SCHEMA_PATH)["$defs"]["candidate"]["required"])

    def test_every_protocol_fixture_passes_and_matches_counts(self):
        self.assertEqual(len(self.cases), 10)
        for entry in self.fixtures["cases"]:
            with self.subTest(case=entry["id"]):
                result = validate_diagnosis_repair_case(entry["envelope"])
                self.assertEqual(result["original_findings"],
                                 entry["expected"]["original_findings"])
                self.assertEqual(result["issue_groups"],
                                 entry["expected"]["issue_groups"])
                self.assertEqual(result["candidates"],
                                 entry["expected"]["candidates"])
                self.assertEqual(result["definitively_enabled_rules"], 0)
                self.assertFalse(entry["envelope"]["global_verdict"]
                                 ["whole_sentence_certified"])

    def test_interacting_repairs_preserve_all_original_findings(self):
        record = self.cases["interacting_two_errors_temporal_context"]
        self.assertEqual(len(record["findings"]), 3)
        self.assertEqual(len(record["groups"]), 1)
        first, second, alternate = record["candidates"]
        self.assertEqual(first["text"],
                         "She has went to the store yesterday.")
        self.assertEqual(second["text"],
                         "She has gone to the store yesterday.")
        self.assertEqual(alternate["text"],
                         "She went to the store yesterday.")
        self.assertTrue(all(len(c["lineage"]) == 3 for c in record["candidates"]))
        self.assertEqual(alternate["lineage"][0]["after"],
                         "no_longer_applicable_after_rewrite")

    def test_introduced_versus_unmasked_are_distinct(self):
        intro = self.cases["edit_introduces_error"]["candidates"][0]
        self.assertEqual(intro["new_findings"][0]["origin"], "introduced")
        unmasked = self.cases["repair_unmasks_blocked_check"]["candidates"][0]
        self.assertEqual(unmasked["new_findings"][0]["origin"], "unmasked")

    def test_violation_without_original_group_fails(self):
        record = deepcopy(self.cases["independent_error_groups"])
        record["groups"] = record["groups"][:1]
        with self.assertRaisesRegex(ValueError, "exactly one issue group"):
            validate_diagnosis_repair_case(record)

    def test_false_resolution_without_new_satisfaction_is_rejected(self):
        record = deepcopy(self.cases["independent_error_groups"])
        record["candidates"][0]["lineage"][0]["recheck_status"] = "VIOLATED"
        with self.assertRaisesRegex(ValueError, "recheck disagree"):
            validate_diagnosis_repair_case(record)

    def test_forged_book_citation_is_rejected_even_in_simulation(self):
        record = deepcopy(self.cases["interacting_two_errors_temporal_context"])
        record["findings"][0]["source_claim_ids"] = ["CGEL-FAKE-PAGE-9999"]
        with self.assertRaisesRegex(ValueError, "client-forged"):
            validate_diagnosis_repair_case(record)

    def test_original_text_and_token_spans_are_immutable(self):
        record = deepcopy(self.cases["interacting_two_errors_temporal_context"])
        record["original"]["tokens"][0]["text"] = "They"
        with self.assertRaisesRegex(ValueError, "token surface does not match"):
            validate_diagnosis_repair_case(record)

    def test_edit_implementation_must_match_candidate_text(self):
        record = deepcopy(self.cases["independent_error_groups"])
        record["candidates"][0]["text"] = "The boys is carrying boxes."
        with self.assertRaisesRegex(ValueError, "text does not equal actual"):
            validate_diagnosis_repair_case(record)

    def test_candidate_parent_cycles_and_duplicate_versions_are_rejected(self):
        record = deepcopy(self.cases["interacting_two_errors_temporal_context"])
        record["candidates"][0]["parent_version_id"] = "u2"
        with self.assertRaisesRegex(ValueError, "cycle or forward parent"):
            validate_diagnosis_repair_case(record)

    def test_introduced_requires_prior_satisfaction_and_causal_evidence(self):
        record = deepcopy(self.cases["edit_introduces_error"])
        record["candidates"][0]["new_findings"][0]["causal_evidence_ids"] = []
        with self.assertRaisesRegex(ValueError, "requires evidence"):
            validate_diagnosis_repair_case(record)

    def test_unmasked_requires_a_prior_blocked_or_ambiguous_check(self):
        record = deepcopy(self.cases["repair_unmasks_blocked_check"])
        record["findings"][1]["status"] = "VIOLATED"
        record["candidates"][0]["lineage"][1]["after"] = "newly_unmasked"
        with self.assertRaisesRegex(ValueError, "prior uncertainty"):
            validate_diagnosis_repair_case(record)

    def test_production_rule_activation_cannot_be_forged_by_caller(self):
        record = deepcopy(self.cases["edit_introduces_error"])
        record["mode"] = "runtime"
        record["findings"][0]["rule_id"] = "DEMO-AGREEMENT-PRIVILEGED"
        with self.assertRaisesRegex(ValueError, "may not enable unregistered"):
            validate_diagnosis_repair_case(
                record, enabled_rule_ids={"DEMO-AGREEMENT-PRIVILEGED"})

    def test_production_rule_without_allowlist_cannot_emit_violation(self):
        record = deepcopy(self.cases["edit_introduces_error"])
        record["mode"] = "runtime"
        record["findings"][0]["rule_id"] = "AGR-002"
        with self.assertRaisesRegex(ValueError, "disabled rule"):
            validate_diagnosis_repair_case(record)

    def test_no_categorical_verdict_on_context_sensitive_exception(self):
        record = self.cases["cambridge_experiential_exception"]
        self.assertEqual(record["findings"], [])
        self.assertEqual(record["global_verdict"]["status"], "NOT_EVALUATED")


if __name__ == "__main__":
    unittest.main()
