"""API contract tests using stubs instead of downloading spaCy/Benepar models."""
import sys
import types
import unittest
import json
from pathlib import Path
from unittest.mock import patch

from jsonschema import Draft202012Validator


_M1_SCHEMA_PATH = Path(__file__).resolve().parents[1] / "docs" / "canonical-burton-roberts-tree.schema.json"
_M1_SCHEMA = json.loads(_M1_SCHEMA_PATH.read_text(encoding="utf-8"))
_M1_VALIDATOR = Draft202012Validator(_M1_SCHEMA)


def _stub_module(name, **attributes):
    module = types.ModuleType(name)
    for key, value in attributes.items():
        setattr(module, key, value)
    sys.modules[name] = module
    return module


class _ParseFailure(Exception):
    pass


_stub_module("parse_engine", ParseFailure=_ParseFailure, analyze=None, load_models=None)
_stub_module("matrix", evaluate=None, _rem_from_text=lambda *args, **kwargs: None)
_stub_module("detector", classify=None, classify_many=None, combine=None)
_stub_module("licensing", _leaves=lambda *args, **kwargs: [], _finding=lambda *args, **kwargs: None)
_stub_module("corrector", sweep=lambda *args, **kwargs: None)
_stub_module("corrections", has_actionable=lambda details: False,
             assemble=lambda *args, **kwargs: None,
             describe=lambda correction: None)
_stub_module("plain", apply_plain_language=lambda details, summary: None,
             plain_text=lambda value: value)

_STUB_NAMES = (
    "parse_engine", "matrix", "detector", "licensing",
    "corrector", "corrections", "plain",
)
_PREVIOUS_MODULES = {name: sys.modules.get(name) for name in _STUB_NAMES}
import api  # noqa: E402
for _name, _module in _PREVIOUS_MODULES.items():
    if _module is None:
        sys.modules.pop(_name, None)
    else:
        sys.modules[_name] = _module


