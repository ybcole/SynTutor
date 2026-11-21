"""Concise, learner-facing explanations from an existing validated syntax tree.

This is presentation, not a new Cambridge rule evaluator or a licence to
claim sentence grammaticality. The fact graph remains the sole source of
recorded nodes, original words, phrase boundaries, and available alternatives.
No book citations, internal status labels or model-status messages appear in
learner prose. The detailed XAI-2..7 evidence remains separately accessible
to server evaluation, not shown as a wall of text to students.
"""
from __future__ import annotations

from typing import Any

VERSION = "learner-explanation-1.0.0"
NAMES = {
    "S": "clause", "S'": "clause", "S''": "clause",
    "S-bar": "clause", "S-dbar": "clause",
    "NP": "noun phrase", "NOM": "noun group",
    "VP": "verb phrase", "PP": "preposition phrase",
    "AP": "adjective phrase", "AdvP": "adverb phrase",
    "N": "noun", "V": "verb", "A": "adjective",
    "Adv": "adverb", "PRO": "pronoun", "PRON": "pronoun",
    "ART": "article", "DET": "determiner", "NAME": "name",
    "P": "preposition", "DEG": "degree word",
    "Q": "quantifier", "QA": "quantifying adjective", "POSS": "possessive",
    "DEM": "demonstrative determiner", "V-part": "participle",
    "PartP": "participle phrase", "Prt": "particle",
    "PRE-DET": "pre-determiner", "PART": "particle", "NEG": "negator",
    "name": "name", "Phrase": "phrase", "PHRASE": "phrase",
    "MOD": "modal auxiliary", "PERF": "perfect auxiliary",
    "PROG": "progressive auxiliary", "PASS": "passive auxiliary",
    "AUX": "auxiliary", "TENSE": "tense marker",
    "C": "clause introducer", "C1": "clause introducer",
    "C2": "clause introducer", "pronoun": "pronoun",
}
BE = {"am", "is", "are", "was", "were", "be", "been", "being"}
HAVE = {"have", "has", "had"}
MODALS = {"can", "could", "may", "might", "must", "shall", "should", "will", "would"}
PRONOUNS = {
    "i": "the person speaking", "me": "the person speaking",
    "you": "the person being addressed",
    "he": "a male person already known in the context",
    "him": "a male person already known in the context",
    "she": "a female person already known in the context",
    "her": "a female person already known in the context",
    "we": "the speaker and other people", "us": "the speaker and other people",
    "they": "people or things already known in the context",
    "them": "people or things already known in the context",
    "it": "a thing, idea or situation already understood",
}
ARTICLES = {"the": "points to something the reader can already identify",
            "a": "introduces one non-specific example",
            "an": "introduces one non-specific example"}
LEXICAL = {"N", "V", "A", "Adv", "P", "PRO", "PRON", "pronoun", "ART", "NAME",
           "name", "DEG", "Q", "QA", "POSS", "DEM", "V-part", "PRE-DET", "PART",
           "Prt", "NEG", "MOD", "PERF", "PROG", "PASS", "AUX", "TENSE", "DET",
           "C", "C1", "C2"}


def _quote(value: str) -> str:
    clean = " ".join(value.split())
    if len(clean) > 110:
        clean = clean[:107].rsplit(" ", 1)[0] + "…"
    return f"“{clean}”" if clean else "this position"


def _node_phrase(n: dict[str, Any] | None) -> str:
    return _quote(n.get("surface", "")) if n else "this part of the sentence"


def _word_kind(node: dict[str, Any], by_id: dict[str, dict]) -> str | None:
    for ancestor in node["ancestor_ids"]:
        parent = by_id.get(ancestor)
        if parent and parent.get("label") in LEXICAL:
            return parent["label"]
    return None


def _first_ancestor(node: dict, by_id: dict[str, dict], labels: set[str]) -> dict | None:
    return next((by_id[k] for k in node["ancestor_ids"]
                 if k in by_id and by_id[k].get("label") in labels), None)


def _phrase_context(node: dict, by_id: dict[str, dict]) -> str | None:
    """Nearest enclosing phrase (never a clause) whose surface differs."""
    return _nearest_context(node, by_id, {"VP", "NP", "NOM", "PP", "AP", "AdvP",
                                          "PartP"})


def _clause_context(node: dict, by_id: dict[str, dict]) -> str | None:
    """Nearest enclosing clause whose surface differs."""
    return _nearest_context(node, by_id, {"S", "S'", "S''", "S-bar", "S-dbar"})


def _nearest_context(node: dict, by_id: dict[str, dict], labels: set[str]) -> str | None:
    own = str(node.get("surface") or "").strip()
    for ancestor_id in node.get("ancestor_ids") or []:
        ancestor = by_id.get(ancestor_id)
        if not ancestor or ancestor.get("label") not in labels:
            continue
        surface = str(ancestor.get("surface") or "").strip()
        if surface and surface != own:
            return _node_phrase(ancestor)
    return None


def _neighbor(graph: dict, node: dict, offset: int) -> str | None:
    span = node.get("token_span")
    if not span or span[0] == span[1]:
        return None
    pos = (span[1] if offset > 0 else span[0] - 1)
    seq = graph.get("token_index", [])
    return seq[pos]["text"] if 0 <= pos < len(seq) else None


def _first_word(surface: str) -> str:
    return surface.split()[0] if surface.split() else ""


def _noun_context(node: dict, by_id: dict[str, dict]) -> str:
    parent = _first_ancestor(node, by_id, {"NP", "NOM"})
    return f" in {_node_phrase(parent)}" if parent and parent["surface"] != node["surface"] else ""


