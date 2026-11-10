"""XAI-3: offline contextual prose strictly limited to observed tree facts.

No external model is called. Original, deterministic observational wording is
deliberately NOT presented as a book-backed claim. Source-backed B-R/Cambridge
teaching stays in the separately reviewed three-channel registry, until
independent human approval makes new function/selection claims eligible.
"""
from __future__ import annotations

from typing import Any

from xai_planner import plan_nodes

VERSION = "xai-composer-3.0.0"
POSITION_WORDS = ("first", "second", "third")


def _mention(node: dict[str, Any] | None) -> str:
    if node is None:
        return "the root"
    label = node["label"]
    kind = node["kind"]
    if kind == "word":
        return f'word “{node["surface"]}”'
    if kind == "elided_terminal":
        return "an elided word position"
    if kind == "gap":
        return "a marked gap"
    if kind == "empty":
        return f'an unspoken {label} position'
    if kind == "triangle" and not label:
        return f'unlabelled triangle “{node["surface"]}”'
    base = label or "unlabelled node"
    return f'{base} “{node["surface"]}”' if node["surface"] else base


def _ordinal(i: int | None) -> str:
    if i is None:
        return "unpositioned"
    return POSITION_WORDS[i] if i < len(POSITION_WORDS) else f"child {i + 1}"


def _join(items: list[str]) -> str:
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    return ", ".join(items[:-1]) + " and " + items[-1]


def _brief(plan: dict[str, Any]) -> str:
    node, parent = plan["node"], plan["parent"]
    kind = node["kind"]
    named = _mention(node)
    where = f'within {_mention(parent)}' if parent else "at the root of this tree"
    if kind == "word":
        return f'The overt {named} is drawn {where}.'
    if kind == "gap":
        return f'A marked gap is drawn {where}; no spoken word is assigned to this position.'
    if kind == "empty":
        return f'The tree shows {named} {where}; it contains no overt word.'
    if kind == "elided_terminal":
        return f'An elided word position is recorded {where}, with no overt token.'
    if kind == "triangle":
        if parent is not None:
            return (f'The tree shows {named} as the {_ordinal(node["position"])} immediate child '
                    f'of {_mention(parent)}; it is one opaque span with no internal daughter nodes.')
        return (f'The tree shows {named} at the root as one opaque span '
                'with no internal daughter nodes.')
    daughters = [_mention(n) for n in plan["children"]]
    if parent is None:
        return (f'At the root, {_mention(node)} directly contains '
                f'{_join(daughters)}.')
    if daughters:
        return (f'{named} is the {_ordinal(node["position"])} immediate child of '
                f'{_mention(parent)} and directly contains {_join(daughters)}.')
    return f'The tree places {named} {_ordinal(node["position"])} under {_mention(parent)}.'


def _expanded(plan: dict[str, Any], graph: dict[str, Any]) -> str:
    node, parent, children, siblings = (
        plan["node"], plan["parent"], plan["children"], plan["siblings"])
    parts = []
    span = node["token_span"]
    if span is not None:
        if span[0] == span[1]:
            parts.append(f'This is a zero-width token position at index {span[0]}.')
        else:
            parts.append(f'The recorded token interval is [{span[0]}, {span[1]}) '
                         f'and its exact source text is “{node["surface"]}”.')
    elif node["kind"] in {"gap", "elided_terminal"}:
        parts.append("The source marks this position without an overt token span.")
    if parent:
        parts.append(f'Its immediate parent is {_mention(parent)}.')
        if siblings:
            parts.append(f'At the same tree level it appears beside {_join([_mention(s) for s in siblings])}.')
    if children:
        parts.append("The immediate daughters, in source order, are "
                     + _join([_mention(child) for child in children]) + ".")
    if node["features"]:
        parts.append("The tree records the literal feature label(s) "
                     + ", ".join(f'[{f}]' for f in node["features"]) + ".")
    if node["index"] is not None:
        parts.append(f'The source marks index {node["index"]} here; '
                     'that index alone does not establish an antecedent.')
    if node["kind"] == "triangle":
        parts.append("The triangle is deliberately underanalysed: there are no verified internal category nodes.")
    if node["kind"] in {"gap", "empty", "elided_terminal"}:
        parts.append("The missing surface is a notation in this tree, not a detected grammar error.")
    if graph["alternatives"]:
        parts.append(f'{len(graph["alternatives"])} separately recorded alternative '
                     'analysis/analyses are not merged into these observations.')
    if graph["movement_links"]:
        relevant = [m for m in graph["movement_links"]
                    if node["node_id"] in m["nodes"].values()]
        if relevant:
            parts.append("The tree explicitly annotates a "
                         + _join([m["kind"] for m in relevant])
                         + " relation involving this node; this observation does not resolve interpretation.")
    parts.append("Category labels describe positions in this tree; they do not by themselves establish "
                 "subject, object, head, complement or adjunct function, or sentence grammaticality.")
    if graph["status"] == "provisional":
        parts.append("This working analysis remains provisional.")
    return " ".join(parts)


def compose_explanations(graph: dict[str, Any], node_id: str | None = None) -> dict[str, Any]:
    """Compose only from verified XAI-2 facts; no model, rules, or new citations."""
    if not isinstance(graph, dict):
        raise ValueError("fact graph is required")
    plans = plan_nodes(graph, node_id=node_id)
    items = []
    for plan in plans:
        node = plan["node"]
        text = _brief(plan)
        deep_text = _expanded(plan, graph)
        if not text or not plan["fact_ids"]:
            raise ValueError("cannot explain a node without witnessed evidence")
        items.append({
            "node_id": node["node_id"],
            "target_kind": node["kind"],
            "label": node["label"],
            "token_span": node["token_span"],
            "char_span": node["char_span"],
            "short": text,
            "deep": deep_text,
            "evidence_atom_ids": plan["fact_ids"],
            "proof": plan["proof"],
            "source_ids": [],
            "evidence_status": "provisional_tree_observation" if graph["status"] == "provisional"
                               else "validated_tree_observation",
            "claim_status": "STRUCTURAL_OBSERVATION_ONLY",
            "uncertainty": "provisional" if graph["status"] == "provisional" else "none",
            "function_status": "unknown_unlicensed",
        })
    return {
        "schema_version": VERSION,
        "language_policy": "ENGLISH_ONLY",
        "status": "provisional" if graph["status"] == "provisional"
                  else "observed" if graph["status"] == "observed"
                  else "unavailable",
        "analysis_id": graph.get("analysis_id"),
        "selected_node_id": node_id,
        "items": items,
        "scope": "tree_observations_not_source_approved_grammar_or_correction",
    }
