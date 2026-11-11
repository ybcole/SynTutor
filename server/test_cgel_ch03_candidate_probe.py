"""Phase-C typed-evidence checker: synthetic evidence, real source rule IDs, no approval."""
import copy
import json
import unittest

from cgel_ch03_candidate_probe import probe_ch03, tokens_with_spans
from cambridge_registry import load_runtime_registry


def fixture(sentence, *relations):
    return {"status": "typed_candidate", "sentence": sentence, "relations": list(relations)}


def selection(sentence, governor, dependent, kind="modal_selects",
              governor_role="central_modal", dependent_role="lexical_verb",
              dependent_form="present_3sg", clause_kind="declarative", **extras):
    tokens = tokens_with_spans(sentence)
    def token_index(word, ordinal=1):
        matches = [token["index"] for token in tokens
                   if token["lower"] == word.casefold()]
        return matches[ordinal - 1]
    return {
        "kind": kind,
        "governor": token_index(governor),
        "dependent": token_index(dependent),
        "governor_role": governor_role,
        "dependent_role": dependent_role,
        "dependent_form": dependent_form,
        "clause_kind": clause_kind,
        "direct_selection": True,
        "same_clause": True,
        "coordinated": False,
        **extras,
    }


def run(sentence, *relations, variety="standard_english"):
    return probe_ch03(sentence, fixture(sentence, *relations), variety=variety)