def _word(node: dict, graph: dict, by_id: dict[str, dict]) -> str:
    word, lower = node["surface"], node["surface"].lower()
    kind = _word_kind(node, by_id)
    clause = _first_ancestor(node, by_id, {"S", "S'", "S''", "S-bar", "S-dbar"})
    # Lexical words name the smallest enclosing phrase. Clause-level words
    # (verbs, auxiliaries, modals, clause markers) fall back to the clause,
    # because their role is defined there.
    raw_context = _phrase_context(node, by_id)
    context = raw_context or _clause_context(node, by_id) or "this part of the sentence"
    next_word = _neighbor(graph, node, 1)
    previous_word = _neighbor(graph, node, -1)

    if kind in {"PRO", "PRON"} or lower in PRONOUNS and kind not in {"N", "V", "A"}:
        meaning = PRONOUNS.get(lower)
        if meaning:
            if raw_context:
                return (f"{_quote(word)} is a pronoun referring to {meaning}. "
                        f"In this sentence, it is part of {context}.")
            return f"{_quote(word)} is a pronoun referring to {meaning} in this sentence."
        return f"{_quote(word)} is a pronoun used to refer to someone or something in this sentence."

    if lower in BE and kind in {"V", "AUX", "PROG", "PASS", "TENSE", "PERF"}:
        form = ("a present-tense" if lower in {"am", "is", "are"}
                else "a past-tense" if lower in {"was", "were"}
                else "a")
        if next_word and next_word.lower() in {"not", "n't"}:
            idx = node["token_span"][1] + 1
            seq = graph.get("token_index", [])
            next_word = seq[idx]["text"] if idx < len(seq) else None
        if kind == "PASS":
            return (f"{_quote(word)} is {form} form of “be” acting as the passive "
                    f"auxiliary in {context}.")
        if kind == "PROG":
            return (f"{_quote(word)} is {form} form of the verb “be”. "
                    + (f"Here it combines with {_quote(next_word)} to describe an activity in progress."
                       if next_word else f"Here it acts as the progressive auxiliary in {context}."))
        if next_word and next_word.lower().endswith("ed") and kind == "AUX":
            return (f"{_quote(word)} is a form of “be.” "
                    f"Here it helps form the verb expression {context}.")
        return (f"{_quote(word)} is {form} form of the verb “be”. "
                f"In this sentence, it forms part of {context}.")

    if lower in HAVE and kind in {"V", "AUX", "PERF"}:
        form = "past-tense" if lower == "had" else "present-tense"
        if kind == "PERF":
            return (f"{_quote(word)} is a {form} form of “have” acting as the perfect "
                    f"auxiliary in {context}.")
        if next_word and next_word.lower() in {"eaten", "gone", "seen", "done", "taken",
                                                "given", "known", "written", "spoken", "been",
                                                "made", "read", "found", "thought", "left"}:
            return (f"{_quote(word)} is a {form} form of “have.” "
                    f"Here it appears before {_quote(next_word)} in the verb phrase {context}.")
        return (f"{_quote(word)} is a {form} form of “have.” "
                f"Here it forms part of {context}; its use depends on the words around it.")

    if lower in MODALS and kind in {"V", "MOD", "AUX"}:
        meaning = ("ability or possibility" if lower in {"can", "could", "may", "might"}
                   else "necessity or obligation" if lower in {"must", "should"}
                   else "a future, expected or hypothetical situation")
        return (f"{_quote(word)} is a modal helping verb that can express {meaning}. "
                f"Here it belongs to the verb phrase {context}.")

    if kind == "Q":
        return f"{_quote(word)} is a quantifier that tells how many or how much."
    if kind == "QA":
        return (f"{_quote(word)} is a quantifying adjective telling how much or "
                "how many.")
    if kind == "Prt":
        return (f"{_quote(word)} is a particle that combines with the verb to "
                "form a phrasal verb.")
    if kind in {"NAME", "name"}:
        return (f"{_quote(word)} is a name identifying a particular person, place, "
                "day or thing.")
    if kind == "POSS":
        return f"{_quote(word)} is a possessive word showing who something belongs to."
    if kind == "DEM":
        return (f"{_quote(word)} is a demonstrative word pointing to something "
                "identified in the context.")
    if kind == "V-part":
        return f"{_quote(word)} is a participle forming part of {context}."
    if kind in {"PRE-DET", "PART", "NEG"}:
        return f"{_quote(word)} is a {NAMES.get(kind, 'function word')} in {context}."

    if kind in {"ART", "DET"} or lower in ARTICLES and kind not in {"N", "V"}:
        meaning = ARTICLES.get(lower)
        if meaning:
            return f"{_quote(word)} is a determiner that {meaning}{_noun_context(node, by_id)}."
        return f"{_quote(word)} is a determiner used to introduce or specify a noun{_noun_context(node, by_id)}."

    if kind == "N":
        return (f"{_quote(word)} is a noun that names someone, something, or an idea"
                f"{_noun_context(node, by_id)}.")
    if kind == "NAME":
        return f"{_quote(word)} is a name identifying a particular person, place or thing in the sentence."
    if kind == "V":
        return (f"{_quote(word)} is the verb in {context}. "
                f"It expresses the action, event or state described there.")
    if kind == "A":
        ap = _first_ancestor(node, by_id, {"AP"})
        if ap and ap["surface"] != word:
            return f"{_quote(word)} is an adjective expressing a quality. In {_node_phrase(ap)}, another word changes its degree or emphasis."
        return f"{_quote(word)} is an adjective expressing a quality or description in this sentence."
    if kind in {"Adv", "DEG"}:
        return f"{_quote(word)} adds detail or emphasis to the surrounding expression {context}."
    if kind == "P":
        if lower in {"here", "there", "where", "everywhere", "nowhere"}:
            return f"{_quote(word)} is a place word that stands for a location in this sentence."
        pp = _first_ancestor(node, by_id, {"PP"})
        if pp and str(pp.get("surface") or "").strip() != word.strip():
            return f"{_quote(word)} introduces the preposition phrase {_node_phrase(pp)}, linking it to the rest of the expression."
        return f"{_quote(word)} is a preposition relating the following words to the surrounding phrase."
    if kind in {"C", "C1", "C2"}:
        if kind == "C2" and lower in {"who", "whom", "whose", "what", "which",
                                      "when", "where", "why", "how"}:
            # Distinguish relative pronouns inside NP/NOM from fronted wh-question phrases.
            enclosing_sdbar = _first_ancestor(node, by_id, {"S-dbar", "S''"})
            sdbar_parent = by_id.get(enclosing_sdbar["parent_id"]) if enclosing_sdbar else None
            if sdbar_parent and sdbar_parent.get("label") in {"NOM", "NP"}:
                return (f"{_quote(word)} is a relative pronoun introducing the relative "
                        f"clause {context}, linking it back to the noun it modifies.")
            return (f"{_quote(word)} is the wh-phrase at the front of the question. "
                    "It corresponds to the missing position inside the clause.")
        if lower in {"that", "whether", "if"}:
            return f"{_quote(word)} introduces the subordinate clause {context}."
        if lower in BE | HAVE | MODALS | {"do", "does", "did"}:
            return (f"{_quote(word)} is an auxiliary verb placed before the subject "
                    "to form a question in this sentence.")
        return f"{_quote(word)} introduces or connects a clause in this sentence."
    if previous_word:
        return (f"{_quote(word)} appears after {_quote(previous_word)}"
                + (f" as part of {context}." if raw_context else " in this sentence."))
    if next_word:
        return f"{_quote(word)} appears before {_quote(next_word)}, as part of this sentence."
    return f"{_quote(word)} is the word at this point in the sentence."


