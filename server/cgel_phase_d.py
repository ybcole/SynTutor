"""Phase D candidate correction for a selected sentence.

This pipeline is deliberately separate from the production matrix and the
fail-closed Cambridge registry. It runs candidate-only probes, proposes their
explicit edit hints, reparses each candidate sentence, reruns the probes and
reports local lineage. It never certifies the whole sentence as grammatical.
"""
from __future__ import annotations

import glob
import hashlib
import importlib
import json
from pathlib import Path
from typing import Any, Callable

if __package__:
    from .parse_engine import analyze
else:
    from parse_engine import analyze


SCHEMA_VERSION = "cgel-phase-d-1.0.0"
MAX_CANDIDATES = 12
MAX_STATES = 40
MAX_SENTENCE = 1200
TEXT_PROBES = [
    ("cgel_spelling_probe", "probe_spelling"),
    ("cgel_pronoun_case_probe", "probe_pronoun_case"),
    ("cgel_proform_probe", "probe_proform"),
    ("cgel_order_usage_probe", "probe_order_usage"),
    ("cgel_final_surface_probe", "probe_final_surface"),
]
TREE_PROBES = [
    ("cgel_punctuation_probe", "probe_all"),
    ("cgel_tense_aspect_probe", "probe_tense_aspect"),
    ("cgel_determiner_probe", "probe_determiner"),
    ("cgel_verb_form_probe", "probe_verb_form"),
    ("cgel_usage_probe", "probe_usage"),
    ("cgel_word_order_probe", "probe_word_order"),
]
SIMPLE_TREE_PROBES = [
    ("cgel_article_parser_probe", "probe_article_parser"),
    ("cgel_case_probe", "probe_pronoun_case"),
    ("cgel_case_probe", "probe_infinitival_case"),
    ("cgel_case_probe", "probe_local_reflexive"),
    ("cgel_case_probe", "probe_pride_reflexive"),
    ("cgel_case_probe", "probe_comparative_like_case"),
    ("cgel_doubling_probe", "probe_consonant_doubling"),
    ("cgel_doubling_probe", "probe_mute_e"),
    ("cgel_doubling_probe", "probe_final_ie"),
    ("cgel_doubling_probe", "probe_final_y_plural"),
    ("cgel_genitive_probe", "probe_plural_genitives"),
    ("cgel_genitive_probe", "probe_personal_genitives"),
    ("cgel_coordination_probe", "probe_coordination"),
    ("cgel_coordination_probe", "probe_coordinated_determiner"),
    ("cgel_comparative_probe", "probe_comparative_gap"),
    ("cgel_comparative_probe", "probe_comparative_subject"),
    ("cgel_catenative_probe", "probe_interrogative_infinitival_subject"),
    ("cgel_catenative_probe", "probe_participial_relative_marker"),
    ("cgel_catenative_probe", "probe_determined_participle"),
    ("cgel_enjoy_parser_probe", "probe_enjoy_parser"),
    ("cgel_modal_parser_probe", "probe_modal_parser"),
    ("cgel_imperative_probe", "probe_inclusive_lets"),
    ("cgel_imperative_probe", "probe_reported_negative_directive"),
    ("cgel_inversion_probe", "probe_which_partitive"),
    ("cgel_lexical_number_probe", "probe_demonstrative_number"),
    ("cgel_lexical_number_probe", "probe_total_number"),
    ("cgel_tag_probe", "probe_tag_auxiliary"),
    ("cgel_tag_probe", "probe_tag_agreement"),
    ("cgel_passive_make_candidate", "probe_passive_make"),
    ("cgel_role_object_probe", "probe_role_object"),
]
ROOT = Path(__file__).resolve().parents[1]


def _load_module(name: str):
    if __package__:
        return importlib.import_module(f"{__package__}.{name}")
    return importlib.import_module(name)


def _rule_map() -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for path in glob.glob(str(ROOT / "grammar/rules/*.json")):
        try:
            data = json.loads(Path(path).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(data, dict):
            data = data.get("rules") or [data]
        for row in data:
            rule_id = row.get("id")
            if not rule_id:
                continue
            diagnostic = row.get("diagnostic") or {}
            rows[rule_id] = {
                "learner_explanation": diagnostic.get("learner_explanation") or "",
                "statement": row.get("statement") or "",
                "rule_type": row.get("rule_type"),
                "sources": row.get("sources") or [],
            }
    return rows


RULES = _rule_map()


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:24]


