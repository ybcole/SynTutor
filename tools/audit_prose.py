#!/usr/bin/env python3
"""Audit authored Cambridge lesson prose for mechanical writing patterns."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUTHORED = ROOT / "web/content/lessons/cambridge-authored"

DEFINITION_OPENERS = re.compile(
    r"^(?:"
    r"(?:Syntax|Morphology|Semantics|Pragmatics|Phonology|Inflection|Productivity|Conversion|Compounding|Affixation|Coordination|Supplementation|Deixis|Anaphora|Punctuation|Tense|Aspect|Mood) (?:is|are|concerns|concern|covers|involve|denotes|describes|expresses)\b"
    r"|(?:The|A|An) (?:noun phrase|verb phrase|adjective phrase|adverb phrase|preposition phrase|clause|phrase|subject|object|complement|adjunct|determiner|determinative|nominal|scale|comparative clause|relative clause|content clause) (?:is|are|concerns|denotes|describes|expresses)\b"
    r"|(?:Dependents|Objects|Nouns|Adjectives|Adverbs|Prepositions|Clauses|Phrases) (?:of|in|are|is|normally|typically)\b"
    r")",
    re.IGNORECASE,
)

INLINE_EXAMPLE = re.compile(r"(?:^|[.!?]\s+)In \*[^*]+\*")
SUMMARY_CLOSER = re.compile(
    r"(?:^|\s)(?:The (?:boundary|distinction|point) matters|The (?:boundary|distinction|point) is|"
    r"This (?:is why|gives|shows|means|matters)|The point is|What matters is)\b",
    re.IGNORECASE,
)
SYMMETRICAL_TITLE = re.compile(r"^(?:Same|Different)\b.+\b(?:same|different)\b", re.IGNORECASE)
BANNED_WORD = re.compile(r"\bbook\b|Diagnostic", re.IGNORECASE)


def paragraphs(chapter: dict):
    for section in chapter.get("sections", []):
        for block in section.get("blocks", []):
            if block.get("type") == "paragraph":
                yield section, block


def sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def audit_chapter(path: Path) -> list[str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"invalid JSON: {exc}"]
    issues: list[str] = []
    all_text = json.dumps(data, ensure_ascii=False)

    if re.search(r"\bbook\b", all_text, re.IGNORECASE):
        issues.append("contains the word 'book'")
    visible = " ".join(
        [data.get("title", ""), data.get("description", "")]
        + [p for p in data.get("intro", [])]
        + [s.get("title", "") for s in data.get("sections", [])]
        + [b.get("text", "") for s in data.get("sections", []) for b in s.get("blocks", []) if b.get("type") in ("paragraph", "subheading")]
        + [b.get("title", "") for s in data.get("sections", []) for b in s.get("blocks", []) if b.get("type") == "note"]
    )
    if re.search(r"\bDiagnostic\b", visible, re.IGNORECASE):
        issues.append("contains visible 'Diagnostic'")

    for section in data.get("sections", []):
        if SYMMETRICAL_TITLE.search(section.get("title", "")):
            issues.append(f"symmetrical section title: {section.get('title')!r}")

    for index, (section, block) in enumerate(paragraphs(data), 1):
        text = block.get("text", "").strip()
        if not text:
            continue
        first = sentences(text)[0] if sentences(text) else text
        label = f"{section.get('id')} paragraph {index}"
        if DEFINITION_OPENERS.search(first):
            issues.append(f"{label}: definition-first opener: {first[:90]!r}")
        if len(INLINE_EXAMPLE.findall(text)) >= 2:
            issues.append(f"{label}: inline example chain")
        if SUMMARY_CLOSER.search(text[-220:]):
            issues.append(f"{label}: summary closer")
        if BANNED_WORD.search(text):
            issues.append(f"{label}: banned wording")
    return issues


def main() -> int:
    files = sorted(AUTHORED.glob("ch*.json"))
    if not files:
        print("No authored chapter files found.", file=sys.stderr)
        return 2
    total = 0
    for path in files:
        issues = audit_chapter(path)
        if issues:
            total += len(issues)
            print(f"\n{path.name}: {len(issues)} issue(s)")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print(f"{path.name}: clean")
    print(f"\n{total} issue(s) across {len(files)} chapter(s)")
    return 1 if total else 0


if __name__ == "__main__":
    raise SystemExit(main())
