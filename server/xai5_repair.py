"""XAI-5: localize checked relations and re-evaluate immutable revisions.

An observed token adjacency is not by itself a licensed grammatical relation.
Only approved XAI-4 findings can create verified error IDs or resolution claims.
The currently shipped XAI-PRE manifest enables ZERO such rules.

Revisions may be user-written; none is silently suggested, applied or certified.
Every revision gets a separately produced canonical-analysis status and a fresh
full XAI-4 evaluation. Never reuse the original syntax tree for edited text.
"""
from __future__ import annotations

from difflib import SequenceMatcher
import hashlib
import json
from typing import Any

from xai4_partial import evaluate_xai4, tokenize
from xai_facts import build_fact_graph

VERSION = "xai5-repair-1.0.0"
MAX_REVISIONS = 4
MAX_SENTENCE = 1200


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:24]


def _tree_graph(analysis: dict[str, Any] | None, text: str) -> dict[str, Any] | None:
    if not isinstance(analysis, dict):
        return None
    tree = analysis.get("tree")
    if not isinstance(tree, dict) or tree.get("sentence") != text:
        return None
    if analysis.get("status") not in {"normalized", "working", "provisional"}:
        return None
    try:
        return build_fact_graph(analysis)
    except (ValueError, KeyError, TypeError, RecursionError):
        # A model-proposed or incomplete tree is not promoted to source truth.
        return None


def _attach_token(graph: dict[str, Any] | None, token: dict[str, Any] | None) -> dict[str, Any]:
    """Exact visible span only; don't conflate XAI-4 raw IDs with B-R token IDs."""
    result = {"status": "unavailable", "node_id": None, "ancestor_node_ids": [],
              "proof_atom_ids": []}
    if not graph or not token or graph.get("status") not in {"observed", "provisional"}:
        return result
    a, b = token["char_span"]
    matches = [
        n for n in graph["nodes"]
        if n["char_span"] is not None
        and n["char_span"][0] <= a and b <= n["char_span"][1]
        and n["kind"] not in {"empty", "gap", "elided_terminal"}
    ]
    # An explicit terminal must match the exact text span; otherwise return a
    # covering constituent/triangle without fabricating its internal lexemes.
    matches.sort(key=lambda n: (
        n["char_span"][1] - n["char_span"][0],
        0 if n["kind"] == "word" and n["char_span"] == [a, b] else 1,
        n["path"],
    ))
    if not matches:
        return result
    smallest = matches[0]
    exact_word = smallest["kind"] == "word" and smallest["char_span"] == [a, b]
    opaque = smallest["kind"] == "triangle"
    ids = {smallest["node_id"], *smallest["ancestor_ids"]}
    proof = [f["fact_id"] for f in graph["atoms"]
             if f["subject_node_id"] in ids
             and f["predicate"] in {"span", "node_kind", "direct_child_of"}]
    return {
        "status": ("exact_word" if exact_word else "opaque_triangle"
                   if opaque else "covering_constituent_only"),
        "node_id": smallest["node_id"],
        "ancestor_node_ids": list(smallest["ancestor_ids"]),
        "proof_atom_ids": list(dict.fromkeys(proof)),
    }


