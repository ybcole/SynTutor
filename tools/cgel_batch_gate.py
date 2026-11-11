#!/usr/bin/env python3
"""Fast *without weaker evidence*: one reusable QA gate per Cambridge source batch.

A batch manifest is a compact, page-by-page audit index, NOT a substitute for
reading the source. This checks ledger consistency, provenance, source-page
offsets, original examples, constraints and runtime nonactivation. It deliberately
does not pretend to verify linguistic truth from an agent's 'checked' flag.

Scaffold (placeholders deliberately FAIL the gate):
    python tools/cgel_batch_gate.py --scaffold --chapter 4 --start 213 --end 252 \
      --report sources/cambridge/chapter_04/PP213_252_REPORT.md \
      --output sources/cambridge/chapter_04/PP213_252_AUDIT.json

Verify an audited, completed batch:
    python tools/cgel_batch_gate.py --manifest sources/cambridge/chapter_04/PP213_252_AUDIT.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from jsonschema import Draft202012Validator
from tools.ledger import LEDGER, MANIFEST, load, ranges

REQUIRED_PAGE_FIELDS = {
    "page", "status", "section", "summary", "source_checked",
    "nonprose_present", "layout_checked", "exceptions_checked",
    "unresolved_items",
}
SAFE_STATUS = {"extracted", "skipped_with_reason", "absent_from_source"}
NO_ERROR_TYPES = {"classification", "descriptive_generalization", "stylistic_or_prescriptive"}
ERROR_TYPES = {"constraint", "variety_restricted"}


def _within_repo(root: Path, relative: Any) -> Path | None:
    if not isinstance(relative, str) or not relative.strip():
        return None
    candidate = (root / relative).resolve()
    if candidate == root.resolve() or not candidate.is_relative_to(root.resolve()):
        return None
    return candidate


def scaffold(chapter: int, start: int, end: int, report: str) -> dict[str, Any]:
    """Create an explicit not-checked-yet starting point; cannot certify a page."""
    if start < 1 or end < start:
        raise ValueError("Invalid printed-page range")
    return {
        "manifest_version": 1,
        "chapter": chapter,
        "printed_start": start,
        "printed_end": end,
        "report": report,
        "source_pdf_page_offset": None,
        "source_anchor": {"printed_page": None, "pdf_page": None},
        "added_rule_ids": [],
        "page_checks": [
            {
                "page": p, "status": "pending", "section": "", "summary": "",
                "source_checked": False, "nonprose_present": None,
                "layout_checked": False, "exceptions_checked": False,
                "unresolved_items": ["NOT_YET_READ"],
            }
            for p in range(start, end + 1)
        ],
    }


def check_batch(manifest: Any, root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    if not isinstance(manifest, dict):
        return ["Batch manifest must be a JSON object"]
    if manifest.get("manifest_version") != 1:
        errors.append("Unsupported manifest_version (expected 1)")
    chapter, start, end = (manifest.get(k) for k in ("chapter", "printed_start", "printed_end"))
    if any(type(v) is not int for v in (chapter, start, end)):
        return errors + ["Chapter and printed page bounds must be integers"]
    bounds = ranges(load(root / "sources/cambridge/source_manifest_2026-11-08.json"))
    if chapter not in bounds:
        return errors + [f"Unknown chapter {chapter}"]
    first, last = bounds[chapter]
    if start < first or end > last or end < start:
        return errors + [f"Batch {start}–{end} falls outside Chapter {chapter}: {first}–{last}"]
    report = _within_repo(root, manifest.get("report"))
    if report is None or not report.is_file() or report.suffix.lower() != ".md":
        errors.append("Report must be an existing Markdown source audit inside this repository")
    offset = manifest.get("source_pdf_page_offset")
    anchor = manifest.get("source_anchor")
    if type(offset) is not int or offset < 0 or not isinstance(anchor, dict):
        errors.append("A verified nonnegative full-volume PDF-page offset and source anchor are required")
    elif (anchor.get("printed_page") != start
          or anchor.get("pdf_page") != start + offset):
        errors.append("Source anchor must map the batch's first printed page to the checked PDF page")

    ledger = load(root / "grammar/coverage/cgel_ledger.json")
    rows = ledger["pages"]
    checks = manifest.get("page_checks")
    if not isinstance(checks, list) or len(checks) != end - start + 1:
        errors.append("Every printed page must have exactly one page_checks entry")
        checks = []
    if checks and [row.get("page") if isinstance(row, dict) else None for row in checks] != list(range(start, end + 1)):
        errors.append("Page checks must list every consecutive printed page exactly once")
    source_page_statuses = {}
    for item in checks:
        if not isinstance(item, dict):
            errors.append("Each page check must be an object")
            continue
        missing = REQUIRED_PAGE_FIELDS - set(item)
        if missing:
            errors.append(f"Page check missing fields: {sorted(missing)}")
            continue
        page = item["page"]
        if type(page) is not int or not start <= page <= end:
            errors.append(f"Invalid batch page: {page!r}")
            continue
        row = rows[page - 1]
        status = item["status"]
        source_page_statuses[page] = status
        if status not in SAFE_STATUS or status != row.get("status"):
            errors.append(f"p{page}: manifest status does not match a completed ledger entry")
        if row.get("chapter") != chapter or row.get("page") != page:
            errors.append(f"p{page}: ledger chapter/page mismatch")
        if status == "extracted":
            if report is not None and row.get("evidence") != report.relative_to(root.resolve()).as_posix():
                errors.append(f"p{page}: ledger evidence must link to this batch report")
            if item["source_checked"] is not True:
                errors.append(f"p{page}: source text not explicitly checked")
            if not isinstance(item["section"], str) or len(item["section"].strip()) < 2:
                errors.append(f"p{page}: source section not recorded")
            if not isinstance(item["summary"], str) or len(item["summary"].strip()) < 20:
                errors.append(f"p{page}: inadequate page-specific source summary")
            if type(item["nonprose_present"]) is not bool:
                errors.append(f"p{page}: unknown table/diagram/footnote presence")
            elif item["nonprose_present"] and item["layout_checked"] is not True:
                errors.append(f"p{page}: table/diagram/footnote layout was not checked")
            if item["exceptions_checked"] is not True:
                errors.append(f"p{page}: exception and qualification check not recorded")
            if not isinstance(item["unresolved_items"], list) or item["unresolved_items"]:
                errors.append(f"p{page}: unresolved source content prevents completed extraction")
        elif status in {"skipped_with_reason", "absent_from_source"}:
            if not isinstance(row.get("reason"), str) or not row["reason"].strip():
                errors.append(f"p{page}: a skip or absence requires a ledger reason")
            if item["source_checked"] is not True:
                errors.append(f"p{page}: source skip/absence not checked")
            if item.get("unresolved_items") not in ([],):
                errors.append(f"p{page}: skip/absence has unresolved source items")

    ids = manifest.get("added_rule_ids")
    if not isinstance(ids, list) or any(not isinstance(x, str) for x in ids):
        return errors + ["added_rule_ids must be a list of unique string IDs"]
    if len(ids) != len(set(ids)):
        errors.append("Duplicate IDs in batch added_rule_ids")
    if any(item.get("status") == "extracted" for item in checks if isinstance(item, dict)) and not ids:
        errors.append("An extracted source batch must cite its added rule IDs (or explain and split it)")
    all_rules = []
    for path in sorted((root / "grammar/rules").glob("*.json")):
        payload = load(path)
        if not isinstance(payload, list):
            errors.append(f"{path.name}: expected JSON rule array")
            continue
        all_rules.extend(payload)
    by_id = {rule.get("id"): rule for rule in all_rules if isinstance(rule, dict)}
    if len(by_id) != len(all_rules):
        errors.append("Duplicate or missing rule IDs in the full grammar catalog")
    schema = load(root / "grammar/schema.json")
    validator = Draft202012Validator(schema)
    runtime = load(root / "grammar/runtime_registry.json")
    enabled = {rule.get("rule_id") for rule in runtime.get("enabled_rules", [])
               if isinstance(rule, dict)}
    for rid in ids:
        rule = by_id.get(rid)
        if rule is None:
            errors.append(f"{rid}: ID not found in grammar rules")
            continue
        for failure in validator.iter_errors(rule):
            errors.append(f"{rid} {failure.json_path}: {failure.message}")
        if rid in enabled:
            errors.append(f"{rid}: freshly extracted rule already in production registry")
        if rule.get("status") != "NEEDS_REVIEW":
            errors.append(f"{rid}: newly extracted record must not claim independent approval")
        covered = set()
        for source in rule.get("sources", []):
            if source.get("chapter") != chapter or "cambridge" not in str(source.get("book", "")).lower():
                continue
            pages = source.get("pages", [])
            pdf_pages = source.get("pdf_pages")
            if (not isinstance(pages, list) or not pages
                    or any(type(p) is not int or p < first or p > last for p in pages)):
                errors.append(f"{rid}: invalid chapter source pages")
                continue
            if type(offset) is int and pdf_pages != [p + offset for p in pages]:
                errors.append(f"{rid}: full-volume PDF citations do not match verified offset")
            if any(rows[p - 1]["status"] != "extracted" for p in pages):
                errors.append(f"{rid}: cites a page not extracted from the source")
            covered.update(pages)
        if not covered.intersection(range(start, end + 1)):
            errors.append(f"{rid}: no Cambridge citation overlaps this batch")
        correct = rule.get("examples", {}).get("correct", [])
        wrong = rule.get("examples", {}).get("incorrect", [])
        if len(correct) < 2 or any(ex.get("origin") != "ai_authored" for ex in correct):
            errors.append(f"{rid}: requires at least 2 original English correct/contrast examples")
        rt = rule.get("rule_type")
        diagnostic = rule.get("diagnostic")
        if rt in NO_ERROR_TYPES and (wrong or diagnostic is not None):
            errors.append(f"{rid}: descriptive/style rule cannot be an error detector")
        if rt == "constraint":
            if len(wrong) < 2 or any(ex.get("origin") != "ai_authored" for ex in wrong):
                errors.append(f"{rid}: a constraint needs 2 original incorrect examples")
            if not isinstance(diagnostic, dict) or diagnostic.get("detector") != "spec_only":
                errors.append(f"{rid}: newly extracted constraint requires non-live spec_only diagnostics")
            elif (len(diagnostic.get("minimal_pairs", [])) < 2
                  or len(diagnostic.get("false_positive_guards", [])) < 2):
                errors.append(f"{rid}: missing 2 minimal pairs or 2 false-positive guards")
        if rt == "variety_restricted":
            if not rule.get("variety"):
                errors.append(f"{rid}: variety-restricted record needs its dialect/register")
            if diagnostic is not None and (not isinstance(diagnostic, dict)
                                            or diagnostic.get("detector") != "spec_only"):
                errors.append(f"{rid}: variety-restricted diagnostic cannot be live")
        mappings = rule.get("burton_roberts_mapping") or []
        if not mappings or any(x.get("relation") != "unverified" for x in mappings):
            errors.append(f"{rid}: fresh B-R crosswalks must remain unverified until independently checked")
    return errors


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--manifest", help="Committed JSON batch audit to validate")
    group.add_argument("--all", action="store_true", help="Validate every committed audit and new extracted page")
    group.add_argument("--scaffold", action="store_true", help="Create unverified page checklist template")
    p.add_argument("--chapter", type=int)
    p.add_argument("--start", type=int)
    p.add_argument("--end", type=int)
    p.add_argument("--report")
    p.add_argument("--output", help="Scaffold output JSON file")
    args = p.parse_args()
    if args.all:
        batches = sorted(ROOT.glob("sources/cambridge/chapter_*/PP*_AUDIT.json"))
        errors = []
        covered = set()
        indexed_rule_ids = set()
        for batch in batches:
            name = batch.relative_to(ROOT).as_posix()
            try:
                manifest = load(batch)
                errors.extend(f"{name}: {problem}" for problem in check_batch(manifest))
                page_checks = manifest.get("page_checks", [])
                for rid in manifest.get("added_rule_ids", []):
                    if not isinstance(rid, str):
                        continue  # The batch-level gate already reports malformed IDs.
                    if rid in indexed_rule_ids:
                        errors.append(f"{name}: {rid} indexed in multiple batch manifests")
                    indexed_rule_ids.add(rid)
                for item in page_checks:
                    if not isinstance(item, dict):
                        continue
                    page = item.get("page")
                    if type(page) is not int:
                        continue
                    if page in covered:
                        errors.append(f"{name}: page {page} is claimed by two batch audits")
                    covered.add(page)
            except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
                errors.append(f"{name}: invalid audit: {exc}")
        # Existing Chapter 3 reports predate structured batch manifests.
        # Future chapter page extraction cannot bypass this new gate simply by
        # omitting the corresponding batch audit from the PR.
        for row in load(LEDGER)["pages"]:
            if row.get("chapter") != 3 and row.get("status") == "extracted":
                if row.get("page") not in covered:
                    errors.append(f"p{row.get('page')}: new extracted page has no batch audit")
        # Future extraction records must be indexed exactly once. The original
        # 691 Chapter 3 Phase B records retain their historical reports.
        for path in sorted((ROOT / "grammar/rules").glob("*.json")):
            for rule in load(path):
                if rule.get("status") != "NEEDS_REVIEW":
                    continue
                if any(
                    source.get("chapter") != 3
                    and "cambridge" in str(source.get("book", "")).lower()
                    for source in rule.get("sources", [])
                ) and rule["id"] not in indexed_rule_ids:
                    errors.append(f"{rule['id']}: new rule missing from future batch manifests")
        print(json.dumps({"audits": len(batches), "pages_audited": len(covered),
                          "passed": not errors, "errors": errors[:60],
                          "error_count": len(errors)}, indent=2))
        return 1 if errors else 0
    if args.scaffold:
        if None in (args.chapter, args.start, args.end, args.report, args.output):
            p.error("--scaffold requires --chapter, --start, --end, --report and --output")
        bounds = ranges(load(MANIFEST))
        if args.chapter not in bounds or not (
            bounds[args.chapter][0] <= args.start <= args.end <= bounds[args.chapter][1]
        ):
            p.error("Scaffold range outside chapter boundaries")
        destination = _within_repo(ROOT, args.output)
        if destination is None:
            p.error("Scaffold destination must be inside repository")
        if destination.exists():
            p.error("Refusing to overwrite an existing batch audit")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(
            scaffold(args.chapter, args.start, args.end, args.report),
            indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Draft only (NOT verified): {destination.relative_to(ROOT)}")
        return 0
    manifest_path = _within_repo(ROOT, args.manifest)
    if manifest_path is None or not manifest_path.is_file():
        p.error("Batch manifest must exist in the repository")
    try:
        result = load(manifest_path)
        failures = check_batch(result)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        failures = [f"Invalid batch source audit: {exc}"]
    print(json.dumps({
        "batch": args.manifest,
        "passed": not failures,
        "errors": failures[:60],
        "error_count": len(failures)
    }, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
