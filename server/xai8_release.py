"""XAI-8 independent-evaluation and release firewall.

Automated structural contracts cannot be turned into independent grammatical
accuracy, repair-meaning or learner-comprehension results. Production release
is held until separate, externally adjudicated evidence has been recorded.
No request body, source passage, user identifier, IP or verbatim text is logged.
"""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, ValidationError

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "evaluation/xai8_release_policy.json"
SCHEMA_PATH = ROOT / "evaluation/xai8_release_policy.schema.json"
VERSION = "xai8-release-decision-1.0.0"
QUALITY_METRICS = (
    "error_precision", "error_recall", "false_positive_rate",
    "function_accuracy", "repair_validity", "meaning_preservation",
    "learner_comprehension_gain", "blind_readability_preference",
)


def load_policy(root: Path | None = None) -> dict[str, Any]:
    base = root or ROOT
    policy = json.loads((base / "evaluation/xai8_release_policy.json").read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator(schema).validate(policy)
    return policy


def evaluate_release(report: dict[str, Any], policy: dict[str, Any] | None = None) -> dict[str, Any]:
    """Fail closed; technical PASS is not authorization to ship diagnostics.

    Neither a client value nor a synthetic fixture may furnish human signoff.
    A future authorized release must update the reviewed policy on the server
    *and* publish a separate, independently audited expert results artifact.
    """
    if not isinstance(report, dict):
        raise ValueError("XAI-8 requires a validated machine evaluation report")
    active = deepcopy(policy) if policy is not None else load_policy()
    try:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        Draft202012Validator(schema).validate(active)
    except (ValidationError, TypeError, ValueError, KeyError):
        return _decision(False, ["INVALID_RELEASE_POLICY"], False, active)
    if report.get("schema_version") != "xai8-evaluation-1.0.0":
        return _decision(False, ["INVALID_EVALUATION_REPORT"], False, active)
    gates = active["technical_gates"]
    checks = {
        "HOLDOUT_PROBES_INSUFFICIENT": report.get("probe_count", -1) >= gates["minimum_nonoverlapping_probes"],
        "PROBE_FAMILIES_INSUFFICIENT": report.get("probe_family_count", -1) >= gates["minimum_probe_families"],
        "PROBE_OVERLAP_WITH_DEVELOPMENT": report.get("xai0_text_overlap_count") == 0,
        "SOURCE_TREE_NODES_INSUFFICIENT": report.get("source_tree_nodes", -1) >= gates["minimum_source_tree_nodes"],
        "INCOMPLETE_NODE_EXPLANATIONS": report.get("source_node_paragraph_coverage") == 1.0,
        "INVALID_FACT_PROOFS": report.get("source_fact_proof_completeness") == 1.0,
        "UNSUPPORTED_BOOK_CLAIMS": report.get("unsupported_book_verified_claim_count") == gates["max_unsupported_book_verified_claims"],
        "INVALID_GLOBAL_GRAMMAR_VERDICTS": report.get("whole_sentence_certifications", -1) == gates["max_global_grammar_certifications"],
        "UNEXPECTED_MODEL_CALLS": report.get("model_provider_calls", -1) == gates["max_model_calls"],
        "UNSAFE_TELEMETRY": report.get("raw_text_telemetry_events") == 0,
        "EVALUATION_FAILURES_PRESENT": report.get("evaluation_failure_count") == 0,
        "SOURCE_RULE_GATE_BYPASSED": report.get("runtime_enabled_cambridge_rule_count") == 0,
        "PRODUCTION_AI_GATE_BYPASSED": report.get("production_ai_model_enabled") is False,
        "MISSING_BENCHMARK_DISCLOSURE": report.get("independent_expert_cases") == 0 and
                                         all(report.get(k) is None for k in QUALITY_METRICS),
    }
    failure = [name for name, ok in checks.items() if not ok]
    tech = not failure
    exp = active["expert_gates"]
    expert = bool(
        active["new_diagnostic_rollout_enabled"] is True
        and active["stage"] in {"CANARY", "GENERAL_RELEASE"}
        and active["rollback"]["kill_switch"] is False
        and active["rollback"]["canary_percent"] > 0
        and exp["adjudicated_case_count"] >= exp["minimum_independently_adjudicated_cases"]
        and exp["independent_linguist_count"] >= exp["minimum_independent_linguists"]
        and len(exp["reviewers"]) >= exp["minimum_independent_linguists"]
        and bool(exp["expert_evaluation_report"])
        and exp["quality_metrics_available"] is True
        and report.get("independent_expert_cases", 0) >= exp["minimum_independently_adjudicated_cases"]
        and all(isinstance(report.get(k), (float, int)) and type(report.get(k)) is not bool
                for k in QUALITY_METRICS)
    )
    if not expert:
        failure.append("INDEPENDENT_EXPERT_AND_LEARNER_QUALITY_REVIEW_MISSING")
    if active["rollback"]["kill_switch"]:
        failure.append("OPERATOR_KILL_SWITCH_ACTIVE")
    if active["rollback"]["canary_percent"] == 0:
        failure.append("CANARY_PERCENT_ZERO")
    return _decision(tech, failure, expert, active)


def _decision(tech: bool, reasons: list[str], expert: bool,
              policy: dict[str, Any]) -> dict[str, Any]:
    eligible = bool(tech and expert and not reasons)
    return {
        "schema_version": VERSION, "language_policy": "ENGLISH_ONLY",
        "technical_acceptance": "PASS" if tech else "FAIL",
        "expert_quality_acceptance": "PASS" if expert else "NOT_MEASURED",
        "release_decision": "ELIGIBLE_FOR_EXPLICIT_REVIEW" if eligible else "HOLD",
        "new_diagnostic_rollout_permitted": eligible,
        "live_canary_percent": policy.get("rollback", {}).get("canary_percent", 0)
                               if eligible else 0,
        "rollback_kill_switch": policy.get("rollback", {}).get("kill_switch", True),
        "reasons": sorted(set(reasons)),
        "independent_linguistic_accuracy_certified": False,
        "whole_sentence_grammar_certified": False,
    }


class OptInAggregateTelemetry:
    """Privacy-safe, in-memory counters; disabled by the production manifest.

    Never accepts raw sentences, tokens, prompts, session IDs, user IDs,
    arbitrary labels, timestamps, or client-supplied monetary amounts.
    Snapshot is only available for batches >= the disclosure threshold.
    """
    MODES = {"generator", "builder", "lessons", "quizzes", "revisions"}
    OUTCOMES = {"observed", "provisional", "unavailable", "blocked"}
    BUCKETS = ("under_100ms", "100_499ms", "500_1999ms", "2000ms_or_more")

    def __init__(self, policy: dict[str, Any] | None = None):
        self._policy = deepcopy(policy) if policy is not None else load_policy()
        self._counts: Counter[tuple[str, str, str]] = Counter()
        self._total = 0

    def record(self, *, opted_in: bool, mode: str, outcome: str, latency_ms: int) -> bool:
        config = self._policy["telemetry"]
        if not config["enabled"] or not opted_in:
            return False
        if (mode not in self.MODES or outcome not in self.OUTCOMES
                or type(latency_ms) is not int or not 0 <= latency_ms <= 60000):
            return False
        bucket = (self.BUCKETS[0] if latency_ms < 100 else
                  self.BUCKETS[1] if latency_ms < 500 else
                  self.BUCKETS[2] if latency_ms < 2000 else self.BUCKETS[3])
        self._counts[(mode, outcome, bucket)] += 1
        self._total += 1
        return True

    def snapshot(self) -> dict[str, Any]:
        minimum = self._policy["telemetry"]["minimum_aggregate_reporting_sample"]
        if self._total < minimum:
            return {"status": "suppressed", "minimum_sample": minimum, "count": None,
                    "counts": None}
        return {"status": "aggregate_only", "minimum_sample": minimum, "count": self._total,
                "counts": [{"mode": a, "outcome": b, "latency_bucket": c, "count": n}
                           for (a, b, c), n in sorted(self._counts.items())]}
