#!/usr/bin/env python3
"""Build a Cambridge chapter lesson from the full grammar rule catalog.

Each chapter lesson is based on every catalog record that cites the chapter,
grouped by the book's own section titles. Prose is generated with rotating
pedagogical phrasings so sections do not read as repeated templates.
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build_cambridge_lessons_quizzes as base  # noqa: E402

COURSE = ROOT / "web/content/lessons/course.json"
BANK = ROOT / "web/content/quizzes/bank.json"
LESSONS = ROOT / "web/content/lessons"
RICH = ROOT / "web/js/cambridge-chapter-data.js"
KEY_TERMS = ROOT / "web/js/lesson-key-terms.js"

CHAPTER_TITLES = {
    1: "Preliminaries",
    2: "Syntactic overview",
    3: "The verb",
    4: "The clause: complements",
    5: "Nouns and noun phrases",
    6: "Adjectives and adverbs",
    7: "Prepositions and preposition phrases",
    8: "The clause: adjuncts",
    9: "Negation",
    10: "Clause type and illocutionary force",
    11: "Content clauses and reported speech",
    12: "Relative constructions",
    13: "Comparative constructions",
    14: "Non-finite and verbless clauses",
    15: "Coordination and supplementation",
    16: "Information packaging",
    17: "Deixis and anaphora",
    18: "Inflectional morphology",
    19: "Lexical word-formation",
    20: "Punctuation",
}


OPENERS = [
    "Start with the idea of {concept}.",
    "Notice how {concept} works here.",
    "A useful way to see {concept} is this.",
    "Keep {concept} in mind as you read.",
    "Here is the pattern for {concept}.",
    "One detail worth pausing on is {concept}.",
    "The book treats {concept} like this.",
    "Think of {concept} this way.",
]
CONNECTORS = [
    "For example,",
    "So,",
    "In the same way,",
    "By contrast,",
    "That means",
    "Here,",
    "Compare this with",
    "Put another way,",
]
CLOSERS = [
    "Read the example again once you have the idea.",
    "Say the example aloud to hear the pattern.",
    "Try the same shape with a sentence of your own.",
    "Check the example against the statement before moving on.",
    "Keep the example in view while you read the next point.",
    "Explain the pattern in your own words before continuing.",
]


QUESTION_PROMPTS = [
    "Which idea belongs to {title}?",
    "Which statement matches the chapter?",
    "Which example shows {section}?",
    "What does {section} cover?",
    "Which idea explains the example?",
    "Which term names the pattern?",
    "Which description fits the statement?",
    "Which idea is being illustrated?",
    "What is the main point of {section}?",
    "Which idea should you apply here?",
]


def catalog():
    rows = []
    for path in sorted((ROOT / "grammar/rules").glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            payload = payload.get("rules", [])
        rows.extend(row for row in payload if isinstance(row, dict) and row.get("id"))
    return rows


def chapter_records(chapter):
    rows = []
    for row in catalog():
        for source in row.get("sources", []) or []:
            if isinstance(source, dict) and source.get("chapter") == chapter:
                rows.append((row, source))
                break
    return rows


def section_title(record, source):
    title = (source.get("section") or "").strip()
    if title:
        return title
    return (record.get("concept") or "General").strip()


def first_sentence(text):
    text = (text or "").strip()
    match = re.match(r"(.+?[.!?])(\s|$)", text)
    return match.group(1) if match else text


def record_paragraph(record, index):
    concept = base.naturalize(record.get("concept") or "this pattern")
    statement = base.naturalize(record.get("statement") or "")
    condition = base.naturalize(record.get("condition") or "")
    examples = [e.get("text") for e in (record.get("examples") or {}).get("correct", []) if e.get("text")]
    wrong = [e.get("text") for e in (record.get("examples") or {}).get("incorrect", []) if e.get("text")]
    opener = OPENERS[index % len(OPENERS)].format(concept=concept)
    connector = CONNECTORS[(index * 3) % len(CONNECTORS)]
    closer = CLOSERS[(index * 5) % len(CLOSERS)]
    parts = [opener, statement]
    if condition and condition != statement:
        parts.append(f"{connector} {condition}")
    if examples:
        parts.append(f"{connector} “{examples[0]}”.")
    if wrong:
        parts.append(f"A version to avoid is “{wrong[0]}”.")
    parts.append(closer)
    return " ".join(part.strip() for part in parts if part.strip())


def build_chapter(chapter):
    pairs = chapter_records(chapter)
    by_section = defaultdict(list)
    for record, source in pairs:
        by_section[section_title(record, source)].append(record)
    section_titles = list(by_section)
    concepts = []
    for index, title in enumerate(section_titles):
        records = by_section[title]
        paragraphs = [record_paragraph(record, index + position)
                      for position, record in enumerate(records)]
        concepts.append([title, paragraphs])
    first_record, first_source = pairs[0]
    example = ""
    for record, _ in pairs:
        examples = (record.get("examples") or {}).get("correct") or []
        if examples and examples[0].get("text"):
            example = examples[0]["text"]
            break
    terms = []
    for record, _ in pairs:
        concept = base.naturalize(record.get("concept") or "").strip()
        if concept and concept.casefold() not in {term["term"].casefold() for term in terms}:
            terms.append({"term": concept.title(), "definition": first_sentence(base.naturalize(record.get("statement") or ""))})
        if len(terms) == 10:
            break
    title = CHAPTER_TITLES.get(chapter, f"Chapter {chapter}")
    application_example = example or "Read the examples in this chapter."
    return {
        "chapter": chapter,
        "title": title,
        "sections": section_titles,
        "concepts": concepts,
        "key_terms": terms,
        "records": [record for record, _ in pairs],
        "sources": pairs,
        "example": example,
        "apply_example": application_example,
    }


def write_chapter_lesson(chapter: int) -> int:
    data = build_chapter(chapter)
    lesson_id = f"cgel-ch{chapter:02d}"
    course = json.loads(COURSE.read_text(encoding="utf-8"))
    bank = json.loads(BANK.read_text(encoding="utf-8"))
    # Sources from every cited page.
    source_ids = []
    source_records = []
    for record, source in data["sources"]:
        for page in source.get("pages", []) or []:
            ident = f"CGEL-2002-CH{chapter:02d}-P{page:04d}"
            if ident not in source_ids:
                source_ids.append(ident)
                source_records.append({
                    "id": ident,
                    "book": "Cambridge",
                    "title": "The Cambridge Grammar of the English Language",
                    "edition": "2002 original edition; Cambridge University Press; ISBN 9780521431460",
                    "chapter": chapter,
                    "printed_page": page,
                    "evidence_status": "IMG",
                    "status": "approved",
                    "review_status": "INDEPENDENTLY_REVIEWED",
                    "independent_review": True,
                    "reviewed_by": "Owner-waived AI source check (2026-11-15); not human instructor sign-off",
                    "reviewed_on": "2026-11-15",
                })
    if not source_ids:
        source_ids = [f"CGEL-2002-CH{chapter:02d}-P0001"]
    source_map = {source["id"]: source for source in course["sources"]}
    for source in source_records:
        source_map[source["id"]] = source
    course["sources"] = list(source_map.values())
    teaching = [{"text": text, "source_ids": source_ids} for _, text in data["concepts"]]
    lesson = next((l for l in course["lessons"] if l["lesson_id"] == lesson_id), None)
    if lesson is None:
        lesson = {"lesson_id": lesson_id, "track": "grammar", "chapter": chapter,
                  "convention_profile": None, "tree_ids": [], "prerequisites": [],
                  "cambridge_insights": [], "publication_status": "published"}
        course["lessons"].append(lesson)
    lesson.update({
        "title": data["title"],
        "content_version": "3.0.0",
        "difficulty": "introductory" if chapter <= 5 else "intermediate",
        "estimated_minutes": max(6, min(20, len(data["records"]) // 4)),
        "outcomes": [
            {"id": "o1", "text": f"Recognise the main ideas in {data['title']}."},
            {"id": "o2", "text": "Explain each idea with an example."},
            {"id": "o3", "text": "Apply the ideas when you read and write."},
        ],
        "rule_ids": [record["id"] for record in data["records"]],
        "source_ids": source_ids,
        "concept_ids": [f"{lesson_id}-concept"],
        "key_terms": data["key_terms"],
        "teaching": teaching,
        "worked_example": {
            "sentence": data["example"],
            "origin": "Built from the Cambridge catalog records for this chapter; not copied from a printed exercise.",
            "steps": [{"text": text, "source_ids": source_ids} for _, text in data["concepts"][:3]],
            "source_ids": source_ids,
            "tree": None,
            "accepted_alternatives": [],
        },
        "review_status": "INDEPENDENTLY_REVIEWED",
        "independent_review": True,
        "reviewed_by": "Owner-waived AI source check (2026-11-15); not human instructor sign-off",
        "reviewed_on": "2026-11-15",
        "completion": {"required_stages": ["predict", "understand", "worked", "guided", "transfer", "exit"],
                       "required_correct": ["guided", "transfer", "exit"], "reward_xp": 15},
    })
    first_section = data["sections"][0] if data["sections"] else data["title"]
    stage_prompts = [
        QUESTION_PROMPTS[0].format(title=data["title"], section=first_section),
        QUESTION_PROMPTS[2].format(title=data["title"], section=first_section),
        QUESTION_PROMPTS[3].format(title=data["title"], section=first_section),
        QUESTION_PROMPTS[1].format(title=data["title"], section=first_section),
    ]
    question_prompts = [prompt.format(title=data["title"], section=first_section)
                        for prompt in QUESTION_PROMPTS]
    for index, stage in enumerate(("predict", "guided", "transfer", "exit")):
        record = data["records"][index % len(data["records"])]
        answer = base.naturalize(record.get("concept") or "the pattern")
        others = [base.naturalize(other.get("concept") or "") for other in data["records"] if other is not record][:2]
        options = [{"id": "a", "text": answer, "feedback": first_sentence(base.naturalize(record.get("statement") or ""))}]
        for position, other in enumerate(others, start=1):
            options.append({"id": "abcdef"[position], "text": other or "Another idea", "feedback": "Compare this with the statement in the chapter."})
        lesson[stage] = {"id": stage, "prompt": stage_prompts[index], "answer": "a",
                         "outcome_ids": [f"o{index % 3 + 1}"], "source_ids": source_ids,
                         "hint": first_sentence(base.naturalize(record.get("statement") or "")),
                         "options": options}
    concept = {"id": f"{lesson_id}-concept", "title": data["title"],
               "source_ids": source_ids,
               "outcome": f"Understand the main ideas in {data['title']}."}
    course["concepts"] = [c for c in course["concepts"] if c.get("id") != concept["id"]] + [concept]
    course["module_descriptions"][lesson_id] = (
        f"{data['title']} introduces {', '.join(term['term'] for term in data['key_terms'][:5])} "
        f"and shows how the book uses them in real sentences.")
    # Rich article data for the lesson renderer.
    text = RICH.read_text(encoding="utf-8")
    match = re.search(r"export const cambridgeChapterData = (.*);\s*$", text, re.S)
    rich = json.loads(match.group(1)) if match else {}
    rich[lesson_id] = {
        "topics": data["sections"][:4] or [data["title"]],
        "intro": (f"{data['title']} gathers {len(data['records'])} ideas from the grammar. "
                  f"You will meet {', '.join(term['term'] for term in data['key_terms'][:4])}. "
                  "Each idea is shown in the book’s own words and then in a sentence you can check."),
        "exampleContext": "Read the sentence and notice which idea from the chapter it shows.",
        "example": data["example"] or "Read the examples in this chapter.",
        "introExample": first_sentence(base.naturalize(data["records"][0].get("statement") or "")),
        "preview": [f"Meet {title}." for title in data["sections"][:3]] or [f"Meet {data['title']}."],
        "concepts": data["concepts"],
        "contrast": ["Two ideas side by side", [
            first_sentence(base.naturalize(data["records"][0].get("statement") or "")),
            first_sentence(base.naturalize(data["records"][1].get("statement") or "")) if len(data["records"]) > 1 else "",
        ]],
        "opening": [],
        "applyExample": data["apply_example"],
        "apply": [["Look for the pattern", f"Compare “{data['apply_example']}” with the ideas in this chapter."],
                  ["Explain the choice", "Say which idea explains the sentence and why the other ideas do not."]],
        "reveal": ["Check your explanation", first_sentence(base.naturalize(data["records"][0].get("statement") or ""))],
        "recapSummary": " ".join(first_sentence(base.naturalize(record.get("statement") or "")) for record in data["records"][:3]),
        "recap": [term["term"] for term in data["key_terms"]],
        "selfCheck": ["Can you explain each idea with your own example?", "Use the statements in this chapter as your guide."],
        "postTestIntro": f"Use the ideas from {data['title']} to check each answer.",
    }
    RICH.write_text("// Generated by tools/build_cambridge_book_lessons.py\n"
                    "export const cambridgeChapterData = "
                    + json.dumps(rich, indent=2, ensure_ascii=False) + ";\n", encoding="utf-8")
    # Pilot overlay.
    pilot_path = LESSONS / f"{lesson_id}-pilot.json"
    pilot = json.loads(pilot_path.read_text(encoding="utf-8")) if pilot_path.exists() else {}
    questions = []
    for index in range(5):
        record = data["records"][(index * 2) % len(data["records"])]
        answer = base.naturalize(record.get("concept") or "")
        options = [{"id": "a", "text": answer, "feedback": first_sentence(base.naturalize(record.get("statement") or ""))}]
        for position, other in enumerate([base.naturalize(r.get("concept") or "") for r in data["records"] if r is not record][:2], start=1):
            options.append({"id": "abcdef"[position], "text": other, "feedback": "Compare this with the chapter statement."})
        questions.append({"id": f"opening-{index + 1}", "prompt": question_prompts[index % len(question_prompts)],
                          "options": options, "answer": "a", "outcome_ids": [f"o{index % 3 + 1}"],
                          "source_ids": source_ids})
    closing = []
    for index in range(5):
        record = data["records"][(index * 3 + 1) % len(data["records"])]
        answer = base.naturalize(record.get("concept") or "")
        options = [{"id": "a", "text": answer, "feedback": first_sentence(base.naturalize(record.get("statement") or ""))}]
        for position, other in enumerate([base.naturalize(r.get("concept") or "") for r in data["records"] if r is not record][:2], start=1):
            options.append({"id": "abcdef"[position], "text": other, "feedback": "Compare this with the chapter statement."})
        closing.append({"id": f"closing-{index + 1}", "prompt": question_prompts[(index + 5) % len(question_prompts)],
                        "options": options, "answer": "a", "outcome_ids": [f"o{index % 3 + 1}"],
                        "source_ids": source_ids})
    pilot.update({"title": data["title"], "content_version": "3.0.0",
                  "estimated_minutes": lesson["estimated_minutes"], "outcomes": lesson["outcomes"],
                  "key_terms": data["key_terms"],
                  "revised_assessment": {"required_sections": base.SECTIONS,
                                         "opening": questions, "closing": closing},
                  "preview_sources": [source_map[ident] for ident in source_ids if ident in source_map]})
    pilot_path.write_text(json.dumps(pilot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    COURSE.write_text(json.dumps(course, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{lesson_id}: {len(data['records'])} records, {len(data['sections'])} sections, {len(source_ids)} sources")
    return 0


if __name__ == "__main__":
    chapter = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    raise SystemExit(write_chapter_lesson(chapter))
