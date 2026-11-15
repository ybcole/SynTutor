"""Sentence-awareness policy for learner explanations.

The explanation may quote the sentence/clause context only when the node's role
depends on it (clause layers, verbs/auxiliaries, movement). A local word or
phrase must not quote the whole sentence, and a word must never fall back to
"same as the enclosing phrase".
"""

import unittest

from api import build_payload
from explanations import explain_analysis
from learner_explanations import compose_learner_explanation

SENTENCE_LEVEL = {"V", "AUX", "MOD", "TENSE", "C1", "C2", "PERF", "PROG",
                  "PASS", "C"}
LEXICAL = {"N", "V", "A", "Adv", "P", "PRO", "PRON", "pronoun", "ART", "NAME",
           "name", "DEG", "Q", "QA", "POSS", "DEM", "V-part", "PRE-DET",
           "PART", "Prt", "NEG", "MOD", "PERF", "PROG", "PASS", "AUX",
           "TENSE", "DET", "C", "C1", "C2"}
SELF_REFERENCE = ("larger expression", "is part of", "is a part of",
                  "part of the larger", "position in", "built around",
                  "beginning with", "preposition phrase", "verb phrase")


def _quote(value):
    clean = " ".join(value.split())
    if len(clean) > 110:
        clean = clean[:107].rsplit(" ", 1)[0] + "..."
    return f"\u201c{clean}\u201d"


def _graph(sentence):
    payload = build_payload(sentence)
    evidence = explain_analysis({**payload["br_analysis"], "sentence": sentence})
    graph = evidence.get("fact_graph")
    by_id = {node["node_id"]: node for node in graph["nodes"]}
    return graph, by_id


def _text(graph, node_id):
    return compose_learner_explanation(graph, node_id=node_id)["text"]


def _lexical_label(node, by_id):
    for ancestor_id in node.get("ancestor_ids") or []:
        ancestor = by_id.get(ancestor_id)
        if ancestor and ancestor.get("label") in LEXICAL:
            return ancestor.get("label")
    return None


class SentenceAwarenessTests(unittest.TestCase):
    SENTENCES = (
        "The clever boy reads a book.",
        "Who did the administrator say that submitted the application before the deadline?",
        "He gave to charity all the money she had left him.",
        "The woman whose car was stolen called the police.",
        "The committee which met yesterday approved the plan.",
    )

    def test_explanations_use_only_necessary_context(self):
        for sentence in self.SENTENCES:
            with self.subTest(sentence=sentence):
                graph, by_id = _graph(sentence)
                texts = {node["node_id"]: _text(graph, node["node_id"])
                         for node in graph["nodes"]}
                full = _quote(sentence)
                for node in graph["nodes"]:
                    text = texts[node["node_id"]]
                    surface = str(node.get("surface") or "").strip()
                    for phrase in SELF_REFERENCE:
                        self.assertNotIn(f"{phrase}\u201c{surface}\u201d", text)
                    if node.get("kind") == "word":
                        label = _lexical_label(node, by_id)
                        parent = by_id.get(node.get("parent_id"))
                        if parent:
                            self.assertNotEqual(
                                text, texts[parent["node_id"]],
                                "a word must keep its own explanation")
                        if label not in SENTENCE_LEVEL and surface != sentence.strip():
                            self.assertNotIn(
                                full, text,
                                "a local word must not quote the whole sentence")

    def test_determiner_uses_its_local_noun_phrase(self):
        graph, by_id = _graph("The clever boy reads a book.")
        determiner = next(
            node for node in graph["nodes"]
            if node.get("kind") == "word"
            and node.get("surface", "").lower() == "the")
        text = _text(graph, determiner["node_id"])
        self.assertIn("clever boy", text.lower())
        self.assertNotIn(_quote("The clever boy reads a book."), text)

    def test_pronoun_does_not_quote_the_whole_clause(self):
        sentence = "He gave to charity all the money she had left him."
        graph, _ = _graph(sentence)
        pronoun = next(
            node for node in graph["nodes"]
            if node.get("kind") == "word"
            and node.get("surface", "").lower() == "he")
        text = _text(graph, pronoun["node_id"])
        self.assertIn("pronoun", text)
        self.assertNotIn(_quote(sentence), text)


if __name__ == "__main__":
    unittest.main()