def _finding_key(finding: dict[str, Any]) -> tuple:
    edit = finding.get("edit_hint") or {}
    span = tuple(edit.get("char_span") or edit.get("span") or [])
    return (
        finding.get("rule_id"),
        finding.get("relation", {}).get("kind"),
        span,
        edit.get("replacement"),
    )


def _normalize(candidate: dict[str, Any], probe: str) -> dict[str, Any] | None:
    rule_id = candidate.get("rule_id")
    if not rule_id:
        return None
    edit = candidate.get("edit_hint")
    if not isinstance(edit, dict):
        edit = None
    rule = RULES.get(rule_id, {})
    return {
        "rule_id": rule_id,
        "source_chapter": candidate.get("source_chapter"),
        "source_pages": candidate.get("source_pages") or [],
        "relation": candidate.get("relation") or {},
        "edit_hint": edit,
        "probe": probe,
        "learner_explanation": rule.get("learner_explanation", ""),
        "statement": rule.get("statement", ""),
        "rule_type": rule.get("rule_type"),
        "production_enabled": False,
    }


def _run_probe(module_name: str, function_name: str, sentence: str,
               tree: dict[str, Any] | None, *, tree_required: bool) -> dict[str, Any]:
    module = _load_module(module_name)
    function = getattr(module, function_name)
    if tree_required and tree is None:
        return {"status": "not_evaluated", "candidates": [],
                "blocked": ["tree_unavailable"]}
    if tree_required:
        try:
            return function(sentence, tree)
        except TypeError:
            return function(sentence, tree, variety="standard_english")
    return function(sentence)


def collect_candidate_findings(sentence: str,
                               tree: dict[str, Any] | None = None, *,
                               include_tree_binding: bool = True) -> dict[str, Any]:
    result = {
        "status": "candidate_only",
        "production_enabled": False,
        "sentence": sentence,
        "findings": [],
        "blocked": [],
        "probes": [],
    }
    for module_name, function_name in TEXT_PROBES:
        try:
            output = _run_probe(module_name, function_name, sentence, tree,
                                tree_required=False)
        except Exception as error:  # probe isolation: one failure is not a finding
            result["blocked"].append(f"{function_name}: {type(error).__name__}: {error}")
            continue
        result["probes"].append(function_name)
        for candidate in output.get("candidates", []):
            finding = _normalize(candidate, function_name)
            if finding is not None:
                result["findings"].append(finding)
        result["blocked"].extend(output.get("blocked", []))
    for module_name, function_name in TREE_PROBES:
        try:
            output = _run_probe(module_name, function_name, sentence, tree,
                                tree_required=True)
        except Exception as error:
            result["blocked"].append(f"{function_name}: {type(error).__name__}: {error}")
            continue
        result["probes"].append(function_name)
        for candidate in output.get("candidates", []):
            finding = _normalize(candidate, function_name)
            if finding is not None:
                result["findings"].append(finding)
        result["blocked"].extend(output.get("blocked", []))
    for module_name, function_name in SIMPLE_TREE_PROBES:
        try:
            output = _run_probe(module_name, function_name, sentence, tree,
                                tree_required=True)
        except Exception as error:
            result["blocked"].append(f"{function_name}: {type(error).__name__}: {error}")
            continue
        result["probes"].append(function_name)
        for candidate in output.get("candidates", []):
            finding = _normalize(candidate, function_name)
            if finding is not None:
                result["findings"].append(finding)
        result["blocked"].extend(output.get("blocked", []))
    seen = set()
    deduped = []
    for finding in result["findings"]:
        key = _finding_key(finding)
        if key in seen:
            continue
        seen.add(key)
        finding["finding_id"] = f"f{len(deduped) + 1:03d}"
        deduped.append(finding)
    result["findings"] = deduped
    if include_tree_binding and tree is not None and deduped:
        try:
            if __package__:
                from .cgel_candidate_xai import (bind_finding,
                                                 build_benepar_index,
                                                 compose_candidate_explanation)
            else:
                from cgel_candidate_xai import (bind_finding,
                                                build_benepar_index,
                                                compose_candidate_explanation)
            index = build_benepar_index(tree, sentence)
            for finding in deduped:
                binding = bind_finding(index, finding)
                finding["tree_binding"] = binding
                finding["candidate_explanation"] = compose_candidate_explanation(
                    index, finding, binding)
        except Exception as error:
            result["blocked"].append(
                f"candidate_xai: {type(error).__name__}: {error}")
    result["blocked"] = list(dict.fromkeys(result["blocked"]))
    return result


