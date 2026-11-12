"""Offline adapter from a narrow parser modal pattern to the Chapter 3 probe."""

from lemminflect import getAllInflections, getLemma

if __package__:
    from .cgel_ch03_candidate_probe import MODALS, SUPPORT_DO, probe_ch03, tokens_with_spans
    from .parse_engine import _ordered_leaves
else:
    from cgel_ch03_candidate_probe import MODALS, SUPPORT_DO, probe_ch03, tokens_with_spans
    from parse_engine import _ordered_leaves


def _modal_relations(node):
    children = node.get("children", [])
    if node["type"] == "VP" and len(children) == 2:
        modal, complement = children
        if modal.get("pos") == "MD" and modal["surface"].casefold() in MODALS:
            if complement["type"] == "S" and len(complement.get("children", [])) == 1:
                complement = complement["children"][0]
            if complement["type"] == "VP":
                parts = complement.get("children", [])
                if parts and all(part["type"] not in {"CC", "CONJP"} for part in parts):
                    yield modal, parts
    for child in children:
        yield from _modal_relations(child)


def _plain_form_for_mistagged_3sg(surface):
    """Confirm a single attested verb paradigm when the parser supplies VB."""
    lemmas = getLemma(surface, upos="VERB", lemmatize_oov=False)
    if len(lemmas) != 1:
        return None
    lemma = lemmas[0]
    forms = getAllInflections(lemma, upos="VERB")
    if (surface != lemma and surface in forms.get("VBZ", ()) and lemma in forms.get("VB", ())
            and surface not in getAllInflections(surface, upos="VERB").get("VB", ())):
        return lemma
    return None


def _relation(modal, parts):
    dependent = parts[0]
    a, b = modal["span"][0], dependent["span"][0]
    if b != a + 1:
        return None
    relation = {
        "kind": "modal_selects", "governor": a, "dependent": b,
        "governor_role": "central_modal", "direct_selection": True,
        "clause_kind": "other", "same_clause": True, "coordinated": False,
    }
    surface = dependent.get("surface", "").casefold()
    pos = dependent.get("pos")
    if pos == "MD" and surface in MODALS:
        if len(parts) != 2 or parts[1]["type"] != "VP":
            return None
        lower = parts[1].get("children", [])
        if not lower or lower[0].get("pos") != "VB":
            return None
        return {**relation, "dependent_role": "central_modal"}
    plain = None
    if pos == "VBZ":
        lemmas = getLemma(surface, upos="VERB", lemmatize_oov=False)
        plain = lemmas[0] if len(lemmas) == 1 else None
    elif pos == "VB" and surface.endswith("s"):
        plain = _plain_form_for_mistagged_3sg(surface)
    if pos == "VBZ" or plain:
        return {**relation, "dependent_role": "lexical_verb", "dependent_form": "present_3sg",
                "candidate_plain_form": plain}
    if len(parts) == 2 and dependent.get("pos") == "TO" and parts[1]["type"] == "VP":
        lexical = parts[1].get("children", [])
        if lexical and lexical[0].get("pos") == "VB" and all(
            part["type"] not in {"CC", "CONJP"} for part in lexical[1:]
        ):
            return {**relation, "dependent_role": "infinitival_marker", "dependent_form": "infinitival_to",
                    "infinitival_verb": lexical[0]["span"][0], "infinitival_verb_form": "plain"}
    return None


def _inverted_do_relation(tree):
    """Recognize root polar questions with explicit auxiliary evidence."""
    children = tree.get("children", [])
    if tree["type"] != "SQ":
        return None
    if len(children) != 4 or children[-1].get("surface") != "?":
        return None
    governor, subject, predicate, _ = children
    if (governor.get("pos") not in {"VBD", "VBP", "VBZ"}
            or governor["surface"].casefold() not in SUPPORT_DO
            or subject["type"] != "NP" or predicate["type"] != "VP"):
        return None
    parts = predicate.get("children", [])
    if len(parts) != 2:
        return None
    dependent, complement = parts
    surface = dependent.get("surface", "").casefold()
    if dependent.get("pos") == "MD" and surface in MODALS and complement["type"] == "VP":
        role = "central_modal"
    elif dependent.get("pos") == "VB" and surface == "be" and complement["type"] == "ADJP":
        role = "copular_be"
    elif dependent.get("pos") == "VB" and complement["type"] == "VP":
        lower = complement.get("children", [])
        if not lower:
            return None
        role = {
            ("have", "VBN"): "perfect_have",
            ("be", "VBN"): "passive_be",
            ("be", "VBG"): "progressive_be",
        }.get((surface, lower[0].get("pos")))
    else:
        return None
    if not role:
        return None
    return {
        "kind": "supportive_do_selects", "governor": governor["span"][0],
        "dependent": dependent["span"][0], "governor_role": "supportive_do",
        "dependent_role": role, "direct_selection": True, "same_clause": True,
        "coordinated": False, "clause_kind": "closed_interrogative",
    }


def probe_modal_parser(sentence, tree, *, variety):
    """Require aligned parser evidence and keep the existing Chapter 3 output contract."""
    tokens = tokens_with_spans(sentence)
    leaves = list(_ordered_leaves(tree))
    if len(tokens) != len(leaves) or any(
        leaf["span"] != [token["index"], token["index"] + 1] or leaf["surface"] != token["text"]
        for leaf, token in zip(leaves, tokens)
    ):
        return {"status": "not_evaluated", "candidates": [], "blocked": ["parser_token_alignment_unavailable"]}
    if any(token["text"] in {'"', '“', '”', "'", "‘", "’"} for token in tokens):
        return {"status": "not_evaluated", "candidates": [], "blocked": ["quotation_scope_unresolved"]}
    relations = [
        relation for modal, parts in _modal_relations(tree)
        if (relation := _relation(modal, parts)) is not None
    ]
    if (relation := _inverted_do_relation(tree)) is not None:
        relations.append(relation)
    result = probe_ch03(sentence, {"status": "typed_candidate", "sentence": sentence, "relations": relations},
                        variety=variety)
    return result
