"""Experimental bounded Burton-Roberts chart candidate generator.

Constructs fresh B-R tree candidates from lexical tags, NOT from Benepar's
selected constituency tree. This deliberately tiny grammar is source-inspired
and is NOT certified for unrestricted English. Never use it to judge grammar.
"""
from __future__ import annotations

import json

# Only explicit source-backed frames; a missing verb entry is unresolved.
FRAMES = {
    "sleep": "intrans", "walk": "intrans", "laugh": "intrans",
    "sigh": "intrans", "smile": "intrans", "dance": "intrans",
    "paddle": "intrans", "inspect": "trans", "admire": "trans",
    "spot": "trans", "dread": "trans",
}
FORMS = {
    "sleeps": "sleep", "slept": "sleep", "walks": "walk",
    "walked": "walk", "laughed": "laugh", "laughs": "laugh",
    "sighed": "sigh", "sighs": "sigh", "smiled": "smile",
    "smiles": "smile", "dances": "dance", "danced": "dance",
    "paddles": "paddle", "paddled": "paddle", "inspects": "inspect",
    "inspected": "inspect", "admires": "admire", "admired": "admire",
    "spots": "spot", "spotted": "spot", "dreads": "dread",
    "dreaded": "dread",
}
PREPS = {"in", "on", "at", "near", "beside", "under", "behind", "by", "with"}
DEICTIC = {"here", "there", "now", "then", "upstairs", "downstairs"}
ARTICLES = {"a", "an", "the"}
PRONOUNS = {"i", "he", "she", "we", "they", "you", "it", "him", "her", "us", "them"}
# Productive signatures, with no claim of semantic attachment verification.
BINARY = [
    ("NP", "DET", "NOM", "BR07-NP-DET-NOM"),
    ("NOM", "AP", "NOM", "BR07-NOM-AP"),
    ("PP", "P", "NP", "BR03-PP-NP"),
    ("VP", "V", "NP", "BR04-VP-TRANSITIVE"),
    ("VP", "VP", "PP", "BR05-VP-PP-ADJUNCT"),
    ("VP", "VP", "AdvP", "BR05-VP-ADVP-ADJUNCT"),
    ("S", "NP", "VP", "BR02-S-SUBJECT-PREDICATE"),
]
UNARY = [
    ("name", "NP", "BR03-NP-NAME"),
    ("pronoun", "NP", "BR03-NP-PRONOUN"),
    ("N", "NOM", "BR07-NOM-N"),
    ("ART", "DET", "BR07-DET-ART"),
    ("A", "AP", "BR03-AP-HEAD"),
    ("Adv", "AdvP", "BR03-ADVP-HEAD"),
]
MAX_TOKENS, MAX_STEPS, MAX_PER_CAT, MAX_OUTPUT = 24, 12000, 8, 5


def branch(label, *children, features=()):
    result = {"label": label, "children": list(children)}
    if features:
        result["features"] = list(features)
    return result


def lexical(token):
    word = token["text"]
    tag = str(token.get("parser_tag") or token.get("tag") or "").upper()
    low = word.lower()
    leaf = {"word": word}
    rows = []
    if tag in ("NNP", "NNPS"):
        rows.append((branch("name", leaf), ("BR03-NAME-TERMINAL",)))
    if tag == "PRP" and low in PRONOUNS:
        rows.append((branch("pronoun", leaf), ("BR03-PRONOUN-TERMINAL",)))
    if tag in ("NN", "NNS"):
        rows.append((branch("N", leaf), ("BR03-NOUN-TERMINAL",)))
    if tag == "DT" and low in ARTICLES:
        rows.append((branch("ART", leaf), ("BR07-ART-WORD",)))
    if tag in ("JJ", "JJR", "JJS"):
        rows.append((branch("A", leaf), ("BR03-ADJECTIVE-TERMINAL",)))
    if tag in ("RB", "RBR", "RBS"):
        rows.append((branch("Adv", leaf), ("BR03-ADVERB-TERMINAL",)))
    if (tag in ("IN", "TO") and low in PREPS) or low in DEICTIC:
        rows.append((branch("P", leaf), ("BR03-PREPOSITION-TERMINAL",)))
    if tag in ("VBD", "VBZ", "VBP"):
        lemma = str(token.get("lemma") or FORMS.get(low, low)).lower()
        if lemma in FRAMES:
            rows.append((branch("V", leaf, features=(FRAMES[lemma], "past" if tag == "VBD" else "pres")), ("BR04-V-TERMINAL",)))
    return rows


