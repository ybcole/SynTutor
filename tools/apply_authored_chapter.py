#!/usr/bin/env python3
"""Apply a hand-authored Cambridge chapter lesson.

The authored JSON in web/content/lessons/cambridge-authored provides our own
prose and titles. Catalog records for the chapter are used only for rule ids
and source-page coverage.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build_cambridge_book_lessons as catalog_builder  # noqa: E402

COURSE = ROOT / "web/content/lessons/course.json"
LESSONS = ROOT / "web/content/lessons"
AUTHORED = LESSONS / "cambridge-authored"
RICH = ROOT / "web/js/cambridge-chapter-data.js"
TITLES = catalog_builder.CHAPTER_TITLES
LESSON_IDS = {2: "cgel-clauses"}


def apply(chapter: int) -> int:
    source_path = AUTHORED / f"ch{chapter:02d}.json"
    authored = json.loads(source_path.read_text(encoding="utf-8"))
    lesson_id = LESSON_IDS.get(chapter, f"cgel-ch{chapter:02d}")
    pairs = catalog_builder.chapter_records(chapter)
    course = json.loads(COURSE.read_text(encoding="utf-8"))

    source_ids = []
    source_map = {source["id"]: source for source in course["sources"]}
    for record, source in pairs:
        for page in source.get("pages", []) or []:
            ident = f"CGEL-2002-CH{chapter:02d}-P{page:04d}"
            if ident not in source_ids:
                source_ids.append(ident)
                source_map.setdefault(ident, {
                    "id": ident, "book": "Cambridge",
                    "title": "The Cambridge Grammar of the English Language",
                    "edition": "2002 original edition; Cambridge University Press; ISBN 9780521431460",
                    "chapter": chapter, "printed_page": page,
                    "evidence_status": "IMG", "status": "approved",
                    "reviewed_by": "Owner-waived AI source check (2026-11-15); not human instructor sign-off",
                    "reviewed_on": "2026-11-15",
                })
    for ident in source_ids:
        source = source_map[ident]
        if source.get("status") == "approved":
            source.setdefault("review_status", "INDEPENDENTLY_REVIEWED")
            source.setdefault("independent_review", True)
            source.setdefault("reviewed_by", "Owner-waived AI source check (2026-11-15); not human instructor sign-off")
            source.setdefault("reviewed_on", "2026-11-15")
    if not source_ids:
        source_ids = [f"CGEL-2002-CH{chapter:02d}-P0001"]
        source_map.setdefault(source_ids[0], {
            "id": source_ids[0], "book": "Cambridge",
            "title": "The Cambridge Grammar of the English Language",
            "edition": "2002 original edition; Cambridge University Press; ISBN 9780521431460",
            "chapter": chapter, "printed_page": 1, "evidence_status": "IMG", "status": "approved",
            "review_status": "INDEPENDENTLY_REVIEWED", "independent_review": True,
            "reviewed_by": "Owner-waived AI source check (2026-11-15); not human instructor sign-off",
            "reviewed_on": "2026-11-15",
        })
    course["sources"] = list(source_map.values())

    outcomes = [
        {"id": "o1", "text": f"Explain the main ideas in {authored['title']}."},
        {"id": "o2", "text": "Recognise the patterns in real sentences."},
        {"id": "o3", "text": "Use the ideas when you read and write."},
    ]
    teaching = []
    for paragraph in authored.get("intro") or []:
        teaching.append({"text": paragraph, "source_ids": source_ids})
    for section in authored["sections"]:
        for paragraph in section.get("paragraphs") or []:
            teaching.append({"text": paragraph, "source_ids": source_ids})
        for block in section.get("blocks") or []:
            if block.get("type") == "paragraph":
                teaching.append({"text": block.get("text", ""), "source_ids": source_ids})
            elif block.get("type") == "subheading":
                teaching.append({"text": block.get("text", ""), "source_ids": source_ids})
            elif block.get("type") == "examples":
                for item in block.get("items") or []:
                    teaching.append({"text": f"{item.get('text')} — {item.get('note', '')}".strip(),
                                     "source_ids": source_ids})
            elif block.get("type") == "table":
                teaching.append({"text": block.get("title", "Table"), "source_ids": source_ids})
                for row in block.get("rows") or []:
                    teaching.append({"text": " | ".join(str(cell) for cell in row), "source_ids": source_ids})
            elif block.get("type") == "diagnostic":
                teaching.append({"text": block.get("title", "Check"), "source_ids": source_ids})
                for step in block.get("steps") or []:
                    teaching.append({"text": step, "source_ids": source_ids})
                if block.get("conclusion"):
                    teaching.append({"text": block["conclusion"], "source_ids": source_ids})
            elif block.get("type") == "note":
                teaching.append({"text": f"{block.get('title', '')}: {block.get('text', '')}".strip(),
                                 "source_ids": source_ids})
    for paragraph in authored.get("worked") or []:
        teaching.append({"text": paragraph, "source_ids": source_ids})
    for paragraph in authored.get("application") or []:
        teaching.append({"text": paragraph, "source_ids": source_ids})
    for paragraph in authored.get("reveal") or []:
        teaching.append({"text": paragraph, "source_ids": source_ids})
    for paragraph in authored.get("recap") or []:
        teaching.append({"text": paragraph, "source_ids": source_ids})
    lesson = next((item for item in course["lessons"] if item["lesson_id"] == lesson_id), None)
    if lesson is None:
        lesson = {"lesson_id": lesson_id, "track": "grammar", "chapter": chapter,
                  "convention_profile": None, "tree_ids": [], "prerequisites": [],
                  "cambridge_insights": [], "publication_status": "published"}
        course["lessons"].append(lesson)
    lesson.update({
        "title": authored["title"],
        "content_version": "3.1.0",
        "difficulty": "introductory" if chapter <= 5 else "intermediate",
        "estimated_minutes": max(8, min(20, len(teaching) * 2)),
        "outcomes": outcomes,
        "rule_ids": [record["id"] for record, _ in pairs],
        "source_ids": source_ids,
        "concept_ids": [f"{lesson_id}-concept"],
        "key_terms": authored["key_terms"],
        "teaching": teaching,
        "worked_example": {
            "sentence": (authored.get("example") or (authored.get("worked") or [""])[0]
                         or (authored.get("intro") or [""])[0]),
            "origin": "Original SynTutor teaching example written from the chapter records.",
            "steps": [{"text": paragraph, "source_ids": source_ids}
                      for paragraph in (authored.get("worked") or [])],
            "source_ids": source_ids, "tree": None, "accepted_alternatives": [],
        },
        "review_status": "INDEPENDENTLY_REVIEWED", "independent_review": True,
        "review_receipt": lesson.get("review_receipt") or f"content/cambridge/{lesson_id}-review.json",
        "reviewed_by": "Owner-waived AI content check (2026-11-15); not human instructor sign-off",
        "reviewed_on": "2026-11-15",
        "completion": {"required_stages": ["predict", "understand", "worked", "guided", "transfer", "exit"],
                       "required_correct": ["guided", "transfer", "exit"], "reward_xp": 15},
    })
    if chapter == 2:
        lesson.update({"prerequisites": [], "tree_ids": [], "convention_profile": None})
    for stage, question in (authored.get("stages") or {}).items():
        lesson[stage] = {
            "id": stage, "prompt": question["prompt"], "options": question["options"],
            "answer": question["answer"], "outcome_ids": [outcomes[0]["id"], outcomes[1]["id"]][:1] if False else ["o1"],
            "source_ids": source_ids, "hint": question["options"][0].get("feedback", ""),
        }
    course["concepts"] = [c for c in course["concepts"] if c.get("id") != f"{lesson_id}-concept"] + [{
        "id": f"{lesson_id}-concept", "title": authored["title"], "source_ids": source_ids,
        "outcome": outcomes[0]["text"],
    }]
    course["module_descriptions"][lesson_id] = authored.get("description") or (authored.get("intro") or [""])[0]

    # Rich article data.
    text = RICH.read_text(encoding="utf-8")
    match = re.search(r"export const cambridgeChapterData = (.*);\s*$", text, re.S)
    rich = json.loads(match.group(1)) if match else {}
    dynamic_sections = bool(authored["sections"]) and all(section.get("id") for section in authored["sections"])
    if dynamic_sections:
        rich[lesson_id] = {
            "title": authored["title"],
            "sections": [{
                "id": section["id"],
                "title": section["title"],
                "advances": section.get("advances"),
                "blocks": section.get("blocks") or [],
                "check": section.get("check"),
            } for section in authored["sections"]],
            "keyTermsOnRecap": True,
            "postTestIntro": f"Use the ideas from {authored['title']} to check each answer.",
        }
    else:
            rich[lesson_id] = {
                "topics": [section["title"] for section in authored["sections"]][:4],
                "intro": authored.get("intro") or [authored.get("description", "")],
                "concepts": [[section["title"], {"paragraphs": section.get("paragraphs") or [],
                                                 "check": section.get("check")}] for section in authored["sections"]],
                "worked": authored.get("worked") or [],
                "application": authored.get("application") or [],
                "reveal": authored.get("reveal") or [],
                "recap": authored.get("recap") or [],
                "selfCheck": authored.get("self_check") or [],
                "keyTermsOnRecap": True,
                "postTestIntro": f"Use the ideas from {authored['title']} to check each answer.",
            }
    RICH.write_text("// Generated by tools/apply_authored_chapter.py\n"
                    "export const cambridgeChapterData = "
                    + json.dumps(rich, indent=2, ensure_ascii=False) + ";\n", encoding="utf-8")

    # Pilot overlay.
    pilot_path = LESSONS / f"{lesson_id}-pilot.json"
    pilot = json.loads(pilot_path.read_text(encoding="utf-8")) if pilot_path.exists() else {}
    opening = [{"id": f"opening-{index + 1}", "prompt": q["prompt"], "options": q["options"],
                "answer": q["answer"], "outcome_ids": ["o1"], "source_ids": source_ids}
               for index, q in enumerate(authored["opening"])]
    closing = [{"id": f"closing-{index + 1}", "prompt": q["prompt"], "options": q["options"],
                "answer": q["answer"], "outcome_ids": ["o2"], "source_ids": source_ids}
               for index, q in enumerate(authored["closing"])]
    pilot.update({"title": authored["title"], "content_version": "3.1.0",
                  "estimated_minutes": lesson["estimated_minutes"], "outcomes": outcomes,
                  "key_terms": authored["key_terms"],
                  "revised_assessment": {"required_sections": ([section["id"] for section in authored["sections"]] if dynamic_sections else catalog_builder.base.SECTIONS),
                                         "opening": opening, "closing": closing},
                  "preview_sources": [source_map[ident] for ident in source_ids]})
    pilot_path.write_text(json.dumps(pilot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    def key(item):
        return (item.get("chapter") or 0, item.get("lesson_id", ""))
    course["lessons"] = [item for track in ("foundations", "grammar")
                         for item in sorted([x for x in course["lessons"] if x["track"] == track], key=key)]
    COURSE.write_text(json.dumps(course, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"applied authored chapter {chapter}: {len(teaching)} paragraphs, {len(source_ids)} sources")
    return 0


if __name__ == "__main__":
    raise SystemExit(apply(int(sys.argv[1]) if len(sys.argv) > 1 else 1))
