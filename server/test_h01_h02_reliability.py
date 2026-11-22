"""Focused H01/H02 reliability sprint regression tests (positive & negative cases).

H01 (Benepar -> Burton-Roberts FINAL-D1 projection):
  1. Contiguous negative-auxiliary contraction & hyphenated compound fusion
     (and negative controls preserving participial 'so-called' and possessive 's).
  2. Previously unresolved B-R constructions (nested/coordinated passives,
     passive complex-transitive, subject wh-questions, root WHADVP, noun-complement
     vs. relative 'that'-clauses, UCP coordinated prepositions, PRE-DET + POSS,
     standalone non-finite clauses).
  3. B-R Ch. 7 Appendix D1 'of'-PP complement attachment inside NOM.

H02 (Linguistic Constraint Matrix, Cambridge rules, corrections, and XAI):
  1. C-ARTICLE false-positive suppression on uncountable/mass/abstract nouns,
     misspelled/unknown words, and post-auxiliary base verbs — while preserving
     genuine missing-article errors.
  2. High-severity false grammatical rule fixes (C-PREP-GERUND on 'used to',
     C-CONDITIONAL-WILL clause scoping, C-STRANDED-PREP it-clefts & hollow-clause
     adjectives, C-SUBJECT-AGREEMENT infinitival/coordinated-wh clauses,
     C-PREP-PRON-CASE verb particles, C-NOUN-FORM decades, C-ADJ-ADV ordinals,
     C-COMMA-SPLICE colon boundaries) — with positive controls preserved.
  3. Duplicate learner finding suppression in supported_findings().
"""
from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

ROOT = Path(__file__).resolve().parents[1]
SERVER_DIR = ROOT / "server"
if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))

import api  # noqa: E402
import burton_roberts as br  # noqa: E402
import findings as findings_mod  # noqa: E402
import parse_engine  # noqa: E402


def _br_leaves(node: dict) -> list[str]:
    if not node.get("children"):
        w = node.get("word") or node.get("surface") or ""
        return [w] if w else []
    out: list[str] = []
    for ch in node.get("children", []):
        out.extend(_br_leaves(ch))
    return out


def _br_labels(node: dict) -> set[str]:
    labs = {node.get("label")}
    for ch in node.get("children", []):
        labs |= _br_labels(ch)
    return labs


def _matrix_error_codes(sentence: str) -> list[str]:
    payload = api.build_payload(sentence)
    return list(payload.get("summary", {}).get("constraints_fired", []))


