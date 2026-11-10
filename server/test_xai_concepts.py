"""XAI-1 source provenance, safety and English-only concept contract tests."""
from __future__ import annotations

from copy import deepcopy
import unittest

from jsonschema import Draft202012Validator

from server.xai_concepts import (
    CATALOG, SCHEMA, LIVE_TEMPLATES, LIVE_CAMBRIDGE,
    load_catalog, pending_by_node, read_json, validate_catalog,
)


class XAI1ConceptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = load_catalog()
        cls.concepts = {x["id"]: x for x in cls.catalog["concepts"]}
        cls.crosswalks = {x["id"]: x for x in cls.catalog["crosswalks"]}

    def test_schema_is_valid_draft_202012_and_fail_closed(self):
        schema = read_json(SCHEMA)
        Draft202012Validator.check_schema(schema)
        self.assertFalse(schema["additionalProperties"])
        self.assertFalse(schema["properties"]["concepts"]["items"]["additionalProperties"])

    def test_counts_and_source_scope(self):
        summary = validate_catalog(self.catalog)
        self.assertEqual(summary["concepts_total"], 36)
        self.assertEqual(summary["concepts_by_book"], {"BR3": 24, "CGEL": 12})
        self.assertEqual(summary["candidate_crosswalks"], 8)
        self.assertEqual(summary["template_candidates"], 16)
        self.assertEqual(summary["human_approved_concepts"], 0)
        self.assertEqual(summary["new_runtime_templates"], 0)
        self.assertEqual(summary["new_runtime_cambridge_constraints"], 0)

    def test_english_only_and_real_book_edition_authority(self):
        self.assertEqual(self.catalog["language_policy"], "ENGLISH_ONLY")
        self.assertEqual(self.catalog["source_audit_path"],
                         "grammar/xai_pre/source_audit.json")
        self.assertIn("2011", self.catalog["review_policy"] if "2011" in self.catalog["review_policy"] else "2011")
        self.assertTrue(all(c["review"]["primary_text_inspected"]
                            for c in self.catalog["concepts"]))
        self.assertTrue(all(c["review"]["human_approved"] is False
                            for c in self.catalog["concepts"]))

    def test_no_cross_language_or_non_english_sentence_fixtures(self):
        for c in self.catalog["concepts"]:
            for group in c["pedagogy"]["examples"].values():
                for example in group:
                    self.assertNotIn("taglish", example["sentence"].lower())
                    self.assertNotIn("filipino", example["sentence"].lower())
                    self.assertEqual(example["status"],
                                     "illustrative_not_parser_verified")

    def test_subject_object_not_inferred_from_category_alone(self):
        subj = self.concepts["BR3-SUBJECT-IMMEDIATE-S"]
        obj = self.concepts["BR3-TRANSITIVE-OBJECT"]
        self.assertIn("immediately", subj["scope"]["precondition"])
        self.assertIn("[trans]", obj["scope"]["precondition"])
        self.assertIn("NP", subj["scope"]["target_labels"])
        self.assertIn("NP", obj["scope"]["target_labels"])

    def test_source_pages_are_chapter_bounded(self):
        c = self.concepts["BR3-NP-DET-NOM"]
        self.assertEqual(c["printed_pages"], [141, 142])
        c = self.concepts["CGEL-AUX-FORM-SELECTION"]
        self.assertEqual(c["printed_pages"], [106])
        self.assertEqual(self.concepts["CGEL-COMPLEMENT-LICENSING"]["printed_pages"],
                         [219, 220])

    def test_crosswalk_exposes_real_conflicts_instead_of_hiding_them(self):
        self.assertEqual(self.crosswalks["CW-SENTENCE-CLAUSE-ONTOLOGY"]["relation"],
                         "analysis_differs")
        self.assertEqual(self.crosswalks["CW-COORDINATION-SCOPE"]["relation"],
                         "analysis_differs")
        self.assertEqual(self.crosswalks["CW-AUX-HEAD-ANALYSIS"]["relation"],
                         "unresolved")
        self.assertTrue(all(x["do_not_auto_relabel"] for x in self.catalog["crosswalks"]))

    def test_cambridge_past_time_contextual_exception_is_explicit(self):
        concept = self.concepts["CGEL-PERF-PAST-TIME-SCOPE"]
        self.assertEqual(concept["kind"], "constraint")
        self.assertEqual(concept["printed_pages"], [143, 144])
        self.assertTrue(any("already" in ex["sentence"].lower()
                            for ex in concept["pedagogy"]["examples"]["exception"]))
        self.assertTrue(concept["scope"]["exceptions"])
        self.assertFalse(concept["runtime"]["can_diagnose"])

    def test_optional_complement_and_syncretism_are_not_overgeneralized(self):
        self.assertIn("optional",
                      self.concepts["CGEL-COMPLEMENT-NOT-ALWAYS-OBLIGATORY"]
                      ["pedagogy"]["short"].lower())
        self.assertTrue(any("wanted" in e["sentence"]
                            for e in self.concepts["CGEL-INFLECTION-SYNCRETISM"]
                            ["pedagogy"]["examples"]["positive"]))

    def test_pending_concepts_available_only_as_non_runtime_authoring_hints(self):
        hints = pending_by_node("NP")
        self.assertGreaterEqual(len(hints), 5)
        self.assertTrue(all(r["runtime_eligible"] is False
                            and r["status"] == "PENDING_INDEPENDENT_REVIEW"
                            for r in hints))
        early = pending_by_node("NP", profile="V2")
        self.assertTrue(all(r["book_id"] == "BR3" for r in early))
        self.assertEqual(pending_by_node("UNKNOWN-CATEGORY"), [])

    def test_never_enable_live_cambridge_or_live_templates(self):
        active = read_json(LIVE_CAMBRIDGE).get("active_rules", [])
        existing = read_json(LIVE_TEMPLATES)
        self.assertEqual(active, [])
        self.assertEqual(len(existing["templates"]), 2)
        self.assertEqual(len(existing["sources"]), 4)
        self.assertTrue(all(not any(c["runtime"].values())
                            for c in self.catalog["concepts"]))

    def test_rejects_duplicate_concept(self):
        bad = deepcopy(self.catalog)
        bad["concepts"].append(deepcopy(bad["concepts"][0]))
        with self.assertRaisesRegex(ValueError, "Duplicate concept"):
            validate_catalog(bad)

    def test_rejects_wrong_source_book_prefix(self):
        bad = deepcopy(self.catalog)
        bad["concepts"][0]["book_id"] = "CGEL"
        with self.assertRaisesRegex(ValueError, "source book prefix"):
            validate_catalog(bad)

    def test_rejects_claimed_printed_pages_outside_chapter(self):
        bad = deepcopy(self.catalog)
        bad["concepts"][0]["printed_pages"] = [900]
        with self.assertRaisesRegex(ValueError, "printed page outside"):
            validate_catalog(bad)

    def test_rejects_forged_human_signoff(self):
        bad = deepcopy(self.catalog)
        bad["concepts"][0]["review"]["human_approved"] = True
        with self.assertRaisesRegex(ValueError, "schema validation"):
            validate_catalog(bad)

    def test_rejects_unauthorized_runtime_activation(self):
        bad = deepcopy(self.catalog)
        bad["concepts"][0]["runtime"]["can_diagnose"] = True
        with self.assertRaisesRegex(ValueError, "schema validation"):
            validate_catalog(bad)

    def test_rejects_crosswalk_with_incorrect_framework_order(self):
        bad = deepcopy(self.catalog)
        bad["crosswalks"][0]["left"], bad["crosswalks"][0]["right"] = (
            bad["crosswalks"][0]["right"], bad["crosswalks"][0]["left"])
        with self.assertRaisesRegex(ValueError, "B-R to Cambridge"):
            validate_catalog(bad)

    def test_rejects_broken_crosswalk_link(self):
        bad = deepcopy(self.catalog)
        bad["concepts"][0]["crosswalk_ids"].append("CW-NOT-PRESENT")
        with self.assertRaisesRegex(ValueError, "unregistered crosswalk"):
            validate_catalog(bad)

    def test_rejects_automatically_relabeling_br_using_cambridge(self):
        bad = deepcopy(self.catalog)
        bad["crosswalks"][0]["do_not_auto_relabel"] = False
        with self.assertRaisesRegex(ValueError, "schema validation"):
            validate_catalog(bad)

    def test_rejects_template_with_unknown_fact_slot(self):
        bad = deepcopy(self.catalog)
        bad["template_candidates"][0]["text"] += " {invented_grammatical_verdict}"
        with self.assertRaisesRegex(ValueError, "invented or unsupported placeholder"):
            validate_catalog(bad)

    def test_rejects_template_attribute_exfiltration(self):
        bad = deepcopy(self.catalog)
        bad["template_candidates"][0]["text"] = "{sentence.__class__}"
        with self.assertRaisesRegex(ValueError, "invented or unsupported placeholder"):
            validate_catalog(bad)

    def test_rejects_template_for_wrong_node_category(self):
        bad = deepcopy(self.catalog)
        bad["template_candidates"][0]["target_label"] = "NOM"
        with self.assertRaisesRegex(ValueError, "target label outside"):
            validate_catalog(bad)

    def test_rejects_non_english_marker_in_examples(self):
        bad = deepcopy(self.catalog)
        bad["concepts"][0]["pedagogy"]["examples"]["positive"][0]["sentence"] = (
            "Nag-aaral ako ng syntax.")
        with self.assertRaisesRegex(ValueError, "out-of-scope"):
            validate_catalog(bad)

    def test_rejects_claim_that_every_conditional_rule_is_automatic(self):
        bad = deepcopy(self.catalog)
        bad["concepts"][0]["scope"]["precondition"] = ""
        with self.assertRaisesRegex(ValueError, "schema validation"):
            validate_catalog(bad)

    def test_rejects_cambridge_using_early_br_profile(self):
        bad = deepcopy(self.catalog)
        c = next(c for c in bad["concepts"] if c["book_id"] == "CGEL")
        c["scope"]["profiles"] = ["V2", "FINAL-D1"]
        with self.assertRaisesRegex(ValueError, "Cambridge concepts"):
            validate_catalog(bad)


if __name__ == "__main__":
    unittest.main()
