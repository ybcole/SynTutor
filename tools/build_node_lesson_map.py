#!/usr/bin/env python3
"""Build separate syntax-node and word-node lesson maps.

Syntax nodes point at the Burton-Roberts syntax sequence (plus a few Cambridge
syntax sections where that sequence has no direct chapter). Word nodes point at
the Cambridge word-class chapters. The maps are intentionally separate.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUTHORED = ROOT / "web/content/lessons/cambridge-authored"
COURSE = ROOT / "web/content/lessons/course.json"
OUT_JS = ROOT / "web/js/node-lessons.js"
OUT_MD = ROOT / "docs/lessons/NODE_LESSON_MAP.md"

# alias group, B-R chapter, why the lesson is directly about the syntax node
SYNTAX_ROWS = [
    (("S", "Sentence", "CLAUSE", "Clause"), "br-02", "concepts", "Subject, predicate, noun phrases and verb phrases", "Subject/predicate split under S and the basic S → NP VP pattern."),
    (("Phrase", "PHRASE", "ROOT"), "br-01", "worked-example", "Phrases, constituents and phrase markers", "Constituent structure and phrase-marker hierarchy."),
    (("NP", "NOM", "N"), "br-07", "worked-example", "Determiner and nominal tree exercise", "The NP → DET NOM → N core structure."),
    (("name", "pronoun"), "br-07", "application", "Pronoun modification and ellipted heads", "Names and pronouns as NP types."),
    (("VP",), "br-04", "introduction", "Introduction to the basic verb phrase", "The basic verb phrase as a headed construction."),
    (("V",), "br-04", "concepts", "Lexical verbs, complements, transitive and intransitive verbs", "Lexical verbs and their complement patterns."),
    (("AP", "A", "DEG"), "br-03", "worked-example", "Adjectives, adverbs, APs and AdvPs", "AP, adjective head A and degree phrase DEG."),
    (("Adv", "AdvP"), "br-03", "worked-example", "Adjectives, adverbs, APs and AdvPs", "Adverb and adverb-phrase categories."),
    (("PP", "P"), "br-03", "prepositions-and-coordination", "Prepositions, prepositional phrases and coordination", "Preposition heads and PP structure."),
    (("AUX", "MOD", "TENSE"), "br-06", "concepts", "Part I: Tense, time, lexical verbs and modals", "Auxiliaries, modals and tense."),
    (("PERF", "PROG", "PASS", "PartP", "V-part"), "br-06", "chain", "Perfect have, progressive be and passive be", "Perfect, progressive and passive auxiliaries."),
    (("DET", "ART", "DEM", "Q", "POSS", "PRE-DET", "QA"), "br-07", "concepts", "Determiners and pre-determiners", "Determiners, demonstratives and quantifiers."),
    (("S-bar", "C"), "br-08", "worked-example", "Complementiser and clause structure (C and S)", "Complementiser C and the S-bar/S relation."),
    (("S-dbar",), "br-09", "concepts", "Main wh-questions and fronting", "Wh-fronting and typed gaps."),
    (("C1", "C2"), "br-10", "subjects-and-control", "Non-finite complementisers and fronted wh-phrases (C1 and C2)", "C1 and C2 positions."),
    (("E",), "br-05", "ellipsis", "Ellipsis and understood complements", "Empty and understood positions."),
    (("TO",), "br-10", "worked-example", "To-infinitive verb phrase exercise", "Infinitival to as a non-finite auxiliary."),
    (("V(I)", "V(II)"), "br-10", "verb-complements", "Non-finite verb complements and Type I and Type II verbs", "Type I and Type II non-finite verb complements."),
    (("trans", "intrans"), "br-04", "concepts", "Lexical verbs, complements, transitive and intransitive verbs", "Transitive and intransitive verb complements."),
    (("ditrans",), "br-04", "worked-example", "Ditransitive verbs", "Ditransitive verb patterns."),
    (("intens", "complex"), "br-04", "predicatives", "Intensive and complex transitive verbs", "Intensive and complex transitive verb patterns."),
    (("prep",), "br-04", "prepositional-complements", "Prepositional verbs and PP complements", "Prepositional complements."),
    (("phrasal", "Prt"), "br-05", "particles", "Phrasal verbs and ellipsis", "Particles and phrasal verbs."),
    (("pres", "past", "-tense"), "br-06", "concepts", "Part I: Tense, time, lexical verbs and modals", "Tense features on auxiliaries and finite verbs."),
    (("CC", "CONJP", "UCP"), "br-03", "prepositions-and-coordination", "Prepositions, prepositional phrases and coordination", "Coordination."),
    (("SQ", "SBARQ"), "br-09", "concepts", "Main wh-questions and fronting", "Wh-question clause structure."),
    (("SINV",), "br-09", "concepts", "Main wh-questions and fronting", "Fronting and inversion in questions."),
    (("FRAG", "INTJ"), "br-01", "concepts", "Structure and constituent tests", "Clause-like fragments and structural constituents."),
    (("NEGATION",), "br-06", "negation", "Negation and auxiliary do", "Negation with auxiliaries."),
    (("WORD",), "br-01", "worked-example", "Phrases, constituents and phrase markers", "Words as the minimal units in the phrase hierarchy."),
]

# alias group, Cambridge chapter, Cambridge section, direct word-class reason
WORD_ROWS = [
    (("NN", "NNS", "NOUN", "N"), 5, "nouns-nps", "Common nouns and noun-headed phrases."),
    (("NNP", "NNPS", "name"), 5, "proper-names", "Proper names and proper nouns."),
    (("PRP", "PRP$", "pronoun"), 5, "pronouns", "Pronouns and pronoun-headed NPs."),
    (("DT", "DET", "ART", "DEM", "POSS", "PRE-DET", "QA"), 5, "determiner", "Determiner function and determinatives."),
    (("Q", "CD"), 5, "quantification", "Quantifiers, numerals and quantification."),
    (("POS",), 5, "genitives", "The possessive ending and genitives."),
    (("JJ", "ADJ", "A"), 6, "criterial-properties", "Adjective category membership."),
    (("JJR", "JJS"), 13, "comparison-preliminaries", "Comparative and superlative adjective grade."),
    (("RB", "ADVERB", "Adv"), 6, "adverbs", "Adverb category membership and morphology."),
    (("RBR", "RBS"), 13, "scalar-inequality", "Comparative and superlative adverb grade."),
    (("VB", "VBD", "VBG", "VBN", "VBP", "VBZ", "VERB", "V"), 3, "verb-phrase", "The verb phrase and verb-headed structure."),
    (("MD", "MOD"), 3, "modal-auxiliaries", "Modal auxiliaries and modal meanings."),
    (("AUX",), 3, "auxiliaries", "Auxiliary verb syntax."),
    (("TO",), 14, "infinitival-structure", "The infinitival marker to."),
    (("IN", "P", "PREPOSITION"), 7, "prepositions-heads", "Prepositions as heads."),
    (("CC",), 15, "coordination-overview", "Coordination and coordinators."),
    (("RP", "Prt"), 4, "particles-idioms", "Particles and verb-particle constructions."),
    ((".", "?", "!"), 20, "primary-terminals", "Primary sentence terminals."),
    ((",", ";", ":"), 20, "secondary-boundaries", "Secondary boundary marks."),
    (("``", "''", "QUOTATION"), 20, "quotation", "Quotation marks."),
    (("(", ")"), 20, "parentheses-dash", "Parentheses and the dash."),
    (("-", "HYPHEN"), 20, "word-level", "Hyphens and word-level punctuation."),
    (("'", "APOSTROPHE"), 20, "apostrophe-slash", "The apostrophe."),
]

course = json.loads(COURSE.read_text(encoding="utf-8"))
br_titles = {l["lesson_id"]: l["title"] for l in course["lessons"] if l["lesson_id"].startswith("br-")}
chapters = {}
for n in range(1, 21):
    data = json.loads((AUTHORED / f"ch{n:02d}.json").read_text(encoding="utf-8"))
    chapters[n] = (data["title"], {s["id"]: s["title"] for s in data["sections"]})

def br_id(chapter: int) -> str:
    return f"br-{chapter:02d}"

def cg_id(chapter: int) -> str:
    return "cgel-clauses" if chapter == 2 else f"cgel-ch{chapter:02d}"

syntax_entries = []
for aliases, lesson, section, section_title, why in SYNTAX_ROWS:
    route = f"#lesson/{lesson}/{section}"
    chapter_title = br_titles[lesson]
    for alias in aliases:
        syntax_entries.append({
            "label": alias, "lesson": lesson, "section": section, "route": route,
            "chapterTitle": chapter_title, "sectionTitle": section_title,
            "why": why, "kind": "syntax",
        })

word_entries = []
for aliases, chapter, section, why in WORD_ROWS:
    chapter_title, sections = chapters[chapter]
    route = f"#lesson/{cg_id(chapter)}/{section}"
    for alias in aliases:
        word_entries.append({
            "label": alias, "lesson": cg_id(chapter), "section": section, "route": route,
            "chapterTitle": chapter_title, "sectionTitle": sections[section],
            "why": why, "kind": "word",
        })

js = [
    "// Generated by tools/build_node_lesson_map.py. Do not edit by hand.",
    "export const SYNTAX_NODE_LESSONS = {",
]
for e in syntax_entries:
    js.append("  " + json.dumps(e["label"]) + ": " + json.dumps({k: v for k, v in e.items()}, ensure_ascii=False) + ",")
js += ["};", "", "export const WORD_NODE_LESSONS = {"]
for e in word_entries:
    js.append("  " + json.dumps(e["label"]) + ": " + json.dumps({k: v for k, v in e.items()}, ensure_ascii=False) + ",")
js += [
    "};", "",
    "export function nodeLesson(type, kind = 'auto') {",
    "  if (type == null) return null;",
    "  const key = String(type);",
    "  if (kind === 'word') return WORD_NODE_LESSONS[key] || WORD_NODE_LESSONS[key.toUpperCase()] || null;",
    "  if (kind === 'syntax') return SYNTAX_NODE_LESSONS[key] || SYNTAX_NODE_LESSONS[key.toUpperCase()] || null;",
    "  return WORD_NODE_LESSONS[key] || SYNTAX_NODE_LESSONS[key]",
    "    || WORD_NODE_LESSONS[key.toUpperCase()] || SYNTAX_NODE_LESSONS[key.toUpperCase()] || null;",
    "}", "",
    "export function nodeLessonRoute(type, kind = 'auto') {",
    "  return nodeLesson(type, kind)?.route || null;",
    "}", "",
]
OUT_JS.write_text("\n".join(js), encoding="utf-8")

lines = [
    "# Node → Lesson Map",
    "",
    "Generated by `tools/build_node_lesson_map.py` from the authored lesson data.",
    "",
    "## Syntax nodes → syntax lessons",
    "",
    "| Node / alias | Lesson route | Lesson / section | Why this section |",
    "| --- | --- | --- | --- |",
]
seen = set()
for e in syntax_entries:
    key = (e["route"], e["why"])
    if key in seen:
        continue
    seen.add(key)
    labels = [x["label"] for x in syntax_entries if x["route"] == e["route"] and x["why"] == e["why"]]
    lines.append(f"| {', '.join(f'`{x}`' for x in labels)} | `{e['route']}` | **{e['sectionTitle']}** — *{e['chapterTitle']}* | {e['why']} |")
lines += [
    "",
    "## Word nodes → Cambridge lessons",
    "",
    "| POS / alias | Lesson route | Lesson / section | Why this section |",
    "| --- | --- | --- | --- |",
]
for e in word_entries:
    lines.append(f"| `{e['label']}` | `{e['route']}` | **{e['chapterTitle']}** — *{e['sectionTitle']}* | {e['why']} |")
lines.append("")
OUT_MD.write_text("\n".join(lines), encoding="utf-8")
print(f"wrote {len(syntax_entries)} syntax aliases and {len(word_entries)} word aliases")