class H01BurtonRobertsReliabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        parse_engine.load_models()

    def _project(self, sentence: str) -> dict:
        raw = parse_engine.analyze(sentence)
        return br.normalize_benepar_candidate(raw)

    # --- H01 Root Cause 1: Contraction & hyphenated compound fusion ---
    def test_negative_aux_contraction_fused_and_normalized(self):
        # B-R Fig. [79b]
        out = self._project("He didn't remember kissing Millie.")
        self.assertEqual(out["status"], "normalized")
        leaves = _br_leaves(out["tree"]["root"])
        self.assertIn("didn't", leaves)
        self.assertNotIn("n't", leaves)

    def test_hyphenated_compound_fused_and_so_called_preserved(self):
        out_compound = self._project("second-hand car salesmen")
        self.assertEqual(out_compound["status"], "normalized")
        self.assertIn("second-hand", _br_leaves(out_compound["tree"]["root"]))

        # Negative control: participial 'so-called' keeps DEG + PartP split
        out_part = self._project("That so-called music is awful.")
        self.assertEqual(out_part["status"], "normalized")
        leaves_part = _br_leaves(out_part["tree"]["root"])
        self.assertIn("so", leaves_part)
        self.assertIn("called", leaves_part)

    def test_possessive_clitic_not_fused_into_single_leaf(self):
        # Negative control: B-R Ch. 7 analyzes POSS -> NP + 's
        out = self._project("Larry's cat slept.")
        self.assertEqual(out["status"], "normalized")
        leaves = _br_leaves(out["tree"]["root"])
        self.assertIn("Larry", leaves)
        self.assertIn("'s", leaves)

    # --- H01 Root Cause 2: Previously unresolved B-R constructions ---
    def test_previously_unresolved_constructions_now_normalize(self):
        cases = [
            "His article was accepted and quickly published.",
            "They did not suspect that they were being observed at all.",
            "Otto was driven mad by the noise.",
            "Who is taking Violetta's icon to Athens?",
            "How are you?",
            "Whose is this?",
            "a proposal that we should support the strike",
            "a proposal that we should support",
            "up and down the staircase",
            "all Gulbenkian's contributions to charity",
            "Murtlock having been hospitalised",
            "it isn't my fault Max crushed your monocle",
            "I am surprised Rory has learned so much because he is usually asleep",
            "Vince is taking what to Athens",
            "how many guests to expect",
        ]
        for sentence in cases:
            with self.subTest(sentence=sentence):
                out = self._project(sentence)
                self.assertEqual(
                    out["status"], "normalized",
                    f"Expected normalized for {sentence!r}, got {out.get('reasons')}",
                )

    def test_noun_complement_vs_relative_that_clause(self):
        # Complete noun complement: projects as S-bar (no S-dbar/C2 relative shell)
        comp = self._project("a proposal that we should support the strike")
        self.assertEqual(comp["status"], "normalized")
        comp_labels = _br_labels(comp["tree"]["root"])
        self.assertIn("S-bar", comp_labels)
        self.assertNotIn("S-dbar", comp_labels)

        # Restrictive relative clause: attaches inside NOM (NP -> DET + NOM(NOM + S-dbar))
        # and places 'that' in C2 per B-R Ch9 [53a]
        rel = self._project("a proposal that we should support")
        self.assertEqual(rel["status"], "normalized")
        root = rel["tree"]["root"]
        self.assertEqual([c["label"] for c in root["children"]], ["DET", "NOM"])
        nom_kids = root["children"][1]["children"]
        self.assertEqual([c["label"] for c in nom_kids], ["NOM", "S-dbar"])
        s_dbar = nom_kids[1]
        self.assertEqual(s_dbar["children"][0]["label"], "C2")
        self.assertEqual(_br_leaves(s_dbar["children"][0]), ["that"])

    def test_nonfinite_wh_infinitive_keeps_to_inside_vp(self):
        # B-R Ch10 [37]: 'to' stays as AUX[-tense] inside VP, never inverted into C1
        out = self._project("how many guests to expect")
        self.assertEqual(out["status"], "normalized")
        s_bar = out["tree"]["root"]["children"][1]
        self.assertEqual(s_bar["label"], "S-bar")
        self.assertEqual(_br_leaves(s_bar["children"][0]), [])  # C1 is empty
        self.assertIn("to", _br_leaves(s_bar["children"][1]))  # 'to' inside S/VP

    def test_finite_vp_adjunct_attaches_outside_the_auxiliary_chain(self):
        for sentence, marker, auxiliary in (
            ("The roads will be slippery if it freezes.", "if", "MOD"),
            ("The children are cheering because the team won.", "because", "PROG"),
        ):
            with self.subTest(sentence=sentence):
                tree = self._project(sentence)["tree"]["root"]
                predicate = tree["children"][-1]
                inner, adjunct = predicate["children"]
                self.assertEqual(inner["label"], "VP")
                self.assertEqual(inner["children"][0]["label"], auxiliary)
                self.assertEqual(adjunct["label"], "S-bar")
                self.assertEqual(_br_leaves(adjunct)[0], marker)

    def test_auxiliary_retains_a_selected_embedded_clause(self):
        tree = self._project("The guide will explain whether the trail is open.")["tree"]["root"]
        predicate = tree["children"][-1]
        self.assertEqual([node["label"] for node in predicate["children"]], ["MOD", "VP"])
        self.assertIn("whether", _br_leaves(predicate["children"][1]))

    # --- H01 Root Cause 3: Ch. 7 Appendix D1 of-PP complement attachment ---
    def test_of_pp_complement_attaches_inside_nom_before_premodifier(self):
        out = self._project("that tall student of maths in the hat")
        self.assertEqual(out["status"], "normalized")

        def _has_nom_n_of_pp(node: dict) -> bool:
            if node.get("label") == "NOM":
                kids = node.get("children", [])
                if (len(kids) == 2 and kids[0].get("label") == "N"
                        and _br_leaves(kids[0]) == ["student"]
                        and kids[1].get("label") == "PP"
                        and _br_leaves(kids[1]) == ["of", "maths"]):
                    return True
            return any(_has_nom_n_of_pp(c) for c in node.get("children", []))

        self.assertTrue(
            _has_nom_n_of_pp(out["tree"]["root"]),
            "Expected NOM -> N(student) + PP(of maths) inside outer AP/PP modifiers",
        )


