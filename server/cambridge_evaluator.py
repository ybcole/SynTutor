"""Fail-closed deterministic executor for runtime-enabled Cambridge rules.

Only reviewed and allow-listed records are considered. This module implements a
small set of explicit surface and structural checks. A rule must carry a machine-readable runtime_check and pass
the registry's source/review/crosswalk/test gates before execution.
"""
from __future__ import annotations

import re
from typing import Any

try:
    from .burton_roberts import validate_canonical_tree
    from .cgel_passive_make_candidate import probe_passive_make
    from .cgel_passive_make_grounding import ground_passive_make_candidates
    from .cambridge_runtime_probes import run_candidate_probe
except ImportError:  # direct script-directory imports
    from burton_roberts import validate_canonical_tree
    from cgel_passive_make_candidate import probe_passive_make
    from cgel_passive_make_grounding import ground_passive_make_candidates
    from cambridge_runtime_probes import run_candidate_probe


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
    def valid_sequence(value: Any) -> bool:
        return (isinstance(value, list) and bool(value)
                and all(isinstance(token, str) and token.strip() for token in value))

    if not isinstance(forbidden, list) or not forbidden or not all(valid_sequence(row) for row in forbidden):
        return {"status": "invalid_check", "matched_sequences": []}
    if not isinstance(exceptions, list) or not all(valid_sequence(row) for row in exceptions):
        return {"status": "invalid_check", "matched_sequences": []}

    exception_spans = []
    for sequence in exceptions:
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


def _evaluate_passive_make(analysis, variety):
    if not variety or variety.casefold() != "standard_english":
        return {"status": "variety_not_selected"}
    parser_evidence = analysis.get("parser_diagnostics")
    if not isinstance(parser_evidence, dict):
        return {"status": "evidence_unavailable"}
    raw = parser_evidence.get("raw_candidate_tree")
    if not isinstance(raw, dict):
        return {"status": "evidence_unavailable"}

    sentence = analysis["tree"]["sentence"]
    try:
        probe = probe_passive_make(sentence, raw, variety="standard_english")
        candidates = probe["candidates"]
        evidence = ground_passive_make_candidates(analysis, candidates)
    except (KeyError, TypeError, ValueError, AttributeError, OSError, RecursionError):
        return {"status": "evidence_unavailable"}
    if probe["status"] != "candidate_only":
        return {"status": "evidence_unavailable"}
    matches = [
        {"relation": candidate["relation"], "char_span": candidate["char_span"],
         "governor_node_id": nodes["governor"]["node_id"],
         "dependent_node_id": nodes["dependent"]["node_id"],
         "grounding": nodes["observed_clause_link"], "edit_hint": candidate["edit_hint"]}
        for candidate, nodes in zip(candidates, evidence)
        if "observed_clause_link" in nodes
    ]
    if matches:
        return {"status": "violation", "structural_matches": matches}
    return {"status": "evidence_unavailable" if candidates else "not_applicable"}


def _evaluate_candidate_probe(sentence: str, rule_id: str,
                              check: dict[str, Any], raw_tree: Any) -> dict[str, Any]:
    probe_name = check.get("probe")
    if not isinstance(probe_name, str) or not probe_name:
        return {"status": "invalid_check", "candidate_matches": []}
    try:
        candidates = run_candidate_probe(probe_name, sentence, raw_tree)
    except KeyError:
        return {"status": "invalid_check", "candidate_matches": []}
    except (TypeError, ValueError, AttributeError, OSError, RecursionError):
        return {"status": "evidence_unavailable", "candidate_matches": []}
    matches = [candidate for candidate in candidates
               if isinstance(candidate, dict) and candidate.get("rule_id") == rule_id]
    if matches:
        return {"status": "violation", "candidate_matches": matches}
    return {"status": "passed", "candidate_matches": []}