def _edits(findings: list[dict[str, Any]]) -> dict[tuple, dict[str, Any]]:
    groups: dict[tuple, dict[str, Any]] = {}
    for finding in findings:
        hint = finding.get("edit_hint")
        if not isinstance(hint, dict):
            continue
        span = hint.get("char_span") or hint.get("span")
        replacement = hint.get("replacement")
        if not (isinstance(span, (list, tuple)) and len(span) == 2
                and all(isinstance(value, int) for value in span)
                and isinstance(replacement, str)):
            continue
        key = (span[0], span[1], replacement)
        group = groups.setdefault(key, {
            "span": list(span), "replacement": replacement, "rule_ids": [],
        })
        if finding["rule_id"] not in group["rule_ids"]:
            group["rule_ids"].append(finding["rule_id"])
    return groups


def _valid_edit(sentence: str, edit: dict[str, Any]) -> bool:
    start, end = edit["span"]
    return 0 <= start <= end <= len(sentence)


def _apply(sentence: str, edits: list[dict[str, Any]]) -> str | None:
    ordered = sorted(edits, key=lambda edit: edit["span"][0], reverse=True)
    previous_start = len(sentence) + 1
    text = sentence
    for edit in ordered:
        start, end = edit["span"]
        if end > previous_start:
            return None
        text = text[:start] + edit["replacement"] + text[end:]
        previous_start = start
    return text


def _lineage(original: list[dict[str, Any]], candidate: list[dict[str, Any]],
             targeted: set[str]) -> list[dict[str, Any]]:
    original_by_rule: dict[str, list[dict[str, Any]]] = {}
    candidate_by_rule: dict[str, list[dict[str, Any]]] = {}
    for finding in original:
        original_by_rule.setdefault(finding["rule_id"], []).append(finding)
    for finding in candidate:
        candidate_by_rule.setdefault(finding["rule_id"], []).append(finding)
    rows = []
    for rule_id, findings in original_by_rule.items():
        if rule_id in candidate_by_rule:
            status = "persists"
        elif rule_id in targeted:
            status = "targeted_cleared"
        else:
            status = "no_longer_detected"
        rows.append({
            "rule_id": rule_id,
            "status": status,
            "original_finding_ids": [finding["finding_id"] for finding in findings],
            "candidate_finding_ids": [finding["finding_id"]
                                      for finding in candidate_by_rule.get(rule_id, [])],
        })
    for rule_id in candidate_by_rule:
        if rule_id not in original_by_rule:
            rows.append({
                "rule_id": rule_id,
                "status": "new_violation",
                "original_finding_ids": [],
                "candidate_finding_ids": [finding["finding_id"]
                                          for finding in candidate_by_rule[rule_id]],
            })
    return rows


def _candidate_score(original_ids: set[str], candidate: dict[str, Any],
                     edit_count: int, char_delta: int) -> tuple:
    candidate_ids = {finding["rule_id"] for finding in candidate["findings"]}
    new_ids = candidate_ids - original_ids
    unresolved = len(candidate["findings"])
    resolved = len(original_ids - candidate_ids)
    return (len(new_ids), unresolved, edit_count, char_delta, -resolved)


