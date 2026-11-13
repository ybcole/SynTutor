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


MUTE_E_BASES = {"hope", "bake", "make", "take", "write", "move", "save", "close"}


def _mute_e_replacement(word, tag):
    if tag != "VBG" or not word.endswith("eing"):
        return None
    base = word[:-3]
    if base not in MUTE_E_BASES or getAllLemmas(word):
        return None
    expected = base[:-1] + "ing"
    if expected in getInflection(base, tag=tag, inflect_oov=False):
        return expected
    return None


def probe_consonant_doubling(sentence, tree, *, variety):
    return _probe_spelling(sentence, tree, variety, _doubling_replacement,
                           "MORPH-078", [1575, 1576], "omitted_final_consonant_doubling")


def probe_mute_e(sentence, tree, *, variety):
    return _probe_spelling(sentence, tree, variety, _mute_e_replacement,
                           "MORPH-080", [1576, 1577], "retained_mute_e_before_ing")


def _final_ie_replacement(word, tag):
    if tag != "VBG" or word not in {"dieing", "lieing", "tieing", "vieing"}:
        return None
    return word[:-5] + "ying"


def probe_final_ie(sentence, tree, *, variety):
    return _probe_spelling(sentence, tree, variety, _final_ie_replacement,
                           "MORPH-083", [1579], "retained_ie_before_ing")


Y_PLURAL_BASES = {"baby", "city", "country", "lady", "party", "story",
                  "boy", "day", "donkey", "key", "toy", "tray"}


def _final_y_plural_replacement(word, tag):
    if tag not in {"NN", "NNS"} or getAllLemmas(word):
        return None
    if word.endswith("ys"):
        base = word[:-1]
        expected = base[:-1] + "ies"
    elif word.endswith("ies"):
        base = word[:-3] + "y"
        expected = base + "s"
    else:
        return None
    if base in Y_PLURAL_BASES and expected in getInflection(base, tag="NNS", inflect_oov=False):
        return expected
    return None


def probe_final_y_plural(sentence, tree, *, variety):
    return _probe_spelling(sentence, tree, variety, _final_y_plural_replacement,
                           "MORPH-092", [1585], "incorrect_final_y_plural")


def _probe_spelling(sentence, tree, variety, replacement_for, rule_id, pages, relation_kind):
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
        replacement = replacement_for(token["lower"], leaf.get("pos"))
        if replacement:
            result["candidates"].append({
                "rule_id": rule_id, "source_chapter": 18, "source_pages": pages,
                "relation": {"kind": relation_kind,
                             "word_char_span": token["char_span"]},
                "edit_hint": {"char_span": token["char_span"], "replacement": replacement,
                              "requires_reparse": True, "safe_to_apply_automatically": False},
            })
    return result
