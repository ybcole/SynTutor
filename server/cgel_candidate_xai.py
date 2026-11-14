"""Map candidate Phase-C findings onto a syntax tree and compose local XAI prose.

Two tree authorities are supported:

* ``canonical_fact_graph`` — the observed B-R/XAI-2 graph used by the node
  inspector when canonicalization succeeds.
* ``benepar_candidate_parse`` — the parser tree used by the candidate probes
  when canonicalization is unavailable.

The mapping is evidence for a local candidate observation. It does not license
grammatical functions, verify an error, enable a registry rule, or certify the
whole sentence.
"""
from __future__ import annotations

from typing import Any

if __package__:
    from .parse_engine import _ordered_leaves, analyze
    from .xai_facts import build_fact_graph
else:
    from parse_engine import _ordered_leaves, analyze
    from xai_facts import build_fact_graph


SCHEMA_VERSION = "cgel-candidate-xai-1.0.0"
CLAUSE_LABELS = {"S", "SQ", "SBAR", "SBARQ", "S'", "S''", "S-bar", "S-dbar"}
PHRASE_LABELS = {"NP", "NOM", "VP", "PP", "AP", "ADJP", "ADVP", "AdvP", "QP"}
LEAF_SURFACES = {"-LRB-": "(", "-RRB-": ")", "-LSB-": "[", "-RSB-": "]",
                 "-LCB-": "{", "-RCB-": "}"}
CAVEAT = ("Candidate-only local observation. The check is not an approved "
          "grammar verdict and does not certify the rest of the sentence.")

NODE_NAMES = {
    "S": "clause", "SQ": "question clause", "SBAR": "subordinate clause",
    "SBARQ": "question clause", "S'": "clause", "S''": "clause",
    "S-bar": "clause", "S-dbar": "clause", "NP": "noun phrase",
    "NOM": "noun group", "VP": "verb phrase", "PP": "preposition phrase",
    "AP": "adjective phrase", "ADJP": "adjective phrase",
    "ADVP": "adverb phrase", "AdvP": "adverb phrase", "QP": "quantity phrase",
    "N": "noun", "NN": "noun", "NNS": "noun", "NNP": "name",
    "NNPS": "name", "V": "verb", "VB": "verb", "VBD": "verb", "VBP": "verb",
    "VBZ": "verb", "VBG": "verb", "VBN": "verb", "MD": "modal auxiliary",
    "A": "adjective", "JJ": "adjective", "JJR": "adjective", "JJS": "adjective",
    "Adv": "adverb", "RB": "adverb", "RBR": "adverb", "RBS": "adverb",
    "P": "preposition", "IN": "preposition", "TO": "infinitive marker",
    "ART": "article", "DET": "determiner", "DT": "determiner",
    "PRP": "pronoun", "PRON": "pronoun", "PRO": "pronoun",
    "CC": "conjunction", "C": "clause introducer", "C2": "clause introducer",
    ".": "punctuation", ",": "punctuation", ":": "punctuation",
    ";": "punctuation", "``": "quotation mark", "''": "quotation mark",
}


def _result(status: str = "unavailable") -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "production_enabled": False,
        "whole_sentence_certified": False,
        "tree_authority": None,
        "items": [],
        "focus_node_ids": [],
        "unmapped_finding_ids": [],
        "blocked": [],
        "caveat": CAVEAT,
    }


def _align(sentence: str, tree: dict[str, Any]):
    leaves = list(_ordered_leaves(tree))
    spans: list[list[int]] = []
    cursor = 0
    for leaf in leaves:
        while cursor < len(sentence) and sentence[cursor].isspace():
            cursor += 1
        expected = LEAF_SURFACES.get(leaf.get("surface", ""), leaf.get("surface", ""))
        if expected in {"``", "''"}:
            if cursor >= len(sentence) or sentence[cursor] not in '"“”‘’':
                return None
            expected = sentence[cursor]
        if not expected:
            return None
        if sentence.startswith(expected, cursor):
            spans.append([cursor, cursor + len(expected)])
            cursor += len(expected)
            continue
        if expected in {"'", "’"} and cursor < len(sentence) and sentence[cursor] in {"'", "’"}:
            spans.append([cursor, cursor + 1])
            cursor += 1
            continue
        return None
    if sentence[cursor:].strip():
        return None
    return leaves, spans


