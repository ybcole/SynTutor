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


def _token_alignment(original: str, revised: str) -> tuple[list[dict[str, Any]], dict[str, str]]:
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
    return {
        "version_id": version, "text": text, "text_hash": _digest(text),
        "tokens": list(evaluation["tokens"]),
        "analysis_status": analysis.get("status", "unresolved"),
        "reparse_status": analysis.get("reparse_status", "unavailable_or_failed"),
        "tree_id": tree.get("tree_id") if tree else None,
        "enabled_rule_ids": list(evaluation["enabled_rule_ids"]),
        "evaluation_status": evaluation["status"],
        "whole_sentence_certified": False,
    }
