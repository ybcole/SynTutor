"""Offline evidence for omitted doubling in a narrow set of verb forms."""

from lemminflect import getAllLemmas, getInflection

if __package__:
    from .cgel_ch03_candidate_probe import tokens_with_spans
    from .parse_engine import _ordered_leaves
else:
    from cgel_ch03_candidate_probe import tokens_with_spans
    from parse_engine import _ordered_leaves


BASES = {"fit", "hop", "plan", "stop", "drop", "rub", "tap", "equip", "admit", "regret"}
SUFFIXES = {"VBD": "ed", "VBN": "ed", "VBG": "ing"}


def _doubling_replacement(word, tag):
    suffix = SUFFIXES.get(tag)
    if suffix is None or not word.endswith(suffix):
        return None
    base = word[:-len(suffix)]
    if base not in BASES:
        return None
    # Keep legitimate words, including hoping and taping, as sense-dependent cases.
    if word == "stoping" or getAllLemmas(word):
        return None
    doubled = base + base[-1] + suffix
    forms = getInflection(base, tag=tag, inflect_oov=False)
    if (doubled in forms or (base == "fit" and suffix == "ed")) and word not in forms:
        return doubled
    return None


def probe_consonant_doubling(sentence, tree, *, variety):
    result = {"status": "not_evaluated", "production_enabled": False, "candidates": []}
    if variety != "standard_english":
        return result
    tokens = tokens_with_spans(sentence)
    leaves = list(_ordered_leaves(tree))
    if len(tokens) != len(leaves) or any(
        leaf["span"] != [token["index"], token["index"] + 1] or leaf["surface"] != token["text"]
        for leaf, token in zip(leaves, tokens)
    ) or any(token["text"] in {'"', '“', '”', "'", '‘', '’'} for token in tokens):
        return result
    result["status"] = "candidate_only"
    for leaf, token in zip(leaves, tokens):
        if not token["text"].islower():
            continue
        replacement = _doubling_replacement(token["lower"], leaf.get("pos"))
        if replacement:
            result["candidates"].append({
                "rule_id": "MORPH-078", "source_chapter": 18, "source_pages": [1575, 1576],
                "relation": {"kind": "omitted_final_consonant_doubling",
                             "word_char_span": token["char_span"]},
                "edit_hint": {"char_span": token["char_span"], "replacement": replacement,
                              "requires_reparse": True, "safe_to_apply_automatically": False},
            })
    return result
