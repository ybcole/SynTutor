"""Chapter 3 Phase C: canonical tree grounding without source/role overclaims."""
from copy import deepcopy
import unittest

from burton_roberts import validate_canonical_tree
from xai_facts import build_fact_graph
from cgel_ch03_candidate_probe import tokens_with_spans
from cgel_ch03_fact_bridge import probe_ch03_on_canonical
from cambridge_registry import load_runtime_registry


def canonical(sentence, subject, parts):
    """Synthetic B-R-shaped fixture, NOT a book-authored or gold grammar tree.

    parts: [(label, [source token indices]), ...] for the overt VP.
    """
    token_list = tokens_with_spans(sentence)
    tokens = [
        {"index": t["index"], "text": t["text"], "char_span": t["char_span"]}
        for t in token_list
    ]
    np = {
        "id": "np", "label": "NP", "triangle": True,
        "words": [t["text"] for t in tokens[:subject]],
        "token_span": [0, subject],
    }
    kids = []
    for label, indices in parts:
        if len(indices) == 1:
            i = indices[0]
            kids.append({
                "id": f"b{i}", "label": label, "children": [
                    {"id": f"w{i}", "word": tokens[i]["text"],
                     "token_span": [i, i + 1]}
                ],
            })
        else:
            kids.append({
                "id": f"b{indices[0]}", "label": label, "triangle": True,
                "words": [tokens[i]["text"] for i in indices],
                "token_span": [indices[0], indices[-1] + 1],
            })
    result = {
        "schema_version": "1.1.0",
        "tree_id": "synthetic-ch03-fixture",
        "sentence": sentence,
        "tokens": tokens,
        "convention_profile": {
            "chapter": 10, "version": "V10", "profile_id": "V10",
        },
        "source": {
            "book": "Burton-Roberts synthetic fixture, not source authority",
            "chapter": 10,
            "evidence_status": "DERIVED_FROM_INSTRUCTIONS",
            "review_status": "NOT_REVIEWED",
        },
        "root": {
            "id": "s", "label": "S", "children": [
                np, {"id": "vp", "label": "VP", "children": kids},
            ],
        },
        "movement": [],
        "accepted_alternatives": [],
    }
    status = validate_canonical_tree(result)
    assert status["valid"], status["errors"]
    return result


def analysis(tree, status="normalized"):
    return {"status": status, "tree": tree}


def bound_facts(tree, *relations, override=None):
    graph = build_fact_graph(analysis(tree))
    envelope = {
        "status": "typed_candidate",
        "sentence": tree["sentence"],
        "tree_id": graph["tree_id"],
        "analysis_id": graph["analysis_id"],
        "relations": list(relations),
    }
    if override:
        envelope.update(override)
    return envelope


def relation(g, d, *, kind="modal_selects", governor_role="central_modal",
             dependent_role="lexical_verb", dependent_form="present_3sg",
             clause_kind="declarative", **extra):
    return {
        "kind": kind, "governor": g, "dependent": d,
        "governor_node_id": f"w{g}", "dependent_node_id": f"w{d}",
        "governor_role": governor_role, "dependent_role": dependent_role,
        "dependent_form": dependent_form, "clause_kind": clause_kind,
        "direct_selection": True, "same_clause": True, "coordinated": False,
        **extra,
    }


