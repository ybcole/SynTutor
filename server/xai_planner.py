"""XAI-3 planner: select only witnessed XAI-2 atoms for each tree node.

This is a structural planner, not a grammatical-function or lexical-role
resolver. Source-review flags supplied in the canonical envelope never license
teaching claims. All slots are selected from the server-created fact graph.
"""
from __future__ import annotations

from typing import Any


def plan_nodes(graph: dict[str, Any], node_id: str | None = None) -> list[dict[str, Any]]:
    if graph.get("schema_version") != "xai-facts-2.0.0":
        raise ValueError("XAI-3 requires a validated XAI-2 fact graph")
    nodes = graph.get("nodes", [])
    by_id = {n["node_id"]: n for n in nodes}
    if len(by_id) != len(nodes):
        raise ValueError("duplicate fact-graph node IDs")
    if node_id is not None and node_id not in by_id:
        raise ValueError("selected node is absent from fact graph")
    if graph.get("status") == "unavailable":
        return []
    if graph.get("status") not in {"observed", "provisional"}:
        raise ValueError("unknown fact-graph observation status")
    atom_map = {}
    ids = set()
    for atom in graph.get("atoms", []):
        ident = atom["fact_id"]
        if ident in ids or atom["subject_node_id"] not in by_id:
            raise ValueError("duplicate or unrelated fact atom")
        ids.add(ident)
        atom_map.setdefault(atom["subject_node_id"], []).append(atom)
    plans = []
    for node in nodes:
        ident = node["node_id"]
        if node_id is not None and ident != node_id:
            continue
        parent = by_id.get(node["parent_id"])
        children = [by_id[c] for c in node["child_ids"]]
        siblings = [by_id[s] for s in node["sibling_ids"]]
        # The recorded tree relation must be witnessed by an explicit atom.
        facts = list(atom_map.get(ident, []))
        predicates = {a["predicate"] for a in facts}
        required = {"node_kind"}
        if node["label"] is not None:
            required.add("category_label")
        if node["token_span"] is not None:
            required.add("span")
        if node["parent_id"] is not None:
            required.add("direct_child_of")
        if not required.issubset(predicates):
            raise ValueError("fact graph lacks a proof for a planned observation")
        child_evidence = []
        for child in children:
            matches = [a for a in atom_map.get(child["node_id"], [])
                       if a["predicate"] == "direct_child_of"
                       and a["object_node_id"] == ident]
            if len(matches) != 1:
                raise ValueError("direct daughter has no unique proof edge")
            child_evidence.extend(matches)
        facts.extend(child_evidence)
        selected_ids = list(dict.fromkeys(a["fact_id"] for a in facts))
        # No invented role/head/selection/valency facts can enter this plan.
        if node["function"] is not None or node["head_node_id"] is not None:
            raise ValueError("unlicensed role/head supplied to observation-only composer")
        plans.append({
            "node": node, "parent": parent, "children": children, "siblings": siblings,
            "fact_ids": selected_ids,
            "proof": [
                {"fact_id": a["fact_id"], "predicate": a["predicate"],
                 "node_id": a["subject_node_id"],
                 "object_node_id": a.get("object_node_id"),
                 "proof_path": a["proof_path"], "uncertainty": a["uncertainty"]}
                for a in facts if a["fact_id"] in selected_ids
            ],
        })
    return plans