def generate_br_chart_candidates(tokens, max_results=MAX_OUTPUT):
    """Return candidate forest only; never return verified/normalized status."""
    if not isinstance(tokens, list) or not 1 <= len(tokens) <= MAX_TOKENS:
        return {"status": "unresolved", "reason": "UNSUPPORTED_INPUT_LENGTH", "candidates": []}
    if not all(isinstance(t, dict) and isinstance(t.get("text"), str)
               and t["text"].strip() for t in tokens):
        return {"status": "unresolved", "reason": "INVALID_TOKENS", "candidates": []}
    n = len(tokens)
    chart = {}
    steps = 0
    truncated = False

    def add(span, node, trace):
        nonlocal steps, truncated
        steps += 1
        if steps > MAX_STEPS:
            truncated = True
            return False
        dest = chart.setdefault(span, {}).setdefault(node["label"], [])
        encoded = json.dumps(node, sort_keys=True)
        if any(json.dumps(x[0], sort_keys=True) == encoded for x in dest):
            return False
        if len(dest) >= MAX_PER_CAT:
            truncated = True
            return False
        dest.append((node, trace))
        return True

    def unary(span):
        while not truncated:
            changed = False
            cells = chart.get(span, {})
            for old, new, rule in UNARY:
                for node, trace in list(cells.get(old, [])):
                    changed |= add(span, branch(new, node), trace + (rule,))
            for node, trace in list(cells.get("V", [])):
                if "intrans" in node.get("features", []):
                    changed |= add(span, branch("VP", node), trace + ("BR04-VP-INTRANSITIVE",))
            for node, trace in list(cells.get("P", [])):
                if node["children"][0]["word"].lower() in DEICTIC:
                    changed |= add(span, branch("PP", node), trace + ("BR03-PP-HEAD",))
            # The Third Edition uses an unfilled DET for bare plural NPs.
            if span[1] - span[0] == 1 and str(tokens[span[0]].get("parser_tag") or "").upper() == "NNS":
                for node, trace in list(cells.get("NOM", [])):
                    changed |= add(span, branch("NP", branch("DET"), node),
                                   trace + ("BR07-EMPTY-DET", "BR07-NP-DET-NOM"))
            if not changed:
                break

    for i, token in enumerate(tokens):
        for node, trace in lexical(token):
            add((i, i+1), node, trace)
        unary((i, i+1))

    for width in range(2, n+1):
        for i in range(n-width+1):
            j = i+width
            for k in range(i+1, j):
                for parent, left, right, rule in BINARY:
                    for a, at in list(chart.get((i, k), {}).get(left, [])):
                        for b, bt in list(chart.get((k, j), {}).get(right, [])):
                            if truncated:
                                break
                            if rule == "BR04-VP-TRANSITIVE" and "trans" not in a.get("features", []):
                                continue
                            add((i, j), branch(parent, a, b), at + bt + (rule,))
            unary((i, j))

    roots = chart.get((0, n), {}).get("S", [])
    return {
        "status": "candidate" if roots else "unresolved",
        "reason": None if roots else "NO_SOURCE_LICENCED_DERIVATION",
        "authority": "EXPERIMENTAL_NOT_INDEPENDENTLY_VERIFIED",
        "independent_linguistic_review": False,
        "semantic_conditions_checked": False,
        "may_certify_grammaticality": False,
        "truncated": truncated,
        "chart_steps": steps,
        "candidates": [
            {"root": node, "rule_ids": list(trace)}
            for node, trace in roots[:max(1, min(MAX_OUTPUT, max_results))]
        ],
    }
