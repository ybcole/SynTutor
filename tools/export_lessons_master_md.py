#!/usr/bin/env python3
"""Export every lesson into one editable Markdown master file.

The Markdown is the human-editable source for lessons. It contains metadata,
article text, key terms, worked examples, stage checks, revised quizzes, trees
and bank quizzes. Edit the Markdown and ask the assistant to apply the changes.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/lessons/CAMBRIDGE_LESSONS_MASTER.md"
COURSE = ROOT / "web/content/lessons/course.json"
BANK = ROOT / "web/content/quizzes/bank.json"
LESSONS = ROOT / "web/content/lessons"


def load_rich():
    text = (ROOT / "web/js/cambridge-chapter-data.js").read_text(encoding="utf-8")
    match = re.search(r"export const cambridgeChapterData = (.*);\s*$", text, re.S)
    return json.loads(match.group(1)) if match else {}


def load_js_lesson_data():
    script = (
        "import {advancedFoundationsChapters} from './web/js/advanced-foundations-lessons.js';"
        "import {lessonKeyTerms} from './web/js/lesson-key-terms.js';"
        "console.log(JSON.stringify({articles: advancedFoundationsChapters, keyTerms: lessonKeyTerms}));"
    )
    result = subprocess.run(["node", "--input-type=module", "-e", script],
                            cwd=ROOT, capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


def pilot_files():
    files = {}
    for path in sorted(LESSONS.glob("*-pilot.json")):
        files[path.name.replace("-pilot.json", "")] = json.loads(
            path.read_text(encoding="utf-8"))
    return files


def options_md(options, indent=""):
    lines = []
    for option in options or []:
        lines.append(f"{indent}- id: {option.get('id')}")
        lines.append(f"{indent}  text: {option.get('text')}")
        if option.get("feedback"):
            lines.append(f"{indent}  feedback: {option.get('feedback')}")
    return lines


def question_md(question, level=4):
    if not question:
        return []
    heading = "#" * level
    lines = [f"{heading} {question.get('id') or 'question'}",
             f"- prompt: {question.get('prompt')}",
             f"- answer: {question.get('answer')}"]
    outcome_ids = question.get("outcome_ids") or []
    if outcome_ids:
        lines.append(f"- outcome_ids: {', '.join(outcome_ids)}")
    source_ids = question.get("source_ids") or []
    if source_ids:
        lines.append(f"- source_ids: {', '.join(source_ids)}")
    if question.get("hint"):
        lines.append(f"- hint: {question.get('hint')}")
    lines.append("- options:")
    lines.extend(options_md(question.get("options"), "  "))
    return lines


def lesson_md(lesson, rich, pilot, bank_items, js_terms=None):
    pilot = pilot or {}
    js_terms = js_terms or {}
    lines = [f"# Lesson: {lesson['lesson_id']} — {lesson.get('title')}", ""]
    meta = [
        ("lesson_id", lesson.get("lesson_id")),
        ("title", lesson.get("title")),
        ("track", lesson.get("track")),
        ("chapter", lesson.get("chapter")),
        ("content_version", pilot.get("content_version") or lesson.get("content_version")),
        ("difficulty", lesson.get("difficulty")),
        ("estimated_minutes", pilot.get("estimated_minutes") or lesson.get("estimated_minutes")),
        ("publication_status", lesson.get("publication_status")),
        ("reviewed_by", lesson.get("reviewed_by")),
        ("reviewed_on", lesson.get("reviewed_on")),
    ]
    for key, value in meta:
        lines.append(f"- {key}: {value}")
    for key in ("rule_ids", "source_ids", "concept_ids", "tree_ids"):
        values = lesson.get(key) or []
        lines.append(f"- {key}: {', '.join(str(value) for value in values)}")
    lines.append("")
    outcomes = pilot.get("outcomes") or lesson.get("outcomes") or []
    lines.append("## Outcomes")
    for outcome in outcomes:
        lines.append(f"- {outcome.get('id')}: {outcome.get('text')}")
    lines.append("")
    terms = pilot.get("key_terms") or lesson.get("key_terms") or [
        {"term": term, "definition": definition}
        for term, definition in (js_terms.get(lesson["lesson_id"]) or [])
    ]
    lines.append("## Key terms")
    if terms:
        for term in terms:
            lines.append(f"- **{term.get('term')}** — {term.get('definition')}")
    else:
        lines.append("- (none)")
    lines.append("")
    lines.append("## Rules")
    for rule_id in lesson.get("rule_ids") or []:
        lines.append(f"- {rule_id}")
    if not lesson.get("rule_ids"):
        lines.append("- (none)")
    lines.append("")
    lines.append("## Sources")
    source_map = {source["id"]: source for source in json.loads(COURSE.read_text(encoding="utf-8"))["sources"]}
    for source_id in lesson.get("source_ids") or []:
        source = source_map.get(source_id, {})
        lines.append(f"- {source_id} (p.{source.get('printed_page', '?')})")
    lines.append("")
    if rich:
        lines.append("## Chapter article")
        lines.append("### Introduction")
        lines.append(rich.get("intro", ""))
        lines.append("")
        lines.append("### Topics")
        for topic in rich.get("topics", []):
            lines.append(f"- {topic}")
        lines.append("")
        lines.append("### Example")
        lines.append(f"- context: {rich.get('exampleContext', '')}")
        lines.append(f"- sentence: {rich.get('example', '')}")
        lines.append(f"- explanation: {rich.get('introExample', '')}")
        lines.append("")
        lines.append("### Preview")
        for item in rich.get("preview", []):
            lines.append(f"- {item}")
        lines.append("")
        for title, text in rich.get("concepts", []):
            lines.append(f"### Concept: {title}")
            lines.append(text)
            lines.append("")
        contrast = rich.get("contrast") or ["", []]
        lines.append(f"### Contrast: {contrast[0]}")
        for item in contrast[1]:
            lines.append(f"- {item}")
        lines.append("")
        lines.append("### Application")
        lines.append(f"- example: {rich.get('applyExample', '')}")
        for title, text in rich.get("apply", []):
            lines.append(f"- **{title}** — {text}")
        lines.append("")
        reveal = rich.get("reveal") or ["", ""]
        lines.append(f"### Reveal: {reveal[0]}")
        lines.append(reveal[1] if len(reveal) > 1 else "")
        lines.append("")
        lines.append("### Recap")
        lines.append(rich.get("recapSummary", ""))
        for item in rich.get("recap", []):
            lines.append(f"- {item}")
        lines.append("")
        lines.append("### Self-check")
        for item in rich.get("selfCheck", []):
            lines.append(f"- {item}")
        lines.append("")
    lines.append("## Teaching blocks")
    for index, block in enumerate(lesson.get("teaching") or [], start=1):
        lines.append(f"### Teaching block {index}")
        lines.append(block.get("text", ""))
        lines.append("")
    worked = lesson.get("worked_example") or {}
    if worked:
        lines.append("## Worked example")
        lines.append(f"- sentence: {worked.get('sentence', '')}")
        lines.append(f"- origin: {worked.get('origin', '')}")
        for step in worked.get("steps") or []:
            lines.append(f"- step: {step.get('text', '')}")
        if worked.get("tree"):
            lines.append("### Tree")
            lines.append("```json")
            lines.append(json.dumps(worked["tree"], indent=2, ensure_ascii=False))
            lines.append("```")
        lines.append("")
    lines.append("## Stage checks")
    for key in ("predict", "guided", "transfer", "exit"):
        lines.extend(question_md(lesson.get(key), 4))
        lines.append("")
    assessment = (pilot.get("revised_assessment") or lesson.get("revised_assessment"))
    if assessment:
        lines.append("## Revised assessment")
        lines.append(f"- required_sections: {', '.join(assessment.get('required_sections') or [])}")
        for kind in ("opening", "closing"):
            lines.append(f"### {kind.title()} questions")
            for index, question in enumerate(assessment.get(kind) or [], start=1):
                lines.append(f"#### {kind}-{index}")
                lines.append(f"- prompt: {question.get('prompt')}")
                lines.append(f"- answer: {question.get('answer')}")
                lines.append(f"- outcome_ids: {', '.join(question.get('outcome_ids') or [])}")
                lines.append(f"- source_ids: {', '.join(question.get('source_ids') or [])}")
                lines.append("- options:")
                lines.extend(options_md(question.get("options"), "  "))
        lines.append("")
    if bank_items:
        lines.append("## Lesson quizzes (bank)")
        for item in bank_items:
            lines.append(f"### {item.get('item_id')}")
            lines.append(f"- kind: {item.get('kind')}")
            lines.append(f"- prompt: {item.get('prompt')}")
            lines.append(f"- answer: {item.get('answer')}")
            lines.append(f"- rationale: {item.get('rationale')}")
            lines.append("- options:")
            lines.extend(options_md(item.get("options"), "  "))
        lines.append("")
    return lines


def main() -> int:
    course = json.loads(COURSE.read_text(encoding="utf-8"))
    bank = json.loads(BANK.read_text(encoding="utf-8"))
    rich = load_rich()
    js_data = load_js_lesson_data()
    rich.update(js_data.get("articles") or {})
    pilots = pilot_files()
    items_by_lesson = {}
    for item in bank.get("items", []):
        items_by_lesson.setdefault(item.get("lesson_id"), []).append(item)
    cambridge_lessons = [lesson for lesson in course.get("lessons", [])
                         if str(lesson.get("lesson_id", "")).startswith("cgel-")]
    cambridge_ids = {lesson["lesson_id"] for lesson in cambridge_lessons}
    lines = [
        "# Cambridge Lessons Master",
        "",
        "This Markdown is the editable source for every Cambridge lesson in the course.",
        "It contains each lesson's metadata, article text, key terms, worked examples,",
        "stage checks, revised quizzes and bank quizzes. Edit any text in place and ask",
        "the assistant to apply the changes; the assistant will look up the matching",
        "lesson, section and question and update the lesson and quiz files precisely.",
        "",
        f"- schema_version: {course.get('schema_version')}",
        f"- course_version: {course.get('course_version')}",
        f"- title: {course.get('title')}",
        f"- lessons: {len(cambridge_lessons)}",
        "",
        "## Tracks",
        "",
    ]
    for track in course.get("tracks", []):
        lines.append(f"- {track.get('id')}: {track.get('title')} — {track.get('description')}")
    lines.append("")
    lines.append("---")
    lines.append("")
    for lesson in cambridge_lessons:
        lesson_id = lesson["lesson_id"]
        lines.extend(lesson_md(lesson, rich.get(lesson_id), pilots.get(lesson_id),
                               items_by_lesson.get(lesson_id, []),
                               js_data.get("keyTerms") or {}))
        lines.append("---")
        lines.append("")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
