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

    def test_sentence_final_punctuation_is_not_fabricated_as_a_phrase_marker_node(self):
        result = normalize_benepar_candidate(candidate("The students laugh."), convention_profile(2))
        self.assertEqual(result["status"], "normalized", result.get("reasons"))
        self.assertEqual([row["text"] for row in result["tree"]["tokens"]],
                         ["The", "students", "laugh"])
        self.assertEqual(result["tree"]["sentence"], "The students laugh.")

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
    def test_chapter_7_gold_tree_projects_without_rewriting_source(self):
        record = {
            "id": "ch7-3", "fig": "[3]", "page": 141,
            "sentence": "the clowns", "status": "IMG", "appendix_nom": False,
            "tree": {
                "label": "NP", "children": [
                    {"label": "DET", "children": [{"label": "ART", "children": [{"word": "the"}]}]},
                    {"label": "NOM", "children": [{"label": "N", "children": [{"word": "clowns"}]}]},
                ],
            },
        }
        source_copy = repr(record)
        result = canonicalize_gold_record(record, {"chapter": 7})
        self.assertEqual(result["status"], "normalized")
        self.assertTrue(validate_canonical_tree(result["tree"])["valid"])
        self.assertEqual(result["tree"]["source"]["printed_page"], 141)
        self.assertEqual(result["tree"]["source"]["evidence_status"], "IMG")
        self.assertEqual(repr(record), source_copy)

    def test_future_label_in_early_chapter_is_rejected(self):
        envelope = {
            "schema_version": "1.0.0", "tree_id": "bad", "tokens": [
                {"index": 0, "text": "the", "char_span": [0, 3]},
            ],
            "sentence": "the", "convention_profile": convention_profile(6),
            "source": {"book": "Burton-Roberts", "chapter": 6, "evidence_status": "IMG"},
            "root": {"id": "r", "label": "NP", "children": [
                {"id": "n", "label": "NOM", "children": [
                    {"id": "w", "word": "the", "token_span": [0, 1]},
                ]},
            ], "token_span": [0, 1]},
            "movement": [], "accepted_alternatives": [],
        }
        validation = validate_canonical_tree(envelope)
        self.assertFalse(validation["valid"])
        self.assertTrue(any("before its introduction" in e for e in validation["errors"]))

    def test_non_tree_alternative_is_preserved_and_reported_unresolved(self):
        record = {
            "id": "ch9-test", "sentence": "they spoke", "status": "IMG",
            "tree": {"label": "S", "children": [{"word": "they"}, {"word": "spoke"}]},
            "accepted_alternatives": [{"wh_gap_category": "PP", "note": "source alternative"}],
        }
        result = canonicalize_gold_record(record, {"chapter": 9})
        self.assertEqual(result["status"], "unresolved")
        self.assertTrue(any("has no tree shape" in e for e in result["errors"]))
        self.assertTrue(any("unmaterialized_accepted_alternative" in n
                            for n in result["partial_tree"]["notes"]))

    def test_gap_index_features_and_elided_terminal_are_preserved(self):
        record = {
            "id": "ch10-gap", "sentence": "Murtlock was taken", "status": "IMG",
            "tree": {
                "label": "S", "children": [
                    {"label": "NP", "children": [
                        {"label": "N", "index": 1, "children": [{"word": "Murtlock"}]},
                    ]},
                    {"label": "VP", "children": [
                        {"label": "PASS", "features": ["past"], "children": [{"word": "was"}]},
                        {"label": "VP", "children": [
                            {"label": "V", "children": [{"word": "taken"}]},
                            {"gap": True, "index": 1},
                        ]},
                    ]},
                ],
            },
        }
        result = canonicalize_gold_record(record, {"chapter": 10})
        self.assertEqual(result["status"], "normalized")
        root = result["tree"]["root"]
        self.assertEqual(root["children"][0]["children"][0]["index"], 1)
        gap = root["children"][1]["children"][1]["children"][1]
        self.assertEqual(gap, {"id": "ch10-gap-root-1-1-1", "gap": True, "index": 1})

    def test_elided_terminal_is_not_counted_as_overt_token(self):
        record = {
            "id": "ch8-elided", "sentence": "I said it", "status": "IMG",
            "tree": {"label": "S", "children": [
                {"word": "I"}, {"word": "that", "elided": True},
                {"word": "said"}, {"word": "it"},
            ]},
        }
        result = canonicalize_gold_record(record, {"chapter": 8})
        self.assertEqual(result["status"], "normalized")
        self.assertEqual([t["text"] for t in result["tree"]["tokens"]], ["I", "said", "it"])
        self.assertTrue(result["tree"]["root"]["children"][1]["elided"])

    def test_actual_chapter_10_index_and_controller_pattern(self):
        record = {
            "id": "ch10-14a", "fig": "[14a]", "page": 228,
            "sentence": "loaded to capacity", "status": "IMG",
            "tree": {"label": "S", "children": [
                {"label": "NP", "children": [{"gap": True, "index": 1}]},
                {"label": "VP", "children": [
                    {"label": "VP", "children": [
                        {"label": "V", "features": ["trans", "-tense"],
                         "children": [{"word": "loaded"}]},
                        {"label": "NP", "children": [{"gap": True, "index": 1}]},
                    ]},
                    {"label": "PP", "triangle": True,
                     "words": ["to", "capacity"]},
                ]},
            ]},
            "note": "The passive participle licenses subject and object gaps.",
            "clause_id": "S2",
            "external_controller": {"index": 1, "controller": "the palanquin",
                                     "source": "Ch10 [14], printed p.227"},
        }
        result = canonicalize_gold_record(record, {"chapter": 10})
        self.assertEqual(result["status"], "normalized", result.get("errors"))
        envelope = result["tree"]
        self.assertEqual(envelope["movement"], [{
            "kind": "external_controller", "index": 1,
            "controller": "the palanquin", "source_ref": "Ch10 [14], printed p.227",
        }])
        self.assertEqual(envelope["root"]["children"][1]["children"][0]["children"][1]["children"][0]["index"], 1)
        self.assertTrue(validate_canonical_tree(envelope)["valid"])

    def test_chapter_9_movement_is_preserved_without_invented_node_links(self):
        record = {
            "id": "ch9-11b", "fig": "[11b]", "page": 199,
            "sentence": "what is Vince taking to Athens", "status": "IMG",
            "tree": {"label": "S-dbar", "children": [
                {"label": "C2", "children": [{"word": "what"}]},
                {"label": "S-bar", "children": [
                    {"label": "C1", "children": [{"word": "is"}]},
                    {"label": "S", "children": [
                        {"label": "NP", "triangle": True, "words": ["Vince"]},
                        {"label": "VP", "children": [
                            {"label": "VP", "children": [
                                {"label": "PROG", "features": ["pres"],
                                 "children": [{"gap": True}]},
                                {"label": "VP", "children": [
                                    {"label": "V", "features": ["trans"],
                                     "children": [{"word": "taking"}]},
                                    {"label": "NP", "children": [{"gap": True}]},
                                ]},
                            ]},
                            {"label": "PP", "triangle": True, "words": ["to", "Athens"]},
                        ]},
                    ]},
                ]},
            ]},
            "movement": [
                {"from": "direct-object NP", "to": "C2"},
                {"from": "PROG auxiliary position", "to": "C1"},
            ],
            "wh_gap_category": "NP",
            "surface_from_tree": "what is Vince taking to Athens",
        }
        result = canonicalize_gold_record(record, {"chapter": 9})
        self.assertEqual(result["status"], "normalized", result.get("errors"))
        movements = result["tree"]["movement"]
        self.assertEqual(len(movements), 2)
        self.assertTrue(all(x["kind"] == "movement" for x in movements))
        self.assertTrue(all("source_ref" in x and "note" in x for x in movements))
        self.assertTrue(any(x.startswith("source_metadata:wh_gap_category=")
                            for x in result["tree"]["notes"]))
        self.assertTrue(any(x.startswith("source_metadata:surface_from_tree=")
                            for x in result["tree"]["notes"]))

    def test_multiple_external_controllers_are_preserved(self):
        record = {
            "id": "ch10-controller-pairs", "sentence": "expect", "status": "IMG",
            "tree": {"label": "S", "children": [
                {"label": "NP", "children": [{"gap": True, "index": 1}]},
                {"label": "VP", "children": [
                    {"label": "V", "features": ["trans"],
                     "children": [{"word": "expect"}]},
                    {"label": "NP", "children": [{"gap": True, "index": 2}]},
                ]},
            ]},
            "external_controllers": [
                {"index": 1, "controller": "Alex", "source": "Ch10 source A"},
                {"index": 2, "controller": "what", "source": "Ch10 source B"},
            ],
            "interpretation": "two indexed controllers",
        }
        result = canonicalize_gold_record(record, {"chapter": 10})
        self.assertEqual(result["status"], "normalized", result.get("errors"))
        rows = result["tree"]["movement"]
        self.assertEqual([x["index"] for x in rows], [1, 2])
        self.assertTrue(all(x["kind"] == "external_controller" for x in rows))
        self.assertTrue(any(x.startswith("source_metadata:interpretation=")
                            for x in result["tree"]["notes"]))

    def test_alternative_tree_is_validated_and_kept(self):
        record = {
            "id": "ch7-alt", "sentence": "the clowns", "status": "IMG",
            "tree": {"label": "NP", "children": [
                {"label": "DET", "children": [{"label": "ART", "children": [{"word": "the"}]}]},
                {"label": "NOM", "children": [{"label": "N", "children": [{"word": "clowns"}]}]},
            ]},
            "accepted_alternatives": [{
                "label": "Alternative NP analysis", "acceptance": "ACCEPTED",
                "tree": {"label": "NP", "children": [
                    {"label": "DET", "children": [{"label": "ART", "children": [{"word": "the"}]}]},
                    {"label": "NOM", "children": [{"label": "N", "children": [{"word": "clowns"}]}]},
                ]},
            }],
        }
        result = canonicalize_gold_record(record, {"chapter": 7})
        self.assertEqual(result["status"], "normalized")
        self.assertEqual(len(result["tree"]["accepted_alternatives"]), 1)
        self.assertTrue(validate_canonical_tree(result["tree"])["valid"])