def build_benepar_index(tree: dict[str, Any], sentence: str) -> dict[str, Any]:
    aligned = _align(sentence, tree)
    if aligned is None:
        return {**_result("unavailable"), "blocked": ["parser_token_alignment_unavailable"]}
    leaves, spans = aligned
    leaf_at = {id(leaf): index for index, leaf in enumerate(leaves)}
    nodes: list[dict[str, Any]] = []
    by_id: dict[str, dict[str, Any]] = {}

    def walk(node: dict[str, Any], path: str, parent_id: str | None,
             ancestors: list[str]) -> dict[str, Any]:
        children = node.get("children", [])
        child_records = [walk(child, f"{path}.{i}", path, [path] + ancestors)
                         for i, child in enumerate(children)]
        if not children and id(node) in leaf_at:
            leaf_index = leaf_at[id(node)]
            char_span = spans[leaf_index]
            token_span = list(node.get("span") or [leaf_index, leaf_index + 1])
            label = node.get("pos") or node.get("type")
            kind = "word"
        else:
            char_span = ([min(record["char_span"][0] for record in child_records),
                          max(record["char_span"][1] for record in child_records)]
                         if child_records else [0, 0])
            token_span = list(node.get("span") or ([0, 0] if not child_records else
                                                   [min(record["token_span"][0] for record in child_records),
                                                    max(record["token_span"][1] for record in child_records)]))
            label = node.get("type")
            kind = "branch"
        record = {
            "node_id": path,
            "label": label,
            "kind": kind,
            "surface": sentence[char_span[0]:char_span[1]],
            "char_span": char_span,
            "token_span": token_span,
            "parent_id": parent_id,
            "child_ids": [record["node_id"] for record in child_records],
            "ancestor_ids": ancestors,
            "position": len(nodes),
        }
        nodes.append(record)
        by_id[record["node_id"]] = record
        return record

    root = walk(tree, "root", None, [])
    for record in nodes:
        record["depth"] = len(record["ancestor_ids"])
    token_index = []
    for token_id in range(len(leaves)):
        covering = [record for record in nodes
                    if record["token_span"] is not None
                    and record["token_span"][0] <= token_id < record["token_span"][1]]
        covering.sort(key=lambda record: (-record["depth"], record["node_id"]))
        token = leaves[token_id]
        token_index.append({
            "token_id": token_id,
            "text": token.get("surface", ""),
            "char_span": list(spans[token_id]),
            "smallest_node_id": covering[0]["node_id"] if covering else root["node_id"],
            "phrase_ancestor_id": next((record["node_id"] for record in covering
                                        if record.get("label") in PHRASE_LABELS), None),
            "clause_ancestor_id": next((record["node_id"] for record in covering
                                        if record.get("label") in CLAUSE_LABELS), None),
            "node_ids_innermost_first": [record["node_id"] for record in covering],
            "opaque": False,
        })
    return {
        **_result("observed"),
        "tree_authority": "benepar_candidate_parse",
        "sentence": sentence,
        "nodes": nodes,
        "token_index": token_index,
        "by_id": by_id,
    }


def _iter_spans(value: Any, *, key: str = "") -> list[list[int]]:
    found: list[list[int]] = []
    if key.endswith("char_span") and isinstance(value, (list, tuple)) and len(value) == 2:
        if all(isinstance(item, int) for item in value):
            found.append([value[0], value[1]])
        return found
    if isinstance(value, dict):
        for child_key, child_value in value.items():
            found.extend(_iter_spans(child_value, key=str(child_key)))
    elif isinstance(value, (list, tuple)):
        for item in value:
            found.extend(_iter_spans(item, key=key))
    return found


def _finding_spans(finding: dict[str, Any]) -> list[list[int]]:
    spans: list[list[int]] = []
    hint = finding.get("edit_hint")
    if isinstance(hint, dict):
        spans.extend(_iter_spans(hint))
    spans.extend(_iter_spans(finding.get("relation") or {}))
    unique = []
    for span in spans:
        if span not in unique:
            unique.append(span)
    return unique


