"""Focused tests for the conservative B-R projection and correction alignment.

Run with: python -m unittest server.test_burton_roberts
"""
import unittest
import re

from server.burton_roberts import (
    align_correction,
    build_canonical_analysis,
    canonicalize_gold_record,
    convention_profile,
    normalize_benepar_candidate,
    validate_canonical_tree,
)


def raw_leaf(node_id, pos, word, punct=False):
    return {
        "id": node_id, "type": pos, "pos": pos, "span": [0, 1],
        "surface": word, "punct": punct,
    }


def candidate(sentence="The students laugh.", punctuation=False):
    token_matches = list(re.finditer(r"\w+|[^\w\s]", sentence))
    words = [m.group(0) for m in token_matches]
    np_words = words[:2]
    vp_words = words[2:]
    leaves = []
    for i, word in enumerate(np_words + vp_words):
        is_punct = word in {".", ",", "!", "?"}
        leaves.append(raw_leaf(f"n{i}", "." if is_punct else "NN", word, is_punct))
    return {
        "sentence": sentence,
        "sentence_index": 0,
        "sentences": [{"start": 0, "end": len(sentence), "text": sentence}],
        "tokens": [
            {"i": i, "t": word, "start": token_matches[i].start(),
             "end": token_matches[i].end(),
             "pos": "PUNCT" if word in {".", ",", "!", "?"} else "NOUN",
             "tag": "." if word in {".", ",", "!", "?"} else "NN"}
            for i, word in enumerate(words)
        ],
        "parse_string": "(S (NP ...) (VP ...))",
        "root": {
            "id": "n-root", "type": "S", "span": [0, len(words)],
            "surface": sentence,
            "children": [
                {"id": "n-np", "type": "NP", "span": [0, 2], "surface": "The students",
                 "children": leaves[:2]},
                {"id": "n-vp", "type": "VP", "span": [2, len(words)], "surface": " ".join(vp_words),
                 "children": leaves[2:]},
            ],
        },
    }


def _offset(sentence, token_index):
    parts = sentence.split()
    start = 0
    for i, part in enumerate(parts):
        if i == token_index:
            return start
        start += len(part) + 1
    return start


class ConventionProfileTests(unittest.TestCase):
    def test_chapter_profiles_and_final_profile(self):
        self.assertEqual(convention_profile(7)["version"], "V7")
        self.assertFalse(convention_profile(7)["appendix_nom"])
        self.assertTrue(convention_profile(7, True)["appendix_nom"])
        final = convention_profile()
        self.assertEqual(final["version"], "FINAL")
        self.assertEqual(final["profile_id"], "FINAL-D1")

    def test_invalid_chapter_and_appendix(self):
        with self.assertRaises(ValueError):
            convention_profile(11)
        with self.assertRaises(ValueError):
            convention_profile(6, True)
        with self.assertRaises(ValueError):
            convention_profile(None, False)


class NormalizationTests(unittest.TestCase):
    def test_v2_flat_np_vp_shell_normalizes(self):
        # Use a full sentence without punctuation: V2 projection is deliberately
        # restricted to exact S -> NP VP and two unanalyzed phrase triangles.
        analysis = candidate("The students laugh")
        result = normalize_benepar_candidate(analysis, convention_profile(2))
        self.assertEqual(result["status"], "normalized")
        tree = result["tree"]
        self.assertEqual(tree["root"]["label"], "S")
        self.assertEqual([x["label"] for x in tree["root"]["children"]], ["NP", "VP"])
        self.assertTrue(all(x["triangle"] for x in tree["root"]["children"]))
        self.assertTrue(validate_canonical_tree(tree)["valid"])

    def test_final_profile_is_unresolved_not_relabelled(self):
        result = normalize_benepar_candidate(candidate("The students laugh"), convention_profile())
        self.assertEqual(result["status"], "unresolved")
        self.assertIsNone(result["tree"])
        self.assertIn("PROFILE_MAPPING_NOT_APPROVED", [r["code"] for r in result["reasons"]])
        self.assertIn("raw_candidate_tree", result["diagnostics"])

    def test_punctuation_prevents_unsupported_promotion(self):
        result = normalize_benepar_candidate(candidate("The students laugh."), convention_profile(2))
        self.assertEqual(result["status"], "unresolved")
        self.assertIn("PUNCTUATION_POLICY_UNVERIFIED", [r["code"] for r in result["reasons"]])

    def test_correction_alignment_keeps_edit_types_and_spans(self):
        cases = [
            ("She go home", "She goes home", "substitution"),
            ("They going", "They are going", "insertion"),
            ("She is happy", "She happy", "deletion"),
            ("Hello world.", "Hello, world!", "punctuation"),
            ("I cant go", "I can't go", "contraction"),
            ("They saw it", "They have seen it", "multi_token_replacement"),
        ]
        for original, corrected, expected in cases:
            with self.subTest(original=original, corrected=corrected):
                aligned = align_correction(original, corrected)
                changed = [op for op in aligned["operations"] if op["kind"] != "unchanged"]
                self.assertTrue(changed)
                self.assertIn(expected, [op["kind"] for op in changed])
                for op in changed:
                    self.assertEqual(len(op["original_char_span"]), 2)
                    self.assertEqual(len(op["corrected_char_span"]), 2)

    def test_build_canonical_analysis_carries_diagnostics_and_correction(self):
        correction = {
            "original_sentence": "The students laugh",
            "corrected_sentence": "The student laughs",
            "edits": [{"start": 4, "end": 12, "original": "students", "replacement": "student"}],
        }
        result = build_canonical_analysis(candidate("The students laugh"), chapter=2,
                                          correction=correction)
        self.assertEqual(result["status"], "normalized")
        self.assertIsNotNone(result["diagnostics"]["raw_candidate_tree"])
        self.assertIsNotNone(result["correction_alignment"])
        self.assertEqual(result["correction_alignment"]["source_edits"], correction["edits"])


class GoldFixtureTests(unittest.TestCase):
