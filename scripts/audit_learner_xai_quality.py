"""Learner-perspective quality audit of the XAI copy.

Run:

    .venv/Scripts/python.exe scripts/audit_learner_xai_quality.py \
        --output artifacts/learner-xai-quality.json

Checks, for every error/suggestion finding and every node explanation:

- length (words/characters);
- reading ease (Flesch approximation);
- internal jargon or ids leaking to the learner;
- whether an error tells the learner what to do;
- whether the text names the word/phrase it is about;
- repeated paragraphs within the same sentence.

It is a heuristic screen, not a human readability study.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "server"))

from api import build_payload  # noqa: E402
from explanations import explain_analysis  # noqa: E402
from learner_explanations import compose_learner_explanation  # noqa: E402

JARGON = ("b-r", "canonical", "constraint", "xai", "matrix", "phrase marker",
          "constituent", "projection", "rule id", "parsed", "token",
          "node", "benepar", "spacy", "cgel", "cambridge grammar checks")
ACTION = ("write", "change", "remove", "use", "add", "move", "drop", "replace",
          "delete", "correct", "say", "put", "insert", "capitalize", "hyphenate")
INTERNAL_ID = re.compile(r"\b(sg-root|n\d+:|C-[A-Z][A-Z-]{2,})\b")


def _words(text):
    return re.findall(r"[A-Za-z][A-Za-z'’-]*", text)


def _syllables(word):
    groups = re.findall(r"[aeiouy]+", word.lower())
    count = len(groups)
    if word.lower().endswith("e") and count > 1:
        count -= 1
    return max(1, count)


def _flesch(text):
    words = _words(text)
    sentences = max(1, len(re.findall(r"[.!?]", text)))
    if not words:
        return None
    syl = sum(_syllables(word) for word in words)
    return round(206.835 - 1.015 * (len(words) / sentences)
                 - 84.6 * (syl / len(words)), 1)


def _flags(text, status=None):
    lowered = text.lower()
    flags = []
    if any(term in lowered for term in JARGON):
        flags.append("jargon")
    if len(_words(text)) > 55:
        flags.append("too-long")
    if status in {"error", "suggestion"} and not any(
            verb in lowered for verb in ACTION):
        flags.append("not-actionable")
    if INTERNAL_ID.search(text):
        flags.append("internal-id")
    if not text.strip():
        flags.append("empty")
    return flags


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", default="artifacts/syntutor-stress-report.json")
    parser.add_argument("--output", default="artifacts/learner-xai-quality.json")
    args = parser.parse_args()
    corpus = json.loads((ROOT / args.corpus).read_text(encoding="utf-8"))
    sentences = [row["sentence"] for row in corpus.get("results", [])]
    flag_counts = Counter()
    readings = []
    findings = []
    worst = []
    for sentence in sentences:
        payload = build_payload(sentence)
        for detail_id, detail in (payload.get("node_details") or {}).items():
            if detail.get("status") not in {"error", "suggestion"}:
                continue
            text = (detail.get("text") or "").strip()
            fix = ((detail.get("remediation") or {}).get("suggested_fix") or "").strip()
            combined = text + (" " + fix if fix else "")
            flags = _flags(combined, detail.get("status"))
            for flag in flags:
                flag_counts[flag] += 1
            ease = _flesch(combined)
            if ease is not None:
                readings.append(ease)
            findings.append({
                "sentence": sentence, "detail": detail_id,
                "constraint": detail.get("constraint"),
                "status": detail.get("status"),
                "words": len(_words(combined)), "flesch": ease,
                "flags": flags, "text": text, "fix": fix,
            })
        analysis = payload.get("br_analysis") or {}
        if analysis.get("status") == "normalized" and analysis.get("tree"):
            graph = explain_analysis({**analysis, "sentence": sentence}).get("fact_graph")
            if graph:
                seen = Counter()
                for node in graph["nodes"]:
                    text = compose_learner_explanation(
                        graph, node_id=node["node_id"]).get("text", "")
                    seen[text] += 1
                for text, count in seen.items():
                    if count > 1:
                        flag_counts["repeated-within-sentence"] += count - 1
    readings.sort()
    report = {
        "schema_version": "learner-xai-quality-1.0.0",
        "sentences": len(sentences),
        "findings": len(findings),
        "flag_counts": dict(flag_counts),
        "reading_ease": {
            "mean": round(sum(readings) / len(readings), 1) if readings else None,
            "median": readings[len(readings) // 2] if readings else None,
            "min": readings[0] if readings else None,
            "max": readings[-1] if readings else None,
        },
        "worst": sorted(
            [row for row in findings if row["flags"]],
            key=lambda row: (len(row["flags"]), row["words"]),
            reverse=True)[:40],
        "detailed": findings,
    }
    destination = ROOT / args.output
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8")
    print(json.dumps({
        "sentences": len(sentences), "findings": len(findings),
        "flag_counts": dict(flag_counts), "reading_ease": report["reading_ease"],
    }, ensure_ascii=True))
    for row in report["worst"][:12]:
        print("FLAG", row["flags"], "|", row["constraint"], "|", row["words"], "w |",
              row["sentence"][:50], "|", row["text"][:90])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