def _phrase(node: dict, graph: dict, by_id: dict[str, dict]) -> str:
    surface = _node_phrase(node)
    label = node.get("label")
    children = [by_id[k] for k in node["child_ids"] if k in by_id]
    parent = by_id.get(node["parent_id"])
    other = next((by_id[k] for k in node["sibling_ids"]
                  if k in by_id and by_id[k]["surface"]), None)
    if not str(node.get("surface") or "").strip():
        if label == "TENSE":
            return ("This position marks the tense of the clause; the tense is not "
                    "carried by a separate spoken word here.")
        if label == "C2":
            return ("This position marks the fronted wh-phrase or relative operator; "
                    "the phrase itself appears at the front of the clause.")
        if label == "C1":
            return ("This position marks the clause introducer; no word is "
                    "pronounced here.")
        if label in {"AUX", "DET"}:
            return ("This position marks structural information that is not "
                    "pronounced as a separate word here.")
        description = NAMES.get(label)
        if description:
            return f"This empty position stands for an omitted {description}."
        return ("This position represents an understood or omitted part of the "
                "sentence, rather than a word that is actually spoken.")
    if label in {"S", "S'", "S''", "S-bar", "S-dbar", "Sentence"}:
        if len(children) >= 2 and children[0].get("label") == "NP" and children[1].get("label") == "VP":
            subject = (_node_phrase(children[0]) if str(children[0].get("surface") or "").strip()
                       else "the understood subject")
            predicate = (_node_phrase(children[1]) if str(children[1].get("surface") or "").strip()
                         else "the predicate")
            return (f"In {surface}, {subject} identifies who or what "
                    f"the sentence is about, and {predicate} tells us "
                    "what happens or what is being described.")
        if label in {"S-bar", "S'", "S''", "S-dbar"} and parent \
                and parent.get("label") in {"S-bar", "S'", "S''", "S-dbar"} \
                and parent.get("surface") == node.get("surface"):
            return f"{surface} is the inner clause layer of this clause."
        if label in {"S-bar", "S'", "S''", "S-dbar"} and children:
            lead_child = children[0]
            lead_label = str(lead_child.get("label") or "")
            lead = (_node_phrase(lead_child)
                    if str(lead_child.get("surface") or "").strip()
                    else "the clause marker")
            is_root_clause = parent is None
            if is_root_clause:
                if label in {"S-dbar", "S''"} or lead_label == "C2":
                    return (f"{surface} is an independent wh-question; {lead} sits in "
                            "the fronted question position (C2) and the following clause "
                            "supplies the rest of the question.")
                lead_first = _first_word(str(lead_child.get("surface") or "")).lower()
                is_inverted_aux = lead_first in (
                    BE | HAVE | MODALS | {"do", "does", "did", "don't", "doesn't",
                                          "didn't", "isn't", "aren't", "wasn't",
                                          "weren't", "haven't", "hasn't", "hadn't",
                                          "can't", "won't", "wouldn't", "couldn't",
                                          "shouldn't", "mustn't", "mightn't"}
                )
                if lead_label == "C1" and is_inverted_aux:
                    return (f"{surface} is an independent yes/no question; the auxiliary "
                            f"{lead} is fronted before the subject to form the question.")
                if lead_label == "C1" and str(lead_child.get("surface") or "").strip():
                    return (f"{surface} is a subordinate clause introduced by {lead}; "
                            "the following clause supplies its subject and predicate.")
                return (f"{surface} is a main clause with a fronted question or "
                        f"clause-initial layer introduced by {lead}.")
            return (f"{surface} is a subordinate clause layer; {lead} introduces "
                    "it and the following clause supplies the rest.")
        if children:
            return f"{surface} is a clause made up of the connected parts of this sentence."
        return f"{surface} is a clause in this sentence."

    if label in {"Phrase", "PHRASE", "PHRASE-a", "PHRASE-b", "PHRASE-c"}:
        return f"{surface} is a phrase in the sentence structure."

    if label == "PartP":
        return f"{surface} is a participle phrase describing or identifying a noun."

    if label == "NP":
        noun = next((c for c in children if c.get("label") in {"N", "NOM", "NAME"}), None)
        if other and parent and parent.get("label") in {"S", "S'", "S''"} and other.get("label") == "VP":
            return (f"{surface} is a noun phrase identifying who or what this clause is about. "
                    f"The accompanying verb phrase {_node_phrase(other)} tells us more about it.")
        if noun:
            if str(noun.get("surface") or "").strip() == str(node.get("surface") or "").strip():
                return (f"{surface} is a noun phrase naming a person, thing, "
                        "group, or idea.")
            return f"{surface} is a noun phrase built around {_node_phrase(noun)}, which names the person or thing being referred to."
        return f"{surface} is a noun phrase referring to a person, thing, group, or idea."

    if label == "NOM":
        return f"{surface} groups a noun with any words that describe or restrict it, forming part of a larger noun phrase."

    if label == "VP":
        if parent and parent.get("label") == "VP" and parent.get("surface") == node.get("surface"):
            parts = ", ".join(str(child.get("label") or "word") for child in children[:4])
            return (f"{surface} is the inner verb-phrase layer containing "
                    f"{parts or 'its parts'}.")
        if len(children) == 1 and children[0].get("label") == "VP":
            return f"{surface} is a nested verb-phrase layer in this clause."
        if other and parent and parent.get("label") in {"S", "S'", "S''"} and other.get("label") == "NP":
            return (f"{surface} is the verb phrase, expressing what happens or is true "
                    f"of {_node_phrase(other)} in this clause.")
        return f"{surface} is a verb phrase that expresses an action, event or state in the sentence."

    if label == "AP":
        first = children[0] if children else None
        last = children[-1] if children else None
        if first and last and first.get("label") in {"DEG", "Adv"} and last.get("label") in {"A", "AP"}:
            return (f"{surface} is an adjective phrase describing a quality. "
                    f"{_node_phrase(first)} adds emphasis to {_node_phrase(last)}.")
        return f"{surface} is an adjective phrase used to describe a quality."

    if label == "PP":
        beginning = children[0] if children else None
        if beginning:
            if str(beginning.get("surface") or "").strip() == str(node.get("surface") or "").strip():
                return (f"{surface} is a short prepositional expression adding "
                        "place, time or manner information.")
            return (f"{surface} is a preposition phrase beginning with {_node_phrase(beginning)}. "
                    "It adds a relationship such as place, time or manner to the surrounding expression.")
        return f"{surface} is a preposition phrase adding information to the surrounding expression."

    if label == "AdvP":
        return f"{surface} is an adverb phrase adding information about how, when, where or to what extent something happens."

    if label in LEXICAL:
        description = NAMES.get(label, "word group")
        if len(children) == 1 and children[0]["kind"] == "word":
            # The branch explains the phrase-marker slot; the word child
            # explains the word itself. Keeping them distinct prevents the
            # learner from seeing the same paragraph twice.
            role = {"C1": "clause-marker", "C2": "fronted-phrase"}.get(label, description)
            context = _phrase_context(node, by_id) or _clause_context(node, by_id) or "this part of the sentence"
            return (f"The {role} position in {context} is filled by "
                    f"{_quote(children[0]['surface'])}.")
        if label in {"V", "AUX", "MOD", "PERF", "PROG", "PASS"}:
            return f"{surface} is the {description} in this part of the sentence."
        return f"{surface} is the {description} in the surrounding phrase."

    if node["kind"] == "triangle":
        if (parent and parent.get("label")
                and str(parent.get("surface") or "").strip() != str(node.get("surface") or "").strip()):
            return f"{surface} is a part of the larger {_node_phrase(parent)} phrase; its internal words are not analysed further here."
        return f"{surface} forms a phrase whose internal words are not analysed further here."

    if (parent and parent.get("surface")
            and str(parent.get("surface")).strip() != str(node.get("surface") or "").strip()):
        return f"{surface} forms one part of the larger expression {_node_phrase(parent)}."
    return f"{surface} is a unit in the structure of this sentence."


