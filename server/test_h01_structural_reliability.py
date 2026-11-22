"""Phase VII comprehensive H01 structural reliability and adversarial tests.

Covers all Burton-Roberts FINAL-D1 structural families remediated in the H01
reliability sprint using independent development sentences (0% overlap with
Evaluations V1, V2, or V3), including positive constructions, negative controls,
ambiguous near-neighbors, determinism, terminal-yield preservation, and JSON
Schema 1.1.0 validation.
"""
from __future__ import annotations

import json
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

from jsonschema import Draft202012Validator  # noqa: E402

import burton_roberts as br  # noqa: E402
import parse_engine  # noqa: E402

SCHEMA_VALIDATOR = Draft202012Validator(
    json.loads((ROOT / "docs/canonical-burton-roberts-tree.schema.json").read_text(encoding="utf-8"))
)


def _leaves(node: dict) -> list[str]:
    if node.get("gap") or node.get("empty"):
        return []
    if "word" in node:
        return [node["word"]]
    if node.get("triangle"):
        return list(node.get("words", []))
    out: list[str] = []
    for ch in node.get("children", []):
        out.extend(_leaves(ch))
    return out


def _walk(node: dict):
    yield node
    for ch in node.get("children", []):
        yield from _walk(ch)


def _find(root: dict, label: str | None = None, surface: str | None = None) -> list[dict]:
    out = []
    for n in _walk(root):
        if label is not None and n.get("label") != label:
            continue
        if surface is not None and " ".join(_leaves(n)).lower() != surface.lower():
            continue
        out.append(n)
    return out


def _has_v_sisters(root: dict, verb: str, *sisters: str, feature: str | None = None) -> bool:
    for vp in _find(root, label="VP"):
        kids = vp.get("children", [])
        if not kids or kids[0].get("label") not in {"V", "V(I)", "V(II)"}:
            continue
        if " ".join(_leaves(kids[0])).lower() != verb.lower():
            continue
        if feature and feature not in (kids[0].get("features") or []):
            continue
        got = [" ".join(_leaves(c)).lower() for c in kids[1:]]
        if all(s.lower() in got for s in sisters):
            return True
    return False


def _has_vp_adjunct(root: dict, surface: str) -> bool:
    for vp in _find(root, label="VP"):
        kids = vp.get("children", [])
        if (len(kids) == 2 and kids[0].get("label") == "VP"
                and " ".join(_leaves(kids[1])).lower() == surface.lower()):
            return True
    return False


def _has_s_daughter(root: dict, label: str, surface: str) -> bool:
    for s in _find(root, label="S"):
        for ch in s.get("children", []):
            if ch.get("label") == label and " ".join(_leaves(ch)).lower() == surface.lower():
                return True
    return False