def correct_selected_sentence(sentence: str, *,
                              max_candidates: int = MAX_CANDIDATES,
                              variety: str = "standard_english") -> dict[str, Any]:
    if not isinstance(sentence, str) or not sentence.strip():
        return {
            "schema_version": SCHEMA_VERSION, "status": "not_evaluated",
            "production_enabled": False, "scope": "selected_sentence_candidate_only",
            "blocked": ["empty_selection"], "original": None, "correction": None,
        }
    if len(sentence) > MAX_SENTENCE:
        return {
            "schema_version": SCHEMA_VERSION, "status": "not_evaluated",
            "production_enabled": False, "scope": "selected_sentence_candidate_only",
            "blocked": ["selection_too_long"], "original": {"text": sentence},
            "correction": None,
        }
    try:
        analysis = analyze(sentence)
        tree = analysis.get("root")
    except Exception as error:
        tree = None
        parse_block = f"parse_failed: {type(error).__name__}: {error}"
    else:
        parse_block = None
    initial = collect_candidate_findings(sentence, tree)
    if parse_block:
        initial["blocked"].append(parse_block)
    original_ids = {finding["rule_id"] for finding in initial["findings"]}
    unresolved = [finding for finding in initial["findings"]
                  if not isinstance(finding.get("edit_hint"), dict)]
    groups = _edits(initial["findings"])
    candidates = []
    seen = {_digest(sentence)}
    if groups and variety == "standard_english":
        unique = list(groups.values())
        packages = [[edit] for edit in unique if _valid_edit(sentence, edit)]
        if len(unique) > 1:
            packages.append(unique)
        for edits in packages[:max_candidates]:
            text = _apply(sentence, edits)
            if text is None or text == sentence or _digest(text) in seen:
                continue
            seen.add(_digest(text))
            try:
                candidate_analysis = analyze(text)
                candidate_tree = candidate_analysis.get("root")
                candidate_result = collect_candidate_findings(text, candidate_tree)
            except Exception as error:
                candidates.append({
                    "text": text,
                    "edits": edits,
                    "status": "candidate_parse_failed",
                    "blocked": [f"{type(error).__name__}: {error}"],
                    "findings": [],
                    "score": None,
                })
                continue
            targeted = {rule_id for edit in edits for rule_id in edit["rule_ids"]}
            lineage = _lineage(initial["findings"], candidate_result["findings"], targeted)
            candidate_ids = {finding["rule_id"] for finding in candidate_result["findings"]}
            new_ids = candidate_ids - original_ids
            score = _candidate_score(original_ids, candidate_result, len(edits),
                                     len(text) - len(sentence))
            candidates.append({
                "text": text,
                "edits": edits,
                "targeted_rule_ids": sorted(targeted),
                "findings": candidate_result["findings"],
                "lineage": lineage,
                "new_rule_ids": sorted(new_ids),
                "safe_local": not new_ids,
                "score": list(score),
                "blocked": candidate_result["blocked"],
            })
    candidates.sort(key=lambda row: (
        row.get("score") is None,
        not row.get("safe_local", False),
        row["score"] if row.get("score") is not None else [999, 999, 999, 999, 999],
        len(row["text"]),
        row["text"],
    ))
    best = next((row for row in candidates
                 if row.get("safe_local") and row.get("score") is not None
                 and row["score"][0] == 0), None)
    if best is None and candidates:
        best = candidates[0]
    if best is not None and not best.get("safe_local", False):
        best = None
    correction = best["text"] if best is not None else None
    remaining = best["findings"] if best is not None else []
    if not initial["findings"]:
        status = "no_findings"
    elif correction and (unresolved or remaining):
        status = "partial_candidate_correction"
    elif correction:
        status = "candidate_correction"
    else:
        status = "no_safe_correction"
    return {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "production_enabled": False,
        "scope": "selected_sentence_candidate_only",
        "original": {
            "text": sentence,
            "sha256": _digest(sentence),
            "findings": initial["findings"],
            "blocked": initial["blocked"],
        },
        "correction": correction,
        "best_candidate": best,
        "candidates": candidates,
        "unresolved_findings": unresolved,
        "blocked": initial["blocked"],
        "caveat": ("Only candidate probes ran. A cleared finding is absence from "
                   "this candidate check, not proof of whole-sentence grammaticality."),
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Phase D candidate correction for one sentence")
    parser.add_argument("sentence")
    parser.add_argument("--max-candidates", type=int, default=MAX_CANDIDATES)
    args = parser.parse_args()
    print(json.dumps(correct_selected_sentence(args.sentence,
                                               max_candidates=args.max_candidates),
                     indent=2, ensure_ascii=False))