def localize_xai4(xai4: dict[str, Any], *, analysis: dict[str, Any] | None = None,
                  sentence: str | None = None) -> dict[str, Any]:
    """Separate verified diagnoses from provisional/blocked observations."""
    if not isinstance(xai4, dict) or xai4.get("schema_version") != "xai4-partial-1.0.0":
        raise ValueError("XAI-5 requires the server-produced XAI-4 result")
    # Caller input must not provide source authority through HTTP. This function
    # is only called after evaluate_xai4 inside the server.
    if sentence is None:
        sentence = (analysis or {}).get("sentence")
        if sentence is None and isinstance((analysis or {}).get("tree"), dict):
            sentence = analysis["tree"].get("sentence")
    if not isinstance(sentence, str):
        sentence = ""
    raw = {t["id"]: t for t in xai4.get("tokens", [])}
    graph = _tree_graph(analysis, sentence)
    observations = []
    for ev in xai4["evaluations"]:
        for row in ev.get("evidence", []):
            gov, target = raw.get(row["governor_token_id"]), raw.get(row["target_token_id"])
            if not gov or not target:
                continue
            observations.append({
                "observation_id": f"o{len(observations)+1:04d}",
                "rule_id": ev["rule_id"],
                "status": ev["status"],
                "authority": "APPROVED_CHECK" if ev.get("runtime_eligible") else "UNAPPROVED_CANDIDATE",
                "sentence_span": list(row["char_span"]),
                "token_span": list(row["token_span"]),
                "affected_token_ids": list(row["affected_token_ids"]),
                "governor_token_id": gov["id"], "target_token_id": target["id"],
                "governor_text": gov["text"], "target_text": target["text"],
                "governor_location": _attach_token(graph, gov),
                "target_location": _attach_token(graph, target),
                "tree_relationship_status": (
                    "position_only_no_licensed_function" if graph else "unavailable"),
                "description": (
                    "A reviewed narrow constraint was evaluated; no whole-sentence verdict follows."
                    if ev.get("runtime_eligible") else
                    "An unapproved raw-token construction candidate was observed. This is not an error diagnosis."
                ),
            })
    diagnoses = []
    for f in xai4["findings"]:
        # Eligibility and finding provenance are established by evaluate_xai4,
        # not untrusted canonical source fields.
        diagnoses.append({
            "finding_id": f["id"], "rule_id": f["rule_id"], "status": "VIOLATED",
            "affected_token_ids": list(f["affected_token_ids"]),
            "governor_token_id": f["governor_token_id"],
            "target_token_id": f["target_token_id"],
            "token_span": list(f["token_span"]), "char_span": list(f["char_span"]),
            "source_claim_ids": list(f["source_claim_ids"]),
            "governor_location": _attach_token(graph, raw.get(f["governor_token_id"])),
            "target_location": _attach_token(graph, raw.get(f["target_token_id"])),
            "interpretation_status": f["interpretation_status"],
        })
    return {
        "schema_version": VERSION, "language_policy": "ENGLISH_ONLY",
        "original_hash": _digest(sentence),
        "original_sentence": sentence,
        "analysis_status": (analysis or {}).get("status", "unresolved"),
        "tree_status": graph["status"] if graph else "unavailable",
        "tree_analysis_id": graph["analysis_id"] if graph else None,
        "enabled_rule_ids": list(xai4["enabled_rule_ids"]),
        "observations": observations, "diagnoses": diagnoses,
        "dependencies": list(xai4["dependencies"]),
        "groups": list(xai4["groups"]),
        "auto_repair_suggestions": [],
        "whole_sentence_certified": False,
        "scope": "observed_token_relations_and_approved_local_diagnoses_only",
    }


def _token_alignment(original: str, revised: str) -> tuple[list[dict[str, Any]], dict[str, str], bool]:
    """Compute source-frozen token edits and alignment for every candidate."""
    old, new = tokenize(original), tokenize(revised)
    sequence = SequenceMatcher(
        a=[t["text"] for t in old], b=[t["text"] for t in new], autojunk=False)
    mapping = {}
    edits = []
    for tag, i, j, k, m in sequence.get_opcodes():
        if tag == "equal":
            for oldtok, newtok in zip(old[i:j], new[k:m]):
                mapping[oldtok["id"]] = newtok["id"]
            continue
        before_start = old[i]["char_span"][0] if i < len(old) else len(original)
        before_end = old[j-1]["char_span"][1] if j > i else before_start
        after_start = new[k]["char_span"][0] if k < len(new) else len(revised)
        after_end = new[m-1]["char_span"][1] if m > k else after_start
        edits.append({
            "operation": "insert" if i == j else "delete" if k == m else "replace",
            "original_char_span": [before_start, before_end],
            "revised_char_span": [after_start, after_end],
            "original_token_ids": [t["id"] for t in old[i:j]],
            "revised_token_ids": [t["id"] for t in new[k:m]],
            "original_text": original[before_start:before_end],
            "replacement_text": revised[after_start:after_end],
        })
    # Whitespace-only edits are real but do not imply changed grammar evidence.
    formatting_changed = not edits and original != revised
    return edits, mapping, formatting_changed


