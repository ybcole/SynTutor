"""XAI-PRE contracts: source approval boundaries and multi-error correction lineage.

This module validates *records*, NOT English grammaticality. It does not run
Benepar, modify the canonical B-R tree, or activate Cambridge grammar rules.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = ROOT / "grammar/xai_pre/source_audit.json"
SCHEMA_PATH = ROOT / "docs/xai/diagnosis-repair-pre.schema.json"
FIXTURE_PATH = ROOT / "grammar/xai_pre/preflight_fixtures.json"

RULE_STATES = frozenset({
    "SATISFIED", "VIOLATED", "NOT_APPLICABLE", "BLOCKED",
    "AMBIGUOUS", "UNIMPLEMENTED",
})
RELATIONSHIPS = frozenset({
    "SHARES_GOVERNOR", "SHARES_CONSTRUCTION", "OVERLAPS_SPAN",
    "CHECK_DEPENDS_ON", "CHECK_BLOCKED_BY", "REPAIR_CONFLICTS",
    "REPAIR_ENABLES", "REPAIR_MASKS", "ALTERNATIVE_INTERPRETATION",
})
OUTCOME_TO_CHECK = {
    "resolved_by_satisfaction": "SATISFIED",
    "no_longer_applicable_after_rewrite": "NOT_APPLICABLE",
    "persists": "VIOLATED",
    "blocked": "BLOCKED",
    "ambiguous": "AMBIGUOUS",
    "not_applicable": "NOT_APPLICABLE",
    "unimplemented": "UNIMPLEMENTED",
    "newly_violated": "VIOLATED",
    "newly_unmasked": "VIOLATED",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate_source_audit(data: dict[str, Any]) -> dict[str, int]:
    """Check that an evidence inventory cannot masquerade as runtime approval.

    Chapter rows report *availability and scoped extraction*, not comprehensive
    linguistic review of the complete volumes.
    """
    _require(data.get("schema_version") == "xai-pre-source-audit-1.0",
             "Unknown XAI-PRE source-audit contract")
    books = {b.get("id"): b for b in data.get("books", [])}
    _require(set(books) == {"BR3", "CGEL"}, "Expected both primary book editions")
    _require(books["BR3"].get("year") == 2011 and
             books["CGEL"].get("year") == 2002,
             "Primary book edition/year mismatch")
    _require(books["CGEL"].get("physical_printing") == "not_established",
             "Do not invent a Cambridge printing date")

    chapter_ids: set[tuple[str, int]] = set()
    for row in data.get("chapters", []):
        book = row.get("book_id")
        number = row.get("chapter")
        _require(book in books and type(number) is int and
                 1 <= number <= books[book]["chapter_count"],
                 "Unknown book/chapter in source inventory")
        key = (book, number)
        _require(key not in chapter_ids, f"Duplicate source chapter {key}")
        chapter_ids.add(key)
        _require(type(row.get("printed_start")) is int and
                 type(row.get("printed_end")) is int and
                 row["printed_end"] >= row["printed_start"] > 0,
                 "Invalid printed page range")
        _require(row.get("coverage") == "not_exhaustively_reviewed_for_xai",
                 "Do not promote chapter topic inventory into full review")
    _require(len(chapter_ids) == 31, "Chapter inventory must have 11 B-R and 20 CGEL rows")

    claims = {}
    for row in data.get("claims", []):
        cid = row.get("id")
        _require(isinstance(cid, str) and cid not in claims, "Invalid/duplicate claim ID")
        claims[cid] = row
        src = row.get("source") or {}
        _require(src.get("book_id") in books, f"{cid}: source book missing")
        chapter = src.get("chapter")
        if chapter is None:
            _require(src.get("book_id") == "BR3" and
                     src.get("printed_locator") == "preface ix–x",
                     f"{cid}: unsupported unnumbered source")
        else:
            _require(type(chapter) is int and
                     (src["book_id"], chapter) in chapter_ids,
                     f"{cid}: source chapter not in manifest")
            pages = src.get("printed_pages")
            _require(isinstance(pages, list) and bool(pages) and
                     all(type(p) is int and
                         next(c for c in data["chapters"]
                              if (c["book_id"], c["chapter"]) ==
                              (src["book_id"], chapter))["printed_start"] <= p <=
                         next(c for c in data["chapters"]
                              if (c["book_id"], c["chapter"]) ==
                              (src["book_id"], chapter))["printed_end"]
                         for p in pages),
                     f"{cid}: source page outside chapter")
        review = row.get("review") or {}
        runtime = row.get("runtime") or {}
        _require(review.get("source_passage_inspected") is True and
                 review.get("independent_human_review") is False and
                 review.get("approval") == "pending_independent_review",
                 f"{cid}: unsubstantiated source sign-off")
        _require(runtime.get("constraint_enabled") is False and
                 runtime.get("may_issue_grammatical_verdict") is False,
                 f"{cid}: source review alone cannot enable runtime grammar")
    _require(len(claims) >= 10, "XAI-PRE requires documented targeted source passages")

    crosswalk_ids = set()
    for row in data.get("crosswalks", []):
        cid = row.get("id")
        _require(isinstance(cid, str) and cid not in crosswalk_ids,
                 "Duplicate crosswalk identifier")
        crosswalk_ids.add(cid)
        left = claims.get(row.get("br_claim_id"), {})
        right = claims.get(row.get("cgel_claim_id"), {})
        _require(left.get("source", {}).get("book_id") == "BR3" and
                 right.get("source", {}).get("book_id") == "CGEL",
                 f"{cid}: both primary source claims required")
        _require(row.get("relation") in
                 {"compatible", "terminology_differs", "analysis_differs",
                  "not_covered", "unresolved"},
                 f"{cid}: unknown relation")
        _require(row.get("review_status") in
                 {"source_compared_pending_independent_linguist_approval",
                  "requires_specific_comparative_tree_source_review"},
                 f"{cid}: cannot self-certify source comparison")
        _require(row.get("may_change_br_tree_labels") is False,
                 f"{cid}: Cambridge cannot silently rename B-R tree categories")

    return {"books": len(books), "chapters": len(chapter_ids),
            "source_passages": len(claims), "crosswalks": len(crosswalk_ids),
            "approved_runtime_constraints": 0}


def _check_tokens(text: str, tokens: list[dict[str, Any]], version: str,
                  seen_global: set[str]) -> set[str]:
    ids: set[str] = set()
    previous_end = 0
    for token in tokens:
        ident = token["id"]
        start, end = token["start"], token["end"]
        _require(ident not in ids and ident not in seen_global,
                 f"{version}: reused or duplicate token identifier {ident}")
        _require(type(start) is int and type(end) is int and
                 previous_end <= start < end <= len(text),
                 f"{version}: token span invalid or out of order")
        _require(text[start:end] == token["text"],
                 f"{version}: token surface does not match original text")
        ids.add(ident)
        seen_global.add(ident)
        previous_end = end
    _require(bool(ids), f"{version}: no token coverage")
    return ids


def _apply_edits(text: str, edits: list[dict[str, Any]],
                 token_ids: set[str], token_rows: list[dict[str, Any]]) -> str:
    ordered = sorted(edits, key=lambda x: (x["start"], x["end"]))
    _require(bool(ordered), "Candidate must include at least one edit")
    previous_end = 0
    pieces = []
    for edit in ordered:
        start, end, replacement = edit["start"], edit["end"], edit["replacement"]
        _require(type(start) is int and type(end) is int and
                 previous_end <= start <= end <= len(text),
                 "Overlapping edits or invalid character offsets")
        op = edit["operation"]
        _require((op == "insert" and start == end and bool(replacement)) or
                 (op == "delete" and start < end and replacement == "") or
                 (op == "replace" and start < end and bool(replacement)),
                 "Edit operation and replacement are inconsistent")
        overlapping = {row["id"] for row in token_rows
                       if row["start"] < end and row["end"] > start}
        supplied = edit["original_token_ids"]
        _require(len(supplied) == len(set(supplied)) and
                 set(supplied) <= token_ids,
                 "Edit contains invalid or duplicated token IDs")
        if op != "insert":
            _require(bool(overlapping) and set(supplied) == overlapping,
                     "Edit provenance must enumerate every affected parent token")
        else:
            _require(not supplied, "Insert must not invent an affected token")
        pieces.extend([text[previous_end:start], replacement])
        previous_end = end
    pieces.append(text[previous_end:])
    return "".join(pieces)


def validate_diagnosis_repair_case(
    data: dict[str, Any], *, enabled_rule_ids: set[str] | None = None,
) -> dict[str, int]:
    """Validate a mock or future runtime record; never diagnose grammar itself."""
    from jsonschema import Draft202012Validator
    schema = load_json(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    problems = sorted(Draft202012Validator(schema).iter_errors(data),
                      key=lambda error: str(list(error.absolute_path)))
    _require(not problems, "XAI contract schema: " + "; ".join(
        f"{'.'.join(map(str, err.absolute_path))}: {err.message}"
        for err in problems[:5]))

    enabled = enabled_rule_ids or set()
    original = data["original"]
    _require(data["global_verdict"]["whole_sentence_certified"] is False,
             "XAI-PRE cannot certify whole-sentence grammaticality")
    _require(original["version_id"] == "u0",
             "XAI-PRE fixtures use immutable original version u0")
    tokens_seen_global: set[str] = set()
    orig_ids = _check_tokens(original["text"], original["tokens"], "u0",
                             tokens_seen_global)
    if original["analysis_status"] in {"unresolved", "not_evaluated"}:
        _require(original["tree_ref"] is None,
                 "A missing/unverified tree cannot be advertised as an available tree")

    findings = {}
    for f in data["findings"]:
        ident = f["id"]
        _require(ident not in findings, f"Duplicate finding ID {ident}")
        findings[ident] = f
        _require(len(f["affected_token_ids"]) ==
                 len(set(f["affected_token_ids"])) and
                 set(f["affected_token_ids"]) <= orig_ids,
                 f"{ident}: affected tokens do not belong to original input")
        _require(f["status"] in RULE_STATES,
                 f"{ident}: invalid partial evaluation state")
        if data["mode"] == "simulation":
            _require(f["rule_id"].startswith("DEMO-") and
                     f["runtime_eligible"] is False,
                     f"{ident}: simulation must not claim production rule authority")
        else:
            _require(f["rule_id"] in enabled or
                     f["status"] in {"UNIMPLEMENTED", "BLOCKED", "AMBIGUOUS",
                                    "NOT_APPLICABLE"},
                     f"{ident}: disabled rule cannot make a definitive judgment")
            if f["status"] in {"SATISFIED", "VIOLATED"}:
                _require(f["runtime_eligible"] is True and
                         bool(f["proof_atom_ids"]) and
                         bool(f["source_claim_ids"]),
                         f"{ident}: definitive result needs active rule and source proof")

    edges: set[tuple[str, str, str]] = set()
    for edge in data["dependencies"]:
        _require(edge["from"] in findings and edge["to"] in findings and
                 edge["from"] != edge["to"] and edge["kind"] in RELATIONSHIPS,
                 "Error dependency must connect distinct original findings")
        key = (edge["from"], edge["to"], edge["kind"])
        _require(key not in edges, "Duplicate error dependency")
        edges.add(key)

    grouped: set[str] = set()
    groups = set()
    for group in data["groups"]:
        _require(group["id"] not in groups, "Duplicate group identifier")
        groups.add(group["id"])
        for fid in group["finding_ids"]:
            _require(fid in findings and fid not in grouped,
                     "Missing or multiply grouped original finding")
            grouped.add(fid)
        if group["coupling"] == "independent":
            _require(len(group["finding_ids"]) == 1,
                     "Independent issue group must have one original finding")
    needed = {ident for ident, f in findings.items()
              if f["status"] in {"VIOLATED", "BLOCKED", "AMBIGUOUS"}}
    _require(grouped == needed,
             "All violations/blocked/ambiguous findings need exactly one issue group")

    versions = {"u0": {"text": original["text"], "tokens": original["tokens"],
                        "token_ids": orig_ids}}
    all_candidate_texts = {original["text"]}
    for c in data["candidates"]:
        version, parent = c["version_id"], c["parent_version_id"]
        _require(version not in versions and parent in versions,
                 "Candidate tree/version lineage has a cycle or forward parent")
        previous = versions[parent]
        expected_text = _apply_edits(previous["text"], c["edits"],
                                     previous["token_ids"], previous["tokens"])
        _require(c["text"] == expected_text,
                 f"{version}: candidate text does not equal actual proposed edits")
        _require(c["text"] not in all_candidate_texts,
                 f"{version}: repeated sentence in correction history")
        all_candidate_texts.add(c["text"])
        token_ids = _check_tokens(c["text"], c["tokens"], version,
                                  tokens_seen_global)
        versions[version] = {"text": c["text"], "tokens": c["tokens"],
                             "token_ids": token_ids}
        if c["analysis_status"] in {"unresolved", "not_evaluated"}:
            _require(c["tree_ref"] is None,
                     f"{version}: cannot expose a nonexistent verified tree")
        _require(set(c["targets"]) <= set(findings),
                 f"{version}: targeted error references original sentence only")
        outcomes = {}
        for row in c["lineage"]:
            fid = row["finding_id"]
            _require(fid in findings and fid not in outcomes,
                     f"{version}: duplicate/unknown original finding")
            outcomes[fid] = row
            _require(OUTCOME_TO_CHECK[row["after"]] == row["recheck_status"],
                     f"{version}: outcome and recheck disagree for {fid}")
            if row["after"] == "newly_violated":
                _require(findings[fid]["status"] == "SATISFIED",
                         f"{version}: newly violated requires prior satisfied evidence")
            if row["after"] == "newly_unmasked":
                _require(findings[fid]["status"] in {"BLOCKED", "AMBIGUOUS"},
                         f"{version}: newly unmasked requires prior uncertainty")
            if data["mode"] == "runtime" and row["after"] == "resolved_by_satisfaction":
                _require(bool(row.get("proof_atom_ids")),
                         f"{version}: cannot claim repair without new proof")
        _require(set(outcomes) == set(findings),
                 f"{version}: every original finding requires a lineage entry")
        introduced = set()
        for row in c["new_findings"]:
            nid = row["id"]
            _require(nid not in introduced and nid not in findings,
                     f"{version}: new finding has repeated/old ID")
            introduced.add(nid)
            previous_f = findings.get(row["prior_finding_id"])
            if row["origin"] == "unmasked":
                _require(previous_f is not None and
                         previous_f["status"] in {"BLOCKED", "AMBIGUOUS"},
                         f"{version}: unmasked finding needs prior blocked/ambiguous check")
            if row["origin"] == "introduced":
                _require(previous_f is not None and
                         previous_f["status"] == "SATISFIED" and
                         previous_f["rule_id"] == row["rule_id"] and
                         bool(row["causal_evidence_ids"]),
                         f"{version}: 'introduced' requires evidence of prior satisfaction")
            _require(row["origin"] != "unknown" or
                     row["prior_finding_id"] is None,
                     f"{version}: unknown-origin finding must not invent a prior linkage")

    return {"original_findings": len(findings), "issue_groups": len(groups),
            "candidates": len(data["candidates"]),
            "versions": len(versions), "definitively_enabled_rules": len(enabled)}