def _tokens_for_span(index: dict[str, Any], span: list[int]) -> list[int]:
    start, end = span
    tokens = index.get("token_index", [])
    if start == end:
        containing = [token for token in tokens
                      if token["char_span"][0] <= start <= token["char_span"][1]]
        if containing:
            return [containing[0]["token_id"]]
        next_token = next((token for token in tokens
                           if token["char_span"][0] >= start), None)
        if next_token is not None:
            return [next_token["token_id"]]
        return [tokens[-1]["token_id"]] if tokens else []
    return [token["token_id"] for token in tokens
            if token["char_span"][0] < end and token["char_span"][1] > start]


def _covering_node(index: dict[str, Any], span: list[int],
                   token_ids: list[int]) -> dict[str, Any] | None:
    nodes = index.get("by_id") or {node["node_id"]: node for node in index.get("nodes", [])}
    candidates = []
    for node in nodes.values():
        if node.get("kind") in {"gap", "empty", "elided_terminal"}:
            continue
        char_span = node.get("char_span")
        token_span = node.get("token_span")
        if not char_span or not token_span:
            continue
        covers_chars = (char_span[0] <= span[0] and span[1] <= char_span[1])
        covers_tokens = all(token_span[0] <= token_id < token_span[1]
                            for token_id in token_ids) if token_ids else False
        if covers_chars or covers_tokens:
            candidates.append(node)
    if not candidates:
        return None
    candidates.sort(key=lambda node: (
        0 if node.get("kind") == "word" else 1,
        node["char_span"][1] - node["char_span"][0],
        -len(node.get("ancestor_ids", [])),
        node["node_id"],
    ))
    return candidates[0]


def _boundary_nodes(index: dict[str, Any], span: list[int]) -> list[str]:
    start, end = span
    tokens = index.get("token_index", [])
    left = next((token for token in reversed(tokens)
                 if token["char_span"][1] <= start), None)
    right = next((token for token in tokens
                  if token["char_span"][0] >= end), None)
    return [token["smallest_node_id"] for token in (left, right) if token]


def _is_clause_node(node: dict[str, Any] | None) -> bool:
    return bool(node) and node.get("label") in CLAUSE_LABELS


def _empty_binding(index: dict[str, Any], reason: str) -> dict[str, Any]:
    return {
        "status": "unmapped",
        "reason": reason,
        "tree_authority": index.get("tree_authority"),
        "spans": [],
        "mapped": [],
        "node_ids": [],
        "affected_node_id": None,
        "governor_node_id": None,
        "clause_node_id": None,
        "phrase_node_id": None,
        "ancestor_node_ids": [],
    }


def _mark_spans(finding: dict[str, Any]) -> list[list[int]]:
    marks = []
    hint = finding.get("edit_hint")
    if isinstance(hint, dict):
        for span in _iter_spans(hint):
            if span not in marks:
                marks.append(span)
    relation = finding.get("relation") or {}
    for span in _iter_spans(relation.get("mark_char_span")):
        if span not in marks:
            marks.append(span)
    return marks