class ChapterThreeCandidateProbeTests(unittest.TestCase):
    def test_raw_sentence_never_generates_an_error_without_typed_relations(self):
        bad = "He must forgets the key."
        self.assertEqual(run(bad)["candidates"], [])
        result = probe_ch03(bad, None, variety="standard_english")
        self.assertEqual(result["status"], "not_evaluated")
        self.assertEqual(result["candidates"], [])
        for fact in [fixture("Another sentence.", {}), {"status": "typed_candidate",
                       "sentence": bad, "relations": "not a list"}]:
            result = probe_ch03(bad, fact, variety="standard_english")
            self.assertEqual(result["status"], "not_evaluated")
            self.assertEqual(result["candidates"], [])

    def test_modal_requires_plain_form_and_provides_optional_edit_hint(self):
        sentence = "He must forgets the key."
        relation = selection(sentence, "must", "forgets", candidate_plain_form="forget")
        result = run(sentence, relation)
        self.assertEqual(result["status"], "candidate_only")
        self.assertFalse(result["production_enabled"])
        self.assertFalse(result["whole_sentence_certified"])
        self.assertEqual(len(result["candidates"]), 1)
        candidate = result["candidates"][0]
        self.assertEqual(candidate["rule_id"], "COMP-034")
        self.assertEqual(candidate["source_pages"], [106])
        self.assertEqual(candidate["evidence_tokens"], ["must", "forgets"])
        self.assertEqual(candidate["status"], "needs_linguistic_validation")
        self.assertEqual(candidate["family"], "verb_form")
        self.assertEqual(candidate["provisional_explanation"][:9], "A central")
        start, end = candidate["char_span"]
        self.assertEqual(sentence[start:end], "must forgets")
        edit = candidate["edit_hint"]
        self.assertFalse(edit["safe_to_apply_automatically"])
        self.assertTrue(edit["requires_reparse"])
        self.assertEqual(sentence[:edit["char_span"][0]] + edit["replacement"]
                         + sentence[edit["char_span"][1]:],
                         "He must forget the key.")

    def test_modal_infinitival_to_requires_marker_and_plain_following_verb(self):
        sentence = "The train might to leave soon."
        relation = selection(sentence, "might", "to",
                             dependent_role="infinitival_marker",
                             dependent_form="infinitival_to",
                             infinitival_verb=4, infinitival_verb_form="plain")
        candidate = run(sentence, relation)["candidates"][0]
        self.assertEqual(candidate["rule_id"], "COMP-034")
        edit = candidate["edit_hint"]
        self.assertEqual(sentence[:edit["char_span"][0]] + edit["replacement"]
                         + sentence[edit["char_span"][1]:],
                         "The train might leave soon.")
        incomplete = dict(relation, infinitival_verb_form="unknown")
        self.assertEqual(run(sentence, incomplete)["candidates"], [])
        lexical_to = dict(relation, dependent_role="lexical_verb")
        self.assertEqual(run(sentence, lexical_to)["candidates"], [])

    def test_double_central_modals_need_standard_english_and_an_aux_relation(self):
        for sentence, left, right in [
            ("She may will finish tomorrow.", "may", "will"),
            ("He will can swim tomorrow.", "will", "can"),
        ]:
            with self.subTest(sentence=sentence):
                relation = selection(sentence, left, right,
                                     dependent_role="central_modal",
                                     dependent_form="modal")
                candidate = run(sentence, relation)["candidates"][0]
                self.assertEqual(candidate["rule_id"], "COMP-031")
                self.assertEqual(candidate["source_pages"], [105, 107])
                self.assertIsNone(candidate["edit_hint"])
                self.assertEqual(candidate["variety_scope"],
                                 "variety_restricted: standard written English")

    def test_double_modal_english_dialect_and_lexical_can_not_automatically_wrong(self):
        sentence = "He might could help."
        rel = selection(sentence, "might", "could",
                        dependent_role="central_modal", dependent_form="modal")
        for variety in ["appalachian_english", "southern_english", " ", None]:
            with self.subTest(variety=variety):
                result = run(sentence, rel, variety=variety)
                self.assertEqual(result["candidates"], [])
                self.assertEqual(result["status"], "not_evaluated")
        sentence = "They may can peaches."
        rel = selection(sentence, "may", "can", dependent_role="lexical_verb",
                        dependent_form="plain")
        self.assertEqual(run(sentence, rel)["candidates"], [])

    def test_coordination_or_non_direct_relation_is_not_double_modal(self):
        sentence = "She may or may not finish."
        rel = selection(sentence, "may", "may", dependent_role="central_modal",
                        dependent_form="modal")
        rel["dependent"] = 3
        rel["coordinated"] = True
        self.assertEqual(run(sentence, rel)["candidates"], [])
        rel["coordinated"] = False
        rel["direct_selection"] = False
        self.assertEqual(run(sentence, rel)["candidates"], [])

    def test_redundant_do_support_has_one_canonical_rule_with_crosslink(self):
        sentence = "Does she have completed the task?"
        rel = selection(sentence, "Does", "have", kind="supportive_do_selects",
                        governor_role="supportive_do", dependent_role="perfect_have",
                        dependent_form="plain", clause_kind="closed_interrogative")
        candidate = run(sentence, rel, rel)["candidates"]
        self.assertEqual(len(candidate), 1)
        self.assertEqual(candidate[0]["rule_id"], "CLS-100")
        self.assertEqual(candidate[0]["supporting_rule_ids"], ["COMP-030"])
        self.assertEqual(candidate[0]["source_pages"], [93, 94])
        self.assertIsNone(candidate[0]["edit_hint"])

    def test_supportive_do_negative_clause_and_lexical_have_guard(self):
        sentence = "They do not are waiting here."
        rel = selection(sentence, "do", "are", kind="supportive_do_selects",
                        governor_role="supportive_do", dependent_role="progressive_be",
                        dependent_form="finite_present", clause_kind="declarative")
        self.assertEqual(run(sentence, rel)["candidates"][0]["rule_id"], "CLS-100")
        sentence = "Does she have a reservation?"
        rel = selection(sentence, "Does", "have", kind="supportive_do_selects",
                        governor_role="supportive_do", dependent_role="lexical_have",
                        dependent_form="plain", clause_kind="closed_interrogative")
        self.assertEqual(run(sentence, rel)["candidates"], [])

    def test_negative_and_emphatic_imperatives_are_guarded(self):
        for sentence, dependent in [("Don't be careless!", "be"),
                                    ("Do be careful!", "be")]:
            with self.subTest(sentence=sentence):
                rel = selection(sentence, sentence.split()[0], dependent,
                                kind="supportive_do_selects",
                                governor_role="supportive_do",
                                dependent_role="copular_be", dependent_form="plain",
                                clause_kind="imperative")
                self.assertEqual(run(sentence, rel)["candidates"], [])

    def test_valid_auxiliary_chains_and_noncentral_modals_not_overcorrected(self):
        for sentence, governor, dependent, role, form in [
            ("He must have spoken already.", "must", "have", "lexical_verb", "plain"),
            ("They might leave soon.", "might", "leave", "lexical_verb", "plain"),
            ("She would rather leave.", "would", "leave", "lexical_verb", "plain"),
        ]:
            with self.subTest(sentence=sentence):
                rel = selection(sentence, governor, dependent, dependent_role=role,
                                dependent_form=form)
                self.assertEqual(run(sentence, rel)["candidates"], [])
        sentence = "He ought to leave soon."
        rel = selection(sentence, "ought", "to", dependent_role="infinitival_marker",
                        dependent_form="infinitival_to", infinitival_verb=3,
                        infinitival_verb_form="plain")
        self.assertEqual(run(sentence, rel)["candidates"], [])

    def test_missing_or_forged_typed_fields_fail_closed(self):
        sentence = "He must forgets the key."
        normal = selection(sentence, "must", "forgets", candidate_plain_form="forget")
        invalid = [
            dict(normal, dependent=True),
            dict(normal, dependent=999),
            dict(normal, governor=normal["dependent"]),
            dict(normal, direct_selection="true"),
            dict(normal, same_clause=False),
            dict(normal, coordinated=None),
            dict(normal, clause_kind="unknown"),
            dict(normal, governor_role="lexical_verb"),
        ]
        for relation in invalid:
            with self.subTest(relation=relation):
                self.assertEqual(run(sentence, relation)["candidates"], [])
        guarded = run(sentence, dict(normal, dependent=999))
        self.assertEqual(guarded["blocked"][0]["reason"],
                         "missing_or_invalid_typed_evidence")

    def test_multiple_independent_candidates_never_certify_whole_sentence(self):
        sentence = "She may will finish, and he must forgets the key."
        modals = selection(sentence, "may", "will", dependent_role="central_modal",
                           dependent_form="modal")
        form = selection(sentence, "must", "forgets", candidate_plain_form="forget")
        result = run(sentence, modals, form)
        self.assertEqual({c["rule_id"] for c in result["candidates"]},
                         {"COMP-031", "COMP-034"})
        self.assertFalse(result["whole_sentence_certified"])
        self.assertEqual(len(result["candidates"]), 2)
        spans = [c["char_span"] for c in result["candidates"]]
        self.assertTrue(spans[0][1] <= spans[1][0])
        self.assertTrue(all(c["status"] == "needs_linguistic_validation"
                            for c in result["candidates"]))

    def test_enabled_registry_remains_empty_even_after_candidate_checks(self):
        self.assertEqual(load_runtime_registry()["active_rules"], [])
        self.assertEqual(load_runtime_registry()["active_rule_ids"], [])
        sentence = "She may will finish tomorrow."
        rel = selection(sentence, "may", "will", dependent_role="central_modal",
                        dependent_form="modal")
        self.assertFalse(run(sentence, rel)["production_enabled"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