def compose_learner_explanation(graph: dict[str, Any] | None,
                                *, node_id: str | None = None) -> dict[str, Any]:
    """Single plain-English paragraph grounded in selected witnessed nodes.

    If no node is selected, the actual root is summarized without changing
    the XAI-7 source-frozen selection or the user input.
    """
    result = {
        "schema_version": VERSION, "language_policy": "ENGLISH_ONLY",
        "analysis_id": None, "selected_node_id": node_id,
        "status": "unavailable", "text": (
            "I couldn't establish a reliable syntax tree for this sentence, "
            "so I can't explain its grammatical structure with confidence."
        ),
        "whole_sentence_certified": False,
        "source_claim_ids": [],
    }
    if not isinstance(graph, dict) or graph.get("status") not in {"observed", "provisional"}:
        return result
    nodes = graph.get("nodes", [])
    if not nodes:
        return result
    by_id = {n["node_id"]: n for n in nodes}
    target = by_id.get(node_id) if node_id is not None else nodes[0]
    if not target:
        return result
    content = _describe_node(target, graph, by_id)
    if graph["status"] == "provisional":
        content = "In this possible reading, " + content[:1].lower() + content[1:]
    return {
        **result, "analysis_id": graph["analysis_id"], "selected_node_id": node_id,
        "status": "provisional" if graph["status"] == "provisional" else "observed",
        "text": content, "whole_sentence_certified": False,
    }


def _describe_node(target, graph, by_id):
    if target["kind"] in {"gap", "empty", "elided_terminal"}:
        parent_n = by_id.get(target.get("parent_id"))
        if target.get("label") == "E" and parent_n and parent_n.get("label") == "N":
            content = ("This elided noun position (E) stands for an understood noun "
                       "omitted through ellipsis and recovered from context.")
        elif target.get("label") == "E" and parent_n and parent_n.get("label") == "VP":
            content = ("This elided verb-phrase position (E) stands for an understood "
                       "verb phrase omitted through ellipsis and recovered from earlier in the sentence.")
        else:
            content = ("This position represents an understood or omitted part of the sentence, "
                       "rather than a word that is actually spoken.")
    elif target["kind"] == "word":
        content = _word(target, graph, by_id)
    else:
        content = _phrase(target, graph, by_id)
    return content


def _source_tokens_by_node(graph, analysis):
    """Bridge parser indices to tree nodes through exact sentence-local offsets."""
    sentences = analysis['sentences']
    offset = sentences[analysis['sentence_index']]['start'] if sentences else 0
    source = {(token['start'] - offset, token['end'] - offset, token['t']): token['i']
              for token in analysis['tokens']}
    aligned = {row['token_id']: source.get((*row['char_span'], row['text']))
               for row in graph['token_index']}
    return {node['node_id']: [aligned[i] for i in node['token_ids']
                              if aligned.get(i) is not None]
            for node in graph['nodes']}


def _word_morphology_summary(leaf):
    """Build concise, evidence-grounded word-level morphology from spaCy/Benepar."""
    tag = leaf.get('type')
    ftag = leaf.get('ftag')
    morph = leaf.get('fmorph') or {}
    low = leaf['surface'].lower()
    if tag != ftag:
        # Only report morphology corroborated by both parsers when they agree,
        # except for clear closed-class items.
        if low in {'not', "n't", 'n’t'} and leaf.get('fdep') == 'neg':
            return 'a negation marker'
        return None
    if tag == 'NN':
        return 'a singular common noun'
    if tag == 'NNS':
        return 'a plural common noun'
    if tag == 'NNP':
        return 'a singular proper name'
    if tag == 'NNPS':
        return 'a plural proper name'
    if tag == 'VBZ':
        return 'a finite third-person singular present-tense verb'
    if tag == 'VBP':
        return 'a finite present-tense verb (non-third-person singular)'
    if tag == 'VBD':
        return 'a finite past-tense verb'
    if tag == 'VBG':
        return 'a non-finite -ing participle verb form'
    if tag == 'VBN':
        from ruleset import PAST_ONLY
        if low in PAST_ONLY:
            return None
        return 'a non-finite past-participle verb form'
    if tag == 'VB':
        return 'a plain (base) verb form'
    if tag == 'MD':
        return 'a modal auxiliary verb'
    if tag == 'JJ':
        return 'an adjective (plain grade)'
    if tag == 'JJR':
        return 'a comparative adjective'
    if tag == 'JJS':
        return 'a superlative adjective'
    if tag == 'RB':
        return 'a negation marker' if leaf.get('fdep') == 'neg' else 'an adverb'
    if tag == 'RBR':
        return 'a comparative adverb'
    if tag == 'RBS':
        return 'a superlative adverb'
    if tag == 'IN':
        return 'a subordinating conjunction' if leaf.get('fdep') == 'mark' else 'a preposition'
    if tag == 'TO':
        return 'the infinitival marker “to”' if leaf.get('fdep') == 'aux' else 'the preposition “to”'
    if tag == 'CC':
        return 'a coordinating conjunction'
    if tag == 'DT':
        if low in {'the'}:
            return 'the definite article'
        if low in {'a', 'an'}:
            return 'an indefinite article'
        if low in {'this', 'that'}:
            return 'a singular demonstrative determiner'
        if low in {'these', 'those'}:
            return 'a plural demonstrative determiner'
        return 'a determiner'
    if tag == 'PRP$':
        return 'a possessive determiner'
    if tag == 'PRP':
        case = {'Nom': 'subject-case', 'Acc': 'object-case'}.get(morph.get('Case'))
        num = {'Sing': 'singular', 'Plur': 'plural'}.get(morph.get('Number'))
        parts = [p for p in (num, case) if p]
        return f'a {" ".join(parts)} personal pronoun' if parts else 'a personal pronoun'
    if tag == 'CD':
        return 'a numeral (quantifier)'
    if tag == 'RP':
        return 'a verb particle'
    if tag in {'WP', 'WDT', 'WRB', 'WP$'}:
        return 'a wh-word (interrogative or relative introducer)'
    return None