def bind_finding(index: dict[str, Any], finding: dict[str, Any]) -> dict[str, Any]:
    spans = _finding_spans(finding)
    if not spans:
        return _empty_binding(index, "finding_has_no_char_span")
    marks = _mark_spans(finding)
    nodes = index.get("by_id") or {node["node_id"]: node for node in index.get("nodes", [])}
    mapped = []
    for span in spans:
        token_ids = _tokens_for_span(index, span)
        node = _covering_node(index, span, token_ids)
        boundary = []
        if node is not None and not token_ids and _is_clause_node(node):
            if node["char_span"][1] - node["char_span"][0] > max(1, 2 * (span[1] - span[0])):
                boundary = _boundary_nodes(index, span)
        if boundary:
            node_info = None
        elif node is None:
            node_info = None
        else:
            node_info = {
                "node_id": node["node_id"],
                "label": node.get("label"),
                "kind": node.get("kind"),
                "surface": node.get("surface"),
                "char_span": node.get("char_span"),
                "token_span": node.get("token_span"),
                "parent_id": node.get("parent_id"),
                "ancestor_ids": list(node.get("ancestor_ids", [])),
            }
        mapped.append({
            "span": span,
            "token_ids": token_ids,
            "mark": span in marks,
            "boundary_node_ids": boundary,
            "node": node_info,
        })
    found = []
    for row in mapped:
        node = row["node"]
        if node and node["node_id"] not in {item["node_id"] for item in found}:
            found.append(node)
    if not found and not any(row["boundary_node_ids"] for row in mapped):
        binding = _empty_binding(index, "no_tree_node_covers_span")
        binding["spans"] = spans
        binding["mapped"] = mapped
        return binding
    mark_nodes = [row["node"] for row in mapped
                  if row["mark"] and row["node"] and not _is_clause_node(row["node"])]
    mark_boundaries = [node_id for row in mapped if row["mark"]
                       for node_id in row["boundary_node_ids"]]
    relation_nodes = [row["node"] for row in mapped
                      if not row["mark"] and row["node"] and not _is_clause_node(row["node"])]
    relation_unique = []
    for node in relation_nodes:
        if node["node_id"] not in {item["node_id"] for item in relation_unique}:
            relation_unique.append(node)
    mark_unique = []
    for node in mark_nodes:
        if node["node_id"] not in {item["node_id"] for item in mark_unique}:
            mark_unique.append(node)
    mark_ids = {node["node_id"] for node in mark_unique}
    relation_unique = [node for node in relation_unique
                       if node["node_id"] not in mark_ids]
    boundary_nodes = [nodes[node_id] for node_id in mark_boundaries if node_id in nodes]
    affected = ((mark_unique[0] if mark_unique else None)
                or (relation_unique[0] if relation_unique else None)
                or (boundary_nodes[0] if boundary_nodes else None)
                or (found[0] if found else None))
    governor = (relation_unique[0] if relation_unique
                else nodes.get((affected or {}).get("parent_id") or ""))
    token_ids = [token_id for row in mapped for token_id in row["token_ids"]]
    if not token_ids:
        for node in boundary_nodes + ([affected] if affected else []):
            span = node.get("token_span")
            if span and span[0] < span[1]:
                token_ids.append(span[0])
                break
    first_token = token_ids[0] if token_ids else None
    token_row = (index.get("token_index", [])[first_token]
                 if first_token is not None and first_token < len(index.get("token_index", []))
                 else {})
    clause_id = token_row.get("clause_ancestor_id")
    phrase_id = token_row.get("phrase_ancestor_id")
    ancestors = list(dict.fromkeys(
        [ancestor for node in found + boundary_nodes
         for ancestor in node.get("ancestor_ids", [])]
        + ([clause_id] if clause_id else [])
    ))
    relation_status = ("mapped_relation"
                       if len(relation_unique) >= 2
                       or (bool(relation_unique) and bool(mark_unique or mark_boundaries))
                       else "mapped_span")
    all_node_ids = list(dict.fromkeys(
        [node["node_id"] for node in found]
        + [node["node_id"] for node in boundary_nodes]
    ))
    return {
        "status": relation_status,
        "reason": None,
        "tree_authority": index.get("tree_authority"),
        "spans": spans,
        "mapped": mapped,
        "node_ids": all_node_ids,
        "mark_node_ids": [node["node_id"] for node in mark_unique],
        "mark_boundary_node_ids": mark_boundaries,
        "relation_node_ids": [node["node_id"] for node in relation_unique],
        "affected_node_id": affected.get("node_id") if affected else None,
        "governor_node_id": governor.get("node_id") if governor else None,
        "clause_node_id": clause_id,
        "phrase_node_id": phrase_id,
        "ancestor_node_ids": ancestors,
    }

def _mention(index: dict[str, Any], node_id: str | None) -> str:
    if not node_id:
        return "this part of the sentence"
    nodes = index.get("by_id") or {node["node_id"]: node for node in index.get("nodes", [])}
    node = nodes.get(node_id)
    if not node:
        return "this part of the sentence"
    label = node.get("label")
    if node.get("kind") == "word" and label not in NODE_NAMES:
        label = next((nodes[ancestor].get("label")
                      for ancestor in node.get("ancestor_ids", [])
                      if ancestor in nodes and nodes[ancestor].get("label") in NODE_NAMES),
                     label)
    name = NODE_NAMES.get(label)
    surface = " ".join(str(node.get("surface") or "").split())
    if name:
        return f'the {name} “{surface}”' if surface else f"the {name}"
    return f'“{surface}”' if surface else "this part of the sentence"