class CanonicalHardeningTests(unittest.TestCase):
    def test_profile_identity_and_refinement_are_consistent(self):
        invalid_profiles = [
            {**convention_profile(6), "appendix_nom": False},
            {**convention_profile(7), "profile_id": "V6"},
            {**convention_profile(), "appendix_nom": False},
            {**convention_profile(2), "unexpected": "value"},
        ]
        for profile in invalid_profiles:
            with self.subTest(profile=profile):
                result = normalize_benepar_candidate(candidate("The students laugh"), profile)
                self.assertEqual(result["status"], "rejected")
                self.assertTrue(any(row["code"] == "INVALID_PROFILE"
                                    for row in result["reasons"]))

    def test_future_label_in_triangle_is_rejected(self):
        envelope = {
            "schema_version": "1.0.0", "tree_id": "future-triangle",
            "sentence": "the", "tokens": [
                {"index": 0, "text": "the", "char_span": [0, 3]},
            ],
            "convention_profile": convention_profile(6),
            "source": {"book": "Burton-Roberts", "chapter": 6, "evidence_status": "IMG"},
            "root": {"id": "r", "label": "NP", "token_span": [0, 1], "children": [
                {"id": "t", "label": "NOM", "triangle": True, "words": ["the"],
                 "token_span": [0, 1]},
            ]},
            "movement": [], "accepted_alternatives": [],
        }
        result = validate_canonical_tree(envelope)
        self.assertFalse(result["valid"])
        self.assertTrue(any("before its introduction" in error for error in result["errors"]))

    def test_falsey_non_array_features_are_not_treated_as_empty(self):
        envelope = {
            "schema_version": "1.0.0", "tree_id": "bad-features",
            "sentence": "the", "tokens": [
                {"index": 0, "text": "the", "char_span": [0, 3]},
            ],
            "convention_profile": convention_profile(2),
            "source": {"book": "Burton-Roberts", "chapter": 2, "evidence_status": "IMG"},
            "root": {"id": "r", "label": "NP", "features": {},
                     "token_span": [0, 1], "children": [
                {"id": "w", "word": "the", "token_span": [0, 1]},
            ]},
            "movement": [], "accepted_alternatives": [],
        }
        result = validate_canonical_tree(envelope)
        self.assertFalse(result["valid"])
        self.assertTrue(any("features must be an array" in error for error in result["errors"]))

    def test_boolean_token_coordinates_are_rejected(self):
        envelope = {
            "schema_version": "1.0.0", "tree_id": "bool-span",
            "sentence": "the", "tokens": [
                {"index": 0, "text": "the", "char_span": [0, 3]},
            ],
            "convention_profile": convention_profile(2),
            "source": {"book": "Burton-Roberts", "chapter": 2, "evidence_status": "IMG"},
            "root": {"id": "r", "label": "NP", "children": [
                {"id": "w", "word": "the", "token_span": [False, 1]},
            ]},
            "movement": [], "accepted_alternatives": [],
        }
        result = validate_canonical_tree(envelope)
        self.assertFalse(result["valid"])
        self.assertTrue(any("two-integer half-open span" in error for error in result["errors"]))

    def test_importer_preserves_diagram_refs_and_multiword_terminal_metadata(self):
        record = {
            "id": "ch5-source-metadata", "sentence": "They gave in", "status": "IMG",
            "tree": {"label": "S", "children": [
                {"label": "NP", "triangle": True, "words": ["They"]},
                {"label": "VP", "ref": "VP1", "children": [
                    {"label": "V", "features": ["intrans", "phrasal"], "children": [
                        {"word": "gave in", "multiword": True},
                    ]},
                ]},
            ]},
        }
        result = canonicalize_gold_record(record, {"chapter": 5})
        self.assertEqual(result["status"], "normalized", result.get("errors"))
        vp = result["tree"]["root"]["children"][1]
        verb = vp["children"][0]
        terminal = verb["children"][0]
        self.assertEqual(vp["source_refs"], ["VP1"])
        self.assertTrue(any(note.startswith("source_node_metadata:multiword=")
                            for note in terminal.get("notes", [])))

    def test_importer_preserves_gap_symbols_and_verb_type_metadata(self):
        gap_record = {
            "id": "ch6-gap-symbol", "sentence": "I left", "status": "IMG",
            "tree": {"label": "S", "children": [
                {"label": "NP", "triangle": True, "words": ["I"]},
                {"label": "VP", "children": [
                    {"label": "V", "features": ["intrans"], "children": [{"word": "left"}]},
                    {"gap": True, "symbol": "•"},
                ]},
            ]},
        }
        gap_result = canonicalize_gold_record(gap_record, {"chapter": 6})
        self.assertEqual(gap_result["status"], "normalized", gap_result.get("errors"))
        gap = gap_result["tree"]["root"]["children"][1]["children"][1]
        self.assertTrue(any("source_node_metadata:symbol=" in note
                            for note in gap.get("notes", [])))

        verb_record = {
            "id": "ch10-verb-type", "sentence": "Alice walks", "status": "IMG",
            "tree": {"label": "S", "children": [
                {"label": "NP", "triangle": True, "words": ["Alice"]},
                {"label": "VP", "children": [
                    {"label": "V", "features": ["intrans"], "verb_type": "I",
                     "children": [{"word": "walks"}]},
                ]},
            ]},
        }
        verb_result = canonicalize_gold_record(verb_record, {"chapter": 10})
        self.assertEqual(verb_result["status"], "normalized", verb_result.get("errors"))
        verb = verb_result["tree"]["root"]["children"][1]["children"][0]
        self.assertTrue(any("source_node_metadata:verb_type=" in note
                            for note in verb.get("notes", [])))


    def test_zero_word_elision_marker_is_unresolved_not_recast_as_a_gap(self):
        record = {
            "id": "ch5-46", "sentence": "William gave some bleach", "status": "IMG",
            "tree": {"label": "S", "children": [
                {"label": "NP", "triangle": True, "words": ["William"]},
                {"label": "VP", "children": [
                    {"label": "V", "features": ["ditrans"], "children": [{"word": "gave"}]},
                    {"label": "NP", "children": [{"elided": True, "symbol": "E"}]},
                    {"label": "NP", "triangle": True, "words": ["some", "bleach"]},
                ]},
            ]},
        }
        result = canonicalize_gold_record(record, {"chapter": 5})
        self.assertEqual(result["status"], "unresolved")
        self.assertTrue(any("elided-element marker" in error for error in result["errors"]))
        self.assertEqual(result["raw_tree"], record["tree"])


    def test_node_provenance_fields_require_string_arrays(self):
        envelope = {
            "schema_version": "1.0.0", "tree_id": "bad-provenance",
            "sentence": "the", "tokens": [
                {"index": 0, "text": "the", "char_span": [0, 3]},
            ],
            "convention_profile": convention_profile(2),
            "source": {"book": "Burton-Roberts", "chapter": 2, "evidence_status": "IMG"},
            "root": {"id": "r", "label": "NP", "source_refs": "not-an-array",
                     "children": [{"id": "w", "word": "the", "token_span": [0, 1]}]},
            "movement": [], "accepted_alternatives": [],
        }
        result = validate_canonical_tree(envelope)
        self.assertFalse(result["valid"])
        self.assertTrue(any("source_refs must be an array of strings" in error
                            for error in result["errors"]))


if __name__ == "__main__":
    unittest.main()