class H02MatrixAndXAIReliabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        parse_engine.load_models()

    # --- H02 Root Cause 1: C-ARTICLE false positives vs. positive controls ---
    def test_article_negative_controls_noncount_misspelled_and_verb(self):
        negative_cases = [
            "I like new stuff.",
            "Genetic manipulation raises ethical questions.",
            "We must end indifference to suffering.",
            "Doing excercise is healthy.",
            "My life has change.",
            "We need major change.",
            "The new policy produced substantial change.",
            "The project involves extensive manipulation of images.",
            "We saw major change in the second quarter.",
            "We discussed the second change.",
        ]
        for sentence in negative_cases:
            with self.subTest(sentence=sentence):
                codes = _matrix_error_codes(sentence)
                self.assertNotIn("C-ARTICLE", codes, f"Unexpected C-ARTICLE on {sentence!r}")

    def test_article_positive_controls_still_detected(self):
        positive_cases = [
            "I saw dog.",
            "She bought book.",
            # Context-sensitive countable uses of dual count/mass nouns
            "We requested second change.",
            "The editor proposed third manipulation.",
        ]
        for sentence in positive_cases:
            with self.subTest(sentence=sentence):
                codes = _matrix_error_codes(sentence)
                self.assertIn("C-ARTICLE", codes, f"Expected C-ARTICLE on {sentence!r}")

    def test_licensing_and_syntactic_accuracy_positive_and_negative_controls(self):
        # Grammatical negative controls (must be grammatical, not unverified/ungrammatical)
        for ok in [
            "The worn blouse was out in the open.",
            "Ann does remember that those skirts that annoyed Kayla stun Dan.",
            "A lot of pants fray.",
        ]:
            with self.subTest(ok=ok):
                payload = api.build_payload(ok)
                self.assertEqual(payload["summary"]["verdict"], "grammatical", payload["summary"])

        # Ungrammatical syntactic positive controls
        bad_cases = [
            ("Rhonda had said that Jesus isn't describing herself.", "C-REFLEXIVE-ANTECEDENT"),
            ("That guy had explained some screen was confusing himself.", "C-REFLEXIVE-ANTECEDENT"),
            ("Robert hasn't talked Brenda.", "C-INTRANSITIVE-OBJECT"),
            ("The portrait resembled.", "C-MISSING-OBJECT"),
            ("The studio announced that the portrait resembled.", "C-MISSING-OBJECT"),
            ("Regina finds out who those museums talk about waiters.", "C-FILLED-GAP"),
            ("Most legislatures that only some spotlights stun might ever collaborate.", "C-NPI-LICENSING"),
            ("Which is Samuel passing high school?", "C-LEFT-BRANCH-ISLAND"),
            ("What did Beverly disgust cashiers and Carla listen to?", "C-COORD-ISLAND"),
            ("Some people can imagine themselves referenced a lot of teachers.", "C-PASSIVE"),
            ("Some library was enjoyable to order this student to escape.", "C-TOUGH-COMPLEMENT"),
            ("He asked me to lent him some money.", "C-TO-BASE"),
            ("But a persons heritage is important.", "C-POSSESSIVE-S"),
        ]
        for sentence, expected_code in bad_cases:
            with self.subTest(sentence=sentence):
                payload = api.build_payload(sentence)
                self.assertEqual(payload["summary"]["verdict"], "ungrammatical")
                self.assertIn(expected_code, payload["summary"]["constraints_fired"])

    def test_valency_depends_on_the_construction(self):
        for sentence in ("The graft took.", "The resin cured.",
                         "The guards talked strategy.", "They talked him into staying."):
            with self.subTest(sentence=sentence):
                codes = _matrix_error_codes(sentence)
                self.assertFalse({"C-MISSING-OBJECT", "C-INTRANSITIVE-OBJECT",
                                  "C-ARTICLE"} & set(codes), codes)

    def test_agreement_feedback_identifies_the_grammatical_relation(self):
        indefinite = api.build_payload("Everyone know the answer.")
        findings = indefinite["learner_analysis"]["findings"]
        reason = next(item["text"] for item in findings if item["constraint"] == "C-INDEFINITE-AGREE")
        self.assertIn("is a singular subject", reason)
        self.assertIn("the form used with 'he', 'she', or 'it'", reason)
        self.assertNotIn("is plural", reason)
        self.assertEqual(indefinite["learner_analysis"]["revision"]["text"], "Everyone knows the answer.")
        relative = api.build_payload("The researchers who works here published a paper.")
        finding = next(item for item in relative["learner_analysis"]["findings"]
                       if item["constraint"] == "C-RELATIVE-AGREE")
        self.assertIn("'who' is the subject", finding["text"])
        self.assertIn("plural antecedent", finding["text"])
        self.assertEqual([relative["parse"]["tokens"][i]["t"] for i in finding["target_token_ids"]], ["works"])
        self.assertEqual([relative["parse"]["tokens"][i]["t"] for i in finding["related_token_ids"]],
                         ["researchers", "who"])
        self.assertEqual(relative["learner_analysis"]["revision"]["text"],
                         "The researchers who work here published a paper.")

    def test_indefinite_agreement_stays_with_the_finite_predicate(self):
        for sentence in ("Someone may not be ready.", "I asked everyone to be ready.",
                         "Everyone who finished can leave.", "None of these candidates are ready.",
                         "I insist that everyone be ready."):
            with self.subTest(sentence=sentence):
                self.assertNotIn("C-INDEFINITE-AGREE", _matrix_error_codes(sentence))
        command = api.build_payload("Everybody stand up!")
        self.assertFalse({"C-INDEFINITE-AGREE", "C-SUBJECT-AGREEMENT"}
                         & set(command["summary"]["constraints_fired"]))
        self.assertIsNone(command["learner_analysis"].get("revision"))
        for sentence in ("Someone are ready.", "Everything look finished."):
            with self.subTest(sentence=sentence):
                self.assertIn("C-INDEFINITE-AGREE", _matrix_error_codes(sentence))

    def test_delay_countability_depends_on_the_noun_phrase(self):
        for sentence in ("The closure caused further delay.", "We reported a second delay."):
            with self.subTest(sentence=sentence):
                self.assertNotIn("C-ARTICLE", _matrix_error_codes(sentence))
        self.assertIn("C-ARTICLE", _matrix_error_codes("We reported second delay."))

    def test_article_correction_can_insert_before_a_witnessed_modifier(self):
        text = "We bought red bicycle."
        payload = api.build_payload(text)
        result = payload["learner_analysis"]
        finding = next(item for item in result["findings"] if item["constraint"] == "C-ARTICLE")
        self.assertEqual([payload["parse"]["tokens"][i]["t"] for i in finding["target_token_ids"]], ["bicycle"])
        self.assertIn("red", [payload["parse"]["tokens"][i]["t"] for i in finding["related_token_ids"]])
        self.assertEqual(result["revision"]["text"], "We bought a red bicycle.")

    def test_coordinated_sva_repair_and_determiner_target_alignment(self):
        # Coordinated VP SVA must repair the disagreeing conjunct ('use' -> 'uses')
        p1 = api.build_payload("Every citizen owns a car and use it daily.")
        self.assertEqual(p1["summary"]["verdict"], "ungrammatical")
        self.assertEqual(
            p1["summary"].get("corrected_sentence"),
            "Every citizen owns a car and uses it daily.",
        )

        # Indefinite 'a' + plural noun ('a test tubes') targets the edited plural noun
        p2 = api.build_payload("Bodies can start their days in a test tubes.")
        self.assertEqual(p2["summary"].get("corrected_sentence"), "Bodies can start their days in a test tube.")
        det_findings = [
            f for f in p2["learner_analysis"]["findings"]
            if f.get("constraint") == "C-DETERMINER-AGREEMENT"
        ]
        self.assertEqual(len(det_findings), 1)
        self.assertEqual(det_findings[0]["target_token_ids"], [8])  # 'tubes'
        self.assertIn(6, det_findings[0]["related_token_ids"])      # 'a'

    # --- H02 Root Cause 2: High-severity false grammatical rules ---
    def test_used_to_passive_and_habitual_not_flagged_but_get_used_to_is(self):
        for ok in [
            "Fire has always been used to prepare the food.",
            "She used to live in London.",
        ]:
            with self.subTest(ok=ok):
                self.assertNotIn("C-PREP-GERUND", _matrix_error_codes(ok))

        for bad in [
            "I look forward to see you.",
            "She got used to wake up early.",
        ]:
            with self.subTest(bad=bad):
                self.assertIn("C-PREP-GERUND", _matrix_error_codes(bad))

    def test_conditional_will_scoped_to_if_clause(self):
        for ok in [
            "If we miss the boat I think we will drown.",
            "Even if today it made laws that would unite it, nobody would obey.",
        ]:
            with self.subTest(ok=ok):
                self.assertNotIn("C-CONDITIONAL-WILL", _matrix_error_codes(ok))

        self.assertIn(
            "C-CONDITIONAL-WILL",
            _matrix_error_codes("If it will rain tomorrow, we will stay inside."),
        )

    def test_stranded_prep_it_cleft_and_hollow_adjective(self):
        for ok in [
            "It's herself that some girl wasn't listening to.",
            "Kristen wasn't ready to return to.",
        ]:
            with self.subTest(ok=ok):
                self.assertNotIn("C-STRANDED-PREP", _matrix_error_codes(ok))

        self.assertIn(
            "C-STRANDED-PREP",
            _matrix_error_codes("Some drivers are apt to listen to."),
        )

    def test_sva_and_prep_pron_case_false_positives_and_controls(self):
        for ok in [
            "What cashiers did Beverly disgust and Carla listen to?",
            "Benjamin does anticipate it to be unexpected that Eva had baked.",
        ]:
            with self.subTest(ok=ok):
                self.assertNotIn("C-SUBJECT-AGREEMENT", _matrix_error_codes(ok))

        self.assertIn("C-SUBJECT-AGREEMENT", _matrix_error_codes("The boys walks."))

        self.assertNotIn(
            "C-PREP-PRON-CASE",
            _matrix_error_codes("Who has every pedestrian figured out she will listen to?"),
        )
        self.assertIn("C-PREP-PRON-CASE", _matrix_error_codes("She gave the book to he."))

    def test_decade_ordinal_and_colon_comma_splice_controls(self):
        self.assertNotIn("C-NOUN-FORM", _matrix_error_codes("In the 1920s people danced."))
        self.assertIn("C-NOUN-FORM", _matrix_error_codes("Two childs played outside."))

        self.assertNotIn("C-ADJ-ADV", _matrix_error_codes("By the 21st century everything changed."))
        self.assertIn("C-ADJ-ADV", _matrix_error_codes("He runs quick."))

        self.assertNotIn(
            "C-COMMA-SPLICE",
            _matrix_error_codes("Television has two effects: First of all, children watch too much."),
        )
        # Negative control: hyphen/dash (PTB tag ':') must NOT reset subordinator scoping
        self.assertNotIn(
            "C-COMMA-SPLICE",
            _matrix_error_codes("Once boxing is banned and no - one accepts it, interest will fade."),
        )
        self.assertIn("C-COMMA-SPLICE", _matrix_error_codes("I went home, she stayed there."))

    # --- H02 Root Cause 3: Duplicate learner findings suppressed ---
    def test_no_duplicate_finite_verb_findings_in_learner_analysis(self):
        payload = api.build_payload(
            "Luckily the most expensive art still being the old, they had to sell it."
        )
        rows = payload.get("learner_analysis", {}).get("findings", [])
        texts = [
            row.get("text")
            for row in rows
            if row.get("constraint") == "C-FINITE-VERB"
        ]
        self.assertGreaterEqual(len(texts), 1)
        self.assertEqual(len(texts), len(set(texts)), f"Duplicate C-FINITE-VERB texts: {texts}")


if __name__ == "__main__":
    unittest.main()