def _citation(finding: dict[str, Any]) -> str:
    chapter = finding.get("source_chapter")
    pages = finding.get("source_pages") or []
    if chapter and pages:
        return f"CGEL Ch. {chapter}, p. {', '.join(str(page) for page in pages)}"
    if pages:
        return "CGEL p. " + ", ".join(str(page) for page in pages)
    return ""


def compose_candidate_explanation(index: dict[str, Any], finding: dict[str, Any],
                                  binding: dict[str, Any]) -> dict[str, Any]:
    nodes = index.get("by_id") or {node["node_id"]: node for node in index.get("nodes", [])}
    affected = nodes.get(binding.get("affected_node_id"))
    governor = nodes.get(binding.get("governor_node_id"))
    clause = nodes.get(binding.get("clause_node_id"))
    phrase = nodes.get(binding.get("phrase_node_id"))
    explanation = (finding.get("learner_explanation") or finding.get("statement")
                   or "No learner explanation is recorded for this candidate rule.")
    citation = _citation(finding)
    context = (f"inside {_mention(index, binding.get('clause_node_id'))}"
               if clause else f"inside {_mention(index, binding.get('phrase_node_id'))}"
               if phrase else "in this sentence")
    relation_ids = binding.get("relation_node_ids") or []
    mark_ids = binding.get("mark_node_ids") or []
    if len(relation_ids) >= 2:
        core = (f"In this sentence, the candidate check links "
                f"{_mention(index, relation_ids[0])} to "
                f"{_mention(index, relation_ids[1])} {context}.")
    elif relation_ids and mark_ids:
        core = (f"In this sentence, the candidate check targets "
                f"{_mention(index, mark_ids[0])} in relation to "
                f"{_mention(index, relation_ids[0])} {context}.")
    elif affected:
        core = (f"In this sentence, the candidate check targets "
                f"{_mention(index, binding.get('affected_node_id'))} {context}.")
    else:
        core = ("In this sentence, the candidate check has no mapped syntax-tree "
                "position for its finding.")
    edit_note = ""
    hint = finding.get("edit_hint")
    if isinstance(hint, dict):
        span = hint.get("char_span") or hint.get("span")
        replacement = hint.get("replacement")
        if isinstance(span, (list, tuple)) and len(span) == 2 and isinstance(replacement, str):
            original = index.get("sentence", "")
            if all(isinstance(value, int) for value in span) and 0 <= span[0] <= span[1] <= len(original):
                before = original[span[0]:span[1]]
                if before and replacement:
                    edit_note = (f" A candidate edit would replace “{before}” with "
                                 f"“{replacement}”; it has not been applied.")
                elif replacement:
                    edit_note = (f" A candidate edit would insert “{replacement}” "
                                 "at this position; it has not been applied.")
                elif before:
                    edit_note = (f" A candidate edit would delete “{before}”; "
                                 "it has not been applied.")
    short = f"{core} {explanation}{edit_note} Candidate observation only; not a verified error."
    deep_parts = [
        core,
        f"Source guidance: {explanation}",
        (f"Source: {citation}." if citation else ""),
        (f"Rule statement: {finding.get('statement')}" if finding.get("statement") else ""),
        (f"Mapped tree position: {binding.get('status')} "
         f"({binding.get('tree_authority')}); affected node {binding.get('affected_node_id') or 'none'}"
         + (f", related node {binding.get('governor_node_id')}" if binding.get('governor_node_id') else "")
         + "."),
        edit_note.strip(),
        CAVEAT,
    ]
    deep = " ".join(part for part in deep_parts if part)
    return {
        "short": short,
        "deep": deep,
        "citation": citation,
        "claim_status": "CANDIDATE_OBSERVATION_NOT_VERIFIED_ERROR",
        "binding_status": binding.get("status"),
        "tree_authority": binding.get("tree_authority"),
        "affected_node_id": binding.get("affected_node_id"),
        "governor_node_id": binding.get("governor_node_id"),
        "clause_node_id": binding.get("clause_node_id"),
        "node_ids": binding.get("node_ids", []),
        "production_enabled": False,
    }


