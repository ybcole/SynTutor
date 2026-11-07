"""Fail-closed deterministic executor for runtime-enabled Cambridge rules.

Only reviewed and allow-listed records are considered. This module implements a
small, explicit surface-pattern check primitive; it does not infer a rule from
Cambridge prose. A rule must carry a machine-readable runtime_check and pass
the registry's source/review/crosswalk/test gates before execution.
"""
from __future__ import annotations

import re
from typing import Any


_TOKEN_RE = re.compile(r"\w+(?:['’]\w+)*|[^\w\s]", re.UNICODE)
_SUPPORTED_CHECK = "forbidden_token_sequences"


def _tokens(sentence: str) -> list[str]:
    return [match.group(0).casefold().replace("’", "'")
            for match in _TOKEN_RE.finditer(sentence)]


def _sequence_positions(tokens: list[str], sequence: list[str]) -> list[int]:
    target = [str(token).casefold().replace("’", "'") for token in sequence]
    width = len(target)
    if width == 0 or width > len(tokens):
        return []
    return [
        index for index in range(len(tokens) - width + 1)
        if tokens[index:index + width] == target
    ]


def _evaluate_forbidden_sequences(sentence: str,
                                  check: dict[str, Any]) -> dict[str, Any]:
    tokens = _tokens(sentence)
    forbidden = check.get("forbidden_sequences")
    exceptions = check.get("exception_sequences", [])
    if not isinstance(forbidden, list) or not forbidden:
        return {"status": "invalid_check", "matched_sequences": []}
    if not isinstance(exceptions, list):
        return {"status": "invalid_check", "matched_sequences": []}

    exception_spans = []
    for sequence in exceptions:
        if not isinstance(sequence, list) or not sequence:
            return {"status": "invalid_check", "matched_sequences": []}
        exception_spans.extend(
            (start, start + len(sequence), sequence)
            for start in _sequence_positions(tokens, sequence)
        )

    matched = []
    violating = []
    excepted = []
    for sequence in forbidden:
        if not isinstance(sequence, list) or not sequence:
            return {"status": "invalid_check", "matched_sequences": []}
        width = len(sequence)
        for start in _sequence_positions(tokens, sequence):
            row = {"sequence": sequence, "token_span": [start, start + width]}
            matches_exception = [
                {"sequence": exception, "token_span": [exception_start, exception_end]}
                for exception_start, exception_end, exception in exception_spans
                if exception_start <= start and start + width <= exception_end
            ]
            matched.append(row)
            if matches_exception:
                excepted.append({**row, "exceptions": matches_exception})
            else:
                violating.append(row)

    if not matched:
        return {"status": "passed", "matched_sequences": []}
    if violating:
        return {
            "status": "violation",
            "matched_sequences": matched,
            "violating_matches": violating,
            "excepted_matches": excepted,
        }
    return {
        "status": "exception",
        "matched_sequences": matched,
        "exception_matches": excepted,
    }


def evaluate_cambridge(analysis: dict[str, Any] | None,
                       registry: dict[str, Any] | None,
                       variety: str | None = None) -> dict[str, Any]:
    """Evaluate only registry.active_rules; never evaluate extracted rules ad hoc."""
    if not isinstance(analysis, dict) or analysis.get("status") != "normalized":
        return {
            "status": "not_evaluated",
            "evaluated_rule_ids": [],
            "findings": [],
            "diagnostics": [{
                "code": "BR_ANALYSIS_UNRESOLVED",
                "message": "Cambridge constraints were not evaluated because no validated canonical B-R tree is available.",
            }],
        }
    envelope = analysis.get("tree")
    if not isinstance(envelope, dict) or not isinstance(envelope.get("root"), dict):
        return {
            "status": "not_evaluated",
            "evaluated_rule_ids": [],
            "findings": [],
            "diagnostics": [{
                "code": "CANONICAL_TREE_MISSING",
                "message": "Cambridge constraints require the validated M1 canonical tree envelope.",
            }],
        }
    if not isinstance(registry, dict):
        registry = {}
    active_rules = registry.get("active_rules", [])
    if not isinstance(active_rules, list) or not active_rules:
        diagnostics = list(registry.get("diagnostics") or [])
        diagnostics.append({
            "code": "NO_RUNTIME_ENABLED_RULES",
            "message": "No Cambridge rule passed the independent-review, source, crosswalk, test, and runtime allow-list gates.",
        })
        return {
            "status": "no_runtime_rules",
            "evaluated_rule_ids": [],
            "findings": [],
            "diagnostics": diagnostics,
        }

    sentence = str(envelope.get("sentence", ""))
    evaluations = []
    findings = []
    diagnostics = list(registry.get("diagnostics") or [])
    evaluated_ids = []
    for rule in active_rules:
        if not isinstance(rule, dict) or not rule.get("rule_id"):
            diagnostics.append({
                "code": "INVALID_ACTIVE_RULE",
                "message": "The registry returned a malformed active rule; it was not evaluated.",
            })
            continue
        rule_id = str(rule["rule_id"])
        rule_type = rule.get("rule_type")
        if rule_type not in {"constraint", "variety_restricted"}:
            diagnostics.append({
                "code": "NON_CONSTRAINT_RULE_BLOCKED",
                "message": f"{rule_id} is not an executable constraint or variety-restricted rule.",
            })
            continue
        if rule_type == "variety_restricted":
            required_variety = str(rule.get("variety") or "").strip()
            if not required_variety or not variety or variety.casefold() != required_variety.casefold():
                evaluations.append({"rule_id": rule_id, "status": "variety_not_selected"})
                continue
        if rule.get("scope") != "sentence":
            diagnostics.append({
                "code": "UNSUPPORTED_RUNTIME_SCOPE",
                "message": f"{rule_id} has scope {rule.get('scope')!r}; this evaluator currently supports sentence-scope checks only.",
            })
            continue
        check = rule.get("runtime_check")
        if not isinstance(check, dict) or check.get("kind") != _SUPPORTED_CHECK:
            diagnostics.append({
                "code": "UNSUPPORTED_RUNTIME_CHECK",
                "message": f"{rule_id} has no supported deterministic runtime_check; it was not executed.",
            })
            continue
        outcome = _evaluate_forbidden_sequences(sentence, check)
        if outcome["status"] == "invalid_check":
            diagnostics.append({
                "code": "INVALID_RUNTIME_CHECK",
                "message": f"{rule_id} has an empty or malformed forbidden_sequences value.",
            })
            continue
        evaluated_ids.append(rule_id)
        evaluations.append({"rule_id": rule_id, **outcome})
        if outcome["status"] == "violation":
            findings.append({
                "rule_id": rule_id,
                "rule_type": rule_type,
                "concept": rule.get("concept"),
                "violation": rule.get("violation"),
                "sources": rule.get("sources", []),
                "matched_sequences": outcome["matched_sequences"],
            })
    return {
        "status": "evaluated" if evaluated_ids else "no_implemented_rules",
        "evaluated_rule_ids": evaluated_ids,
        "evaluations": evaluations,
        "findings": findings,
        "diagnostics": diagnostics,
    }