def _dep_role_phrase(leaf, leaves):
    """Describe a word's dependency function relative to its attested governor."""
    dep = leaf.get('fdep')
    gov = leaves.get(leaf.get('fhead'))
    if not gov or leaf.get('fhead') == leaf.get('span', [None])[0]:
        if dep == 'ROOT':
            return 'the main predicate head of the sentence'
        return None
    gs = _quote(gov['surface'])
    return {
        'nsubj': f'the subject of {gs}',
        'nsubjpass': f'the passive subject of {gs}',
        'dobj': f'the direct object of {gs}',
        'iobj': f'the indirect object of {gs}',
        'pobj': f'the complement (object) of the preposition {gs}',
        'attr': f'the predicative complement of {gs}',
        'acomp': f'the predicative adjective complement of {gs}',
        'amod': f'a modifier describing {gs}',
        'advmod': f'an adverbial modifier of {gs}',
        'det': f'a determiner specifying {gs}',
        'poss': f'a possessive determiner for {gs}',
        'nummod': f'a numeral quantifying {gs}',
        'compound': f'a noun modifier forming a compound with {gs}',
        'prt': f'a particle combining with the verb {gs}',
        'mark': f'a clause marker introducing the subordinate clause headed by {gs}',
        'aux': f'an auxiliary verb supporting {gs}',
        'auxpass': f'a passive auxiliary supporting {gs}',
        'neg': f'a negation marker modifying {gs}',
        'cc': f'a coordinator linking constituents around {gs}',
        'prep': f'a preposition linking its complement to {gs}',
    }.get(dep)