class H01StructuralReliabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        parse_engine.load_models()

    def _analyze_br(self, sentence: str) -> dict:
        parsed = parse_engine.analyze(sentence)
        return br.build_canonical_analysis(parsed, reference_records=[])

    def _assert_normalized_valid(self, sentence: str) -> dict:
        res = self._analyze_br(sentence)
        self.assertEqual(
            res["status"], "normalized",
            f"Expected normalized for {sentence!r}, got {res.get('reasons')}",
        )
        tree = res["tree"]
        self.assertIsNotNone(tree)
        errors = list(SCHEMA_VALIDATOR.iter_errors(tree))
        self.assertEqual(errors, [], f"Schema errors on {sentence!r}: {errors}")
        self.assertTrue(br.validate_canonical_tree(tree)["valid"])
        expected_tokens = [tok["text"].lower() for tok in tree["tokens"]]
        actual_leaves = [w.lower() for w in _leaves(tree["root"])]
        self.assertEqual(actual_leaves, expected_tokens, f"Yield mismatch on {sentence!r}")
        return tree["root"]

    # --- A. Gerundial complements vs nominal gerunds & negative controls ---
    def test_gerundial_subject_control_and_free_control_complements(self):
        for sent, verb, comp in [
            ("Elena contemplated leaving the firm.", "contemplated", "leaving the firm"),
            ("Marcus admitted breaking the lantern.", "admitted", "breaking the lantern"),
            ("The pilot postponed crossing the channel.", "postponed", "crossing the channel"),
        ]:
            with self.subTest(sentence=sent):
                root = self._assert_normalized_valid(sent)
                self.assertTrue(_has_v_sisters(root, verb, comp))
                self.assertTrue(_find(root, "S-bar", comp), "Gerundial complement must be S-bar, not NP")
                self.assertTrue(any(n.get("gap") and n.get("index") == 1 for n in _walk(root)))

        # Free-control clausal gerund under 'forbid' has unindexed covert subject
        free_root = self._assert_normalized_valid("The bylaw forbids entering the tunnel.")
        self.assertTrue(_find(free_root, "S-bar", "entering the tunnel"))
        self.assertTrue(any(n.get("gap") and n.get("index") is None for n in _walk(free_root)))

        # Nominal gerund contrast stays an NP object
        nom_root = self._assert_normalized_valid("The bylaw forbids parking beside the entrance.")
        self.assertTrue(_has_v_sisters(nom_root, "forbids", "parking beside the entrance", feature="trans"))

        # Negative control: gerund-only verb with subjectless to-infinitive stays unresolved
        bad = self._analyze_br("Elena contemplated to leave the firm.")
        self.assertEqual(bad["status"], "unresolved")

    # --- B & E. Fronted constituents, coordinated NMLs, and mixed coordinated subjects ---
    def test_fronted_temporal_nps_and_coordinated_nominals(self):
        for sent, fronted, coord_n in [
            ("The next morning, Clara studied the trade and tariff agreements in detail.",
             "The next morning", "trade and tariff"),
            ("Last winter, the council revised its water and energy policies without delay.",
             "Last winter", "water and energy"),
            ("One rainy afternoon, Devon signed the Parks and Wildlife Charter on site.",
             "One rainy afternoon", "Parks and Wildlife"),
        ]:
            with self.subTest(sentence=sent):
                root = self._assert_normalized_valid(sent)
                self.assertTrue(_has_s_daughter(root, "NP", fronted))
                self.assertTrue(_find(root, "N", coord_n))

        # Shared possessive determiner over coordinated NOM (B-R Ch. 7 pp. 142-144)
        for sent, adv, nom_text in [
            ("Unfortunately, his singing and loud laughter are disturbing the neighbours.",
             "Unfortunately", "singing and loud laughter"),
            ("Surprisingly, their research and field trials have impressed the board.",
             "Surprisingly", "research and field trials"),
        ]:
            with self.subTest(sentence=sent):
                root = self._assert_normalized_valid(sent)
                self.assertTrue(_has_s_daughter(root, "AdvP", adv))
                self.assertTrue(_find(root, "NOM", nom_text))

        # Bare gerund coordinated with NP in subject position
        mixed_root = self._assert_normalized_valid("Swimming and fresh air improved his stamina.")
        self.assertTrue(_find(mixed_root, "NP", "Swimming and fresh air"))

    # --- C. Subject-wh vs object-wh questions ---
    def test_subject_wh_vs_object_wh_questions(self):
        prog = self._assert_normalized_valid("Who was shouting?")
        self.assertEqual(prog["label"], "S-dbar")
        self.assertTrue(_find(prog, "C1", "was"))
        self.assertTrue(_find(prog, "PROG"))

        perf = self._assert_normalized_valid("What has happened?")
        self.assertEqual(perf["label"], "S-dbar")
        self.assertTrue(_find(perf, "C1", "has"))
        self.assertTrue(_find(perf, "PERF"))

        lex = self._assert_normalized_valid("Who laughed?")
        self.assertEqual(lex["label"], "S-dbar")
        self.assertTrue(any(n.get("label") == "C1" and n.get("empty") for n in _walk(lex)))

        pass_q = self._assert_normalized_valid("Who was invited?")
        self.assertEqual(pass_q["label"], "S-dbar")
        self.assertTrue(_find(pass_q, "C1", "was"))
        self.assertTrue(_find(pass_q, "PASS"))

        complex_subj = self._assert_normalized_valid("Which guests were waiting outside?")
        self.assertEqual(complex_subj["label"], "S-dbar")
        self.assertTrue(_find(complex_subj, "C1", "were"))

        obj_q = self._assert_normalized_valid("Who did Clara invite?")
        self.assertEqual(obj_q["label"], "S-dbar")
        self.assertTrue(_find(obj_q, "C1", "did"))
        self.assertTrue(_find(obj_q, "TENSE"))

        # Long-distance embedded subject-wh extraction with matrix aux inversion
        ld_subj = self._assert_normalized_valid("Who did she notice was leading the procession?")
        self.assertEqual(ld_subj["label"], "S-dbar")
        self.assertTrue(_find(ld_subj, "C1", "did"))
        self.assertTrue(_find(ld_subj, "PROG", "was"))

    # --- D & F. Stranded prepositions, long-distance extraction, and passive wh ---
    def test_stranded_prepositions_active_and_passive(self):
        # Active transitive + direct object + stranded adjunct PP (wh is NOT direct object)
        for sent, verb, dobj, prep in [
            ("Which key did Nora open the cabinet with?", "open", "the cabinet", "with"),
            ("Whose notebook did he copy the diagram from?", "copy", "the diagram", "from"),
            ("Which brush did the artist paint the ceiling with yesterday?", "paint", "the ceiling", "with"),
            ("Whose knife do you think he sliced the bread with?", "sliced", "the bread", "with"),
        ]:
            with self.subTest(sentence=sent):
                root = self._assert_normalized_valid(sent)
                self.assertEqual(root["label"], "S-dbar")
                self.assertTrue(_has_v_sisters(root, verb, dobj, feature="trans"))
                self.assertTrue(_has_vp_adjunct(root, prep))

        # Benefactive for-ditransitive with stranded preposition
        ben = self._assert_normalized_valid("Who did Daniel bake the tart for?")
        self.assertTrue(_has_v_sisters(ben, "bake", "the tart", "for", feature="ditrans"))

        # Passive wh-interrogatives with non-overlapping passive + wh gaps
        p_to = self._assert_normalized_valid("Who was the parcel sent to?")
        self.assertTrue(_find(p_to, "PASS"))
        self.assertTrue(_has_v_sisters(p_to, "sent", "to", feature="ditrans"))

        p_for = self._assert_normalized_valid("Who was the ticket reserved for?")
        self.assertTrue(_find(p_for, "PASS"))
        self.assertTrue(_has_v_sisters(p_for, "reserved", "for", feature="ditrans"))

        p_loc = self._assert_normalized_valid("Which shelf was the sculpture placed on?")
        self.assertTrue(_find(p_loc, "PASS"))
        self.assertTrue(_has_v_sisters(p_loc, "placed", "on", feature="complex"))

        p_adj = self._assert_normalized_valid("Which saw was the timber cut with?")
        self.assertTrue(_find(p_adj, "PASS"))
        self.assertTrue(_has_vp_adjunct(p_adj, "with"))

        p_dob = self._assert_normalized_valid("What were the winners awarded?")
        self.assertTrue(_find(p_dob, "PASS"))
        self.assertTrue(any(n.get("label") == "V" and "ditrans" in (n.get("features") or []) for n in _walk(p_dob)))

    # --- G. Discontinuous / extraposed noun complements vs propositional objects ---
    def test_extraposed_noun_complements_and_negative_control(self):
        r1 = self._assert_normalized_valid("The suspicion arose in court that the ledger had been altered.")
        self.assertTrue(_has_s_daughter(r1, "S-bar", "that the ledger had been altered"))
        self.assertFalse(_has_v_sisters(r1, "arose", "that the ledger had been altered"))

        r2 = self._assert_normalized_valid("News spread rapidly that the tunnel had reopened.")
        self.assertTrue(_has_s_daughter(r2, "S-bar", "that the tunnel had reopened"))
        self.assertTrue(any("intrans" in (n.get("features") or []) for n in _find(r2, "V", "spread")))

        r3 = self._assert_normalized_valid("The possibility remains that the crew will finish the clearing up.")
        self.assertTrue(_has_s_daughter(r3, "S-bar", "that the crew will finish the clearing up"))
        self.assertTrue(_find(r3, "N", "clearing up"))

        # Negative control: propositional transitive verb keeps that-clause inside VP
        neg = self._assert_normalized_valid("The report confirmed that the ferry had departed.")
        self.assertFalse(_has_s_daughter(neg, "S-bar", "that the ferry had departed"))
        self.assertTrue(_has_v_sisters(neg, "confirmed", "that the ferry had departed", feature="trans"))

    # --- H. Embedded wh-interrogatives & structural ambiguity preservation ---
    def test_embedded_wh_nonfinite_extraction_and_ambiguity_guard(self):
        # Unambiguous Type I ECM subject extraction (overt object blocks object gap)
        r1 = self._assert_normalized_valid("She asked who the committee expected to chair the meeting.")
        self.assertTrue(any(n.get("label") == "V(I)" and _leaves(n) == ["expected"] for n in _walk(r1)))
        self.assertTrue(_has_v_sisters(r1, "chair", "the meeting", feature="trans"))

        # Unambiguous Type I ECM subject extraction ('believe' is not subject-control)
        r2 = self._assert_normalized_valid("Who do you believe to be responsible?")
        self.assertTrue(any(n.get("label") == "V(I)" and _leaves(n) == ["believe"] for n in _walk(r2)))

        # Unambiguous subject-control object extraction ('choose' is not Type I)
        r3 = self._assert_normalized_valid("I wonder who the coach chose to replace.")
        self.assertTrue(any(n.get("label") == "V" and _leaves(n) == ["replace"]
                            and "trans" in (n.get("features") or []) for n in _walk(r3)))

        # Genuinely ambiguous: Type I ECM subject extraction vs subject-control object extraction
        ambig = self._analyze_br("I wonder who the men wanted to help.")
        self.assertEqual(ambig["status"], "unresolved")
        self.assertEqual(ambig["reasons"][0]["code"], "STRUCTURAL_AMBIGUITY")
        self.assertTrue(ambig.get("ambiguous"))
        self.assertGreaterEqual(len(ambig.get("alternative_readings", [])), 2)

        # Classic Burton-Roberts Ch. 4 [52b] ditransitive vs complex ambiguity
        find_ambig = self._analyze_br("Max found Bill an amusing companion.")
        self.assertEqual(find_ambig["status"], "unresolved")
        self.assertEqual(find_ambig["reasons"][0]["code"], "STRUCTURAL_AMBIGUITY")

    # --- I. Sentential relative clauses vs NP-modifying relative clauses ---
    def test_sentential_vs_np_modifying_relative_clauses(self):
        for sent, rel_text in [
            ("The train arrived early, which nobody had expected.", "which nobody had expected"),
            ("She passed all the exams, which was astonishing.", "which was astonishing"),
        ]:
            with self.subTest(sentence=sent):
                root = self._assert_normalized_valid(sent)
                self.assertTrue(_has_s_daughter(root, "S-dbar", rel_text))
                # Relative clause C1 must stay empty (no false auxiliary fronting)
                s_dbar = _find(root, "S-dbar", rel_text)[0]
                c1_nodes = _find(s_dbar, "C1")
                self.assertTrue(c1_nodes and c1_nodes[0].get("empty"))

        # NP-modifying non-restrictive relative stays inside NP
        np_rel = self._assert_normalized_valid("Milo bought the bicycles, which were expensive.")
        self.assertFalse(_has_s_daughter(np_rel, "S-dbar", "which were expensive"))
        self.assertTrue(any(n.get("label") == "NP" and "which were expensive" in " ".join(_leaves(n))
                            for n in _walk(np_rel)))

    # --- Phase III. Complement vs. adjunct vs. NP-modifier selection ---
    def test_pp_complement_vs_adjunct_vs_np_modifier_distinctions(self):
        # Animate benefactive for-ditransitives
        for sent, verb, dobj, pp in [
            ("Nadia saved a seat for Owen.", "saved", "a seat", "for Owen"),
            ("Claire reserved a room for Dr. Patel.", "reserved", "a room", "for Dr. Patel"),
            ("She found a coat for her sister.", "found", "a coat", "for her sister"),
        ]:
            with self.subTest(sentence=sent):
                root = self._assert_normalized_valid(sent)
                self.assertTrue(_has_v_sisters(root, verb, dobj, pp, feature="ditrans"))

        # Duration/temporal 'for'-PP is an adjunct (NEVER ditransitive)
        dur = self._assert_normalized_valid("Daniel baked a loaf for two hours.")
        self.assertTrue(_has_v_sisters(dur, "baked", "a loaf", feature="trans"))
        self.assertTrue(_has_vp_adjunct(dur, "for two hours"))

        temp = self._assert_normalized_valid("He left a note for the morning.")
        self.assertTrue(_has_v_sisters(temp, "left", "a note", feature="trans"))
        self.assertTrue(_has_vp_adjunct(temp, "for the morning"))

        # NP-internal 'for'-complement stays inside NP (NEVER ditransitive)
        ticket = self._assert_normalized_valid("Hannah bought a ticket for the opera.")
        self.assertTrue(_has_v_sisters(ticket, "bought", "a ticket for the opera", feature="trans"))

        eve = self._assert_normalized_valid("Nadia saved a seat for the evening.")
        self.assertFalse(any("ditrans" in (n.get("features") or []) for n in _find(eve, "V")))

        # Animate recipient 'to'-PP vs inanimate geographical GPE directional adjunct
        recip = self._assert_normalized_valid("Trevor mailed three parcels to his cousin.")
        self.assertTrue(_has_v_sisters(recip, "mailed", "three parcels", "to his cousin", feature="ditrans"))

        geo = self._assert_normalized_valid("Trevor mailed three parcels to Lisbon.")
        self.assertTrue(_has_v_sisters(geo, "mailed", "three parcels", feature="trans"))
        self.assertTrue(_has_vp_adjunct(geo, "to Lisbon"))

        # Institutional recipient ('the museum') preserves ditransitivity (B-R Ch. 5 Ex. 2d)
        inst = self._assert_normalized_valid("They sold the sketches to the museum.")
        self.assertTrue(_has_v_sisters(inst, "sold", "the sketches", "to the museum", feature="ditrans"))

        # Complex-transitive locative complement
        loc = self._assert_normalized_valid("Owen placed the compass on the map.")
        self.assertTrue(_has_v_sisters(loc, "placed", "the compass", "on the map", feature="complex"))

    # --- Determinism check ---
    def test_projection_is_byte_deterministic(self):
        for sent in [
            "Elena contemplated leaving the firm.",
            "Which key did Nora open the cabinet with?",
            "Who was the parcel sent to?",
            "The suspicion arose in court that the ledger had been altered.",
            "She passed all the exams, which was astonishing.",
        ]:
            r1 = json.dumps(self._analyze_br(sent)["tree"], sort_keys=True)
            r2 = json.dumps(self._analyze_br(sent)["tree"], sort_keys=True)
            self.assertEqual(r1, r2)


if __name__ == "__main__":
    unittest.main()
