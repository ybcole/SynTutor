"""Contract tests for the book-linked B-R structural coverage registry.

Run: python -m unittest server.test_br_native_grammar -v
No spaCy, Benepar model, network, or database is required.
"""
from __future__ import annotations

import copy
import unittest

from server.br_native_grammar import (
    _validated_registry,
    audit_br_constructions,
    load_br_construction_registry,
)
from server.final_d1_labels import final_d1_display_labels


def envelope(root, chapter=10, version="FINAL"):
    return {
        "convention_profile": {
            "chapter": chapter,
            "version": version,
            "appendix_nom": True if version == "FINAL" else None,
            "profile_id": "FINAL-D1" if version == "FINAL" else f"V{chapter}",
        },
        "root": root,
    }


def simple_root():
    return {
        "label": "S",
        "children": [
            {"label": "NP", "children": [
                {"label": "name", "children": [{"word": "Max"}]},
            ]},
            {"label": "VP", "children": [
                {"label": "V", "features": ["intrans"], "children": [{"word": "slept"}]},
            ]},
        ],
    }


class RegistryTests(unittest.TestCase):
    def test_registry_is_loaded_and_all_chapters_are_covered(self):
        catalog = load_br_construction_registry()
        self.assertEqual(catalog["schema_version"], "0.1.0")
        self.assertGreaterEqual(len(catalog["rules"]), 80)
        self.assertGreaterEqual(len(catalog["obligations"]), 10)
        chapters = {r["chapter_introduced"] for r in catalog["rules"] + catalog["obligations"]}
        self.assertEqual(chapters, set(range(1, 11)))
        for rule in catalog["rules"] + catalog["obligations"]:
            self.assertEqual(rule["source"]["review_status"], "NEEDS_INDEPENDENT_EXAMPLE_AUDIT")

    def test_registry_rejects_duplicate_source_rule(self):
        catalog = copy.deepcopy(load_br_construction_registry())
        catalog["rules"].append(copy.deepcopy(catalog["rules"][0]))
        with self.assertRaisesRegex(ValueError, "distinct"):
            _validated_registry(catalog)

    def test_canonical_intransitive_is_shape_covered_not_grammaticality_certified(self):
        result = audit_br_constructions(envelope(simple_root()))
        self.assertEqual(result["state"], "shape_covered_semantics_unverified")
        self.assertEqual(result["pattern_coverage"]["examined"], 5)
        self.assertEqual(result["pattern_coverage"]["matched"], 5)
        self.assertEqual(result["pattern_coverage"]["fraction"], 1.0)
        self.assertFalse(result["may_certify_grammaticality"])
        self.assertFalse(result["independent_linguistic_review"])
        self.assertTrue(all(x["semantic_conditions_unchecked"] for x in result["covered_patterns"]))

    def test_opaque_triangle_keeps_its_b_r_category(self):
        root = {
            "label": "S",
            "children": [
                {"label": "NP", "triangle": True, "words": ["Max"]},
                {"label": "VP", "triangle": True, "words": ["slept"]},
            ],
        }
        result = audit_br_constructions(envelope(root, chapter=2, version="V2"))
        self.assertEqual(result["pattern_coverage"]["fraction"], 1.0)

    def test_unlabelled_triangle_does_not_invent_np_category(self):
        root = {
            "label": "S-dbar",
            "children": [
                {"label": "C2", "children": [
                    {"triangle": True, "unlabelled": True, "words": ["which", "book"]},
                ]},
                {"label": "S-bar", "children": [
                    {"label": "C1", "empty": True, "empty_role": "complementiser"},
                    {"label": "S", "triangle": True, "words": ["I", "read"]},
                ]},
            ],
        }
        result = audit_br_constructions(envelope(root))
        self.assertIn(result["state"], {"partially_covered", "shape_covered_semantics_unverified"})
        self.assertTrue(any("@unlabelled" in u["children"] for u in result["uncovered_patterns"]))

    def test_raw_penn_label_is_a_verification_violation(self):
        root = simple_root()
        root["children"][0]["label"] = "ADJP"
        result = audit_br_constructions(envelope(root))
        self.assertEqual(result["state"], "invalid_label")
        self.assertIn("PENN_LABEL_LEAK", [v["code"] for v in result["violations"]])

    def test_unknown_structure_remains_uncovered_not_declared_ungrammatical(self):
        root = {"label": "S", "children": [
            {"label": "NP", "triangle": True, "words": ["I"]},
            {"label": "PP", "triangle": True, "words": ["at", "home"]},
        ]}
        result = audit_br_constructions(envelope(root))
        self.assertEqual(result["state"], "partially_covered")
        self.assertTrue(result["uncovered_patterns"])
        self.assertFalse(result["violations"])
        self.assertFalse(result["may_certify_grammaticality"])

    def test_exact_source_match_is_not_claimed_to_be_human_approved(self):
        result = audit_br_constructions(
            envelope(simple_root()),
            normalization_trace=[{"rule_id": "EXACT_IMG_GOLD_REFERENCE"}],
        )
        self.assertEqual(result["state"], "source_matched_unreviewed")
        self.assertTrue(result["exact_reference_match"])
        self.assertFalse(result["independent_linguistic_review"])

    def test_book_numbered_vp_reference_is_not_lost_in_display(self):
        source_vp = {
            "id": "vp", "label": "VP", "source_refs": ["VP1"],
            "children": [{"id": "token", "word": "slept"}],
        }
        labels = final_d1_display_labels(source_vp)
        self.assertEqual(labels["vp"], ["VP₁"])

    def test_bad_profile_rejected(self):
        with self.assertRaisesRegex(ValueError, "FINAL"):
            audit_br_constructions(envelope(simple_root(), chapter=9, version="FINAL"))

    def test_chapter_specific_rule_introduction(self):
        root = simple_root()
        result = audit_br_constructions(envelope(root, chapter=2, version="V2"))
        # The S -> NP VP shell exists in V2; 'name' and lexical V
        # arrive in later chapters and cannot claim V2 source support.
        self.assertEqual(result["state"], "partially_covered")
        self.assertTrue(any(x["parent"] == "NP" for x in result["uncovered_patterns"]))


if __name__ == "__main__":
    unittest.main()