def _runtime_description(node, graph, by_id, ids, leaves):
    """Explain witnessed features, internal structure, and local relations on the existing graph."""
    label = node.get('label') or _word_kind(node, by_id)
    surface = _node_phrase(node)
    basic = _describe_node(node, graph, by_id)
    if graph['status'] == 'provisional':
        # Use the selected observation. Provisional constituents never acquire
        # a head, attachment or function solely from their display position,
        # but single-word nodes may report independently corroborated morphology.
        label_name = NAMES.get(label)
        if len(ids) == 1 and ids[0] in leaves:
            morph_desc = _word_morphology_summary(leaves[ids[0]])
            if morph_desc:
                return f'{surface} is {morph_desc}. Because the full syntax tree is provisional, its wider clause attachment remains uncertain.'
        if label_name and node['surface']:
            return f'The working tree groups {surface} as a {label_name}. Its role in the full structure remains provisional.'
        return f'{surface} is visible in the working tree. Its structural role remains uncertain.'
    if not ids or node['kind'] in {'gap', 'empty', 'elided_terminal', 'triangle'}:
        return basic
    tokens = [leaves[i] for i in ids if i in leaves]
    if not tokens:
        return basic
    leaf = tokens[0]
    parent = by_id.get(node.get('parent_id'))
    children = [by_id[i] for i in node.get('child_ids', []) if i in by_id]

    # --- 1. Clause-level explanations (S, S', S'', S-bar, S-dbar) ------------ #
    if label == 'S':
        child_labels = [c.get('label') for c in children]
        overt = [c for c in children if c.get('surface')]
        # Coordinated clauses (S -> S CC S)
        cc_child = next((c for c in children if c.get('kind') == 'word' and c.get('surface', '').lower() in {'and', 'but', 'or', 'nor', 'so', 'yet'}), None)
        s_kids = [c for c in children if c.get('label') in {'S', "S'", 'S-bar'}]
        if cc_child and len(s_kids) >= 2:
            return (f'{surface} is a coordinated clause joining {_node_phrase(s_kids[0])} and '
                    f'{_node_phrase(s_kids[1])} with the coordinator {_node_phrase(cc_child)}.')
        # Clause with fronted adverbial/subordinate clause (S -> AdvP/PP/S'/S-bar + S)
        if len(children) == 2 and child_labels[0] in {'AdvP', 'PP', "S'", 'S-bar', 'S″', 'S-dbar'} and child_labels[1] == 'S':
            return (f'{surface} places the fronted modifier {_node_phrase(children[0])} before the '
                    f'main clause {_node_phrase(children[1])}.')
        # Standard declarative or embedded subject + predicate clause (S -> NP VP ...)
        if len(children) >= 2 and child_labels[0] == 'NP' and child_labels[1] == 'VP':
            subject, predicate = children[0], children[1]
            embedded = bool(parent and parent.get('label') in {'S-bar', "S'", 'S″', 'S-dbar', 'PP'})
            if not subject.get('surface'):
                subj_desc = 'an understood (unspoken) subject'
            else:
                subj_desc = f'the subject {_node_phrase(subject)}'
            role = ' This clause is embedded inside a larger structure.' if embedded else ''
            extra = f' It also includes {_node_phrase(children[2])}.' if len(children) > 2 and children[2].get('surface') else ''
            if subject.get('surface') and predicate.get('surface'):
                return (f'{_node_phrase(subject)} is the subject of this clause, and '
                        f'{_node_phrase(predicate)} is its predicate.{extra}{role}')
            if predicate.get('surface'):
                return f'This clause pairs {subj_desc} with the predicate {_node_phrase(predicate)}.{extra}{role}'
        # Inverted question clause (S -> AUX/MOD/PERF/PROG/PASS/TENSE + NP + VP)
        if len(children) >= 2 and child_labels[0] in {'MOD', 'PERF', 'PROG', 'PASS', 'TENSE', 'AUX', 'V'} and child_labels[1] == 'NP':
            rest = f' before the predicate {_node_phrase(children[2])}' if len(children) > 2 and children[2].get('surface') else ''
            return (f'{surface} is an inverted clause with the fronted auxiliary {_node_phrase(children[0])} '
                    f'before the subject {_node_phrase(children[1])}{rest}.')
    if label in {"S'", 'S-bar'}:
        c1 = next((c for c in children if c.get('label') in {'C', 'C1'}), None)
        body = next((c for c in children if c.get('label') in {'S', "S'", 'VP'}), None)
        if c1 and body and body.get('surface'):
            if c1.get('surface'):
                intro = f'introduced by the complementiser {_node_phrase(c1)}'
            else:
                intro = 'with an empty complementiser position'
            p_lbl = parent.get('label') if parent else None
            fn = ('modifying a noun' if p_lbl in {'NOM', 'NP'}
                  else 'completing a verb or adjective' if p_lbl in {'VP', 'AP'}
                  else 'attached as a subordinate clause' if p_lbl in {'S', 'S″', 'S-dbar'}
                  else 'functioning as a subordinate clause')
            return f'{surface} is a subordinate clause {intro}, containing {_node_phrase(body)} and {fn}.'
    if label in {'S″', "S''", 'S-dbar'}:
        c2 = next((c for c in children if c.get('label') == 'C2'), None)
        body = next((c for c in children if c.get('label') in {"S'", 'S-bar', 'S'}), None)
        if c2 and body and body.get('surface'):
            p_lbl = parent.get('label') if parent else None
            if p_lbl in {'NOM', 'NP'}:
                if c2.get('surface'):
                    return f'{surface} is a relative clause introduced by {_node_phrase(c2)} and describing the preceding noun.'
                return f'{surface} is a contact relative clause (with an omitted relative pronoun) describing the preceding noun.'
            if c2.get('surface'):
                return f'{surface} fronts the wh-phrase {_node_phrase(c2)} before {_node_phrase(body)}.'

    # --- 2. Word-level & single-token lexical-category explanations ---------- #
    if node['kind'] == 'word' and leaf.get('fdep') == 'neg' and leaf['surface'].lower() in {'not', "n't", 'n’t'}:
        gov = leaves.get(leaf.get('fhead'))
        extra = f' negating {_quote(gov["surface"])}' if gov and gov['surface'] != leaf['surface'] else ''
        return f'{surface} is a negation marker{extra} within the verb phrase.'
    if len(ids) == 1 and label == 'N' and leaf.get('type') == leaf.get('ftag'):
        form = {'NN': 'singular', 'NNS': 'plural'}.get(leaf['type'])
        if form:
            containing = _first_ancestor(node, by_id, {'NP'})
            dep_role = _dep_role_phrase(leaf, leaves)
            role = f' It heads {_node_phrase(containing)}' if containing and containing['surface'] != node['surface'] else ' It functions'
            if dep_role:
                return f'{surface} is a {form} noun.{role} and serves as {dep_role}.'
            if containing and containing['surface'] != node['surface']:
                return f'{surface} is a {form} noun. It is the noun in {_node_phrase(containing)}.'
            return f'{surface} is a {form} noun.'
    if len(ids) == 1 and label in {'name', 'NAME'}:
        dep_role = _dep_role_phrase(leaf, leaves)
        num = 'plural' if leaf.get('type') == 'NNPS' else 'singular'
        role = f' It serves as {dep_role}.' if dep_role else ' It refers to a specific person, place, or entity.'
        return f'{surface} is a {num} proper name.{role}'
    if len(ids) == 1 and label == 'V' and leaf.get('type') == leaf.get('ftag'):
        form = {'VBZ': 'a finite third-person singular present-tense form',
                'VBP': 'a finite present-tense form',
                'VBD': 'a finite past-tense form',
                'VBG': 'a non-finite -ing participle form',
                'VBN': 'a non-finite past-participle form',
                'VB': 'a plain (base) verb form'}.get(leaf['type'])
        marked = next((by_id[key] for key in [node['node_id'], *node['ancestor_ids']]
                       if by_id[key].get('label') == 'V'), None)
        from ruleset import PAST_ONLY
        if leaf['type'] == 'VBN' and leaf['surface'].lower() in PAST_ONLY:
            form = None
        feats = set(marked.get('features', [])) if marked else set()
        valency = (
            'takes two objects (ditransitive)' if 'ditrans' in feats
            else 'links the subject to a predicative complement (intensive)' if 'intens' in feats
            else 'takes an object and a predicative complement (complex transitive)' if 'complex' in feats
            else 'selects a prepositional complement' if 'prep' in feats
            else 'takes a direct object (transitive)' if 'trans' in feats
            else 'has no direct object (intransitive)' if 'intrans' in feats
            else None
        )
        if form and node.get('label') != 'V':
            return (f'{surface} is {form} of the lexical verb in this phrase'
                    + (f', where it {valency}.' if valency else '.'))
        if form and valency:
            return f'{surface} heads this verb phrase and {valency} in this analysis. It is {form}.'
        if form:
            return f'{surface} is the lexical verb heading this verb phrase. It is {form}.'
    if len(ids) == 1 and label in {'MOD', 'PERF', 'PROG', 'PASS', 'TENSE', 'AUX', 'TO'}:
        aux_role = {
            'MOD': ('a modal auxiliary', 'the plain (base) form of the following verb'),
            'PERF': ('the perfect auxiliary', 'a past participle'),
            'PROG': ('the progressive auxiliary', 'an -ing participle'),
            'PASS': ('the passive auxiliary', 'a past participle'),
            'TENSE': ('a tense-carrying auxiliary (do-support)', 'the plain (base) form of the following verb'),
            'AUX': ('an auxiliary verb', 'the form of the following verb'),
            'TO': ('the infinitival marker', 'a plain (base) verb phrase'),
        }[label]
        gov = leaves.get(leaf.get('fhead'))
        target_v = f' supporting {_quote(gov["surface"])}' if gov and gov['surface'] != leaf['surface'] else ''
        tense_txt = {'VBD': ' (past tense)', 'VBZ': ' (3rd-person singular present)', 'VBP': ' (present tense)'}.get(leaf.get('type'), '')
        return f'{surface} is {aux_role[0]}{tense_txt}{target_v}; it selects {aux_role[1]}.'
    if len(ids) == 1 and label in {'pronoun', 'PRON', 'PRO'}:
        morph = leaf.get('fmorph') or {}
        case = {'Nom': 'subject', 'Acc': 'object'}.get(morph.get('Case'))
        role = {'nsubj': 'subject', 'nsubjpass': 'subject', 'dobj': 'object',
                'iobj': 'object', 'pobj': 'object'}.get(leaf.get('fdep'))
        dep_role = _dep_role_phrase(leaf, leaves)
        if case and role == case and leaf.get('type') == leaf.get('ftag') == 'PRP':
            tail = f' It serves as {dep_role}.' if dep_role else f' It serves as the {role} here.'
            return f'{surface} is a pronoun in the {case} form.{tail}'
        if leaf['surface'].lower().endswith(('self', 'selves')):
            tail = f' It serves as {dep_role}.' if dep_role else ''
            return f'{surface} is a reflexive pronoun referring back to an earlier antecedent in the clause.{tail}'
        if leaf['surface'].lower() in {'it', 'they', 'you', 'them', 'we', 'us', 'he', 'him', 'she', 'her', 'i', 'me'}:
            tail = f' It serves as {dep_role}.' if dep_role else ' Its referent depends on the wider context.'
            return f'{surface} is a personal pronoun.{tail}'
    if len(ids) == 1 and label in {'P', 'Prt', 'PART'}:
        dep_role = _dep_role_phrase(leaf, leaves)
        pp_anc = _first_ancestor(node, by_id, {'PP'})
        if label == 'P' and pp_anc and pp_anc.get('surface') != node.get('surface'):
            return f'{surface} is the preposition heading {_node_phrase(pp_anc)}' + (f', acting as {dep_role}.' if dep_role else '.')
        if dep_role:
            return f'{surface} is a {NAMES.get(label, "word")} serving as {dep_role}.'
    if len(ids) == 1 and label in {'A', 'Adv', 'DEG', 'Q', 'QA', 'PRE-DET', 'POSS', 'V-part'}:
        morph_desc = _word_morphology_summary(leaf)
        dep_role = _dep_role_phrase(leaf, leaves)
        if morph_desc and dep_role:
            return f'{surface} is {morph_desc} serving as {dep_role}.'
        if morph_desc:
            ctx = _phrase_context(node, by_id)
            return f'{surface} is {morph_desc}' + (f' inside {ctx}.' if ctx else '.')
    if len(ids) == 1 and label in {'C', 'C1', 'C2', 'CC', 'CONJ'}:
        cl_ctx = _clause_context(node, by_id)
        if label in {'C', 'C1'}:
            return f'{surface} is a complementiser (clause introducer) marking the subordinate clause {cl_ctx or "here"}.'
        if label == 'C2':
            p_anc = _first_ancestor(node, by_id, {'S″', "S''", 'S-dbar'})
            p_par = by_id.get(p_anc.get('parent_id')) if p_anc else None
            if p_par and p_par.get('label') in {'NOM', 'NP'}:
                return f'{surface} is a relative pronoun introducing the relative clause {cl_ctx or "here"} and linking it to the noun.'
            return f'{surface} is a fronted wh-word introducing {cl_ctx or "this clause"}.'
        if leaf.get('type') == 'CC':
            return f'{surface} is a coordinating conjunction linking parallel constituents in {cl_ctx or "this sentence"}.'

    # --- 3. Phrase-level explanations (NP, NOM, VP, PP, AP, AdvP, PartP) ----- #
    if label in {'NP', 'NOM', 'ART', 'DET', 'DEM', 'AP', 'AdvP', 'PP', 'VP', 'PartP'}:
        matching = set(ids)
        heads = [leaves[i] for i in ids if i in leaves and (
            leaves[i].get('fdep') == 'ROOT' or leaves[i].get('fhead') not in matching)]
        head = heads[0] if len(heads) == 1 else None
        if label in {'NP', 'NOM'} and head and head.get('type') in {'NN', 'NNS', 'NNP', 'NNPS', 'PRP'}:
            head_text = _quote(head['surface'])
            if label == 'NOM' and node['surface'] != head['surface']:
                mod_kids = [c for c in children if c.get('label') in {'AP', 'PP', 'S″', "S''", 'S-dbar', "S'", 'S-bar', 'PartP'} and c.get('surface')]
                if mod_kids:
                    return f'{surface} is the nominal headed by {head_text}, modified by {_node_phrase(mod_kids[0])}.'
                return f'{surface} is the nominal headed by {head_text}. Its other words help narrow its reference.'
            if label == 'NP' and parent:
                dep = head.get('fdep')
                ancestor_tokens = graph['source_tokens'].get(parent['node_id'], [])
                governor = leaves.get(head.get('fhead'))
                if governor and head['fhead'] in ancestor_tokens:
                    role = {('S', 'nsubj'): 'subject', ('S', 'nsubjpass'): 'passive subject',
                            ('VP', 'dobj'): 'direct object', ('VP', 'iobj'): 'indirect object',
                            ('VP', 'attr'): 'predicative complement',
                            ('PP', 'pobj'): 'complement'}.get((parent.get('label'), dep))
                    if role:
                        start = f'{surface} is a noun phrase serving as the {role} of {_quote(governor["surface"])}.'
                        if head['surface'] != node['surface']:
                            start += f' The noun {head_text} heads this phrase.'
                        return start
        if label in {'ART', 'DET', 'DEM'} and len(ids) == 1 and leaf.get('fdep') == 'det':
            noun = leaves.get(leaf.get('fhead'))
            phrase = _first_ancestor(node, by_id, {'NP'})
            if (noun and phrase and leaf['fhead'] in graph['source_tokens'].get(phrase['node_id'], [])
                    and noun.get('type') in {'NN', 'NNS', 'NNP', 'NNPS'}):
                if node['kind'] == 'word' and label == 'ART':
                    kind_art = 'the definite article' if leaf['surface'].lower() == 'the' else 'an indefinite article'
                    return f'{surface} is {kind_art} that helps specify the reference of {_quote(noun["surface"])}.'
                return f'{surface} is the {NAMES[label]} for {_quote(noun["surface"])} within {_node_phrase(phrase)}.'
        if label == 'PP':
            if (len(children) == 2 and [child['label'] for child in children] == ['P', 'NP']
                    and children[0]['surface'] and children[1]['surface']):
                p_role = ''
                if parent and parent.get('label') in {'NOM', 'NP'}:
                    p_role = ' It postmodifies the preceding noun.'
                elif parent and parent.get('label') in {'VP', 'S'}:
                    p_role = ' It functions as an adverbial or complement in the clause.'
                return (f'{surface} is a preposition phrase headed by the preposition {_node_phrase(children[0])}. '
                        f'The noun phrase {_node_phrase(children[1])} is its complement.{p_role}')
        if label in {'AP', 'AdvP'} and head and head.get('type') in {'JJ', 'JJR', 'JJS', 'RB', 'RBR', 'RBS'}:
            governor = leaves.get(head.get('fhead'))
            if governor and parent and head['fhead'] in graph['source_tokens'].get(parent['node_id'], []):
                if head.get('fdep') in {'amod', 'advmod'}:
                    return f'{surface} is an {NAMES[label]} headed by {_quote(head["surface"])}, modifying {_quote(governor["surface"])}.'
                if head.get('fdep') == 'acomp' and parent.get('label') == 'VP':
                    return f'{surface} is an adjective phrase headed by {_quote(head["surface"])}, serving as the predicative complement of {_quote(governor["surface"])}.'
        if label == 'VP':
            # (a) Auxiliary + inner VP
            auxiliary = next((c for c in children if c.get('label') in {'MOD', 'PERF', 'PROG', 'PASS', 'TENSE', 'TO'}), None)
            complement = next((c for c in children if c.get('label') == 'VP' and c['surface']), None)
            if auxiliary and auxiliary['surface'] and complement:
                form = {'MOD': 'the plain form', 'PERF': 'a past participle', 'PROG': 'an -ing form',
                        'PASS': 'a past participle', 'TENSE': 'the plain form', 'TO': 'the plain form'}.get(auxiliary['label'])
                return (f'{surface} is a verb phrase combining {_node_phrase(auxiliary)} with '
                        f'{_node_phrase(complement)}. In this construction, {_node_phrase(auxiliary)} selects {form}.')
            # (b) Coordinated VP (VP -> VP CC VP)
            vp_kids = [c for c in children if c.get('label') == 'VP' and c.get('surface')]
            cc_kid = next((c for c in children if c.get('kind') == 'word' and c.get('surface', '').lower() in {'and', 'but', 'or'}), None)
            if cc_kid and len(vp_kids) >= 2:
                return f'{surface} coordinates the verb phrases {_node_phrase(vp_kids[0])} and {_node_phrase(vp_kids[1])} with {_node_phrase(cc_kid)}.'
            # (c) Adjunct-modified VP (VP -> VP + PP/AdvP/S')
            if len(vp_kids) == 1 and len(children) == 2:
                adj = next((c for c in children if c is not vp_kids[0] and c.get('surface')), None)
                if adj:
                    return (f'{surface} expands the core verb phrase {_node_phrase(vp_kids[0])} '
                            f'with the adverbial modifier {_node_phrase(adj)}.')
            # (d) Lexical VP (V + complements)
            v_kid = next((c for c in children if c.get('label') == 'V' and c.get('surface')), None)
            if v_kid:
                comps = [c for c in children if c is not v_kid and c.get('surface')]
                feats = set(v_kid.get('features', []))
                if comps:
                    comp_list = ' and '.join(_node_phrase(c) for c in comps[:2])
                    comp_kind = (
                        'predicative complement' if 'intens' in feats
                        else 'indirect and direct objects' if 'ditrans' in feats and len(comps) >= 2
                        else 'object and predicative complement' if 'complex' in feats and len(comps) >= 2
                        else 'prepositional complement' if 'prep' in feats
                        else 'complement'
                    )
                    return f'{surface} is a verb phrase headed by {_node_phrase(v_kid)}, with {comp_list} as its {comp_kind}.'
                return f'{surface} is an intransitive verb phrase headed by {_node_phrase(v_kid)} with no direct object.'
        if label == 'PartP':
            p_role = f' modifying {_node_phrase(parent)}' if parent and parent.get('surface') and parent.get('surface') != node.get('surface') else ''
            return f'{surface} is a participial phrase{p_role}.'
    return basic


