"""Audit parser-backed learner explanations for self-reference and repeats.

Run after the stress harness:

    .venv/Scripts/python.exe scripts/audit_explanation_self_reference.py

The model-free lesson/gold coverage audit remains in
``scripts/audit_learner_explanations.py``. This script adds the live parser
path used by `/api/explain` and checks every node for:

- a phrase quote that repeats the node's own surface
  ("He forms one part of the larger expression 'He'");
- a word or lexical wrapper whose paragraph is identical to its parent;
- an empty position described as "this position" rather than an omitted part.

It is a reporting tool, not a grammar verdict.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "server"))

from api import build_payload  # noqa: E402
from explanations import explain_analysis  # noqa: E402
from learner_explanations import compose_learner_explanation  # noqa: E402

EXTRA_CASES = [
    "He gave to charity all the money she had left him.",
    "He is here.",
    "Who did the administrator say that submitted the application before the deadline?",
]

SELF_REFERENCE_PHRASES = (
    "larger expression", "is part of", "is a part of", "part of the larger",
    "position in", "built around", "beginning with", "preposition phrase",
    "verb phrase", "clause ", "in “",
)
# Nodes whose role genuinely depends on the whole clause/sentence may quote it.
SENTENCE_LEVEL_LABELS = {"V", "AUX", "MOD", "TENSE", "C1", "C2", "PERF",
                         "PROG", "PASS", "C"}
LEXICAL_LABELS = {"N", "V", "A", "Adv", "P", "PRO", "PRON", "pronoun", "ART",
                  "NAME", "name", "DEG", "Q", "QA", "POSS", "DEM", "V-part",
                  "PRE-DET", "PART", "Prt", "NEG", "MOD", "PERF", "PROG",
                  "PASS", "AUX", "TENSE", "DET", "C", "C1", "C2"}


def _quote(value: str) -> str:
    clean = " ".join(value.split())
    if len(clean) > 110:
        clean = clean[:107].rsplit(" ", 1)[0] + "..."
    return f"“{clean}”" if clean else "this position"


def _lexical_label(node, by_id):
    for ancestor_id in node.get("ancestor_ids") or []:
        ancestor = by_id.get(ancestor_id)
        if ancestor and ancestor.get("label") in LEXICAL_LABELS:
            return ancestor.get("label")
    return None


def audit_sentence(sentence: str) -> list[dict]:
    payload = build_payload(sentence)
    analysis = payload.get("br_analysis") or {}
    if analysis.get("status") != "normalized" or not analysis.get("tree"):
        return []
    evidence = explain_analysis({**analysis, "sentence": sentence})
    graph = evidence.get("fact_graph")
    if not graph:
        return []
    by_id = {node["node_id"]: node for node in graph["nodes"]}
    texts: dict[str, str] = {}
    problems = []
    for node in graph["nodes"]:
        text = compose_learner_explanation(
            graph, node_id=node["node_id"]).get("text", "")
        texts[node["node_id"]] = text
        surface = str(node.get("surface") or "").strip()
        parent = by_id.get(node.get("parent_id"))
        reasons = []
        if surface:
            for phrase in SELF_REFERENCE_PHRASES:
                if f"{phrase}“{surface}”" in text:
                    reasons.append(f"self-reference:{phrase.strip()}")
                    break
            if "this position" in text and node.get("kind") != "empty":
                reasons.append("this-position-on-overt-node")
        # Structural layers may legitimately repeat their parent; the UI
        # collapses them. Words and lexical wrappers must never do so.
        if (parent and parent.get("node_id") in texts
                and text == texts.get(parent["node_id"])
                and (node.get("kind") == "word"
                     or _lexical_label(node, by_id) is not None)):
            reasons.append("identical-to-parent")
        # Sentence-awareness: a local word or phrase should not quote the whole
        # sentence; only clause-level roles need that context.
        sentence_quote = _quote(sentence)
        if (surface and surface != sentence.strip()
                and sentence_quote in text):
            if node.get("kind") == "word":
                if _lexical_label(node, by_id) not in SENTENCE_LEVEL_LABELS:
                    reasons.append("over-context:full-sentence")
            elif node.get("label") in {"NP", "NOM", "PP", "AP", "AdvP", "PartP"}:
                reasons.append("over-context:full-sentence")
        if reasons:
            problems.append({
                "sentence": sentence,
                "node_id": node["node_id"],
                "label": node.get("label"),
                "surface": surface,
                "reasons": reasons,
                "text": text,
            })
    return problems


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", default="artifacts/syntutor-stress-report.json")
    parser.add_argument("--output", default="artifacts/explanation-self-reference-audit.json")
    args = parser.parse_args()
    report_path = ROOT / args.report
    sentences = []
    if report_path.exists():
        report = json.loads(report_path.read_text(encoding="utf-8"))
        sentences.extend(row["sentence"] for row in report.get("results", []))
    sentences.extend(EXTRA_CASES)
    seen = set()
    unique = [sentence for sentence in sentences
              if not (sentence in seen or seen.add(sentence))]
    problems = []
    for index, sentence in enumerate(unique, 1):
        print(f"[{index}/{len(unique)}] {sentence[:76]}", flush=True)
        problems.extend(audit_sentence(sentence))
    output = {
        "schema_version": "explanation-self-reference-audit-1.0.0",
        "sentences": len(unique),
        "problems": problems,
        "problem_count": len(problems),
    }
    destination = ROOT / args.output
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8")
    print(json.dumps({"sentences": len(unique), "problems": len(problems)},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