def explain_candidate_findings(index: dict[str, Any], findings: list[dict[str, Any]], *,
                               node_id: str | None = None) -> dict[str, Any]:
    if index.get("status") not in {"observed"}:
        return {**_result("unavailable"),
                "blocked": index.get("blocked") or ["tree_index_unavailable"],
                "tree_authority": index.get("tree_authority")}
    items = []
    unmapped = []
    for finding in findings:
        binding = bind_finding(index, finding)
        explanation = compose_candidate_explanation(index, finding, binding)
        if node_id is not None:
            nodes = index.get("by_id") or {node["node_id"]: node
                                           for node in index.get("nodes", [])}
            selected = nodes.get(node_id) or {}
            selected_ancestors = set(selected.get("ancestor_ids") or [])
            related = set(binding.get("node_ids") or [])
            related_ancestors = set(binding.get("ancestor_node_ids") or [])
            if (node_id not in related
                    and node_id not in related_ancestors
                    and not (related & selected_ancestors)
                    and not (set(binding.get("mark_boundary_node_ids") or []) & selected_ancestors)):
                continue
        item = {
            "finding_id": finding.get("finding_id"),
            "rule_id": finding.get("rule_id"),
            "source_chapter": finding.get("source_chapter"),
            "source_pages": finding.get("source_pages") or [],
            "status": "candidate_observation",
            "production_enabled": False,
            "tree_binding": binding,
            "explanation": explanation,
        }
        items.append(item)
        if binding.get("status") == "unmapped":
            unmapped.append(finding.get("finding_id"))
    focus = []
    for item in items:
        for candidate in ([item["tree_binding"].get("affected_node_id"),
                           item["tree_binding"].get("governor_node_id"),
                           item["tree_binding"].get("clause_node_id")]
                          + list(item["tree_binding"].get("node_ids") or [])):
            if candidate and candidate not in focus:
                focus.append(candidate)
    return {
        **_result("candidate_only"),
        "tree_authority": index.get("tree_authority"),
        "sentence": index.get("sentence"),
        "items": items,
        "focus_node_ids": focus,
        "unmapped_finding_ids": unmapped,
        "blocked": list(index.get("blocked") or []),
    }


def candidate_xai_for_sentence(sentence: str, *, analysis: dict[str, Any] | None = None,
                               candidate_tree: dict[str, Any] | None = None,
                               node_id: str | None = None) -> dict[str, Any]:
    if not isinstance(sentence, str) or not sentence.strip():
        return {**_result("not_evaluated"), "blocked": ["empty_sentence"]}
    index = None
    if (isinstance(analysis, dict)
            and analysis.get("status") in {"normalized", "working", "provisional"}
            and isinstance(analysis.get("tree"), dict)):
        try:
            graph = build_fact_graph(analysis)
            if graph.get("status") == "observed":
                graph = {**graph, "tree_authority": "canonical_fact_graph",
                         "sentence": sentence,
                         "by_id": {node["node_id"]: node for node in graph.get("nodes", [])}}
                index = graph
        except Exception:
            index = None
    if candidate_tree is None:
        try:
            candidate_tree = analyze(sentence).get("root")
        except Exception as error:
            return {**_result("not_evaluated"),
                    "blocked": [f"parse_failed: {type(error).__name__}: {error}"]}
    if index is None:
        index = build_benepar_index(candidate_tree, sentence)
    if index.get("status") != "observed":
        return {**_result("unavailable"), "blocked": index.get("blocked") or [],
                "tree_authority": index.get("tree_authority")}
    try:
        if __package__:
            from .cgel_phase_d import collect_candidate_findings
        else:
            from cgel_phase_d import collect_candidate_findings
        found = collect_candidate_findings(sentence, candidate_tree,
                                           include_tree_binding=False)
    except Exception as error:
        return {**_result("unavailable"),
                "blocked": [f"candidate_collection_failed: {type(error).__name__}: {error}"],
                "tree_authority": index.get("tree_authority")}
    result = explain_candidate_findings(index, found.get("findings", []), node_id=node_id)
    result["blocked"] = list(dict.fromkeys(result.get("blocked", []) + found.get("blocked", [])))
    result["sentence"] = sentence
    return result
