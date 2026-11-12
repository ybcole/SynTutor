"""Align passive causative candidate evidence to the canonical fact graph."""

if __package__:
    from .xai_facts import build_fact_graph
else:
    from xai_facts import build_fact_graph


def observe_clause_link(nodes, auxiliary, governor, dependent):
    """Observe a sister clause and co-indexed gaps in the normalized tree."""
    predicate = nodes.get(governor["parent_id"])
    if (not predicate or predicate["label"] != "VP" or auxiliary["label"] != "PASS"
            or auxiliary["parent_id"] not in predicate["ancestor_ids"]):
        return None
    children = [nodes[node_id] for node_id in predicate["child_ids"]]
    clause = next((node for node in children if node["label"] == "S-bar"
                   and node["node_id"] in dependent["ancestor_ids"]), None)
    if clause is None:
        return None
    lower_s = next((nodes[node_id] for node_id in clause["child_ids"]
                    if nodes[node_id]["label"] == "S"), None)
    if lower_s is None or not lower_s["child_ids"]:
        return None
    lower_subject = nodes[lower_s["child_ids"][0]]
    if lower_subject["label"] != "NP":
        return None
    object_gaps = [nodes[node_id] for node in children if node["label"] == "NP"
                   for node_id in node["child_ids"] if nodes[node_id]["kind"] == "gap"]
    subject_gaps = [nodes[node_id] for node_id in lower_subject["child_ids"]
                    if nodes[node_id]["kind"] == "gap"]
    upper_clause = next((nodes[node_id] for node_id in governor["ancestor_ids"]
                         if nodes[node_id]["label"] == "S"), None)
    if upper_clause is None or not upper_clause["child_ids"]:
        return None
    promoted = nodes[upper_clause["child_ids"][0]]
    if promoted["label"] != "NP" or promoted["index"] is None:
        return None
    for obj in object_gaps:
        for subj in subject_gaps:
            if obj["index"] == subj["index"] == promoted["index"]:
                return {"passive_node_id": auxiliary["node_id"], "predicate_node_id": predicate["node_id"],
                        "clause_node_id": clause["node_id"],
                        "object_gap_node_id": obj["node_id"], "subject_gap_node_id": subj["node_id"],
                        "shared_index": obj["index"]}
    return None


def ground_passive_make_candidates(analysis, candidates):
    if (analysis.get("status") != "normalized" or not candidates
            or analysis["tree"].get("accepted_alternatives")):
        return []
    graph = build_fact_graph(analysis)
    if graph["status"] != "observed":
        return []
    nodes_by_id = {node["node_id"]: node for node in graph["nodes"]}
    tokens_by_span = {tuple(token["char_span"]): token for token in graph["token_index"]}
    evidence_rows = []
    for candidate in candidates:
        relation = candidate["relation"]
        evidence = {}
        spans = {
            "auxiliary": tuple(relation["passive_auxiliary_char_span"]),
            "governor": tuple(relation["governor_char_span"]),
            "dependent": tuple(relation["dependent_char_span"]),
        }
        for role, span in spans.items():
            token = tokens_by_span.get(span)
            if token and not token["opaque"]:
                if role == "auxiliary":
                    lexical = next((nodes_by_id[node_id] for node_id in token["node_ids_innermost_first"]
                                    if nodes_by_id[node_id]["label"] == "PASS"), None)
                else:
                    lexical = nodes_by_id.get(token["lexical_ancestor_id"])
                if lexical:
                    evidence[role] = {"node_id": lexical["node_id"], "label": lexical["label"]}
        if spans.keys() <= evidence.keys():
            link = observe_clause_link(nodes_by_id, nodes_by_id[evidence["auxiliary"]["node_id"]],
                                       nodes_by_id[evidence["governor"]["node_id"]],
                                       nodes_by_id[evidence["dependent"]["node_id"]])
            if link:
                evidence["observed_clause_link"] = link
        evidence_rows.append(evidence)
    return evidence_rows
