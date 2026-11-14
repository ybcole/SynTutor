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
ARTICLES = {"the": "points to something identifiable in context",
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


def _larger_context(node: dict, by_id: dict[str, dict]) -> str | None:
    """Nearest enclosing phrase whose surface is not just this node's surface."""
    own = str(node.get("surface") or "").strip()
    labels = {"S", "S'", "S''", "S-bar", "S-dbar",
              "VP", "NP", "NOM", "PP", "AP", "AdvP"}
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
    raw_context = _larger_context(node, by_id)
    context = raw_context or "the sentence as a whole"
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
        if next_word and next_word.lower().endswith("ing"):
            return (f"{_quote(word)} is {form} form of the verb “be”. "
                    f"Here it combines with {_quote(next_word)} to describe an activity in progress.")
        if next_word and next_word.lower().endswith("ed") and kind in {"PASS", "AUX"}:
            return (f"{_quote(word)} is a form of “be.” "
                    f"Here it helps form the verb expression {context}.")
        return (f"{_quote(word)} is {form} form of the verb “be”. "
                f"In this sentence, it forms part of {context}.")

    if lower in HAVE and kind in {"V", "AUX", "PERF"}:
        form = "past-tense" if lower == "had" else "present-tense"
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
            return f"{surface} is the inner clause layer of this subordinate clause."
        if label in {"S-bar", "S'", "S''", "S-dbar"} and children:
            lead = (_node_phrase(children[0])
                    if str(children[0].get("surface") or "").strip()
                    else "the clause marker")
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
            context = _larger_context(node, by_id) or "this part of the sentence"
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
    if target["kind"] in {"gap", "empty", "elided_terminal"}:
        content = ("This position represents an understood or omitted part of the sentence, "
                   "rather than a word that is actually spoken.")
    elif target["kind"] == "word":
        content = _word(target, graph, by_id)
    else:
        content = _phrase(target, graph, by_id)
    if graph["status"] == "provisional":
        content = "In this possible reading, " + content[:1].lower() + content[1:]
    return {
        **result, "analysis_id": graph["analysis_id"], "selected_node_id": node_id,
        "status": "provisional" if graph["status"] == "provisional" else "observed",
        "text": content, "whole_sentence_certified": False,
    }
