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
        if (parent and parent.get("node_id") in texts
                and text == texts.get(parent["node_id"])):
            reasons.append("identical-to-parent")
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