class SyntaxGeneratorApiContractTests(unittest.TestCase):
    sentence = "The birds sing."

    @staticmethod
    def candidate():
        return {
            "id": "n0", "type": "S", "surface": "The birds sing.",
            "children": [
                {"id": "n1", "type": "NP", "surface": "The birds",
                 "children": [{"id": "n2", "type": "DT", "surface": "The"},
                              {"id": "n3", "type": "NNS", "surface": "birds"}]},
                {"id": "n4", "type": "VP", "surface": "sing",
                 "children": [{"id": "n5", "type": "VBP", "surface": "sing"}]},
            ],
        }

    def analysis(self):
        tokens = [
            {"i": 0, "t": "The", "pos": "DT", "start": 0, "end": 3},
            {"i": 1, "t": "birds", "pos": "NNS", "start": 4, "end": 9},
            {"i": 2, "t": "sing", "pos": "VBP", "start": 10, "end": 14},
            {"i": 3, "t": ".", "pos": ".", "start": 14, "end": 15},
        ]
        return {
            "sentence": self.sentence,
            "sentence_index": 0,
            "sentence_count": 1,
            "sentences": [{"start": 0, "end": len(self.sentence), "text": self.sentence}],
            "tokens": tokens,
            "parse_string": "(S (NP The birds) (VP sing) .)",
            "root": self.candidate(),
            "nodes": [],
        }

    @staticmethod
    def clean_evaluation():
        return {
            "details": {},
            "summary": {
                "verdict": "grammatical", "valid": True,
                "valid_edges": 2, "violated_edges": 0, "unrated_edges": 0,
                "explanation": "No legacy matrix errors were found.",
                "constraints_fired": [], "checker_errors": [],
            },
        }

    def test_v2_payload_exposes_candidate_and_canonical_analysis_separately(self):
        with patch.object(api, "analyze", return_value=self.analysis()), \
             patch.object(api, "evaluate", return_value=self.clean_evaluation()), \
             patch.object(api, "classify", return_value=None), \
             patch.object(api, "_contrastive", return_value=""), \
             patch.object(api, "_pipeline_narration", return_value={"stages": []}), \
             patch.object(api, "_rule_concepts", return_value=[]):
            payload = api.build_payload(self.sentence, convention_version="V2")

        self.assertEqual(payload["br_analysis"]["status"], "normalized")
        self.assertEqual(payload["br_analysis"]["convention_version"], "V2")
        self.assertEqual(payload["br_analysis"]["tree"]["root"]["label"], "S")
        self.assertEqual(
            list(_M1_VALIDATOR.iter_errors(payload["br_analysis"]["tree"])), [])
        self.assertEqual(payload["br_analysis"]["canonical_schema"],
                         "docs/canonical-burton-roberts-tree.schema.json")
        self.assertEqual(payload["tree"], self.candidate())
        self.assertEqual(payload["candidate_tree"], self.candidate())
        self.assertIn("br_analysis", payload)
        self.assertEqual(payload["meta"]["tree_authority"].split(";")[0],
                         "B-R canonical analysis is in br_analysis")
        self.assertEqual(payload["meta"]["br_convention_version"], "V2")
        self.assertEqual(payload["cambridge_evaluation"]["status"], "no_runtime_rules")
        self.assertEqual(payload["cambridge_evaluation"]["evaluated_rule_ids"], [])

    def test_unsupported_free_analysis_stays_explicitly_unresolved(self):
        with patch.object(api, "analyze", return_value=self.analysis()), \
             patch.object(api, "evaluate", return_value=self.clean_evaluation()), \
             patch.object(api, "classify", return_value=None), \
             patch.object(api, "_contrastive", return_value=""), \
             patch.object(api, "_pipeline_narration", return_value={"stages": []}), \
             patch.object(api, "_rule_concepts", return_value=[]):
            payload = api.build_payload(self.sentence, convention_version="V10")

        self.assertEqual(payload["br_analysis"]["status"], "unresolved")
        self.assertEqual(payload["br_analysis"]["diagnostics"][0]["code"], "PROFILE_MAPPING_NOT_APPROVED")
        self.assertEqual(payload["tree"], self.candidate())


    def test_correction_payload_parses_the_repaired_sentence_separately(self):
        original = "She goes home."
        corrected = "She go home."

        def fixture(sentence):
            words = sentence.rstrip(".").split()
            tokens = []
            cursor = 0
            for i, word in enumerate(words):
                start = sentence.index(word, cursor)
                end = start + len(word)
                tokens.append({"i": i, "t": word, "pos": "NN", "start": start, "end": end})
                cursor = end
            if sentence.endswith("."):
                tokens.append({"i": len(tokens), "t": ".", "pos": ".", 
                               "start": len(sentence) - 1, "end": len(sentence)})
            leaves = [
                {"id": f"leaf-{i}", "type": "NN", "span": [i, i + 1],
                 "surface": word, "pos": "NN", "punct": False}
                for i, word in enumerate(words)
            ]
            root = {
                "id": "root", "type": "S", "span": [0, len(tokens)],
                "surface": sentence, "children": [
                    {"id": "np", "type": "NP", "span": [0, 1],
                     "surface": words[0], "children": [leaves[0]]},
                    {"id": "vp", "type": "VP", "span": [1, len(tokens)],
                     "surface": " ".join(words[1:]), "children": leaves[1:]},
                ],
            }
            return {
                "sentence": sentence, "sentence_index": 0, "sentence_count": 1,
                "sentences": [{"start": 0, "end": len(sentence), "text": sentence}],
                "tokens": tokens, "parse_string": "(S ...)", "root": root, "nodes": [],
            }

        def bad_evaluation(*args, **kwargs):
            result = self.clean_evaluation()
            result["summary"]["verdict"] = "ungrammatical"
            result["summary"]["valid"] = False
            return result

        correction = {"corrected_sentence": corrected}
        with patch.object(api, "analyze", side_effect=lambda text, sentence_index=0: fixture(text)), \
             patch.object(api, "evaluate", side_effect=bad_evaluation), \
             patch.object(api, "classify", return_value=None), \
             patch.object(api, "_contrastive", return_value=""), \
             patch.object(api, "_pipeline_narration", return_value={"stages": []}), \
             patch.object(api, "_rule_concepts", return_value=[]), \
             patch.object(api.corrections, "has_actionable", return_value=True), \
             patch.object(api.corrections, "assemble", return_value=correction), \
             patch.object(api.corrections, "describe", return_value="A correction is available."):
            payload = api.build_payload(original, convention_version="V10")

        correction_payload = payload["summary"]["correction"]
        self.assertEqual(correction_payload["corrected_sentence"], corrected)
        self.assertIn("corrected_br_analysis", correction_payload)
        self.assertIsNotNone(correction_payload["corrected_candidate_parse"])
        self.assertIn("go", str(correction_payload["corrected_candidate_parse"]["tree"]))
        self.assertNotIn("goes", str(correction_payload["corrected_candidate_parse"]["tree"]))
        replacement = next(edit for edit in correction_payload["alignment"]["edits"]
                           if edit["operation"] == "replace")
        self.assertEqual(replacement["original_tokens"][0]["text"], "goes")
        self.assertEqual(replacement["corrected_tokens"][0]["text"], "go")

    def test_invalid_sentence_index_is_rejected_before_parsing(self):
        for value in (-1, True, 1.5):
            with self.subTest(value=value), patch.object(api, "analyze") as parse:
                with self.assertRaisesRegex(ValueError, "sentence_index"):
                    api.build_payload(self.sentence, sentence_index=value, chapter=2)
                parse.assert_not_called()

    def test_invalid_convention_is_rejected_before_parsing(self):
        with patch.object(api, "analyze") as parse:
            with self.assertRaises(ValueError):
                api.build_payload(self.sentence, convention_version="V11")
            parse.assert_not_called()


    def test_chapter_selection_routes_to_matching_convention_profile(self):
        with patch.object(api, "analyze", return_value=self.analysis()), \
             patch.object(api, "evaluate", return_value=self.clean_evaluation()), \
             patch.object(api, "classify", return_value=None), \
             patch.object(api, "_contrastive", return_value=""), \
             patch.object(api, "_pipeline_narration", return_value={"stages": []}), \
             patch.object(api, "_rule_concepts", return_value=[]):
            payload = api.build_payload(self.sentence, chapter=2)

        self.assertEqual(payload["meta"]["br_convention_version"], "V2")
        self.assertEqual(payload["meta"]["br_profile_id"], "V2")
        self.assertEqual(payload["br_analysis"]["convention_version"], "V2")

    def test_chapter_and_explicit_convention_conflict_is_rejected_before_parse(self):
        with patch.object(api, "analyze") as parse:
            with self.assertRaisesRegex(ValueError, "chapter 2 requires convention_version V2"):
                api.build_payload(self.sentence, chapter=2, convention_version="V3")
            parse.assert_not_called()

    def test_chapter_7_appendix_d1_is_explicit_in_shared_payload(self):
        with patch.object(api, "analyze", return_value=self.analysis()), \
             patch.object(api, "evaluate", return_value=self.clean_evaluation()), \
             patch.object(api, "classify", return_value=None), \
             patch.object(api, "_contrastive", return_value=""), \
             patch.object(api, "_pipeline_narration", return_value={"stages": []}), \
             patch.object(api, "_rule_concepts", return_value=[]):
            payload = api.build_payload(self.sentence, chapter=7, appendix_nom=True)

        self.assertEqual(payload["meta"]["br_convention_version"], "V7")
        self.assertEqual(payload["meta"]["br_profile_id"], "V7-APPENDIX-D1")
        self.assertTrue(payload["meta"]["br_appendix_nom"])

    def test_multi_sentence_request_reports_selected_sentence(self):
        analysis = self.analysis()
        analysis["sentence_index"] = 1
        analysis["sentence_count"] = 2
        analysis["sentences"] = [
            {"start": 0, "end": 15, "text": "The cats sleep."},
            {"start": 16, "end": 31, "text": self.sentence},
        ]
        for token in analysis["tokens"]:
            token["start"] += 16
            token["end"] += 16
        with patch.object(api, "analyze", return_value=analysis), \
             patch.object(api, "evaluate", return_value=self.clean_evaluation()), \
             patch.object(api, "classify", return_value=None), \
             patch.object(api, "_contrastive", return_value=""), \
             patch.object(api, "_pipeline_narration", return_value={"stages": []}), \
             patch.object(api, "_rule_concepts", return_value=[]):
            payload = api.build_payload("The cats sleep. The birds sing.",
                                        sentence_index=1, chapter=2)

        self.assertEqual(payload["meta"]["sentence_count"], 2)
        self.assertEqual(payload["meta"]["target_sentence"], 2)
        self.assertEqual(payload["parse"]["text"], self.sentence)
        self.assertEqual(payload["br_analysis"]["status"], "normalized")


if __name__ == "__main__":
    unittest.main(verbosity=2)
