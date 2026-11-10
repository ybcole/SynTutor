"""XAI-2: deterministic, sentence-specific observations of a B-R tree.

No claim in this module is a Cambridge grammar verdict, a head assignment, or
an independently approved grammatical function. The XAI-1 concept registry is
pending independent review; it is NEVER a runtime role-licensing registry.

A fact is a witnessed property of an already validated canonical/working
tree. Triangles remain opaque; indexed positions are not silently linked.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any

VERSION = "xai-facts-2.0.0"
PHRASES = {"S", "S'", "S''", "NP", "NOM", "VP", "PP", "AP", "AdvP"}
CLAUSES = {"S", "S'", "S''"}
LEXICAL = {"V", "N", "P", "A", "Adv", "ART", "PRO", "PRON", "NAME"}
AUXILIARIES = {"MOD", "PERF", "PROG", "PASS", "TENSE"}


def _kind(node: dict[str, Any]) -> str:
    if "word" in node:
        return "elided_terminal" if node.get("elided") else "word"
    if node.get("gap"):
        return "gap"
    if node.get("empty"):
        return "empty"
    if node.get("triangle"):
        return "triangle"
    return "branch"


def _span(node: dict[str, Any], children: list[dict[str, Any]]) -> list[int] | None:
    if node.get("token_span") is not None:
        return list(node["token_span"])
    spans = [child["token_span"] for child in children if child["token_span"]
             and child["token_span"][0] < child["token_span"][1]]
    return [min(s[0] for s in spans), max(s[1] for s in spans)] if spans else None


def _char_span(tokens: list[dict[str, Any]], span: list[int] | None) -> list[int] | None:
    if span is None:
        return None
    a, b = span
    if a == b:
        if a < len(tokens):
            pos = tokens[a]["char_span"][0]
        elif tokens:
            pos = tokens[-1]["char_span"][1]
        else:
            pos = 0
        return [pos, pos]
    return [tokens[a]["char_span"][0], tokens[b - 1]["char_span"][1]]


def _subgraph(root: dict[str, Any], tokens: list[dict[str, Any]],
              sentence: str, provisional: bool) -> dict[str, Any]:
    """Copy verified node properties without guessing missing branches/roles."""
    records: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    atoms: list[dict[str, Any]] = []
    evidence_kind = "provisional_tree_observation" if provisional else "validated_tree_observation"
    uncertainty = "provisional" if provisional else "none"
    provenance = ["provisional_working_tree" if provisional else "validated_canonical_tree"]

    def atom(predicate: str, subject: str, value: Any, path: str,
             other: str | None = None) -> None:
        atoms.append({
            "fact_id": f"f{len(atoms) + 1:05d}",
            "predicate": predicate,
            "subject_node_id": subject,
            "object_node_id": other,
            "value": value,
            "evidence_kind": evidence_kind,
            "uncertainty": uncertainty,
            "source_rule_ids": [],
            "provenance": provenance,
            "proof_path": path,
        })

    def visit(node: dict[str, Any], path: str, parent_id: str | None,
              ancestors: list[str], position: int | None) -> dict[str, Any]:
        ident = node.get("id") or path
        kind = _kind(node)
        label = node.get("label")
        children = node.get("children", [])
        child_ids = [child.get("id") or f"{path}.{i}" for i, child in enumerate(children)]
        child_records = [visit(child, f"{path}.{i}", ident, [ident] + ancestors, i)
                         for i, child in enumerate(children)]
        span = _span(node, child_records)
        chars = _char_span(tokens, span)
        # Real source substrings preserve contractions and original whitespace.
        surface = sentence[chars[0]:chars[1]] if chars else ""
        if kind in {"gap", "empty", "elided_terminal"}:
            surface = ""
        if not sentence and span and span[0] < span[1]:
            surface = " ".join(t["text"] for t in tokens[span[0]:span[1]])
        sibling_ids = []
        if parent_id is not None:
            # Filled after the full pre-order traversal.
            sibling_ids = []
        entry = {
            "node_id": ident,
            "path": path,
            "kind": kind,
            "label": label,
            "surface": surface,
            "token_span": span,
            "char_span": chars,
            "token_ids": list(range(span[0], span[1])) if span else [],
            "parent_id": parent_id,
            "child_ids": child_ids,
            "sibling_ids": sibling_ids,
            "position": position,
            "ancestor_ids": ancestors,
            "features": list(node.get("features", [])),
            "index": node.get("index"),
            "empty_role": node.get("empty_role") if kind == "empty" else None,
            "head_node_id": None,
            "head_status": "unknown_unlicensed",
            "function": None,
            "function_status": "unknown_unlicensed",
            "observation_status": "provisional" if provisional else "validated",
        }
        records.append(entry)
        atom("node_kind", ident, kind, path)
        if label is not None:
            atom("category_label", ident, label, path)
        if span is not None:
            atom("span", ident, {"token_span": span, "char_span": chars, "surface": surface}, path)
        for feature in entry["features"]:
            atom("feature_marked", ident, feature, path)
        if entry["index"] is not None:
            atom("index_marked", ident, entry["index"], path)
        if kind == "empty":
            atom("empty_position", ident, {"empty_role": entry["empty_role"], "token_span": span}, path)
        if kind == "gap":
            atom("gap_position", ident, {"index": entry["index"]}, path)
        if kind == "triangle":
            atom("opaque_triangle", ident, {"unlabelled": bool(node.get("unlabelled")),
                                           "words": list(node["words"])}, path)
        if kind == "elided_terminal":
            atom("elided_terminal", ident, node["word"], path)
        for i, child in enumerate(child_records):
            child_id = child["node_id"]
            edge = {"parent_id": ident, "child_id": child_id,
                    "position": i,
                    "sibling_ids": [c for c in child_ids if c != child_id],
                    "edge_status": "provisional" if provisional else "observed"}
            edges.append(edge)
            atom("direct_child_of", child_id, {"position": i, "siblings": edge["sibling_ids"]},
                 child["path"], ident)
        return entry

    visit(root, "root", None, [], None)
    # visit() emits entries after descendants. Sort into stable root-first order.
    records.sort(key=lambda item: (item["path"].count("."), [int(x) for x in item["path"].split(".")[1:]]))
    by_id = {r["node_id"]: r for r in records}
    for edge in edges:
        by_id[edge["child_id"]]["sibling_ids"] = edge["sibling_ids"]
    edges.sort(key=lambda e: (by_id[e["parent_id"]]["path"], e["position"]))

    # A shape match does not license a grammatical function or source citation.
    observed_shapes = []
    for entry in records:
        daughters = [by_id[x]["label"] for x in entry["child_ids"]]
        if entry["label"] == "S" and daughters == ["NP", "VP"]:
            observed_shapes.append({
                "parent_id": entry["node_id"],
                "shape": "S > NP VP",
                "candidate_concept_ids": ["BR3-S-DAUGHTERS", "BR3-SUBJECT-IMMEDIATE-S",
                                          "BR3-PREDICATE-IMMEDIATE-S"],
                "status": "observed_shape_only_pending_independent_approval",
                "licensed_functions": [],
            })
        if entry["label"] == "VP" and any(by_id[x]["label"] in AUXILIARIES
                                         for x in entry["child_ids"]):
            observed_shapes.append({
                "parent_id": entry["node_id"],
                "shape": "VP with overt auxiliary-category daughter",
                "candidate_concept_ids": ["BR3-NESTED-AUX-VPS"],
                "status": "observed_shape_only_pending_independent_approval",
                "licensed_functions": [],
            })

    token_index = []
    for token in tokens:
        i = token["index"]
        covering = [r for r in records if r["token_span"] is not None
                    and r["token_span"][0] <= i < r["token_span"][1]]
        covering.sort(key=lambda r: (-len(r["ancestor_ids"]), r["path"]))
        smallest = covering[0] if covering else None
        # A triangle represents opaque words; never fabricate word/lexical nodes.
        token_index.append({
            "token_id": i, "text": token["text"], "char_span": list(token["char_span"]),
            "smallest_node_id": smallest["node_id"] if smallest else None,
            "lexical_ancestor_id": next((r["node_id"] for r in covering if r["label"] in LEXICAL
                                         and r["kind"] != "triangle"), None),
            "phrase_ancestor_id": next((r["node_id"] for r in covering if r["label"] in PHRASES), None),
            "clause_ancestor_id": next((r["node_id"] for r in covering if r["label"] in CLAUSES), None),
            "node_ids_innermost_first": [r["node_id"] for r in covering],
            "opaque": bool(smallest and smallest["kind"] == "triangle"),
        })

    return {"nodes": records, "edges": edges, "atoms": atoms, "token_index": token_index,
            "observed_shapes": observed_shapes}


def build_fact_graph(analysis: dict[str, Any], node_id: str | None = None) -> dict[str, Any]:
    """Return a sidecar fact graph; validate input, and never mutate the tree."""
    if not isinstance(analysis, dict):
        raise ValueError("analysis must be an object")
    if node_id is not None and (not isinstance(node_id, str) or len(node_id) > 200):
        raise ValueError("node_id must be a string of at most 200 characters")
    tree = analysis.get("tree")
    result = {
        "schema_version": VERSION,
        "language_policy": "ENGLISH_ONLY",
        "status": "unavailable",
        "analysis_id": None,
        "tree_id": None,
        "profile": None,
        "sentence": None,
        "nodes": [], "edges": [], "atoms": [], "token_index": [],
        "movement_links": [], "alternatives": [], "observed_shapes": [],
        "target": None,
        "limitations": [
            "Tree observations are not grammaticality judgments.",
            "Head, function, complement, adjunct and valency claims require independently approved licenses.",
        ],
    }
    if not isinstance(tree, dict) or analysis.get("status") not in {
        "normalized", "provisional", "working",
    }:
        return result
    # Late import keeps the original explanation and validation contracts intact.
    from explanations import validate_envelope
    validate_envelope(tree)
    provisional = (analysis.get("status") != "normalized"
                   or tree["source"].get("evidence_status") == "UNCERTAIN")
    sentence = tree.get("sentence") or ""
    tokens = tree["tokens"]
    graph = _subgraph(tree["root"], tokens, sentence, provisional)
    ids = {node["node_id"] for node in graph["nodes"]}
    if node_id is not None and node_id not in ids:
        raise ValueError("node_id is not present in the canonical tree")
    result.update(graph)
    result.update({
        "status": "provisional" if provisional else "observed",
        "analysis_id": hashlib.sha256(
            json.dumps({key: tree.get(key) for key in ("tree_id", "sentence",
                         "tokens", "convention_profile", "root", "movement",
                         "accepted_alternatives")}, sort_keys=True, ensure_ascii=False,
                       separators=(",", ":")).encode("utf-8")).hexdigest()[:24],
        "tree_id": tree["tree_id"],
        "profile": dict(tree["convention_profile"]),
        "sentence": sentence,
        "target": next((r for r in graph["nodes"] if r["node_id"] == node_id), None),
    })
    for i, item in enumerate(tree.get("movement", [])):
        # Only explicit links on validated nodes are reportable as relationships.
        links = {key: item[key] for key in ("from_node_id", "to_node_id", "gap_node_id")
                 if item.get(key) in ids}
        if not links:
            continue
        result["movement_links"].append({
            "link_id": f"m{i:04d}",
            "kind": item["kind"], "nodes": links,
            "index": item.get("index"),
            "status": "provisional_explicit_annotation" if provisional
                      else "explicit_tree_annotation",
            "source_rule_ids": [],
        })
    for alt in tree.get("accepted_alternatives", []):
        # Alternatives are disjoint analyses, not more children of the primary tree.
        sub = _subgraph(alt["root"], tokens, sentence, True)
        result["alternatives"].append({
            "analysis_id": alt["analysis_id"],
            "acceptance": alt["acceptance"],
            "status": "conditional_alternative_not_merged",
            "nodes": sub["nodes"],
            "edges": sub["edges"],
            "observed_shapes": sub["observed_shapes"],
        })
    return result