def _reanalyze(text: str, *, chapter: int | None = None) -> dict[str, Any]:
    """Reparse the actual edited sentence; a failed parse is explicitly unknown."""
    try:
        from parse_engine import analyze
        from burton_roberts import build_canonical_analysis
        parsed = analyze(text, sentence_index=0)
        if parsed.get("sentence") != text:
            return {"status": "unresolved", "tree": None, "sentence": text,
                    "reparse_status": "source_not_fully_parsed"}
        analysis = build_canonical_analysis(
            parsed, chapter=chapter, appendix_nom=None)
        if not isinstance(analysis, dict):
            raise ValueError("canonicalizer returned an invalid analysis")
        analysis = {**analysis, "sentence": text}
        if analysis.get("status") not in {"normalized", "working", "provisional", "unresolved"}:
            return {"status": "unresolved", "tree": None, "sentence": text,
                    "reparse_status": "unsupported_analysis"}
        return {**analysis, "reparse_status": (
            "parsed" if analysis.get("status") == "normalized" else "unresolved")}
    except (Exception, RecursionError):
        return {"status": "unresolved", "tree": None, "sentence": text,
                "reparse_status": "unavailable_or_failed"}


def _snapshot(version: str, text: str, analysis: dict[str, Any],
              evaluation: dict[str, Any]) -> dict[str, Any]:
    tree = analysis.get("tree")
    if not isinstance(tree, dict) or tree.get("sentence") != text:
        tree = None
    # A new normalized canonical tree may be inspected independently.
    # Never present the old tree as the edited sentence's parse.
    if tree is not None and analysis.get("status") == "normalized":
        try:
            from explanations import validate_envelope
            validate_envelope(tree)
        except (ValueError, TypeError, RecursionError):
            tree = None
    else:
        tree = None
    return {
        "version_id": version, "text": text, "text_hash": _digest(text),
        "canonical_tree": tree,
        "tokens": list(evaluation["tokens"]),
        "analysis_status": analysis.get("status", "unresolved"),
        "reparse_status": analysis.get("reparse_status", "unavailable_or_failed"),
        "tree_id": tree.get("tree_id") if tree else None,
        "enabled_rule_ids": list(evaluation["enabled_rule_ids"]),
        "evaluation_status": evaluation["status"],
        "whole_sentence_certified": False,
    }