class CanonicalBridgeTests(unittest.TestCase):
    def assert_not_active(self, result):
        self.assertFalse(result["production_enabled"])
        self.assertFalse(result["whole_sentence_certified"])
        self.assertEqual(result["role_licensing"], "unverified")
        self.assertNotEqual(result["status"], "evaluated")

    def test_modal_3sg_candidate_is_bound_to_the_actual_overt_tree(self):
        sentence = "He must forgets the key"
        tree = canonical(sentence, 1, [
            ("MOD", [1]), ("V", [2]), ("NP", [3, 4]),
        ])
        rel = relation(1, 2, candidate_plain_form="forget")
        result = probe_ch03_on_canonical(
            analysis(tree), bound_facts(tree, rel), variety="standard_english",
        )
        self.assert_not_active(result)
        self.assertEqual(result["status"], "candidate_only")
        self.assertEqual(len(result["candidates"]), 1)
        cand = result["candidates"][0]
        self.assertEqual(cand["rule_id"], "COMP-034")
        self.assertEqual(cand["source_pages"], [106])
        self.assertEqual(cand["status"], "tree_bound_relation_unverified")
        self.assertEqual(cand["grounding"]["governor_node_id"], "w1")
        self.assertEqual(cand["grounding"]["dependent_node_id"], "w2")
        self.assertEqual(cand["grounding"]["governor_observed_label"], "MOD")
        self.assertEqual(cand["grounding"]["dependent_observed_label"], "V")
        self.assertEqual(cand["grounding"]["shared_vp_node_id"], "vp")
        self.assertEqual(cand["grounding"]["shared_clause_node_id"], "s")
        self.assertFalse(cand["grounding"]["head_and_selection_licensed"])
        self.assertEqual(sentence[slice(*cand["char_span"])], "must forgets")
        self.assertFalse(cand["edit_hint"]["safe_to_apply_automatically"])
        self.assertEqual(cand["grounding"]["tree_id"], tree["tree_id"])

    def test_double_modal_standard_english_still_candidate_not_a_dialect_error(self):
        sentence = "She may will finish"
        tree = canonical(sentence, 1, [
            ("MOD", [1]), ("MOD", [2]), ("V", [3]),
        ])
        rel = relation(1, 2, dependent_role="central_modal", dependent_form="modal")
        result = probe_ch03_on_canonical(
            analysis(tree), bound_facts(tree, rel), variety="standard_english",
        )
        self.assert_not_active(result)
        self.assertEqual([c["rule_id"] for c in result["candidates"]], ["COMP-031"])
        self.assertEqual(result["candidates"][0]["grounding"]["dependent_observed_label"], "MOD")
        dialect = probe_ch03_on_canonical(
            analysis(tree), bound_facts(tree, rel), variety="southern_english",
        )
        self.assert_not_active(dialect)
        self.assertEqual(dialect["status"], "not_evaluated")
        self.assertEqual(dialect["candidates"], [])

    def test_do_support_candidate_deduplicated_with_source_link(self):
        sentence = "They do not are waiting"
        tree = canonical(sentence, 1, [
            ("AUX", [1]), ("Adv", [2]), ("PROG", [3]), ("V", [4]),
        ])
        rel = relation(
            1, 3, kind="supportive_do_selects", governor_role="supportive_do",
            dependent_role="progressive_be", dependent_form="finite_present",
        )
        result = probe_ch03_on_canonical(
            analysis(tree), bound_facts(tree, rel, deepcopy(rel)),
            variety="standard_english",
        )
        self.assert_not_active(result)
        self.assertEqual(len(result["candidates"]), 1)
        cand = result["candidates"][0]
        self.assertEqual(cand["rule_id"], "CLS-100")
        self.assertEqual(cand["supporting_rule_ids"], ["COMP-030"])
        self.assertEqual(cand["grounding"]["governor_observed_label"], "AUX")
        self.assertEqual(cand["grounding"]["dependent_observed_label"], "PROG")

    def test_valid_auxiliary_and_lexical_have_remain_unflagged(self):
        sentence = "He must forget"
        tree = canonical(sentence, 1, [("MOD", [1]), ("V", [2])])
        rel = relation(1, 2, dependent_form="plain")
        result = probe_ch03_on_canonical(
            analysis(tree), bound_facts(tree, rel), variety="standard_english",
        )
        self.assert_not_active(result)
        self.assertEqual(result["candidates"], [])
        sentence = "She does have money"
        tree = canonical(sentence, 1, [
            ("AUX", [1]), ("V", [2]), ("NP", [3]),
        ])
        rel = relation(1, 2, kind="supportive_do_selects",
                       governor_role="supportive_do", dependent_role="lexical_have",
                       dependent_form="plain")
        result = probe_ch03_on_canonical(
            analysis(tree), bound_facts(tree, rel), variety="standard_english",
        )
        self.assert_not_active(result)
        self.assertEqual(result["candidates"], [])

    def test_provisional_or_invalid_canonical_analysis_never_runs(self):
        tree = canonical("He must forgets", 1, [
            ("MOD", [1]), ("V", [2]),
        ])
        rel = relation(1, 2)
        for status in ("provisional", "unresolved", "working"):
            with self.subTest(status=status):
                result = probe_ch03_on_canonical(
                    analysis(tree, status), bound_facts(tree, rel),
                    variety="standard_english",
                )
                self.assert_not_active(result)
                self.assertEqual(result["status"], "not_evaluated")
        uncertain = deepcopy(tree)
        uncertain["source"]["evidence_status"] = "UNCERTAIN"
        facts = bound_facts(tree, rel)
        result = probe_ch03_on_canonical(
            analysis(uncertain), facts, variety="standard_english",
        )
        self.assert_not_active(result)
        self.assertEqual(result["status"], "not_evaluated")
        invalid = deepcopy(tree)
        invalid["tokens"][1]["text"] = "forged"
        result = probe_ch03_on_canonical(
            analysis(invalid), facts, variety="standard_english",
        )
        self.assert_not_active(result)
        self.assertEqual(result["blocked"], ["invalid_canonical_tree"])

    def test_forged_or_stale_tree_and_analysis_ids_do_not_match(self):
        tree = canonical("He must forgets", 1, [
            ("MOD", [1]), ("V", [2]),
        ])
        fact = bound_facts(tree, relation(1, 2))
        for change in ({"tree_id": "another-tree"}, {"analysis_id": "forged"},
                       {"sentence": "Different text"}, {"relations": "bad"}):
            with self.subTest(change=change):
                result = probe_ch03_on_canonical(
                    analysis(tree), dict(fact, **change), variety="standard_english",
                )
                self.assert_not_active(result)
                self.assertEqual(result["blocked"], ["candidate_provenance_mismatch"])

    def test_wrong_terminal_node_ids_and_unlicensed_labels_are_blocked(self):
        sentence = "He must forgets"
        tree = canonical(sentence, 1, [
            ("MOD", [1]), ("V", [2]),
        ])
        rel = relation(1, 2)
        for bad in [
            dict(rel, governor_node_id="w2"),
            dict(rel, dependent_node_id="np"),
            dict(rel, dependent_role="perfect_have"),
            dict(rel, governor_role="supportive_do"),
        ]:
            with self.subTest(rel=bad):
                result = probe_ch03_on_canonical(
                    analysis(tree), bound_facts(tree, bad), variety="standard_english",
                )
                self.assert_not_active(result)
                self.assertEqual(result["candidates"], [])
                self.assertEqual(result["blocked"][0]["reason"],
                                 "opaque_or_unmatched_lexical_category")

    def test_opaque_triangles_do_not_invent_auxiliary_heads(self):
        sentence = "He must forgets"
        tree = canonical(sentence, 1, [
            ("VP", [1, 2]),
        ])
        rel = relation(1, 2)
        result = probe_ch03_on_canonical(
            analysis(tree), bound_facts(tree, rel), variety="standard_english",
        )
        self.assert_not_active(result)
        self.assertEqual(result["candidates"], [])
        self.assertEqual(result["blocked"][0]["reason"],
                         "opaque_or_unmatched_lexical_category")

    def test_open_or_ambiguous_analyses_fail_closed(self):
        tree = canonical("He must forgets", 1, [
            ("MOD", [1]), ("V", [2]),
        ])
        fact = bound_facts(tree, relation(1, 2))
        tree["accepted_alternatives"] = [{
            "analysis_id": "alternate-candidate",
            "root": deepcopy(tree["root"]),
            "acceptance": "NEEDS_REVIEW",
            "rationale": "A separate synthetic analysis, not merged into the primary tree.",
        }]
        result = probe_ch03_on_canonical(
            analysis(tree), fact, variety="standard_english",
        )
        self.assert_not_active(result)
        self.assertEqual(result["candidates"], [])
        self.assertIn(result["blocked"][0],
                      ("alternative_analysis_unresolved", "invalid_canonical_tree"))

    def test_forged_review_flag_does_not_activate_source_rule(self):
        tree = canonical("He must forgets", 1, [
            ("MOD", [1]), ("V", [2]),
        ])
        tree["source"]["review_status"] = "HUMAN_APPROVED"
        result = probe_ch03_on_canonical(
            analysis(tree), bound_facts(tree, relation(1, 2)),
            variety="standard_english",
        )
        self.assert_not_active(result)
        self.assertEqual(result["candidates"][0]["grounding"]["head_and_selection_licensed"], False)
        self.assertEqual(load_runtime_registry()["active_rules"], [])

    def test_malformed_unhashable_metadata_is_blocked_without_throwing(self):
        tree = canonical("He must forgets", 1, [
            ("MOD", [1]), ("V", [2]),
        ])
        rel = relation(1, 2)
        for bad in [
            dict(rel, dependent_role=[]),
            dict(rel, governor_role={}),
            dict(rel, clause_kind=[]),
            dict(rel, kind={}),
            dict(rel, governor=True),
            dict(rel, dependent="2"),
        ]:
            with self.subTest(bad=bad):
                result = probe_ch03_on_canonical(
                    analysis(tree), bound_facts(tree, bad),
                    variety="standard_english",
                )
                self.assert_not_active(result)
                self.assertEqual(result["candidates"], [])
                self.assertTrue(result["blocked"])

    def test_actual_course_tree_opaque_words_cannot_synthesize_heads(self):
        # The book-backed course tree is a real repository fixture, not a
        # manufactured error tree. Its opaque triangles do not certify roles.
        from test_builder_evaluation import tree as course_tree
        t = course_tree("br-02")
        self.assertTrue(validate_canonical_tree(t)["valid"])
        self.assertEqual(t["sentence"], "The robins sing")
        attempted = relation(1, 2, candidate_plain_form="sing")
        result = probe_ch03_on_canonical(
            analysis(t), bound_facts(t, attempted),
            variety="standard_english",
        )
        self.assert_not_active(result)
        self.assertEqual(result["candidates"], [])
        self.assertTrue(result["blocked"])

    def test_current_workflows_keep_zero_live_cambridge_rules(self):
        registry = load_runtime_registry()
        self.assertEqual(registry["active_rule_ids"], [])
        self.assertEqual(registry["active_rules"], [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
