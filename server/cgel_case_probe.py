"""Offline case evidence for simple active declaratives."""

if __package__:
    from .cgel_ch03_candidate_probe import tokens_with_spans
    from .parse_engine import _ordered_leaves
else:
    from cgel_ch03_candidate_probe import tokens_with_spans
    from parse_engine import _ordered_leaves


SUBJECT_FORMS = {"me": "I", "him": "he", "her": "she", "us": "we", "them": "they"}
OBJECT_FORMS = {"i": "me", "he": "him", "she": "her", "we": "us", "they": "them"}
# Narrow lexical frames with a single direct object and no predicative complement.
TRANSITIVE_FORMS = {"admire", "admires", "admired", "greet", "greets", "greeted",
                    "thank", "thanks", "thanked", "notice", "notices", "noticed"}


def probe_pronoun_case(sentence, tree, *, variety):
    result = {"status": "not_evaluated", "production_enabled": False, "candidates": []}
    if variety != "standard_english":
        return result
    tokens = tokens_with_spans(sentence)
    leaves = list(_ordered_leaves(tree))
    if len(tokens) != len(leaves) or any(
        leaf["span"] != [token["index"], token["index"] + 1] or leaf["surface"] != token["text"]
        for leaf, token in zip(leaves, tokens)
    ):
        return result
    result["status"] = "candidate_only"
    parts = tree.get("children", [])
    if tree["type"] != "S" or [node["type"] for node in parts] != ["NP", "VP", "."]:
        return result
    if parts[-1].get("surface") != ".":
        return result
    predicate = parts[1].get("children", [])
    if len(predicate) != 2:
        return result
    verb, obj = predicate
    if (verb.get("pos") not in {"VBD", "VBP", "VBZ"} or obj["type"] != "NP"
            or verb["surface"].casefold() not in TRANSITIVE_FORMS):
        return result
    for node, role, forms in [(parts[0], "subject", SUBJECT_FORMS), (obj, "direct_object", OBJECT_FORMS)]:
        pronouns = list(_ordered_leaves(node))
        if len(pronouns) != 1 or pronouns[0].get("pos") != "PRP":
            continue
        pronoun = pronouns[0]
        expected = forms.get(pronoun["surface"].casefold())
        if expected is None:
            continue
        span = tokens[pronoun["span"][0]]["char_span"]
        result["candidates"].append({
            "rule_id": "COMP-084", "source_chapter": 4, "source_pages": [237],
            "supporting_sources": [{"rule_id": "PHR-283", "chapter": 5, "pages": [459]}] if role == "subject" else [],
            "relation": {"kind": role, "pronoun_char_span": span,
                         "verb_char_span": tokens[verb["span"][0]]["char_span"]},
            "expected_pronoun": expected, "edit_hint": None,
        })
    return result


def _for_subjects(node):
    parts = node.get("children", [])
    if (node["type"] == "SBAR" and len(parts) == 2 and parts[0].get("pos") == "IN"
            and parts[0]["surface"].casefold() == "for" and parts[1]["type"] == "S"):
        clause = parts[1].get("children", [])
        if [child["type"] for child in clause] == ["NP", "VP"]:
            subject, predicate = clause
            pronouns = list(_ordered_leaves(subject))
            vp = predicate.get("children", [])
            if (len(pronouns) == 1 and pronouns[0].get("pos") == "PRP" and len(vp) == 2
                    and vp[0].get("pos") == "TO" and vp[0]["surface"].casefold() == "to"
                    and vp[1]["type"] == "VP"):
                lower = vp[1].get("children", [])
                if lower and lower[0].get("pos") == "VB":
                    yield parts[0], pronouns[0]
    for child in parts:
        yield from _for_subjects(child)


def probe_infinitival_case(sentence, tree, *, variety):
    """Recognize an explicit for-clause with a single personal-pronoun subject."""
    result = {"status": "not_evaluated", "production_enabled": False, "candidates": []}
    if variety != "standard_english":
        return result
    tokens = tokens_with_spans(sentence)
    leaves = list(_ordered_leaves(tree))
    if len(tokens) != len(leaves) or any(
        leaf["span"] != [token["index"], token["index"] + 1] or leaf["surface"] != token["text"]
        for leaf, token in zip(leaves, tokens)
    ) or any(token["text"] in {'"', '“', '”', "'", "‘", "’"} for token in tokens):
        return result
    result["status"] = "candidate_only"
    for marker, pronoun in _for_subjects(tree):
        expected = OBJECT_FORMS.get(pronoun["surface"].casefold())
        if expected:
            result["candidates"].append({
                "rule_id": "CLS-285", "source_chapter": 14, "source_pages": [1182],
                "relation": {"kind": "for_infinitival_subject",
                             "marker_char_span": tokens[marker["span"][0]]["char_span"],
                             "pronoun_char_span": tokens[pronoun["span"][0]]["char_span"]},
                "expected_pronoun": expected, "edit_hint": None,
            })
    return result


