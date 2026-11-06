"""API contract tests using stubs instead of downloading spaCy/Benepar models."""
import sys
import types
import unittest
from unittest.mock import patch


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
        self.assertEqual(payload["br_analysis"]["tree"]["label"], "S")
        self.assertEqual(payload["tree"], self.candidate())
        self.assertEqual(payload["candidate_tree"], self.candidate())
        self.assertIn("br_analysis", payload)
        self.assertEqual(payload["meta"]["tree_authority"].split(";")[0],
                         "B-R canonical analysis is in br_analysis")
        self.assertEqual(payload["meta"]["br_convention_version"], "V2")

    def test_unsupported_free_analysis_stays_explicitly_unresolved(self):
        with patch.object(api, "analyze", return_value=self.analysis()), \
             patch.object(api, "evaluate", return_value=self.clean_evaluation()), \
             patch.object(api, "classify", return_value=None), \
             patch.object(api, "_contrastive", return_value=""), \
             patch.object(api, "_pipeline_narration", return_value={"stages": []}), \
             patch.object(api, "_rule_concepts", return_value=[]):
            payload = api.build_payload(self.sentence, convention_version="V10")

        self.assertEqual(payload["br_analysis"]["status"], "unresolved")
        self.assertEqual(payload["br_analysis"]["diagnostics"][0]["code"], "NO_SAFE_B_R_MAPPING")
        self.assertEqual(payload["tree"], self.candidate())

    def test_invalid_convention_is_rejected_before_parsing(self):
        with patch.object(api, "analyze") as parse:
            with self.assertRaises(ValueError):
                api.build_payload(self.sentence, convention_version="V11")
            parse.assert_not_called()


if __name__ == "__main__":
    unittest.main(verbosity=2)
