"""Model-free tests for B-R normalization, validation, and correction alignment."""
import unittest
from br_tree import build_correction_alignment, normalize_candidate, validate_tree


class BrTreeTests(unittest.TestCase):
    @staticmethod
    def token(i, word, start):
        return {"i": i, "t": word, "start": start, "end": start + len(word)}

    def test_v2_supported_top_level_mapping(self):
        sentence = "The birds sing."
        tokens = [self.token(0, "The", 0), self.token(1, "birds", 4),
                  self.token(2, "sing", 10), self.token(3, ".", 14)]
        candidate = {"id": "n0", "type": "S", "span": [0, 4], "surface": sentence,
                     "children": [
                         {"id": "n1", "type": "NP", "span": [0, 2], "surface": "The birds",
                          "children": [{"id": "n2", "type": "DT", "surface": "The"},
                                       {"id": "n3", "type": "NNS", "surface": "birds"}]},
                         {"id": "n4", "type": "VP", "span": [2, 3], "surface": "sing",
                          "children": [{"id": "n5", "type": "VBP", "surface": "sing"}]},
                         {"id": "n6", "type": ".", "surface": ".", "punct": True},
                     ]}
        result = normalize_candidate(candidate, tokens, sentence, "V2", [])
        self.assertEqual(result["status"], "normalized")
        self.assertEqual(result["source"]["method"], "supported_v2_top_level_mapping")
        self.assertEqual([x["label"] for x in result["tree"]["children"]], ["NP", "VP"])
        self.assertTrue(all(x["triangle"] for x in result["tree"]["children"]))
        self.assertEqual(validate_tree(result["tree"], "V2", ["the", "birds", "sing"]), [])

    def test_v10_unmapped_candidate_is_unresolved(self):
        result = normalize_candidate({"id": "n0", "type": "S", "children": []},
                                     [], "An unmapped sentence.", "V10", [])
        self.assertEqual(result["status"], "unresolved")
        self.assertIsNone(result["tree"])
        self.assertEqual(result["diagnostics"][0]["code"], "NO_SAFE_B_R_MAPPING")

    def test_exact_img_reference_is_used(self):
        record = {
            "_convention_version": "V7", "_chapter": 7, "_source_path": "book.json",
            "id": "ch7-1", "page": 141, "status": "IMG", "sentence": "they",
            "tree": {"label": "NP", "children": [
                {"label": "pronoun", "children": [{"word": "they"}]},
            ]},
        }
        result = normalize_candidate({}, [self.token(0, "they", 0)], "they", "V7", [record])
        self.assertEqual(result["status"], "normalized")
        self.assertEqual(result["source"]["tree_id"], "ch7-1")
        self.assertEqual(result["tree"]["children"][0]["label"], "pronoun")

    def test_unverified_and_incorrect_source_records_are_rejected(self):
        for status in ("IMG_ANOMALY", "DERIVED_FROM_INSTRUCTIONS", "TXT"):
            record = {
                "_convention_version": "V7", "_chapter": 7, "id": status,
                "status": status, "sentence": "they",
                "tree": {"label": "NP", "children": [{"word": "they"}]},
            }
            result = normalize_candidate({}, [self.token(0, "they", 0)], "they", "V7", [record])
            self.assertEqual(result["status"], "unresolved")
        incorrect = {
            "_convention_version": "V7", "status": "IMG", "correct": False,
            "sentence": "they", "tree": {"label": "NP", "children": [{"word": "they"}]},
        }
        self.assertEqual(normalize_candidate({}, [self.token(0, "they", 0)], "they",
                                             "V7", [incorrect])["status"], "unresolved")

    def test_distinct_reference_analyses_return_ambiguous(self):
        def record(tree_id, label):
            return {
                "_convention_version": "V7", "_chapter": 7, "id": tree_id,
                "status": "IMG", "sentence": "they",
                "tree": {"label": "NP", "children": [
                    {"label": label, "children": [{"word": "they"}]},
                ]},
            }
        result = normalize_candidate({}, [self.token(0, "they", 0)], "they", "V7",
                                     [record("a", "pronoun"), record("b", "name")])
        self.assertEqual(result["status"], "unresolved")
        self.assertEqual(result["diagnostics"][0]["code"], "AMBIGUOUS_REFERENCE")

    def test_accepted_alternatives_are_preserved(self):
        base = {"label": "NP", "children": [{"label": "N", "children": [{"word": "clowns"}]}]}
        alt = {"label": "NP", "children": [
            {"label": "NOM", "children": [{"label": "N", "children": [{"word": "clowns"}]}]},
        ]}
        record = {
            "_convention_version": "V7", "_chapter": 7, "id": "alternatives",
            "status": "IMG", "sentence": "clowns", "tree": base,
            "accepted_alternatives": [{"label": "B", "tree": alt}],
        }
        result = normalize_candidate({}, [self.token(0, "clowns", 0)], "clowns", "V7", [record])
        self.assertEqual(result["status"], "normalized")
        self.assertEqual(len(result["accepted_alternatives"]), 1)
        self.assertEqual(result["accepted_alternatives"][0]["label"], "B")

    def test_gap_elided_and_empty_nodes_are_retained(self):
        source_tree = {"label": "S", "children": [
            {"label": "NP", "triangle": True, "words": ["they"]},
            {"label": "VP", "children": [
                {"label": "AUX", "features": ["-tense"], "children": [{"word": "to"}]},
                {"label": "VP", "children": [
                    {"label": "V", "features": ["intrans"], "children": [{"word": "go"}]},
                    {"label": "NP", "children": []},
                    {"gap": True, "index": 1},
                    {"word": "that", "elided": True},
                ]},
            ]},
        ]}
        record = {
            "_convention_version": "V10", "_chapter": 10, "id": "gap-fixture",
            "status": "IMG", "sentence": "they to go", "tree": source_tree,
        }
        tokens = [self.token(0, "they", 0), self.token(1, "to", 5), self.token(2, "go", 8)]
        result = normalize_candidate({}, tokens, "they to go", "V10", [record])
        self.assertEqual(result["status"], "normalized")
        serialized = str(result["tree"])
        self.assertIn("'gap': True", serialized)
        self.assertIn("'empty': True", serialized)
        self.assertIn("'elided': True", serialized)

    def test_validator_rejects_future_label_and_function_label(self):
        tree = {"id": "a", "label": "NP", "features": [], "index": None,
                "triangle": False, "span": [0, 1], "surface": "cats",
                "children": [{"id": "b", "label": "NOM", "features": [], "index": None,
                              "triangle": True, "words": ["cats"], "span": [0, 1],
                              "surface": "cats"}]}
        self.assertTrue(any("NOM" in e and "introduced after V3" in e
                            for e in validate_tree(tree, "V3", ["cats"])))
        invalid = {"id": "a", "label": "Subject", "features": [], "index": None,
                   "triangle": True, "words": ["cats"], "span": [0, 1], "surface": "cats"}
        self.assertTrue(any("function" in e for e in validate_tree(invalid, "V3", ["cats"])))


    def test_v5_elided_e_symbol_is_preserved_without_consuming_tokens(self):
        source_tree = {"label": "S", "children": [
            {"label": "NP", "triangle": True, "words": ["William"]},
            {"label": "VP", "children": [
                {"label": "V", "features": ["ditrans"], "children": [{"word": "gave"}]},
                {"label": "NP", "children": [{"symbol": "E", "elided": True}]},
                {"label": "NP", "triangle": True, "words": ["some", "bleach"]},
            ]},
        ]}
        record = {
            "_convention_version": "V5", "_chapter": 5, "id": "ch5-46",
            "status": "IMG", "sentence": "William gave some bleach", "tree": source_tree,
        }
        tokens = [self.token(0, "William", 0), self.token(1, "gave", 8),
                  self.token(2, "some", 13), self.token(3, "bleach", 18)]
        result = normalize_candidate({}, tokens, "William gave some bleach", "V5", [record])
        self.assertEqual(result["status"], "normalized")
        elision = result["tree"]["children"][1]["children"][1]["children"][0]
        self.assertEqual(elision["symbol"], "E")
        self.assertEqual(elision["span"], [2, 2])

    def test_v9_unlabelled_wh_triangle_is_allowed_only_under_c2(self):
        tree = {"label": "S-dbar", "children": [
            {"label": "C2", "children": [{"triangle": True, "words": ["which", "books"]}]},
            {"label": "S-bar", "children": [
                {"label": "C1", "children": [{"word": "are"}]},
                {"label": "S", "children": [
                    {"label": "NP", "triangle": True, "words": ["you"]},
                    {"label": "VP", "children": [{"label": "V", "features": ["intrans"],
                                                   "children": [{"word": "sing"}]}]},
                ]},
            ]},
        ]}
        runtime = normalize_candidate(
            {}, None, "Which books are you sing", "V9",
            [{
                "_convention_version": "V9", "_chapter": 9, "id": "wh-triangle",
                "status": "IMG", "sentence": "Which books are you sing", "tree": tree,
            }],
        )
        self.assertEqual(runtime["status"], "normalized")
        self.assertIsNone(runtime["tree"]["children"][0]["children"][0]["label"])

    def test_v10_nonfinite_feature_is_allowed_on_lexical_and_perfect_heads(self):
        for head_label in ("V", "PERF"):
            tree = {"id": "a", "label": head_label, "features": ["-tense"],
                    "index": None, "triangle": False, "span": [0, 1],
                    "surface": "having", "children": [
                        {"id": "b", "word": "having", "span": [0, 1], "surface": "having"}
                    ]}
            self.assertEqual(validate_tree(tree, "V10", ["having"]), [])

    def test_indexed_external_controller_is_preserved(self):
        tree = {"label": "S", "children": [
            {"label": "NP", "children": [{"gap": True, "index": 1}]},
            {"label": "VP", "children": [
                {"label": "V", "features": ["intrans", "-tense"],
                 "children": [{"word": "apologising"}]}
            ]},
        ]}
        controller = {"index": 1, "controller": "he", "source": "Ch10 [18], p.228"}
        result = normalize_candidate(
            {}, None, "apologising", "V10",
            [{
                "_convention_version": "V10", "_chapter": 10, "id": "control",
                "status": "IMG", "sentence": "apologising", "tree": tree,
                "external_controller": controller,
            }],
        )
        self.assertEqual(result["status"], "normalized")
        self.assertEqual(result["external_controller"], controller)


    def test_correction_alignment_handles_replacement_and_insertion(self):
        original, corrected = "She can goes home.", "She can go home now."
        tokens = [self.token(0, "She", 0), self.token(1, "can", 4),
                  self.token(2, "goes", 8), self.token(3, "home", 13),
                  self.token(4, ".", 17)]
        tree = {"id": "n0", "span": [0, 5], "children": [
            {"id": "n1", "span": [0, 1]}, {"id": "n2", "span": [1, 2]},
            {"id": "n3", "span": [2, 3]}, {"id": "n4", "span": [3, 4]},
            {"id": "n5", "span": [4, 5]},
        ]}
        result = build_correction_alignment(original, corrected, tokens, tree)
        operations = {edit["operation"] for edit in result["edits"]}
        self.assertIn("replace", operations)
        self.assertIn("insert", operations)
        changed = next(edit for edit in result["edits"] if edit["operation"] == "replace")
        self.assertEqual(changed["original_tokens"][0]["text"], "goes")
        self.assertEqual(changed["corrected_tokens"][0]["text"], "go")
        self.assertIn("n3", changed["affected_terminal_ids"])


    def test_correction_alignment_uses_original_document_offset_and_punctuation(self):
        original = "She goes home."
        corrected = "She go home!"
        tokens = [
            {"i": 0, "t": "She", "start": 12, "end": 15},
            {"i": 1, "t": "goes", "start": 16, "end": 20},
            {"i": 2, "t": "home", "start": 21, "end": 25},
            {"i": 3, "t": ".", "start": 25, "end": 26},
        ]
        tree = {"id": "root", "span": [0, 4], "children": [
            {"id": "she", "span": [0, 1]},
            {"id": "goes", "span": [1, 2]},
            {"id": "home", "span": [2, 3]},
            {"id": "period", "span": [3, 4]},
        ]}
        result = build_correction_alignment(
            original, corrected, tokens, tree, source_char_offset=12
        )
        replacement = next(edit for edit in result["edits"] if edit["operation"] == "replace"
                           and edit["original_tokens"][0]["text"] == "goes")
        punctuation = next(edit for edit in result["edits"] if edit["operation"] == "replace"
                           and edit["original_tokens"][0]["text"] == ".")
        self.assertIn("goes", replacement["affected_terminal_ids"])
        self.assertEqual(punctuation["corrected_tokens"][0]["text"], "!")

    def test_deletion_alignment_preserves_repeated_word_identity(self):
        result = build_correction_alignment("The the cat.", "The cat.")
        self.assertEqual([edit["operation"] for edit in result["edits"]], ["delete"])
        self.assertEqual(result["edits"][0]["original_token_range"], [1, 2])
        self.assertEqual(result["edits"][0]["original_tokens"][0]["text"], "the")

    def test_multi_token_replacement(self):
        result = build_correction_alignment("She goes home.", "She is going home.")
        changed = next(edit for edit in result["edits"] if edit["operation"] == "replace")
        self.assertEqual([row["text"] for row in changed["original_tokens"]], ["goes"])
        self.assertEqual([row["text"] for row in changed["corrected_tokens"]], ["is", "going"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