def _recheck_lineage(before_eval: dict[str, Any], after_eval: dict[str, Any],
                     original_to_revised: dict[str, str],
                     edits: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Track only ORIGINAL APPROVED findings; never infer a global grammar pass."""
    rows = []
    available = [ev for ev in after_eval["evaluations"] if ev.get("runtime_eligible")]
    for f in before_eval["findings"]:
        wanted_gov = original_to_revised.get(f["governor_token_id"])
        same_rule = [ev for ev in available if ev["rule_id"] == f["rule_id"]]
        candidates = []
        for ev in same_rule:
            for m in ev.get("evidence", []):
                # Where governor survives, its identity anchors the comparison.
                if wanted_gov and m["governor_token_id"] != wanted_gov:
                    continue
                candidates.append((ev, m))
        if not candidates and not wanted_gov:
            # Replacing the original governor may preserve its syntactic role,
            # but we cannot prove the role. Use only corresponding raw position.
            try:
                old_index = int(f["governor_token_id"][1:])
            except ValueError:
                old_index = -100
            candidates = [(ev, m) for ev in same_rule
                          for m in ev.get("evidence", [])
                          if abs(int(m["governor_token_id"][1:]) - old_index) <= 1]
        if len(candidates) == 1:
            ev, m = candidates[0]
            state = ev["status"]
            outcome = {
                "SATISFIED": "resolved_by_satisfaction",
                "VIOLATED": "persists",
                "NOT_APPLICABLE": "no_longer_applicable_after_rewrite",
                "BLOCKED": "blocked",
                "AMBIGUOUS": "ambiguous",
            }.get(state, "unimplemented")
            basis = "fresh_approved_rule_re_evaluation_with_token_alignment"
        else:
            state = ("NOT_APPLICABLE" if any(ev["status"] == "NOT_APPLICABLE"
                                            for ev in same_rule) else "BLOCKED")
            changed = any(set(edit["original_token_ids"]) &
                          set(f["affected_token_ids"]) for edit in edits)
            outcome = "no_longer_applicable_after_rewrite" if changed and state == "NOT_APPLICABLE" else "blocked"
            basis = "inapplicability_only" if outcome.startswith("no_longer") else "insufficient_identity_or_analysis"
        rows.append({
            "original_finding_id": f["id"], "rule_id": f["rule_id"],
            "outcome": outcome, "after_check_status": state,
            "evidence_basis": basis,
            "whole_sentence_certified": False,
        })
    return rows


def _new_findings(before_eval: dict[str, Any], after_eval: dict[str, Any],
                  edits: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Do not label a finding 'introduced' without a prior evidenced pass."""
    original_rules = {r["rule_id"] for r in before_eval["findings"]}
    prior = {ev["rule_id"]: ev for ev in before_eval["evaluations"]
             if ev.get("runtime_eligible")}
    new = []
    for after in after_eval["findings"]:
        old = prior.get(after["rule_id"])
        if after["rule_id"] in original_rules:
            # Could be persistence elsewhere: ambiguous without proven match.
            origin = "unknown"
            reason = "Original check also reported a violation; token identity may have changed."
        elif old is not None and old.get("status") == "SATISFIED" and edits:
            # Even then, a rule pass for one token does not rule out another.
            origin = "unknown"
            reason = "No verified one-to-one construction alignment proves this edit introduced the finding."
        else:
            origin = "unknown"
            reason = "No conclusive prior local state exists; an issue may have been unmasked."
        new.append({"finding_id": after["id"], "rule_id": after["rule_id"],
                    "origin": origin, "causal_evidence_ids": [],
                    "reason": reason, "whole_sentence_certified": False})
    return new


def _validate_revisions(payload: dict[str, Any]) -> tuple[str, list[dict[str, Any]], str | None, int | None]:
    if not isinstance(payload, dict) or set(payload) - {"text", "candidates", "variety", "chapter"}:
        raise ValueError("Only text, candidates, variety and chapter may be supplied")
    text = payload.get("text")
    if not isinstance(text, str) or not text.strip() or len(text) > MAX_SENTENCE:
        raise ValueError("Original text must contain 1 to 1200 characters")
    if len(tokenize(text)) > 200:
        raise ValueError("Original text exceeds 200 source tokens")
    variety = payload.get("variety")
    if variety is not None and (not isinstance(variety, str) or not variety.strip() or len(variety) > 80):
        raise ValueError("Selected variety is invalid")
    chapter = payload.get("chapter")
    if chapter is not None and (type(chapter) is not int or chapter < 1 or chapter > 11):
        raise ValueError("Chapter must be 1 to 11 or null")
    candidates = payload.get("candidates", [])
    if not isinstance(candidates, list) or len(candidates) > MAX_REVISIONS:
        raise ValueError("At most four revision candidates are supported")
    for i, candidate in enumerate(candidates, 1):
        if not isinstance(candidate, dict) or set(candidate) - {"text", "parent_version_id"}:
            raise ValueError("Each revision must have only text and parent_version_id")
        value = candidate.get("text")
        if (not isinstance(value, str) or not value.strip()
                or len(value) > MAX_SENTENCE or len(tokenize(value)) > 200):
            raise ValueError("A revision contains invalid or oversized English text")
        if value == text:
            raise ValueError("A revision must differ from the original text")
        parent = candidate.get("parent_version_id", "u0")
        if parent not in {"u0"} | {f"v{j}" for j in range(1, i)}:
            raise ValueError("Revision parent must be the original or an earlier revision")
    return text, candidates, variety, chapter


def recheck_revisions(payload: dict[str, Any], *, analyzer=None,
                      root=None) -> dict[str, Any]:
    """Immutable original and up to four alternative/staged user revisions.

    analyzer and root are **server-side dependency injection only** for tests.
    No HTTP handler forwards these arguments from user input. The production
    backend uses the actual parser/canonicalizer on every snapshot.
    """
    text, candidates, variety, chapter = _validate_revisions(payload)
    parse = analyzer or (lambda value: _reanalyze(value, chapter=chapter))
    versions: dict[str, tuple[dict, dict, dict]] = {}

    def observe(ident: str, value: str):
        try:
            analysis = parse(value)
            if not isinstance(analysis, dict):
                raise ValueError("analyzer returned non-object")
            analysis = {**analysis, "sentence": value}
        except (Exception, RecursionError):
            analysis = {"status": "unresolved", "tree": None,
                        "sentence": value, "reparse_status": "unavailable_or_failed"}
        evaluated = evaluate_xai4(value, analysis_status=analysis.get("status", "unresolved"),
                                  variety=variety, root=root)
        localized = localize_xai4(evaluated, analysis=analysis, sentence=value)
        versions[ident] = (analysis, evaluated, localized)
        return _snapshot(ident, value, analysis, evaluated), localized

    original, origin_map = observe("u0", text)
    results = []
    for i, row in enumerate(candidates, start=1):
        ident = f"v{i}"
        revised = row["text"]
        parent_id = row.get("parent_version_id", "u0")
        parent_text = text if parent_id == "u0" else results[int(parent_id[1:]) - 1]["snapshot"]["text"]
        # Reparse AND re-run every approved/blocked check from scratch on this
        # exact version; do not propagate original tree evidence to revisions.
        snapshot, localization = observe(ident, revised)
        edits, token_map, formatting = _token_alignment(text, revised)
        step_edits, step_map, step_formatting = _token_alignment(parent_text, revised)
        lineage = _recheck_lineage(versions["u0"][1], versions[ident][1], token_map, edits)
        step_lineage = _recheck_lineage(
            versions[parent_id][1], versions[ident][1], step_map, step_edits)
        fresh = _new_findings(versions["u0"][1], versions[ident][1], edits)
        results.append({
            "version_id": ident, "parent_version_id": parent_id,
            "snapshot": snapshot, "edits_from_original": edits,
            "formatting_only_change": formatting,
            "step_edits": step_edits,
            "step_formatting_only_change": step_formatting,
            "token_alignment": token_map,
            "original_finding_lineage": lineage,
            "parent_finding_lineage": step_lineage,
            "new_findings": fresh,
            "localization": localization,
            "meaning_status": "not_assessed",
            "candidate_status": "user_revision_not_a_verified_correction",
            "whole_sentence_certified": False,
        })
    return {
        "schema_version": VERSION, "language_policy": "ENGLISH_ONLY",
        "mode": "server_recheck", "original": original,
        "original_localization": origin_map,
        "revisions": results, "original_finding_ids": [f["id"] for f in versions["u0"][1]["findings"]],
        "auto_suggestions": [], "whole_sentence_certified": False,
        "global_verdict": "NOT_CERTIFIED",
        "diagnostic_rule_count": len(versions["u0"][1]["enabled_rule_ids"]),
        "note": ("Every revision is independently reparsed and all eligible checks are rerun. "
                 "Absence of a finding is not a whole-sentence grammar certificate."),
    }


def repair_request(data: dict[str, Any]) -> dict[str, Any]:
    """HTTP-safe entrypoint; no runtime source, analyzer or rule injection."""
    return recheck_revisions(data)