def _evaluate_candidate_probe_set(sentence: str, rule_id: str,
                                   check: dict[str, Any], raw_tree: Any,
                                   cache: dict[str, dict[str, list[dict[str, Any]]]]) -> dict[str, Any]:
    set_name = check.get("set")
    if set_name != "phase_c":
        return {"status": "invalid_check", "candidate_matches": []}
    if set_name not in cache:
        try:
            if __package__:
                from .cgel_phase_d import collect_candidate_findings
            else:
                from cgel_phase_d import collect_candidate_findings
            result = collect_candidate_findings(sentence, raw_tree,
                                                include_tree_binding=False)
        except Exception:
            return {"status": "evidence_unavailable", "candidate_matches": []}
        grouped: dict[str, list[dict[str, Any]]] = {}
        for finding in result.get("findings", []):
            grouped.setdefault(finding.get("rule_id"), []).append(finding)
        cache[set_name] = grouped
    matches = cache[set_name].get(rule_id, [])
    if matches:
        return {"status": "violation", "candidate_matches": matches}
    return {"status": "passed", "candidate_matches": []}


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
    if variety is not None and (not isinstance(variety, str) or not variety.strip()):
        return {
            "status": "invalid_variety",
            "evaluated_rule_ids": [],
            "findings": [],
            "diagnostics": [{
                "code": "INVALID_SELECTED_VARIETY",
                "message": "Selected variety must be a non-empty string or null.",
            }],
        }
    if isinstance(variety, str):
        variety = variety.strip()
    try:
        validation = validate_canonical_tree(envelope)
    except Exception as exc:
        validation = {"valid": False, "errors": [f"{type(exc).__name__}: {exc}"]}
    if not validation.get("valid"):
        return {
            "status": "not_evaluated",
            "evaluated_rule_ids": [],
            "findings": [],
            "diagnostics": [{
                "code": "CANONICAL_TREE_INVALID",
                "message": "Cambridge rules require a valid M1 Burton-Roberts canonical envelope: "
                           + "; ".join(validation.get("errors") or ["validation failed"]),
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
    candidate_cache: dict[str, dict[str, list[dict[str, Any]]]] = {}
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
        check = rule.get("runtime_check")
        kind = check.get("kind") if isinstance(check, dict) else None
        if kind == "passive_make_missing_to" and rule_id == "CLS-357" and (
                rule.get("scope") == "clause" and set(check) == {"kind"}):
            outcome = _evaluate_passive_make(analysis, variety)
        elif kind == "candidate_probe_set":
            raw_tree = (analysis.get("parser_diagnostics") or {}).get("raw_candidate_tree")
            outcome = _evaluate_candidate_probe_set(sentence, rule_id, check, raw_tree,
                                                     candidate_cache)
        elif kind == "candidate_probe":
            raw_tree = (analysis.get("parser_diagnostics") or {}).get("raw_candidate_tree")
            outcome = _evaluate_candidate_probe(sentence, rule_id, check, raw_tree)
        elif rule.get("scope") != "sentence":
            diagnostics.append({
                "code": "UNSUPPORTED_RUNTIME_SCOPE",
                "message": f"{rule_id} has no supported check for scope {rule.get('scope')!r}.",
            })
            continue
        elif kind == _SUPPORTED_CHECK:
            outcome = _evaluate_forbidden_sequences(sentence, check)
        else:
            diagnostics.append({
                "code": "UNSUPPORTED_RUNTIME_CHECK",
                "message": f"{rule_id} has no supported deterministic runtime_check; it was not executed.",
            })
            continue
        if outcome["status"] == "invalid_check":
            diagnostics.append({
                "code": "INVALID_RUNTIME_CHECK",
                "message": f"{rule_id} has an empty or malformed forbidden_sequences value.",
            })
            continue
        evaluations.append({"rule_id": rule_id, **outcome})
        if outcome["status"] in {"evidence_unavailable", "variety_not_selected"}:
            continue
        evaluated_ids.append(rule_id)
        if outcome["status"] == "violation":
            findings.append({
                "rule_id": rule_id,
                "rule_type": rule_type,
                "concept": rule.get("concept"),
                "violation": rule.get("violation"),
                "sources": rule.get("sources", []),
                "matched_sequences": outcome.get("violating_matches", outcome.get("matched_sequences", [])),
                "excepted_matches": outcome.get("excepted_matches", []),
                **({"structural_matches": outcome["structural_matches"]} if "structural_matches" in outcome else {}),
                **({"candidate_matches": outcome["candidate_matches"]} if "candidate_matches" in outcome else {}),
            })
    return {
        "status": "evaluated" if evaluated_ids else "no_implemented_rules",
        "evaluated_rule_ids": evaluated_ids,
        "evaluations": evaluations,
        "findings": findings,
        "diagnostics": diagnostics,
    }
