#!/usr/bin/env python3
"""Apply the Cambridge Lessons Master Markdown to the lesson and quiz data.

The Markdown is the source of truth. This tool reads each lesson block and
writes the metadata, article text, key terms, teaching blocks, worked example,
stage checks, revised assessment and bank quizzes back to:

- web/content/lessons/course.json
- web/content/lessons/<lesson>-pilot.json
- web/js/cambridge-chapter-data.js
- web/js/lesson-key-terms.js
- web/content/quizzes/bank.json
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MD = ROOT / "docs/lessons/CAMBRIDGE_LESSONS_MASTER.md"
COURSE = ROOT / "web/content/lessons/course.json"
BANK = ROOT / "web/content/quizzes/bank.json"
LESSONS = ROOT / "web/content/lessons"
RICH = ROOT / "web/js/cambridge-chapter-data.js"
KEY_TERMS = ROOT / "web/js/lesson-key-terms.js"


def unquote(value):
    return value.strip()


def parse_question(lines):
    question = {"options": []}
    in_options = False
    current = None
    for line in lines:
        stripped = line.rstrip()
        match = re.match(r"^- (prompt|answer|hint|kind|rationale|outcome_ids|source_ids):\s*(.*)$", stripped)
        if match:
            in_options = False
            key, value = match.group(1), match.group(2)
            if key in ("outcome_ids", "source_ids"):
                question[key] = [item.strip() for item in value.split(",") if item.strip()]
            else:
                question[key] = unquote(value)
            continue
        if re.match(r"^- options:\s*$", stripped):
            in_options = True
            current = None
            continue
        option = re.match(r"^\s+- id:\s*(.+)$", stripped)
        if in_options and option:
            current = {"id": unquote(option.group(1))}
            question["options"].append(current)
            continue
        field = re.match(r"^\s+(text|feedback):\s*(.*)$", stripped)
        if in_options and field and current is not None:
            current[field.group(1)] = unquote(field.group(2))
    return question


def split_subsections(lines, prefix="### "):
    out = {}
    current = None
    for line in lines:
        if line.startswith(prefix):
            current = line[len(prefix):].strip()
            out[current] = []
        elif current is not None:
            out[current].append(line)
    return out


def text_of(lines):
    return " ".join(line.strip() for line in lines if line.strip())


def bullets_of(lines):
    return [line.strip()[2:].strip() for line in lines if line.strip().startswith("- ")]


def parse_lesson(header, body):
    lesson_id, title = [part.strip() for part in header.split("—", 1)]
    meta = {}
    for line in body:
        match = re.match(r"^- ([a-z_]+):\s*(.*)$", line)
        if match:
            meta[match.group(1)] = match.group(2).strip()
        if line.startswith("## "):
            break
    sections = {}
    current = None
    for line in body:
        if line.startswith("## "):
            current = line[3:].strip()
            sections[current] = []
        elif current is not None:
            sections[current].append(line)
    lesson = {"lesson_id": lesson_id, "title": title, "meta": meta}
    outcomes = []
    for line in sections.get("Outcomes", []):
        match = re.match(r"^- ([^:]+):\s*(.*)$", line)
        if match:
            outcomes.append({"id": match.group(1).strip(), "text": match.group(2).strip()})
    lesson["outcomes"] = outcomes
    terms = []
    for line in sections.get("Key terms", []):
        match = re.match(r"^- \*\*(.+?)\*\*\s+—\s*(.*)$", line)
        if match:
            terms.append({"term": match.group(1).strip(), "definition": match.group(2).strip()})
    lesson["key_terms"] = terms
    article_lines = sections.get("Chapter article", [])
    article = {}
    subs = split_subsections(article_lines)
    article["intro"] = text_of(subs.get("Introduction", []))
    article["topics"] = bullets_of(subs.get("Topics", []))
    example_lines = subs.get("Example", [])
    example = {}
    for line in example_lines:
        match = re.match(r"^- (context|sentence|explanation):\s*(.*)$", line)
        if match:
            example[match.group(1)] = match.group(2).strip()
    article["exampleContext"] = example.get("context", "")
    article["example"] = example.get("sentence", "")
    article["introExample"] = example.get("explanation", "")
    article["preview"] = bullets_of(subs.get("Preview", []))
    concepts = []
    contrast = None
    application = None
    reveal = None
    recap = None
    self_check = subs.get("Self-check", [])
    for key, lines in subs.items():
        if key.startswith("Concept: "):
            concepts.append([key[len("Concept: "):].strip(), text_of(lines)])
        elif key.startswith("Contrast: "):
            contrast = [key[len("Contrast: "):].strip(), bullets_of(lines)]
        elif key == "Application":
            apply_items = []
            apply_example = ""
            for line in lines:
                match = re.match(r"^- example:\s*(.*)$", line)
                bold = re.match(r"^- \*\*(.+?)\*\*\s+—\s*(.*)$", line)
                if match:
                    apply_example = match.group(1).strip()
                elif bold:
                    apply_items.append([bold.group(1).strip(), bold.group(2).strip()])
            application = {"example": apply_example, "items": apply_items}
        elif key.startswith("Reveal: "):
            reveal = [key[len("Reveal: "):].strip(), text_of(lines)]
        elif key == "Recap":
            recap_bullets = bullets_of(lines)
            recap = {"summary": text_of([line for line in lines if not line.strip().startswith("- ")]),
                     "items": recap_bullets}
    article["concepts"] = concepts
    article["contrast"] = contrast or ["", []]
    article["applyExample"] = (application or {}).get("example", "")
    article["apply"] = (application or {}).get("items", [])
    article["reveal"] = reveal or ["", ""]
    article["recapSummary"] = (recap or {}).get("summary", "")
    article["recap"] = (recap or {}).get("items", [])
    article["selfCheck"] = [item for item in self_check if item.strip()]
    lesson["article"] = article
    teaching = []
    for name, lines in split_subsections(sections.get("Teaching blocks", [])).items():
        if name.startswith("Teaching block"):
            teaching.append({"text": text_of(lines), "source_ids": lesson.get("source_ids", [])})
    lesson["teaching"] = teaching
    worked_lines = sections.get("Worked example", [])
    worked = {"sentence": "", "origin": "", "steps": [], "tree": None, "accepted_alternatives": []}
    for line in worked_lines:
        match = re.match(r"^- (sentence|origin):\s*(.*)$", line)
        step = re.match(r"^- step:\s*(.*)$", line)
        if match:
            worked[match.group(1)] = match.group(2).strip()
        elif step:
            worked["steps"].append({"text": step.group(1).strip()})
    tree_lines = subs.get("Tree", [])
    if tree_lines:
        raw = "\n".join(line for line in tree_lines if not line.startswith("```"))
        try:
            worked["tree"] = json.loads(raw)
        except json.JSONDecodeError:
            pass
    lesson["worked_example"] = worked
    stages = {}
    for name, lines in split_subsections(sections.get("Stage checks", []), "#### ").items():
        stages[name] = parse_question(lines)
    lesson["stages"] = stages
    assessment = None
    for line in sections.get("Revised assessment", []):
        match = re.match(r"^- required_sections:\s*(.*)$", line)
        if match:
            assessment = {"required_sections": [item.strip() for item in match.group(1).split(",") if item.strip()],
                          "opening": [], "closing": []}
            break
    if assessment is not None:
        for kind, lines in split_subsections(sections.get("Revised assessment", []), "### ").items():
            if kind.lower().startswith("opening"):
                target = assessment["opening"]
            elif kind.lower().startswith("closing"):
                target = assessment["closing"]
            else:
                continue
            for name, qlines in split_subsections(lines, "#### ").items():
                question = parse_question(qlines)
                question["id"] = name
                target.append(question)
    lesson["revised_assessment"] = assessment
    bank_items = []
    for item_id, lines in split_subsections(sections.get("Lesson quizzes (bank)", [])).items():
        item = parse_question(lines)
        item["item_id"] = item_id
        bank_items.append(item)
    lesson["bank_items"] = bank_items
    return lesson


def parse_md():
    text = MD.read_text(encoding="utf-8")
    chunks = re.split(r"(?m)^# Lesson: ", text)[1:]
    lessons = {}
    for chunk in chunks:
        header, _, body = chunk.partition("\n")
        lesson = parse_lesson(header, body.splitlines())
        lessons[lesson["lesson_id"]] = lesson
    return lessons


def apply() -> int:
    lessons = parse_md()
    course = json.loads(COURSE.read_text(encoding="utf-8"))
    rich = {}
    key_terms = {}
    for lesson in course["lessons"]:
        lesson_id = lesson["lesson_id"]
        if not lesson_id.startswith("cgel-") or lesson_id not in lessons:
            continue
        parsed = lessons[lesson_id]
        meta = parsed["meta"]
        lesson["title"] = parsed["title"]
        lesson["content_version"] = meta.get("content_version", lesson.get("content_version"))
        lesson["difficulty"] = meta.get("difficulty", lesson.get("difficulty"))
        lesson["estimated_minutes"] = int(meta.get("estimated_minutes") or lesson.get("estimated_minutes") or 8)
        lesson["reviewed_by"] = meta.get("reviewed_by", lesson.get("reviewed_by"))
        lesson["reviewed_on"] = meta.get("reviewed_on", lesson.get("reviewed_on"))
        lesson["outcomes"] = parsed["outcomes"] or lesson.get("outcomes")
        lesson["key_terms"] = parsed["key_terms"]
        if lesson_id.startswith("cgel-ch"):
            lesson.pop("revised_assessment", None)
        for key in ("rule_ids", "source_ids", "concept_ids", "tree_ids"):
            if meta.get(key) is not None:
                lesson[key] = [item.strip() for item in meta.get(key, "").split(",") if item.strip()]
        source_ids = lesson.get("source_ids") or []
        lesson["teaching"] = parsed["teaching"] or lesson.get("teaching")
        for block in lesson["teaching"]:
            block["source_ids"] = block.get("source_ids") or source_ids
        worked = parsed["worked_example"]
        worked["source_ids"] = source_ids
        for step in worked.get("steps", []):
            step["source_ids"] = step.get("source_ids") or source_ids
        lesson["worked_example"] = worked
        for stage in ("predict", "guided", "transfer", "exit"):
            if stage in parsed["stages"]:
                question = parsed["stages"][stage]
                question["id"] = stage
                question["source_ids"] = question.get("source_ids") or source_ids
                question["outcome_ids"] = question.get("outcome_ids") or [lesson["outcomes"][0]["id"]]
                lesson[stage] = question
        rich[lesson_id] = parsed["article"]
        key_terms[lesson_id] = [[term["term"], term["definition"]] for term in parsed["key_terms"]]
        if lesson_id.startswith("cgel-ch"):
            pilot_path = LESSONS / f"{lesson_id}-pilot.json"
            pilot = json.loads(pilot_path.read_text(encoding="utf-8"))
            pilot["title"] = parsed["title"]
            pilot["content_version"] = meta.get("content_version", pilot.get("content_version"))
            pilot["estimated_minutes"] = int(meta.get("estimated_minutes") or pilot.get("estimated_minutes") or 8)
            pilot["outcomes"] = parsed["outcomes"] or pilot.get("outcomes")
            pilot["key_terms"] = parsed["key_terms"]
            if parsed["revised_assessment"]:
                pilot["revised_assessment"] = parsed["revised_assessment"]
            pilot_path.write_text(json.dumps(pilot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        if parsed["bank_items"]:
            bank = json.loads(BANK.read_text(encoding="utf-8"))
            by_id = {item["item_id"]: item for item in bank["items"]}
            for item in parsed["bank_items"]:
                target = by_id.get(item["item_id"])
                if target is None:
                    continue
                for key in ("kind", "prompt", "answer", "rationale"):
                    if item.get(key):
                        target[key] = item[key]
                if item.get("options"):
                    old_options = {option.get("id"): option for option in target.get("options", [])}
                    merged_options = []
                    for option in item["options"]:
                        row = dict(old_options.get(option.get("id"), {}))
                        row["id"] = option.get("id")
                        row["text"] = option.get("text")
                        if option.get("feedback"):
                            row["rationale"] = option["feedback"]
                        merged_options.append(row)
                    target["options"] = merged_options
            BANK.write_text(json.dumps(bank, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    # Merge article data, preserving fields the Markdown does not cover.
    existing = {}
    if RICH.exists():
        match = re.search(r"export const cambridgeChapterData = (.*);\s*$",
                          RICH.read_text(encoding="utf-8"), re.S)
        if match:
            existing = json.loads(match.group(1))
    merged = {}
    for lesson_id, article in rich.items():
        merged[lesson_id] = {**existing.get(lesson_id, {}), **article}
    RICH.write_text(
        "// Generated by tools/apply_lessons_master_md.py\n"
        "export const cambridgeChapterData = "
        + json.dumps(merged, indent=2, ensure_ascii=False) + ";\n",
        encoding="utf-8")
    # Update the key-term map used by the renderer.
    script = ("import {lessonKeyTerms} from './web/js/lesson-key-terms.js';"
              "console.log(JSON.stringify(lessonKeyTerms));")
    existing_terms = json.loads(subprocess.run(
        ["node", "--input-type=module", "-e", script],
        cwd=ROOT, capture_output=True, text=True, check=True).stdout)
    existing_terms.update({lesson_id: terms for lesson_id, terms in key_terms.items()})
    key_text = KEY_TERMS.read_text(encoding="utf-8")
    prefix, rest = key_text.split("export const lessonKeyTerms = ", 1)
    suffix = rest.split("\n};\n", 1)[1]
    KEY_TERMS.write_text(
        prefix + "export const lessonKeyTerms = "
        + json.dumps(existing_terms, indent=2, ensure_ascii=False) + ";\n" + suffix,
        encoding="utf-8")
    COURSE.write_text(json.dumps(course, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"applied {len(lessons)} Cambridge lessons")
    return 0


if __name__ == "__main__":
    raise SystemExit(apply())
