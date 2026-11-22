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
            "a proposal that we should support the strike",
            "a proposal that we should support",
            "up and down the staircase",
            "all Gulbenkian's contributions to charity",
            "Murtlock having been hospitalised",
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

        # Relative clause with missing object: projects as S-dbar -> C2 + S-bar
        rel = self._project("a proposal that we should support")
        self.assertEqual(rel["status"], "normalized")
        rel_labels = _br_labels(rel["tree"]["root"])
        self.assertIn("S-dbar", rel_labels)
        self.assertIn("C2", rel_labels)

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
        ]
        for sentence in negative_cases:
            with self.subTest(sentence=sentence):
                codes = _matrix_error_codes(sentence)
                self.assertNotIn("C-ARTICLE", codes, f"Unexpected C-ARTICLE on {sentence!r}")

    def test_article_positive_controls_still_detected(self):
        positive_cases = [
            "I saw dog.",
            "She bought book.",
        ]
        for sentence in positive_cases:
            with self.subTest(sentence=sentence):
                codes = _matrix_error_codes(sentence)
                self.assertIn("C-ARTICLE", codes, f"Expected C-ARTICLE on {sentence!r}")

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
