#!/usr/bin/env python3
"""Measure exact complete-tree agreement against transcribed chapter fixtures.

This is source-fixture compliance, not independent free-sentence gold.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "server"))
from parse_engine import analyze  # noqa: E402
from burton_roberts import build_canonical_analysis  # noqa: E402
from br_tree import _atoms, _source_yield  # noqa: E402


def signature(node):
    if not isinstance(node, dict):
        return None
    # The canonical envelope represents ellipsis as an empty node and Chapter
    # 10 verb classes as V(I)/V(II) labels. Normalize both source spellings so
    # the comparison is about structure, not representation.
    if node.get("symbol") == "E" or node.get("elided") or node.get("empty"):
        label = node.get("label")
        if label in {"DET", "C1"}:
            # A reviewed zero-word DET/C1 is represented canonically as an
            # empty node; source fixtures may write a childless branch.
            return ("ZERO", label)
        return ("E",)
    label = node.get("label")
    if label == "Sentence":
        label = "S"
    if label in {"DET", "C1"}:
        children = node.get("children")
        if children is None or children == [] or all(
                isinstance(child, dict) and child.get("empty") for child in children):
            return ("ZERO", label)
    verb_type = node.get("verb_type")
    if label == "V" and verb_type in {"I", "II"}:
        label = f"V({verb_type})"
    word = node.get("word")
    return (
        label, word.casefold() if isinstance(word, str) else word,
        bool(node.get("triangle")),
        tuple(sorted(node.get("features") or [])),
        tuple(signature(child) for child in node.get("children") or []),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rows = []
    exact = normalized = unresolved = reference = 0
    partial = incorrect = legacy = 0
    mismatches = []
    for chapter in range(1, 11):
        path = ROOT / "web/content/book" / f"ch{chapter:02d}.trees.json"
        for record in json.loads(path.read_text(encoding="utf-8"))["trees"]:
            if record.get("status") != "IMG" or not record.get("sentence") or not record.get("tree"):
                continue
            if record.get("correct") is False:
                # Intentionally incorrect analyses are lesson contrasts, not
                # grammatical gold trees.
                incorrect += 1
                rows.append({"record_id": record["id"], "chapter": chapter,
                             "status": "incorrect_example", "exact": False})
                continue
            if chapter > 1 and record["tree"].get("label") == "Sentence":
                # A V1-era flat Sentence label cannot be a valid V2+ reference
                # (V2 requires S -> NP VP). Keep it as a lesson example rather
                # than pretending it is a complete canonical tree.
                legacy += 1
                rows.append({"record_id": record["id"], "chapter": chapter,
                             "status": "legacy_label_fixture", "exact": False})
                continue
            source_words = _source_yield(record["tree"])
            if source_words != _atoms(record["sentence"]):
                # Some records transcribe only the subtree under discussion.
                # They cannot be complete-tree gold for the whole sentence.
                partial += 1
                rows.append({"record_id": record["id"], "chapter": chapter,
                             "status": "partial_fixture", "exact": False})
                continue
            result = build_canonical_analysis(analyze(record["sentence"]), chapter=chapter)
            if result.get("status") != "normalized" or not result.get("tree"):
                unresolved += 1
                rows.append({"record_id": record["id"], "chapter": chapter,
                             "status": "unresolved", "exact": False})
                continue
            normalized += 1
            trace = [item.get("rule_id") for item in result.get("normalization_trace", [])]
            if "EXACT_IMG_GOLD_REFERENCE" in trace:
                reference += 1
            envelope = result["tree"]
            candidates = [envelope.get("root")]
            candidates.extend(alt.get("root") for alt in envelope.get("accepted_alternatives") or [])
            same = any(signature(candidate) == signature(record["tree"])
                       for candidate in candidates if isinstance(candidate, dict))
            exact += 1 if same else 0
            if not same:
                mismatches.append({"record_id": record["id"], "chapter": chapter,
                                   "sentence": record["sentence"]})
            rows.append({"record_id": record["id"], "chapter": chapter,
                         "status": "normalized", "exact": same,
                         "ambiguous": bool(result.get("ambiguous")),
                         "accepted_alternatives": len(envelope.get("accepted_alternatives") or [])})
    report = {
        "schema_version": "final-d1-exact-fixtures-1.1.0",
        "source": "web/content/book/ch01.trees.json..ch10.trees.json (IMG sentence-aligned)",
        "claim": "Exact complete-tree agreement against transcribed chapter fixtures; not independent free-sentence gold.",
        "source_img_records": normalized + unresolved + partial + incorrect + legacy,
        "complete_img_records": normalized + unresolved,
        "partial_fixtures": partial,
        "incorrect_examples": incorrect,
        "legacy_label_fixtures": legacy,
        "normalized": normalized,
        "exact_matches": exact,
        "exact_rate": round(exact / normalized, 4) if normalized else None,
        "reference_path_matches": reference,
        "unresolved": unresolved,
        "mismatches": mismatches,
        "rows": rows,
    }
    text = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
        print(f"wrote {args.output}")
    else:
        print(text)
    print({key: report[key] for key in (
        "source_img_records", "complete_img_records", "partial_fixtures",
        "incorrect_examples", "legacy_label_fixtures", "normalized",
        "exact_matches", "exact_rate", "reference_path_matches", "unresolved")})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
