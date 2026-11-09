"""XAI-0 model-free contracts and measurement semantics.

The tests here verify that the audit does not invent adjudicated labels or
parser metrics. Real Benepar measurements run separately in runtime CI.
"""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "scripts/audit_xai0_baseline.py"
spec = importlib.util.spec_from_file_location("xai0_baseline", PATH)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class XAI0BaselineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.corpus = audit.load_cases()

    def test_development_corpus_has_116_non_gold_cases(self):
        rows = self.corpus["cases"]
        self.assertEqual(len(rows), 116)
        self.assertTrue(all(x["expected_status"] == "NOT_ADJUDICATED" for x in rows))
        self.assertEqual(self.corpus["review_status"], "NOT_HUMAN_ADJUDICATED")
        self.assertGreaterEqual(len({x["family"] for x in rows}), 10)

    def test_contains_hard_correction_and_cambridge_exceptions(self):
        text = {x["text"] for x in self.corpus["cases"]}
        for item in (
            "I hate you.", "She had eaten.", "She had breakfast.",
            "She had went home.", "She have went to a stores, and he don't likes it.",
            "We've already discussed it yesterday.",
            "She had wanted the car.", "I saw the man with the telescope.",
            "Nag-aaral ako ng syntax.", "She left. He stayed.",
        ):
            with self.subTest(sentence=item):
                self.assertIn(item, text)

    def test_second_sentence_case_has_index_one(self):
        target = next(x for x in self.corpus["cases"]
                      if x["id"] == "x0-multisentence-second")
        self.assertEqual(target["selected_sentence_index"], 1)

    def test_no_gold_or_source_authority_in_development_data(self):
        changed = copy.deepcopy(self.corpus)
        changed["cases"][0]["expected_status"] = "GRAMMATICAL"
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "bad.json"
            path.write_text(json.dumps(changed))
            with self.assertRaisesRegex(ValueError, "unsupported grammaticality"):
                audit.load_cases(path)
        changed = copy.deepcopy(self.corpus)
        changed["source_authority"] = "Cambridge"
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "bad.json"
            path.write_text(json.dumps(changed))
            with self.assertRaisesRegex(ValueError, "source authority"):
                audit.load_cases(path)

    def test_rejects_duplicate_cases_and_unbounded_text(self):
        for operation, message in (
            (lambda d: d["cases"].append(d["cases"][0]), "duplicate"),
            (lambda d: d["cases"][0].update(text="x" * 651), "length"),
        ):
            with self.subTest(message=message):
                data = copy.deepcopy(self.corpus)
                operation(data)
                with tempfile.TemporaryDirectory() as temp:
                    path = Path(temp) / "bad.json"
                    path.write_text(json.dumps(data))
                    with self.assertRaises(ValueError):
                        audit.load_cases(path)

    def test_real_inventory_has_two_templates_four_sources_zero_runtime_rules(self):
        inventory = audit.static_inventory()
        self.assertEqual(inventory["reviewed_template_rows"], 2)
        self.assertEqual(inventory["source_records"], 4)
        self.assertEqual(inventory["runtime_enabled_cambridge_rules"], 0)
        self.assertEqual(inventory["template_channels"]["structural"], 1)
        self.assertEqual(inventory["template_channels"]["grammatical"], 1)

    def test_summary_distinguishes_node_counts_from_gold_accuracy(self):
        records = [
            {
                "id": "r1", "family": "basic", "intent": "grammatical_control",
                "parser_status": "parsed", "br_status": "normalized",
                "explanation_status": "EXPLAINED",
                "working_tree_observed": False, "br_reason_codes": [],
                "all_nodes": 4, "terminal_nodes": 2,
                "source_cited_nodes": 1, "source_cited_terminal_nodes": 0,
                "all_labels": {"S": 1, "NP": 1, "VP": 1, "V": 1},
                "labels_without_cited_explanation": {"NP": 1, "VP": 1, "V": 1},
                "control_vs_legacy_disagreement": True,
                "malformed_probe_vs_legacy_no_flag": False,
                "root_endpoint_checked": True, "root_endpoint_matches": True,
                "timing_ms": {"total": 10.0},
            },
            {
                "id": "r2", "family": "basic", "intent": "malformed_probe",
                "parser_status": "parsed", "br_status": "unresolved",
                "explanation_status": "ANALYSIS_UNRESOLVED",
                "working_tree_observed": True, "br_reason_codes": ["UNRESOLVED"],
                "all_nodes": 0, "terminal_nodes": 0,
                "source_cited_nodes": 0, "source_cited_terminal_nodes": 0,
                "all_labels": {}, "labels_without_cited_explanation": {},
                "control_vs_legacy_disagreement": False,
                "malformed_probe_vs_legacy_no_flag": True,
                "root_endpoint_checked": False, "root_endpoint_matches": None,
                "timing_ms": {"total": 12.0},
            },
        ]
        data = audit.status_counters(records)
        self.assertEqual(data["parser_cases_parsed"], 2)
        self.assertEqual(data["br_normalized"], 1)
        self.assertEqual(data["source_cited_node_coverage_percent"], 25)
        self.assertEqual(data["source_cited_terminal_coverage_percent"], 0)
        self.assertEqual(data["source_cited_node_labels"], {"S": 1})
        self.assertEqual(data["by_family"]["basic"]["br_normalized"], 1)
        self.assertEqual(data["by_family"]["basic"]["br_unresolved"], 1)
        self.assertEqual(data["control_legacy_disagreements"], 1)
        self.assertEqual(data["malformed_probe_legacy_no_flag_count"], 1)
        self.assertEqual(data["root_endpoint_mismatches"], 0)
        self.assertTrue(any("not expert-adjudicated" in s for s in data["notes"]))

    def test_percentile_bounded_and_empty_metric_unavailable(self):
        self.assertIsNone(audit.percentile([], 95))
        self.assertEqual(audit.percentile([10, 20, 30], 50), 20)
        self.assertEqual(audit.percentile([10, 20, 30], 95), 29.0)

    def test_model_missing_does_not_fake_actual_parser_coverage(self):
        from unittest.mock import patch
        with patch("parse_engine.load_models", side_effect=FileNotFoundError("models offline")):
            result = audit.audit_dataset(self.corpus["cases"][:1], require_models=False)
            self.assertFalse(result["model_status"]["ready"])
            self.assertEqual(result["summary"]["parser_cases_parsed"], 0)
            self.assertIsNone(result["summary"]["source_cited_node_coverage_percent"])
            self.assertEqual(result["provenance"]["measurement_status"],
                             "models_unavailable_no_parser_metrics")
            with self.assertRaisesRegex(RuntimeError, "requires real NLP models"):
                audit.audit_dataset(self.corpus["cases"][:1], require_models=True)


if __name__ == "__main__":
    unittest.main()
