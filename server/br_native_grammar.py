"""Book-linked, conservative Burton–Roberts construction auditing.

This module deliberately separates *shape recognition* from *linguistic proof*.
A known parent/child pattern is not sufficient to certify complement selection,
movement, control, attachment, or interpretation. Callers must not turn the
"pattern_covered" result into a grammaticality verdict.

The source JSON is a versioned *draft* catalog. Its per-record review state is
visible and no automatic promotion to "human verified" takes place.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any
import json
import re

CATALOG = Path(__file__).resolve().parents[1] / "grammar/br_native_constructions.json"
_PENN = re.compile(
    r"^(?:ROOT|TOP|SBARQ?|SINV|SQ|FRAG|ADJP|ADVP|PRP\$?|WDT|WP\$?|WHNP|WHPP|WHADVP|WHADJP|"
    r"NNP?S?|VB[DPZGN]?|VBP|VBZ|MD|RB[RS]?|JJ[RS]?|DT|IN|CC|CD|NML|NX)$"
)
_VALID_VERSIONS = {"FINAL", *(f"V{i}" for i in range(1, 11))}


def _validated_registry(raw: dict[str, Any]) -> dict[str, Any]:
    if raw.get("schema_version") != "0.1.0":
        raise ValueError("Unsupported B–R construction registry schema")
    if not isinstance(raw.get("rules"), list) or not isinstance(raw.get("obligations"), list):
        raise ValueError("B–R construction registry requires rules and obligations")
    seen: set[str] = set()
    for section in ("rules", "obligations"):
        for row in raw[section]:
            rid = row.get("id")
            if not isinstance(rid, str) or not rid.startswith("BR") or rid in seen:
                raise ValueError("Construction IDs must be distinct B–R identifiers")
            seen.add(rid)
            chapter = row.get("chapter_introduced")
            if type(chapter) is not int or not 1 <= chapter <= 10:
                raise ValueError(f"{rid}: invalid introduction chapter")
            source = row.get("source")
            if not isinstance(source, dict) or not isinstance(source.get("printed_pages"), list):
                raise ValueError(f"{rid}: missing book-page references")
            if not source["printed_pages"] or not all(type(p) is int and 1 <= p <= 253 for p in source["printed_pages"]):
                raise ValueError(f"{rid}: invalid book-page reference")
            if section == "rules":
                if (not isinstance(row.get("parent"), str) or
                        not isinstance(row.get("children"), list) or
                        not all(isinstance(label, str) and label for label in row["children"]) or
                        not isinstance(row.get("condition"), str)):
                    raise ValueError(f"{rid}: incomplete structural pattern")
    return raw


@lru_cache(maxsize=1)
def load_br_construction_registry() -> dict[str, Any]:
    with CATALOG.open(encoding="utf-8") as stream:
        return _validated_registry(json.load(stream))


def _chapter(profile: dict[str, Any]) -> int:
    version = profile.get("version")
    chapter = profile.get("chapter")
    if version not in _VALID_VERSIONS:
        raise ValueError("Unknown B–R convention version")
    if version == "FINAL":
        if chapter != 10 or not profile.get("appendix_nom"):
            raise ValueError("FINAL must be the complete FINAL-D1 profile")
        return 10
    if type(chapter) is not int or version != f"V{chapter}":
        raise ValueError("Convention chapter/version mismatch")
    return chapter


def _child_type(node: dict[str, Any]) -> str:
    if "word" in node:
        return "@word"
    if node.get("symbol") == "E" and node.get("elided") is True:
        return "@ellipsis"
    if node.get("gap"):
        return "@gap"
    if node.get("empty"):
        return "@empty"
    # A triangle suppresses internal analysis, not its known category.
    # An unlabelled triangle is never silently assigned a category.
    if node.get("unlabelled") or (node.get("triangle") and node.get("label") is None):
        return "@unlabelled"
    if node.get("label") == "V" and node.get("verb_type") in ("I", "II"):
        return f"V({node['verb_type']})"
    return str(node.get("label", "@unknown"))


def audit_br_constructions(
    envelope: dict[str, Any],
    *,
    normalization_trace: list[dict[str, Any]] | None = None,
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Report rule-pattern coverage, not a guarantee of linguistic correctness.

    Unrecognized patterns are left UNCOVERED, not deemed ungrammatical:
    the catalog is intentionally incomplete and book conventions are
    chapter-sensitive. Penn category leakage *is* an invariant violation.
    """
    registry = _validated_registry(registry) if registry is not None else load_br_construction_registry()
    profile = envelope.get("convention_profile") or {}
    chapter = _chapter(profile)
    index: dict[tuple[str, tuple[str, ...]], list[dict[str, Any]]] = {}
    for rule in registry["rules"]:
        if rule["chapter_introduced"] > chapter:
            continue
        key = (rule["parent"], tuple(rule["children"]))
        index.setdefault(key, []).append(rule)

    covered: list[dict[str, Any]] = []
    unknown: list[dict[str, Any]] = []
    violations: list[dict[str, str]] = []
    examined = 0

    def visit(node: Any, path: str) -> None:
        nonlocal examined
        if not isinstance(node, dict):
            violations.append({"path": path, "code": "MALFORMED_NODE"})
            return
        label = node.get("label")
        if isinstance(label, str) and _PENN.fullmatch(label):
            # Some tags overlap real B-R categories (S, NP, VP): only the
            # *unambiguously* Penn-specific labels should ever be rejected.
            if label not in {"S", "NP", "VP"}:
                violations.append({"path": path, "code": "PENN_LABEL_LEAK", "label": label})
        children = node.get("children")
        if not isinstance(children, list) or not children:
            return
        examined += 1
        child_labels = tuple(_child_type(child) for child in children)
        matches = index.get((str(label), child_labels), [])
        detail = {"path": path, "parent": label, "children": list(child_labels)}
        if matches:
            covered.append({
                **detail, "rule_ids": [r["id"] for r in matches],
                "source_pages": sorted({page for r in matches for page in r["source"]["printed_pages"]}),
                "semantic_conditions_unchecked": True,
            })
        else:
            unknown.append(detail)
        for i, child in enumerate(children):
            visit(child, f"{path}/children/{i}")

    visit(envelope.get("root"), "root")
    trace = normalization_trace or []
    exact_reference = any(
        row.get("rule_id") == "EXACT_IMG_GOLD_REFERENCE" for row in trace
    )
    if violations:
        state = "invalid_label"
    elif exact_reference:
        state = "source_matched_unreviewed"
    elif unknown:
        state = "partially_covered"
    else:
        state = "shape_covered_semantics_unverified"
    return {
        "catalog_version": registry["schema_version"],
        "source_edition": registry["edition"],
        "state": state,
        "exact_reference_match": exact_reference,
        "pattern_coverage": {
            "matched": len(covered),
            "examined": examined,
            "fraction": round(len(covered) / examined, 4) if examined else None,
        },
        "covered_patterns": covered,
        "uncovered_patterns": unknown,
        "violations": violations,
        "semantic_conditions_checked": False,
        "independent_linguistic_review": False,
        "may_certify_grammaticality": False,
        "notice": (
            "These are book-linked structural signatures only, not a formal proof "
            "of attachment, selection, semantic interpretation, or universal B-R correctness."
        ),
    }
