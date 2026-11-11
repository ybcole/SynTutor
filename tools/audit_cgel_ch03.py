#!/usr/bin/env python3
"""Fail-closed Cambridge Chapter 3 QA inventory and candidate test-corpus builder.

Uses committed English grammar records and ledger only. Does NOT verify that a
linguistic claim matches the copyright-protected CGEL PDF, decide grammaticality,
approve rules, or enable runtime diagnoses. Source-level spot checks are documented
separately with printed-page references.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
CHAPTER = 3
START, END = 71, 212
CORPUS = Path("evaluation/cgel_ch03_candidate_corpus.json")
PREFIXES = {"AGR", "CLS", "COMP", "MORPH", "OTH", "PHR", "WCAT"}
LEGACY_WITHOUT_DIAGNOSTIC = {"AGR-002", "MORPH-004", "MORPH-005", "MORPH-006"}
CHECKED_CONSTRAINT_TYPES = {"constraint", "variety_restricted"}
NON_ERROR_TYPES = {"classification", "descriptive_generalization", "stylistic_or_prescriptive"}
ANNOTATED_GUARD_RE = re.compile(r"^(.*?)\s+\[([^\[\]]+)\]\s*$", re.S)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def source_pages(rule: dict) -> list[int]:
    return sorted({
        p for source in rule.get("sources", [])
        if source.get("chapter") == CHAPTER
        and "cambridge" in str(source.get("book", "")).lower()
        for p in source.get("pages", [])
        if isinstance(p, int) and not isinstance(p, bool)
    })


def normalize_guard(text: str) -> tuple[str, str | None]:
    """Remove an explicit test annotation, not a grammatical word or clause."""
    match = ANNOTATED_GUARD_RE.fullmatch(text)
    return (match.group(1).strip(), match.group(2).strip()) if match else (text.strip(), None)


def load_all_rules(root: Path = ROOT) -> list[dict]:
    rules = []
    for path in sorted((root / "grammar" / "rules").glob("*.json")):
        payload = load_json(path)
        if not isinstance(payload, list):
            raise ValueError(f"{path}: expected rule list")
        rules.extend(payload)
    return rules


def build_candidate_corpus(chapter_rules: list[dict]) -> dict:
    cases = []
    for rule in sorted(chapter_rules, key=lambda row: row["id"]):
        diagnostic = rule.get("diagnostic")
        if not isinstance(diagnostic, dict):
            continue
        rid = rule["id"]
        family = diagnostic["error_family"]
        pages = source_pages(rule)
        variety = diagnostic.get("variety_scope", "standard_english")
        common = {"rule_id": rid, "error_family": family,
                  "source_pages": pages, "variety_scope": variety}
        for ix, pair in enumerate(diagnostic.get("minimal_pairs", []), 1):
            pieces = pair.split("|||")
            if len(pieces) != 2 or not all(p.strip() for p in pieces):
                raise ValueError(f"{rid}: invalid candidate minimal pair {ix}")
            wrong, corrected = (part.strip() for part in pieces)
            cases.append({**common, "id": f"{rid}:error:{ix:02d}",
                          "kind": "error", "sentence": wrong,
                          "expected_correction": corrected,
                          "source_kind": "minimal_pair", "annotation": None})
        for ix, guard in enumerate(diagnostic.get("false_positive_guards", []), 1):
            valid, note = normalize_guard(guard)
            cases.append({**common, "id": f"{rid}:guard:{ix:02d}",
                          "kind": "valid", "sentence": valid,
                          "expected_correction": None,
                          "source_kind": "false_positive_guard", "annotation": note})
        for ix, example in enumerate(rule.get("examples", {}).get("correct", []), 1):
            if example.get("origin") != "ai_authored":
                continue  # no textbook examples duplicated into evaluation fixtures
            valid, note = normalize_guard(example["text"])
            cases.append({**common, "id": f"{rid}:correct:{ix:02d}",
                          "kind": "valid", "sentence": valid,
                          "expected_correction": None, "source_kind": "source_rule_example",
                          "annotation": note})
    family_counts: dict[str, dict[str, int]] = {}
    for case in cases:
        counts = family_counts.setdefault(case["error_family"], {"error": 0, "valid": 0})
        counts[case["kind"]] += 1
    coverage_gaps = {
        family: {"error_needed": max(0, 10 - counts["error"]),
                 "valid_needed": max(0, 10 - counts["valid"])}
        for family, counts in sorted(family_counts.items())
        if counts["error"] < 10 or counts["valid"] < 10
    }
    return {
        "schema_version": "cgel-ch03-candidate-corpus-1",
        "chapter": CHAPTER,
        "language_policy": "ENGLISH_ONLY",
        "authority": "SOURCE_EXTRACTED_CANDIDATES_NOT_GOLD_ADJUDICATED",
        "runtime_status": "not_enabled",
        "measurement_status": "not_evaluated",
        "diagnostic_rule_ids": sorted({case["rule_id"] for case in cases}),
        "total_cases": len(cases),
        "counts_by_family": dict(sorted(family_counts.items())),
        "families_below_full_10_10_gate": coverage_gaps,
        "cases": cases,
    }


def audit(root: Path = ROOT) -> tuple[dict, list[str], dict]:
    errors: list[str] = []
    all_rules = load_all_rules(root)
    by_id = {r.get("id"): r for r in all_rules}
    if len(by_id) != len(all_rules):
        errors.append("Rule IDs must be unique across all rule JSON files")
    chapter_rules = [r for r in all_rules if any(\n        s.get("chapter") == CHAPTER and "cambridge" in str(s.get("book", "")).lower()\n        for s in r.get("sources", []))]
    ledger = load_json(root / "grammar/coverage/cgel_ledger.json")["pages"]
    chapter_rows = [row for row in ledger if row.get("chapter") == CHAPTER]
    expected = list(range(START, END + 1))
    if [row.get("page") for row in chapter_rows] != expected:
        errors.append("Chapter 3 ledger must contain every page 71..212 in order")
    extracted = [row for row in chapter_rows if row.get("status") == "extracted"]
    skipped = [row for row in chapter_rows if row.get("status") == "skipped_with_reason"]
    if [r["page"] for r in skipped] != [71, 72, 73]:
        errors.append("Only the three documented chapter-contents pages may be skipped")
    if len(extracted) != 139 or any(row["page"] < 74 for row in extracted):
        errors.append("Chapter 3 requires 139 extracted expository pages")
    if len(extracted) + len(skipped) != len(chapter_rows):
        errors.append("Chapter 3 source-page inventory remains incomplete")
    for row in chapter_rows:
        path = row.get("evidence")
        if not isinstance(path, str) or not path.strip() or not (root / path).is_file():
            errors.append(f"p{row.get('page')}: missing or non-existent page evidence")
        if row.get("status") == "skipped_with_reason" and not row.get("reason"):
            errors.append(f"p{row.get('page')}: skip reason missing")

    counts = Counter()
    legacy_blockers = []
    spec_only = []
    unresolved_crosswalks = []
    by_type = Counter()
    for rule in chapter_rules:
        rid = rule.get("id", "")
        by_type[rule.get("rule_type")] += 1
        counts[rule.get("status")] += 1
        srcs = [s for s in rule.get("sources", [])
                if s.get("chapter") == CHAPTER
                and "cambridge" in str(s.get("book", "")).lower()]
        for source in srcs:
            pp = source.get("pages", [])
            if not pp or any(not (isinstance(p, int) and not isinstance(p, bool)
                                  and 74 <= p <= 212) for p in pp):
                errors.append(f"{rid}: source pages outside Chapter 3 expository range")
            if source.get("pdf_pages") != [p + 20 for p in pp]:
                errors.append(f"{rid}: full-volume PDF pages must equal printed+20")
        if not rule.get("concept") or not rule.get("statement") or not rule.get("condition"):
            errors.append(f"{rid}: missing concept/statement/condition")
        if len(rule.get("examples", {}).get("correct", [])) < 2:
            errors.append(f"{rid}: fewer than two correct original/attributed examples")
        if rule.get("rule_type") == "variety_restricted" and not rule.get("variety"):
            errors.append(f"{rid}: variety scope absent")
        incorrect = rule.get("examples", {}).get("incorrect", [])
        diagnostic = rule.get("diagnostic")
        if rule.get("rule_type") == "constraint" and len(incorrect) < 2:
            errors.append(f"{rid}: constraint missing two negative examples")
        if rule.get("rule_type") in NON_ERROR_TYPES and (incorrect or diagnostic):
            errors.append(f"{rid}: descriptive/style/classification must not supply error detector")
        if rule.get("rule_type") in CHECKED_CONSTRAINT_TYPES and diagnostic:
            if not isinstance(diagnostic, dict) or diagnostic.get("detector") != "spec_only":
                errors.append(f"{rid}: Chapter 3 has an unexpected enabled or invalid detector")
            else:
                spec_only.append(rid)
                guards = diagnostic.get("false_positive_guards", [])
                pairs = diagnostic.get("minimal_pairs", [])
                if len(guards) < 2 or len(pairs) < 2:
                    errors.append(f"{rid}: missing candidate minimal pairs or false-positive guards")
                incorrect_set = {example.get("text", "").strip() for example in incorrect}
                for pair in pairs:
                    halves = pair.split("|||")
                    if (len(halves) != 2 or not all(h.strip() for h in halves)
                            or halves[0].strip() not in incorrect_set):
                        errors.append(f"{rid}: candidate repair does not match a wrong example")
                if rule.get("rule_type") == "variety_restricted" and not str(
                        diagnostic.get("variety_scope", "")).startswith("variety_restricted:"):
                    errors.append(f"{rid}: variety-limited error lacks variety diagnostic scope")
        elif rule.get("rule_type") == "constraint":
            if rid in LEGACY_WITHOUT_DIAGNOSTIC and rule.get("status") == "APPROVED":
                legacy_blockers.append(rid)
            else:
                errors.append(f"{rid}: a new constraint lacks diagnostic specification")
        mappings = rule.get("burton_roberts_mapping") or []
        if not mappings:
            errors.append(f"{rid}: missing B-R mapping lifecycle entry")
        if any(m.get("relation") == "unverified" for m in mappings):
            unresolved_crosswalks.append(rid)
        for rel in rule.get("related_rules", []):
            if isinstance(rel, str) and rel not in by_id:
                errors.append(f"{rid}: related rule does not exist: {rel}")
    if set(legacy_blockers) != LEGACY_WITHOUT_DIAGNOSTIC:
        errors.append("The four documented legacy diagnostic blockers changed without a migration audit")
    if len(chapter_rules) < 695:
        errors.append("Chapter 3 rules unexpectedly declined below 695")
    if len(spec_only) < 35:
        errors.append("Chapter 3 diagnostic candidate count unexpectedly declined below 35")
    if len(all_rules) < 887:
        errors.append("The full catalog unexpectedly declined below 887")

    # Fail closed: a source-extracted candidate may never appear in the active registry.
    registry = load_json(root / "grammar/runtime_registry.json")
    enabled = {entry.get("rule_id") for entry in registry.get("enabled_rules", [])}
    unsafe = enabled.intersection({r.get("id") for r in chapter_rules
                                   if r.get("status") == "NEEDS_REVIEW"
                                   or (r.get("diagnostic") or {}).get("detector") == "spec_only"})
    if unsafe:
        errors.append("Source-only Chapter 3 rules were unsafely enabled: "
                      + ", ".join(sorted(str(x) for x in unsafe)))
    corpus = build_candidate_corpus(chapter_rules)
    if corpus["total_cases"] == 0:
        errors.append("No Chapter 3 candidate evaluation examples were generated")
    summary = {
        "chapter": CHAPTER,
        "source_pages": 142,
        "extracted_pages": len(extracted),
        "contents_only_skips": len(skipped),
        "unprocessed_chapter_pages": len(chapter_rows) - len(extracted) - len(skipped),
        "catalog_total": len(all_rules),
        "ch03_rules": len(chapter_rules),
        "chapter_rule_types": dict(sorted(by_type.items())),
        "chapter_statuses": dict(sorted(counts.items())),
        "diagnostic_spec_only": len(spec_only),
        "diagnostic_candidate_ids": sorted(spec_only),
        "legacy_diagnostic_blockers": sorted(legacy_blockers),
        "unverified_burton_roberts_crosswalks": len(unresolved_crosswalks),
        "runtime_eligible_claimed": 0,
        "candidate_cases": corpus["total_cases"],
        "candidate_family_counts": corpus["counts_by_family"],
        "candidate_family_gaps": corpus["families_below_full_10_10_gate"],
        "semantic_pdf_verification": "targeted_manual_checkpoints_only; not part of this automated test",
        "automated_gate_passed": not errors,
    }
    return summary, errors, corpus


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="compare candidate corpus and fail on QA problems")
    parser.add_argument("--write-corpus", action="store_true", help="write source-derived candidate corpus")
    parser.add_argument("--output", help="write JSON summary to path")
    opts = parser.parse_args()
    summary, errors, candidate = audit()
    path = ROOT / CORPUS
    if opts.write_corpus:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(candidate, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if opts.check:
        if not path.is_file():
            errors.append(f"Missing candidate corpus: {CORPUS}")
        elif load_json(path) != candidate:
            errors.append(f"Outdated or ungrounded candidate corpus: {CORPUS}")
    result = {"summary": summary, "errors": errors}
    text = json.dumps(result, indent=2, ensure_ascii=False)
    if opts.output:
        Path(opts.output).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