def build_learner_analysis(analysis, br_analysis, explanation, findings, relationships, leaves, summary):
    """Prepare the existing learner explanations once for the browser session."""
    resolved = br_analysis.get('status') == 'normalized' and br_analysis.get('tree')
    graph = explanation.get('fact_graph')
    if not graph and br_analysis.get('working_tree'):
        from xai_facts import build_fact_graph
        graph = build_fact_graph({'status': 'working', 'tree': br_analysis['working_tree']})
    result = {'version': 1, 'tree_status': 'canonical' if resolved else 'unavailable',
              'findings': findings, 'nodes': {}, 'relationships': relationships,
              'sentence_text': (explanation.get('learner_explanation') or {}).get('text'),
              'verdict': summary.get('verdict')}
    correction = summary.get('correction')
    if correction and correction.get('validated'):
        offset = analysis['sentences'][analysis['sentence_index']]['start']
        witnessed = {i for row in findings if row['target_token_ids'] for i in
                     row['target_token_ids'] + row['related_token_ids']}
        tokens = analysis['tokens']
        if correction.get('edits') and all(any(
                token['i'] in witnessed and token['start'] - offset <= edit['start']
                < token['end'] - offset for token in tokens) for edit in correction['edits']):
            result['revision'] = {'text': correction['corrected_sentence'],
                                  'impact': correction.get('impact', {}),
                                  'conditional_simple_past': all(
                                      edit.get('constraint') == 'C-BE-PAST' for edit in correction['edits'])}
    if not graph or not graph.get('nodes'):
        return result
    by_id = {node['node_id']: node for node in graph['nodes']}
    source_tokens = _source_tokens_by_node(graph, analysis)
    graph = {**graph, 'source_tokens': source_tokens}
    result['tree_status'] = 'provisional' if graph['status'] == 'provisional' else 'canonical'
    for node in graph['nodes']:
        ident = node['node_id']
        ids = source_tokens[ident]
        covered = set(ids)
        related = [row for row in findings if covered.intersection(
            row['target_token_ids'] + row['related_token_ids']) or (
                node['parent_id'] is None and not row['target_token_ids'] and not row['related_token_ids'])]
        # A branch with an overt descendant may discuss that descendant's
        # finding, but only an exact word (or its one-word category) is marked.
        exact = len(ids) == 1 and len(node['token_ids']) == 1 and node['kind'] in {'word', 'branch'}
        if exact and node['kind'] == 'branch':
            exact = len(node['child_ids']) == 1 and by_id[node['child_ids'][0]]['kind'] == 'word'
        observed = []
        seen_rel = set()
        for row in relationships:
            if row['matches'] and covered.intersection(row['participants']):
                if row['text'] not in seen_rel:
                    seen_rel.add(row['text'])
                    observed.append(row['text'])
        result['nodes'][ident] = {
            'text': _runtime_description(node, graph, by_id, ids, leaves),
            'findings': [row['id'] for row in related],
            'relationship': observed[0] if observed else None,
            'relationships': observed[:3],
            'error': exact and any(ids[0] in row['target_token_ids'] for row in related),
            'related': exact and any(ids[0] in row['related_token_ids'] for row in related),
        }
        if node['parent_id'] is None and resolved:
            result['sentence_text'] = result['nodes'][ident]['text']
    return result
