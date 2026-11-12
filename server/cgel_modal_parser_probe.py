"""Offline adapter from a narrow parser modal pattern to the Chapter 3 probe."""

from lemminflect import getAllInflections, getLemma

if __package__:
    from .cgel_ch03_candidate_probe import MODALS, probe_ch03, tokens_with_spans
    from .parse_engine import _ordered_leaves
else:
    from cgel_ch03_candidate_probe import MODALS, probe_ch03, tokens_with_spans
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
    result = probe_ch03(sentence, {"status": "typed_candidate", "sentence": sentence, "relations": relations},
                        variety=variety)
    return result
