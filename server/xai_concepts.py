"""XAI-1 English-only B-R/Cambridge concept registry (not runtime teaching).

The primary-source inspection has been scoped to named printed pages.
Concepts and templates here are *candidates*. They are not imported by the
production explanation registry or Cambridge evaluator, and cannot classify
any student's sentence as grammatical/ungrammatical.
"""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
from string import Formatter
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "grammar/xai_concepts/catalog.json"
SCHEMA = ROOT / "grammar/xai_concepts/catalog.schema.json"
PRE_AUDIT = ROOT / "grammar/xai_pre/source_audit.json"
B_R_MANIFEST = ROOT / "sources/burton_roberts/source_manifest_2026-11-08.json"
CGEL_MANIFEST = ROOT / "sources/cambridge/source_manifest_2026-11-08.json"
LIVE_TEMPLATES = ROOT / "grammar/explanation_templates.json"
LIVE_CAMBRIDGE = ROOT / "grammar/runtime_registry.json"

ALLOWED_TOKENS = frozenset({"ENGLISH_ONLY"})
PRE_APPROVAL_STATUS = "SOURCE_CHECKED_PENDING_INDEPENDENT_REVIEW"
UNAPPROVED_STAGE = "XAI_2_3_CANDIDATE_NOT_RUNTIME_ELIGIBLE"
NON_ENGLISH_SENTINELS = ("nag-aaral", "kumain na", "mahirap today",
                         "pwede bang", "gusto ko", "kasi traffic",
                         "taglish", "filipino")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _need(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def _chapters():
    br = read_json(B_R_MANIFEST)
    cg = read_json(CGEL_MANIFEST)
    assert br["chapter_count"] == 11 and cg["chapter_count"] == 20
    chapters = {}
    for book_id, manifest in (("BR3", br), ("CGEL", cg)):
        for row in manifest["files"]:
            key = (book_id, row["chapter"])
            chapters[key] = (
                row["printed_start"],
                row["printed_end"] if book_id == "BR3"
                else row["printed_end_by_sequence"],
            )
    return chapters


def validate_catalog(data: dict[str, Any]) -> dict[str, Any]:
    """Validate links, page bounds, provenance and fail-closed activation status.

    Does not certify that a book-backed claim is correct: independent review
    must assess the linguistic claim, exceptions, variety and representative
    examples. Parser-backed applicability is deferred to XAI-2/4.
    """
    schema = read_json(SCHEMA)
    Draft202012Validator.check_schema(schema)
    failures = sorted(Draft202012Validator(schema).iter_errors(data),
                      key=lambda e: str(tuple(e.absolute_path)))
    _need(not failures, "XAI-1 schema validation: " + "; ".join(
        f"{'.'.join(map(str, e.absolute_path))}: {e.message}" for e in failures[:5]))
    _need(data["language_policy"] in ALLOWED_TOKENS,
          "XAI-1 concepts are strictly English-only")
    _need(data["source_audit_path"] == "grammar/xai_pre/source_audit.json",
          "Source authority must use the checked preflight audit")

    pre = read_json(PRE_AUDIT)
    _need(pre["status"] == "targeted_source_checks_pending_independent_review",
          "Preflight source authority unexpectedly changed")
    chapters = _chapters()
    _need(len(chapters) == 31, "Expected complete B-R/CGEL chapter inventory")

    concepts = {}
    by_book = Counter()
    by_kind = Counter()
    reviewed_pages = set()
    scoped_families = set()
    for c in data["concepts"]:
        ident = c["id"]
        _need(ident not in concepts, f"Duplicate concept ID {ident}")
        _need(ident.startswith(c["book_id"] + "-"),
              f"{ident}: source book prefix does not match")
        concepts[ident] = c
        key = (c["book_id"], c["chapter"])
        _need(key in chapters, f"{ident}: unknown source chapter")
        start, end = chapters[key]
        _need(all(start <= p <= end for p in c["printed_pages"]),
              f"{ident}: cited printed page outside declared chapter")
        _need(c["review"]["status"] == PRE_APPROVAL_STATUS and
              c["review"]["human_approved"] is False,
              f"{ident}: source check is not independent human approval")
        _need(not any(c["runtime"].values()),
              f"{ident}: pending source concepts cannot be live grammar or teaching rules")
        _need(c["scope"]["precondition"].strip() and
              c["scope"]["target_labels"] and c["scope"]["profiles"],
              f"{ident}: contextual applicability conditions missing")
        if c["kind"] == "constraint":
            _need(bool(c["pedagogy"]["examples"]["contrast"]) or
                  bool(c["pedagogy"]["examples"]["exception"]) or
                  bool(c["scope"]["exceptions"]),
                  f"{ident}: executable-constraint candidate needs counterexamples or exceptions")
        if c["book_id"] == "CGEL":
            _need(c["scope"]["profiles"] == ["FINAL-D1"],
                  f"{ident}: Cambridge concepts must not authorize early B-R chapter notation")
        else:
            _need("FINAL-D1" in c["scope"]["profiles"],
                  f"{ident}: B-R concept must have FINAL-D1 scope")
        by_book[c["book_id"]] += 1
        by_kind[c["kind"]] += 1
        for p in c["printed_pages"]:
            reviewed_pages.add((c["book_id"], c["chapter"], p))
        scoped_families.update(c["scope"]["target_labels"])
        for group in c["pedagogy"]["examples"].values():
            for ex in group:
                s = (ex["sentence"] + " " + ex["explanation"]).lower()
                _need(not any(marker in s for marker in NON_ENGLISH_SENTINELS),
                      f"{ident}: out-of-scope evaluation/example language")
    _need({"BR3", "CGEL"} <= set(by_book), "Both primary books must be represented")

    crosswalks = {}
    for w in data["crosswalks"]:
        ident = w["id"]
        _need(ident not in crosswalks, f"Duplicate crosswalk {ident}")
        crosswalks[ident] = w
        left = concepts.get(w["left"])
        right = concepts.get(w["right"])
        _need(left is not None and right is not None,
              f"{ident}: broken concept crosswalk reference")
        _need(left["book_id"] == "BR3" and right["book_id"] == "CGEL",
              f"{ident}: a crosswalk must connect B-R to Cambridge in that order")
        _need(w["do_not_auto_relabel"] is True,
              f"{ident}: Cambridge concepts must never relabel the B-R tree")
        _need(w["relation"] in {"compatible", "terminology_differs",
                                "analysis_differs", "not_covered", "unresolved"},
              f"{ident}: invalid crosswalk relation")
        _need(ident in left["crosswalk_ids"],
              f"{ident}: left-hand source concept has no reverse crosswalk")
    for c in concepts.values():
        _need(set(c["crosswalk_ids"]) <= set(crosswalks),
              f"{c['id']}: reference to unregistered crosswalk")

    templates = {}
    for t in data["template_candidates"]:
        ident = t["id"]
        _need(ident not in templates, f"Duplicate template candidate ID {ident}")
        templates[ident] = t
        concept = concepts.get(t["concept_id"])
        _need(concept is not None, f"{ident}: no provenance concept")
        _need(t["stage"] == UNAPPROVED_STAGE and t["requires_fact_graph"] is True,
              f"{ident}: template cannot be enabled before the XAI-2 fact graph")
        _need(t["target_label"] in concept["scope"]["target_labels"],
              f"{ident}: target label outside concept's reviewed source scope")
        for template_name in ("text", "deep_text"):
            try:
                parsed = list(Formatter().parse(t[template_name]))
            except ValueError as exc:
                raise ValueError(f"{ident}: malformed prose template") from exc
            slots = [part[1] for part in parsed if part[1] is not None]
            _need(all(slot in t["required_fact_keys"] for slot in slots),
                  f"{ident}: invented or unsupported placeholder")
            _need(all(slot.isidentifier() and slot.lower() == slot
                      for slot in slots),
                  f"{ident}: expression or attribute access prohibited")

    live_templates = read_json(LIVE_TEMPLATES)
    live_rules = read_json(LIVE_CAMBRIDGE)
    live_ids = {x["id"] for x in live_templates.get("templates", [])}
    _need(not (set(templates) & live_ids),
          "XAI-1 candidate collides with existing runtime template identifier")
    _need(len(live_rules.get("active_rules", [])) == 0,
          "Cannot claim XAI-1 baseline retains zero enabled Cambridge checks")

    return {
        "concepts_total": len(concepts),
        "concepts_by_book": dict(sorted(by_book.items())),
        "concepts_by_kind": dict(sorted(by_kind.items())),
        "source_checked_distinct_printed_pages": len(reviewed_pages),
        "source_checked_chapters": len({(c["book_id"], c["chapter"])
                                       for c in concepts.values()}),
        "candidate_crosswalks": len(crosswalks),
        "unresolved_or_different_crosswalks": sum(
            w["relation"] in {"unresolved", "analysis_differs", "not_covered"}
            for w in crosswalks.values()
        ),
        "template_candidates": len(templates),
        "source_checked_node_categories": sorted(scoped_families),
        "human_approved_concepts": 0,
        "new_runtime_templates": 0,
        "new_runtime_cambridge_constraints": 0,
    }


def load_catalog() -> dict[str, Any]:
    data = read_json(CATALOG)
    validate_catalog(data)
    return data


def pending_by_node(label: str, *, profile: str = "FINAL-D1") -> list[dict[str, Any]]:
    """Return *non-learner-facing* authoring candidates for XAI-2/3.

    Never turn these into live /api/explain prose without separate source
    approval, a licensed source construction and fact-specific evidence.
    """
    _need(isinstance(label, str) and len(label) <= 60, "Invalid B-R node label")
    _need(isinstance(profile, str) and len(profile) <= 32, "Invalid convention profile")
    registry = load_catalog()
    return [
        {"concept_id": c["id"], "book_id": c["book_id"],
         "printed_pages": c["printed_pages"], "status": "PENDING_INDEPENDENT_REVIEW",
         "runtime_eligible": False,
         "short": c["pedagogy"]["short"]}
        for c in registry["concepts"]
        if label in c["scope"]["target_labels"]
        and profile in c["scope"]["profiles"]
    ]