REFLEXIVE_SUBJECTS = {
    "myself": {"i"}, "yourself": {"you"}, "yourselves": {"you"},
    "himself": {"he", "they"}, "herself": {"she", "they"}, "itself": {"it"},
    "ourselves": {"we"}, "themselves": {"they"}, "themself": {"they"},
}


def _conditional_clauses(tree):
    if tree["type"] != "S":
        return
    for node in tree.get("children", []):
        parts = node.get("children", [])
        if (node["type"] == "SBAR" and len(parts) == 2 and parts[0].get("pos") == "IN"
                and parts[0]["surface"].casefold() == "if" and parts[1]["type"] == "S"):
            yield parts[1]


def probe_local_reflexive(sentence, tree, *, variety):
    """Use local subject evidence in a simple finite conditional adjunct."""
    result = {"status": "not_evaluated", "production_enabled": False, "candidates": []}
    if variety != "standard_english":
        return result
    tokens = tokens_with_spans(sentence)
    leaves = list(_ordered_leaves(tree))
    if len(tokens) != len(leaves) or any(
        leaf["span"] != [token["index"], token["index"] + 1] or leaf["surface"] != token["text"]
        for leaf, token in zip(leaves, tokens)
    ) or any(token["text"] in {'"', '“', '”', "'", "‘", "’"} for token in tokens):
        return result
    result["status"] = "candidate_only"
    for clause in _conditional_clauses(tree):
        body = clause.get("children", [])
        if [part["type"] for part in body] != ["NP", "VP"]:
            continue
        subject, predicate = body
        vp = predicate.get("children", [])
        if len(vp) != 2 or vp[1]["type"] != "NP" or vp[0].get("pos") not in {"VBD", "VBP", "VBZ"}:
            continue
        # A small set of ordinary transitive verbs excludes predicative readings.
        if vp[0]["surface"].casefold() not in TRANSITIVE_FORMS | {
            "blame", "blames", "blamed", "injure", "injures", "injured", "hurt", "hurts",
        }:
            continue
        subjects = list(_ordered_leaves(subject))
        objects = list(_ordered_leaves(vp[1]))
        if len(subjects) != 1 or len(objects) != 1 or any(
            leaf.get("pos") != "PRP" for leaf in subjects + objects
        ):
            continue
        local, reflexive = subjects[0], objects[0]
        controller = local["surface"].casefold()
        allowed = REFLEXIVE_SUBJECTS.get(reflexive["surface"].casefold())
        if controller not in OBJECT_FORMS.keys() | {"it", "you"} or not allowed or controller in allowed:
            continue
        result["candidates"].append({
            "rule_id": "CLS-1101", "source_chapter": 17, "source_pages": [1457],
            "relation": {"kind": "reflexive_local_subject_mismatch",
                         "subject_char_span": tokens[local["span"][0]]["char_span"],
                         "reflexive_char_span": tokens[reflexive["span"][0]]["char_span"]},
            "edit_hint": None,
        })
    return result


def probe_pride_reflexive(sentence, tree, *, variety):
    """Recognize the simple finite pride + personal object + on frame."""
    result = {"status": "not_evaluated", "production_enabled": False, "candidates": []}
    if variety != "standard_english":
        return result
    tokens = tokens_with_spans(sentence)
    leaves = list(_ordered_leaves(tree))
    if len(tokens) != len(leaves) or any(
        leaf["span"] != [token["index"], token["index"] + 1] or leaf["surface"] != token["text"]
        for leaf, token in zip(leaves, tokens)
    ):
        return result
    result["status"] = "candidate_only"
    parts = tree.get("children", [])
    if tree["type"] != "S" or [part["type"] for part in parts] != ["NP", "VP", "."]:
        return result
    predicate = parts[1].get("children", [])
    if len(predicate) != 3:
        return result
    verb, obj, phrase = predicate
    if (verb.get("pos") not in {"VBD", "VBP", "VBZ"}
            or verb["surface"].casefold() not in {"pride", "prides", "prided"}
            or obj["type"] != "NP" or phrase["type"] != "PP"):
        return result
    obj_leaves = list(_ordered_leaves(obj))
    pp = phrase.get("children", [])
    if (len(obj_leaves) != 1 or obj_leaves[0].get("pos") != "PRP"
            or obj_leaves[0]["surface"].casefold() not in SUBJECT_FORMS.keys() | {"it", "you"}
            or len(pp) != 2 or pp[0].get("pos") != "IN"
            or pp[0]["surface"].casefold() != "on" or pp[1]["type"] not in {"NP", "S"}):
        return result
    result["candidates"].append({
        "rule_id": "CLS-1103", "source_chapter": 17, "source_pages": [1488],
        "relation": {"kind": "pride_requires_reflexive_object",
                     "verb_char_span": tokens[verb["span"][0]]["char_span"],
                     "object_char_span": tokens[obj_leaves[0]["span"][0]]["char_span"]},
        "edit_hint": None,
    })
    return result
