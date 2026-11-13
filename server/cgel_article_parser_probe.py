"""Offline article-form evidence for a restricted set of known onsets."""

if __package__:
    from .cgel_ch03_candidate_probe import tokens_with_spans
    from .matrix import A_SOUND_CONST_WORDS, AN_SILENT_H_WORDS, _indefinite_article
    from .parse_engine import _ordered_leaves
else:
    from cgel_ch03_candidate_probe import tokens_with_spans
    from matrix import A_SOUND_CONST_WORDS, AN_SILENT_H_WORDS, _indefinite_article
    from parse_engine import _ordered_leaves

# Limit this prototype to established onsets. Herb and homage vary by pronunciation.
KNOWN_ONSETS = (
    A_SOUND_CONST_WORDS | (AN_SILENT_H_WORDS - {"herb", "homage"})
    | {"apple", "apples", "engine", "error", "interim", "ordinary", "unusual",
       "old", "owl", "small", "red", "report", "short", "supposedly", "book"}
)


def _article_contexts(node):
    if node["type"] == "NP":
        leaves = list(_ordered_leaves(node))
        if len(leaves) >= 2 and leaves[0].get("pos") == "DT":
            yield leaves
    for child in node.get("children", []):
        yield from _article_contexts(child)


def probe_article_parser(sentence, tree, *, variety):
    result = {"status": "candidate_only", "production_enabled": False, "candidates": [], "blocked": []}
    if variety != "standard_english":
        return {**result, "status": "not_evaluated", "blocked": ["explicit_standard_english_required"]}
    tokens = tokens_with_spans(sentence)
    leaves = list(_ordered_leaves(tree))
    if len(tokens) != len(leaves) or any(
        leaf["span"] != [token["index"], token["index"] + 1]
        or {"-LRB-": "(", "-RRB-": ")"}.get(leaf["surface"], leaf["surface"]) != token["text"]
        for leaf, token in zip(leaves, tokens)
    ):
        return {**result, "status": "not_evaluated", "blocked": ["parser_token_alignment_unavailable"]}
    if any(token["text"] in {'"', '“', '”', "'", "‘", "’"} for token in tokens):
        return {**result, "status": "not_evaluated", "blocked": ["quotation_scope_unresolved"]}
    seen = set()
    for phrase in _article_contexts(tree):
        article = phrase[0]["span"][0]
        text = tokens[article]["text"]
        if article in seen or text.lower() not in {"a", "an"}:
            continue
        indices = [leaf["span"][0] for leaf in phrase]
        words = [tokens[index]["text"] for index in indices]
        parenthesised = words[1] == "("
        offset = 2 if parenthesised else 1
        if parenthesised and (len(words) < 5 or words[3] != ")"):
            continue
        onset = words[offset].lower()
        if onset not in KNOWN_ONSETS or (words[offset].isupper() and len(words[offset]) > 1):
            continue
        seen.add(article)
        required = _indefinite_article(onset)
        if required == text.lower():
            continue
        result["candidates"].append({
            "rule_id": "MORPH-141",
            "condition": "parenthesised_modifier_read_aloud" if parenthesised else "known_onset",
            "source_chapter": 18, "source_pages": [1618],
            "supporting_sources": [{"rule_id": "OTH-726", "chapter": 20, "pages": [1748]}] if parenthesised else [],
            "relation": {
                "kind": "article_precedes_onset",
                "governor_char_span": tokens[article]["char_span"],
                "dependent_char_span": tokens[indices[offset]]["char_span"],
            },
            "edit_hint": {
                "char_span": tokens[article]["char_span"],
                "replacement": required.capitalize() if text[0].isupper() else required,
                "requires_reparse": True, "safe_to_apply_automatically": False,
            },
        })
    return result
